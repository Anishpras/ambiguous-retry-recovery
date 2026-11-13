"""Provider: contracts 1 and 2, attempt records, lagged status replica, webhook emission and the
private effect ledger (PROTOCOL.md §2.1-§2.4).

The provider talks to the engine only through sim.schedule / sim.log / sim.now, so a copy of it can
be run forward on its own (ORACLE-O's "will it ever commit" question, see sim.FastForward).
"""
import copy

from . import ids
from . import scenarios

# Phase constants duplicated here to avoid a circular import with sim.py.
PROVIDER, DELIVERY = 1, 2

SEQ_TICK = 1000   # provider_seq = SEQ_TICK * t_emit + index of the op's emission within that tick


class Attempt(object):
    """Provider-side (hidden) state of one dispatched attempt."""

    def __init__(self, logical_op, op_key, k, attempt_id, payload, script, dispatch_t):
        self.logical_op = logical_op          # scorer's operation (differs from op_key only for A-fk)
        self.op_key = op_key                  # key on the wire
        self.k = k
        self.attempt_id = attempt_id
        self.payload = copy.deepcopy(payload)
        self.payload_hash = ids.payload_hash(payload)
        self.script = script
        self.dispatch_t = dispatch_t
        self.state = "in_flight"   # in_flight|lost|rejected|pending|committed|aborted|in_progress_reply|replay_reply|conflict_reply
        self.arrive_t = None
        self.accepted_t = None     # set only if the attempt executes
        self.end_t = None          # commit or abort time
        self.commit_t = None
        self.violation = False


class Provider(object):
    def __init__(self, sim, scenario, contract):
        if contract not in (1, 2):
            raise ValueError("contract must be 1 or 2")
        self.sim = sim
        self.scenario = scenario
        self.contract = contract
        self.lag = scenario["lag"]          # int, or None for "never"
        self.options = sim.options          # named options (arr/options.py); defaults = frozen protocol
        self.attempts = {}                  # attempt_id -> Attempt, in dispatch order
        self.records = []                   # status replica source, append-only, time-ordered
        self.dedup = {}                     # contract 2: op_key -> active/released record
        self.ledger = []                    # PRIVATE effect ledger (scoring only)
        self.last_seq = {}
        self.seq_order_violations = []
        self.emissions = []
        self._tick_emits = {}               # (op_key, t) -> emissions so far in that tick
        self._emit_count = {}               # (attempt_id, event) -> emissions so far

    # ------------------------------------------------------------------ overridable identities
    def effect_id(self, op_key, attempt_id):
        return ids.effect_id(op_key, attempt_id)

    def provider_seq(self, att, event):
        """Per-op_key sequence, strictly increasing in emission order (§2.4).

        Clarification C1 (v1.0): derived from the emission clock, not a running count, because a
        count leaks hidden emissions (S08 vs S09 under V4). Fix M4 (v1.2): the v1.0 form
        100*t + 10*k + rank was not monotone when a later attempt emitted before an earlier one in
        the same tick (e.g. a delayed arrival); the value is now 1000*t_emit + j, where j is the
        index of this op's emission within that tick. Strictly monotone by construction; it leaks
        only same-tick emissions, never counts across ticks."""
        key = (att.op_key, self.sim.now)
        j = self._tick_emits.get(key, 0)
        self._tick_emits[key] = j + 1
        return self.sim.now * SEQ_TICK + j

    def event_id(self, att, event):
        """Opaque emission ID. Fix M4 (v1.2): a genuine repeat emission of the same event type for the
        same attempt (e.g. a provider that defers twice) gets a new ID; duplicated deliveries of one
        emission share it. The first emission keeps the v1.0 form."""
        key = (att.attempt_id, event)
        n = self._emit_count.get(key, 0)
        self._emit_count[key] = n + 1
        return ids.event_id(att.op_key, att.attempt_id, event, n)

    # ------------------------------------------------------------------ client-facing entry points
    def dispatch(self, logical_op, op_key, k, attempt_id, payload):
        script = scenarios.attempt_script(self.scenario, logical_op, k, self.options["retry_fault"])
        att = Attempt(logical_op, op_key, k, attempt_id, payload, script, self.sim.now)
        if attempt_id in self.attempts:
            raise ValueError("duplicate attempt id " + attempt_id)
        self.attempts[attempt_id] = att
        if script["arrive"] is None:
            # Lost before arrival: no record, no terminal negative, nothing can ever be observed.
            att.state = "lost"
            self.sim.log("request_lost", "network", False, logical_op, attempt_id=attempt_id)
            return
        at = self.sim.now + script["arrive"]
        self.sim.log("request_sent", "network", False, logical_op, attempt_id=attempt_id, arrives_at=at)
        self.sim.schedule(at, PROVIDER, "arrival", attempt_id)

    def status_reply(self, logical_op, op_key, t):
        """Status read issued at t, answered at t+1 from records with record_time <= t - L (§2.2).
        `not_found` is never authoritative; it carries the attempts the replica shows as aborted."""
        cutoff = None if self.lag is None else t - self.lag
        visible = [] if cutoff is None else [r for r in self.records
                                             if r["op_key"] == op_key and r["time"] <= cutoff]
        committed = [r for r in visible if r["state"] == "committed"]
        if committed:
            r = committed[0]   # earliest visible commit (records are time-ordered)
            obs = {"type": "status", "result": "found", "op_key": op_key, "effect_id": r["effect_id"],
                   "attempt_id": r["attempt_id"], "payload_hash": r["payload_hash"]}
        else:
            terminal = sorted(set(r["attempt_id"] for r in visible if r["state"] == "aborted"))
            obs = {"type": "status", "result": "not_found", "op_key": op_key, "terminal_attempts": terminal}
            if self.options["status_lists_pending"]:
                # Option: the reply also lists attempts the replica shows as accepted and not finished.
                ended = set(r["attempt_id"] for r in visible if r["state"] in ("committed", "aborted"))
                obs["pending_attempts"] = sorted(set(r["attempt_id"] for r in visible
                                                     if r["state"] == "accepted") - ended)
        truth = self._truth(logical_op, t)
        hidden = {"cutoff": cutoff, "visible_records": len(visible),
                  "true_effects_now": truth["effects"], "true_pending_now": truth["pending"]}
        return obs, hidden

    def _truth(self, logical_op, t):
        effects = ["%s@%d" % (e["attempt_id"].split("#")[-1], e["commit_time"]) for e in self.ledger
                   if e["logical_op"] == logical_op and e["commit_time"] <= t]
        pending = [a.attempt_id.split("#")[-1] for a in self.attempts.values()
                   if a.logical_op == logical_op and a.state == "pending"]
        return {"effects": effects, "pending": pending}

    # ------------------------------------------------------------------ phase-1 provider events
    def on_arrival(self, attempt_id):
        att = self.attempts[attempt_id]
        t = self.sim.now
        att.arrive_t = t
        s = att.script
        if s["decision"] == "reject":
            # Refused before execution: terminal negative, never executes, creates no record.
            att.state = "rejected"
            att.end_t = t
            self.sim.log("arrival_rejected", "provider", False, att.logical_op, attempt_id=attempt_id)
            self._respond(att, "rejected", {})
            return
        if self.contract == 2:
            rec = self.dedup.get(att.op_key)
            if rec is not None and t - rec["created"] > self.options["dedup_window"]:
                rec = None   # window expired (option; the default window covers the whole experiment)
            if rec is not None and rec["state"] == "aborted" and self.options["abort_record"] == "replay_failure":
                # Option: the stored failure is replayed; the key is burned and this attempt is
                # refused before execution (a terminal negative for it).
                att.state = "rejected"
                att.end_t = t
                self.sim.log("dedup_replay_failure", "provider", False, att.logical_op, attempt_id=attempt_id,
                             record_attempt=rec["attempt_id"])
                self._respond(att, "rejected", {})
                return
            if rec is not None and rec["state"] in ("pending", "committed"):
                # Contract 2 (§2.3): an active record for this key answers the attempt; no new effect.
                att.end_t = t
                if rec["payload_hash"] != att.payload_hash:
                    att.state = "conflict_reply"
                    self.sim.log("dedup_conflict", "provider", False, att.logical_op, attempt_id=attempt_id,
                                 record_attempt=rec["attempt_id"])
                    self._respond(att, "conflict", {})
                elif rec["state"] == "pending":
                    att.state = "in_progress_reply"
                    self.sim.log("dedup_in_progress", "provider", False, att.logical_op,
                                 attempt_id=attempt_id, record_attempt=rec["attempt_id"])
                    self._respond(att, "in_progress", {})
                else:
                    att.state = "replay_reply"
                    self.sim.log("dedup_replay", "provider", False, att.logical_op, attempt_id=attempt_id,
                                 record_attempt=rec["attempt_id"], effect_id=rec["effect_id"])
                    self._respond(att, "ok", {"payload_hash": rec["payload_hash"],
                                              "effect_id": rec["effect_id"]})
                return
            # No record, or an aborted (released) record: the attempt executes normally.
        att.state = "pending"
        att.accepted_t = t
        if self.contract == 2:
            self._dedup_on_accept(att)
        self._record(att, "accepted")
        self.sim.log("arrival_accepted", "provider", False, att.logical_op, attempt_id=attempt_id,
                     dedup_record=(self.contract == 2))
        self._emit(att, "processing", {})
        for d in s["deferred_after"]:
            self.sim.schedule(t + d, PROVIDER, "deferred", attempt_id)
        if s["commit_after"] is not None:
            self.sim.schedule(t + s["commit_after"], PROVIDER, "commit", attempt_id)
        else:
            self.sim.schedule(t + s["abort_after"], PROVIDER, "abort", attempt_id)

    def on_deferred(self, attempt_id):
        att = self.attempts[attempt_id]
        if att.state != "pending":
            return
        # Temporary failure; the provider keeps the attempt and retries internally (not authoritative).
        self.sim.log("deferred", "provider", False, att.logical_op, attempt_id=attempt_id)
        self._emit(att, "deferred", {})

    def on_commit(self, attempt_id):
        att = self.attempts[attempt_id]
        t = self.sim.now
        att.state = "committed"
        att.commit_t = att.end_t = t
        eid = self._commit_effect(att)
        if self.contract == 2:
            self._dedup_on_commit(att, eid)
        self._emit(att, "committed", {"payload_hash": att.payload_hash, "effect_id": eid})
        self._respond(att, "ok", {"payload_hash": att.payload_hash, "effect_id": eid})

    def on_abort(self, attempt_id):
        att = self.attempts[attempt_id]
        t = self.sim.now
        att.state = "aborted"
        att.end_t = t
        if self.contract == 2:
            self._dedup_on_abort(att)
        self._record(att, "aborted")
        self.sim.log("abort", "provider", False, att.logical_op, attempt_id=attempt_id)
        self._emit(att, "aborted", {})
        self._respond(att, "error", {})   # default for aborts; every scripted abort loses it
        if att.script["violation_commit_after"] is not None:
            self.sim.schedule(att.arrive_t + att.script["violation_commit_after"], PROVIDER,
                              "violation_commit", attempt_id)

    def on_violation_commit(self, attempt_id):
        """S15 only: the provider commits an attempt it already reported as aborted, violating its
        terminal-negative guarantee. The released dedup record is not consulted or restored
        (clarification C19), and no second response is sent."""
        att = self.attempts[attempt_id]
        att.state = "committed"
        att.commit_t = self.sim.now
        att.violation = True
        eid = self._commit_effect(att, violation=True)
        self._emit(att, "committed", {"payload_hash": att.payload_hash, "effect_id": eid})

    # ------------------------------------------------------------------ helpers
    def _commit_effect(self, att, violation=False):
        eid = self.effect_id(att.op_key, att.attempt_id)
        self.ledger.append({"effect_id": eid, "op_key": att.op_key, "logical_op": att.logical_op,
                            "attempt_id": att.attempt_id, "payload_hash": att.payload_hash,
                            "commit_time": self.sim.now, "violation": violation})
        self._record(att, "committed", effect_id=eid)
        self.sim.log("commit_after_abort" if violation else "commit", "provider", False, att.logical_op,
                     attempt_id=att.attempt_id, effect_id=eid)
        self.sim.log("ledger_entry", "scorer", False, att.logical_op, effect_id=eid,
                     attempt_id=att.attempt_id, commit_time=self.sim.now, violation=violation)
        return eid

    def _dedup_on_accept(self, att):
        # Contract 2: the record exists from acceptance (arrival), not from commit.
        if self.options["dedup_record_at"] == "acceptance":
            self.dedup[att.op_key] = {"attempt_id": att.attempt_id, "payload_hash": att.payload_hash,
                                      "state": "pending", "effect_id": None, "created": self.sim.now}

    def _dedup_on_commit(self, att, eid):
        rec = self.dedup.get(att.op_key)
        if self.options["dedup_record_at"] == "commit":
            # Option (mutant M3 as configuration): the record only appears when an attempt commits.
            self.dedup[att.op_key] = {"attempt_id": att.attempt_id, "payload_hash": att.payload_hash,
                                      "state": "committed", "effect_id": eid, "created": self.sim.now}
            return
        if rec is not None and rec["attempt_id"] == att.attempt_id:
            rec["state"] = "committed"
            rec["effect_id"] = eid

    def _dedup_on_abort(self, att):
        rec = self.dedup.get(att.op_key)
        if rec is not None and rec["attempt_id"] == att.attempt_id:
            rec["state"] = "aborted"   # released: a later attempt with this key executes normally

    def _record(self, att, state, effect_id=None):
        self.records.append({"time": self.sim.now, "op_key": att.op_key, "attempt_id": att.attempt_id,
                             "state": state, "payload_hash": att.payload_hash, "effect_id": effect_id})

    def _emit(self, att, event, extra):
        offsets = att.script["webhooks"].get(event)
        if offsets is None:
            return   # this event type is not emitted for this attempt
        seq = self.provider_seq(att, event)
        last = self.last_seq.get(att.op_key)
        if last is not None and seq <= last:
            self.seq_order_violations.append({"op_key": att.op_key, "t": self.sim.now, "seq": seq, "last": last})
        self.last_seq[att.op_key] = seq
        obs = {"type": "webhook", "event": event, "event_id": self.event_id(att, event),
               "provider_seq": seq, "op_key": att.op_key, "attempt_id": att.attempt_id}
        obs.update(extra)
        times = [self.sim.now + o for o in offsets]
        self.emissions.append({"t": self.sim.now, "event": event, "attempt_id": att.attempt_id, "seq": seq,
                               "deliveries": times})
        self.sim.log("webhook_emitted", "provider", False, att.logical_op, event=event, attempt_id=att.attempt_id,
                     provider_seq=seq, event_id=obs["event_id"], deliveries=times)
        if not offsets:
            self.sim.log("webhook_lost", "network", False, att.logical_op, event=event, attempt_id=att.attempt_id)
        for at in times:
            self.sim.schedule(at, DELIVERY, "webhook", copy.deepcopy(obs))

    def _respond(self, att, natural_kind, fields):
        """Each attempt gets at most one response, `after` ticks after the provider's decision
        (commit/abort for executed attempts; arrival for rejected and contract-2 replies)."""
        spec = att.script["response"]
        if spec is None:
            self.sim.log("response_lost", "network", False, att.logical_op, attempt_id=att.attempt_id,
                         kind=natural_kind)
            return
        kind = spec.get("kind", natural_kind)
        obs = {"type": "response", "kind": kind, "op_key": att.op_key, "attempt_id": att.attempt_id}
        if kind == "ok":
            if not fields:
                raise ValueError("an ok response needs an effect")
            obs.update(fields)
        at = self.sim.now + spec.get("after", 1)
        self.sim.log("response_sent", "provider", False, att.logical_op, attempt_id=att.attempt_id, kind=kind,
                     arrives_at=at)
        self.sim.schedule(at, DELIVERY, "response", {"logical_op": att.logical_op, "obs": obs})

    # ------------------------------------------------------------------ copies for ORACLE-O
    def clone(self, new_sim):
        memo = {id(self.sim): new_sim, id(self.scenario): self.scenario}
        return copy.deepcopy(self, memo)
