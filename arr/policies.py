"""Client recovery policies A, B, Bw, C, D and D+I (PROTOCOL.md §3). A-fk is policy A run by a
runtime that issues a fresh op_key per attempt.

Isolation (V4): this module imports nothing. A policy object handles one logical operation. It
receives deep-copied observation dicts from the client runtime and returns a list of actions:
    {"type": "dispatch"}                         the runtime assigns the attempt_id, enforces the budget
    {"type": "status_read"}                      answered one tick later
    {"type": "set_timer", "delay": d, "tag": s}  delivered back as {"type": "timer", "tag": s}
Observation types: start, dispatched (runtime ack carrying the assigned attempt_id), response,
timeout, status, webhook, timer. belief() returns "unresolved", "complete" or "failed".
"""

POLL_INTERVAL = 5   # C, D, D+I (§2.2); V5 checks it equals the run constant
WAIT_TAU = 15       # Bw (§3); V5 checks it equals the run constant


def _dispatch(reason=""):
    action = {"type": "dispatch"}
    if reason:
        action["reason"] = reason
    return action


def _status():
    return {"type": "status_read"}


def _timer(delay, tag):
    return {"type": "set_timer", "delay": delay, "tag": tag}


class Policy(object):
    name = "?"

    def __init__(self):
        self.op_key = None
        self.payload_hash = None
        self.budget = 0
        self.attempts = []     # attempt_ids, from the runtime's `dispatched` acks
        self.keys = []         # op_keys used by those attempts (one key unless the runtime is A-fk)
        self._belief = "unresolved"

    def belief(self):
        return self._belief

    def report(self):
        return {"belief": self._belief, "attempts": list(self.attempts)}

    def budget_left(self):
        return len(self.attempts) < self.budget

    def observe(self, obs):
        kind = obs.get("type")
        if kind == "start":
            self.op_key = obs["op_key"]
            self.payload_hash = obs["payload_hash"]
            self.budget = obs["budget"]
            self.keys = [self.op_key]
            return [_dispatch()]
        if kind == "dispatched":
            self.attempts.append(obs["attempt_id"])
            if obs["op_key"] not in self.keys:
                self.keys.append(obs["op_key"])
            return []
        handler = {"response": self.on_response, "timeout": self.on_timeout, "status": self.on_status,
                   "webhook": self.on_webhook, "timer": self.on_timer}.get(kind)
        return handler(obs) if handler is not None else []

    def on_response(self, obs):
        return []

    def on_timeout(self, obs):
        return []

    def on_status(self, obs):
        return []

    def on_webhook(self, obs):
        return []

    def on_timer(self, obs):
        return []


# ---------------------------------------------------------------------------------------------
class PolicyA(Policy):
    """A: immediate retry. Operation-level 'last terminal-looking event wins'.

    Matching is by op_key only (no payload or attempt correlation). Failure-named webhooks
    (`aborted`, `deferred`) are mapped to failure by name (naive mapping, design update §2.4).
    Pre-freeze clarification C9: every failure signal is acted on whatever the current belief;
    budget exhaustion sets `failed` only if the belief is not `complete`."""
    name = "A"
    FAILURE_WEBHOOKS = ("aborted", "deferred")
    FAILURE_RESPONSES = ("error", "in_progress", "rejected")

    def _mine(self, obs):
        return obs.get("op_key") in self.keys

    def _retry_or_fail(self):
        if self.budget_left():
            return [_dispatch()]
        if self._belief != "complete":
            self._belief = "failed"
        return []

    def on_failure_signal(self, obs):
        return self._retry_or_fail()

    def on_response(self, obs):
        if not self._mine(obs):
            return []
        kind = obs.get("kind")
        if kind == "ok":
            self._belief = "complete"
            return []
        if kind in self.FAILURE_RESPONSES:
            return self.on_failure_signal(obs)
        return []   # `conflict` is not among A's signals

    def on_timeout(self, obs):
        return self.on_failure_signal(obs)

    def on_webhook(self, obs):
        if not self._mine(obs):
            return []
        event = obs.get("event")
        if event == "committed":
            self._belief = "complete"
            return []
        if event in self.FAILURE_WEBHOOKS:
            self._belief = "failed"
            return self.on_failure_signal(obs)
        return []   # `processing` ignored


class PolicyB(PolicyA):
    """B: one status read on every failure signal; `found` -> complete, anything else -> retry."""
    name = "B"

    def on_failure_signal(self, obs):
        return [_status()]

    def on_status(self, obs):
        if not self._mine(obs):
            return []
        if obs.get("result") == "found":
            self._belief = "complete"
            return []
        return self._retry_or_fail()   # includes not_found with terminal attempts


class PolicyBw(PolicyB):
    """Bw: B, but the single status read is issued WAIT_TAU ticks after the failure signal. At most
    one wait is pending; failure signals during the wait are absorbed. Pre-freeze clarification C15:
    if the belief is already `complete` when the wait ends, there is nothing to verify and no read
    is issued (implied by the study lead's S04 tie note)."""
    name = "Bw"

    def __init__(self):
        Policy.__init__(self)
        self.waiting = False

    def on_failure_signal(self, obs):
        if self.waiting:
            return []
        self.waiting = True
        return [_timer(WAIT_TAU, "verify")]

    def on_timer(self, obs):
        if obs.get("tag") != "verify":
            return []
        self.waiting = False
        if self._belief == "complete":
            return []
        return [_status()]


# ---------------------------------------------------------------------------------------------
class PolicyD(Policy):
    """D: reconcile with the §2.5 evidence rules; retry only when every dispatched attempt has its
    own terminal negative, no positive evidence exists and budget remains. Ambiguous evidence
    (timeout, error, not_found, processing, deferred) never triggers a retry."""
    name = "D"

    def __init__(self):
        Policy.__init__(self)
        self.positive = {}        # attempt_id -> [evidence labels]
        self.terminal = {}        # attempt_id -> [evidence labels]
        self.seen_events = []     # webhook event_ids already applied
        self.highest_seq = None
        self.conflicts = []
        self.ambiguous = False    # a timeout or error has been observed
        self.polling = False
        self.evidence = []        # evidence log: [t, label]

    def report(self):
        return {"belief": self._belief, "attempts": list(self.attempts),
                "positive": sorted(self.positive), "terminal": sorted(self.terminal),
                "conflicts": [dict(c) for c in self.conflicts], "highest_seq": self.highest_seq,
                "evidence": [list(e) for e in self.evidence]}

    def _note(self, obs, label):
        self.evidence.append([obs.get("t"), label])

    def _correlated(self, obs):
        # Correlation (§2.5): op_key and payload_hash match this operation, and the attempt is ours.
        return (obs.get("op_key") == self.op_key and obs.get("payload_hash") == self.payload_hash
                and obs.get("attempt_id") in self.attempts)

    def _positive(self, obs, label):
        if self._correlated(obs):
            self.positive.setdefault(obs["attempt_id"], []).append(label)
            self._note(obs, "positive: " + label)
        else:
            self._note(obs, "ignored uncorrelated: " + label)

    def _terminal(self, attempt_id, obs, label):
        # A terminal negative marks that attempt terminal, and it stays terminal.
        if attempt_id in self.attempts:
            self.terminal.setdefault(attempt_id, []).append(label)
            self._note(obs, "terminal %s: %s" % (attempt_id, label))

    # ---- observations
    def on_response(self, obs):
        attempt_id = obs.get("attempt_id")
        kind = obs.get("kind")
        if obs.get("op_key") != self.op_key or attempt_id not in self.attempts:
            self._note(obs, "ignored uncorrelated response " + str(kind))
            return self._after(obs)
        if kind == "ok":
            self._positive(obs, "response ok")
        elif kind in ("rejected", "in_progress", "conflict"):
            # Terminal negative for THIS attempt only (in_progress says nothing about the earlier one).
            self._terminal(attempt_id, obs, "response " + kind)
        elif kind == "error":
            self.ambiguous = True
            self._note(obs, "ambiguous: response error")
        return self._after(obs)

    def on_timeout(self, obs):
        self.ambiguous = True
        self._note(obs, "ambiguous: timeout " + str(obs.get("attempt_id")))
        return self._after(obs)

    def on_status(self, obs):
        if obs.get("op_key") != self.op_key:
            self._note(obs, "ignored uncorrelated status")
            return self._after(obs)
        if obs.get("result") == "found":
            self._positive(obs, "status found")
        else:
            # `not_found` itself is NOT authoritative (stale replica, or the attempt may still
            # commit). Only each listed terminal attempt is a terminal negative for that attempt.
            self._note(obs, "not authoritative: status not_found")
            for attempt_id in obs.get("terminal_attempts", []):
                self._terminal(attempt_id, obs, "status terminal_attempts")
        return self._after(obs)

    def on_webhook(self, obs):
        event_id = obs.get("event_id")
        if event_id in self.seen_events:
            self._note(obs, "duplicate delivery ignored " + str(event_id))   # §2.5 duplicates
            return []
        self.seen_events.append(event_id)
        if obs.get("op_key") != self.op_key:
            self._note(obs, "ignored uncorrelated webhook")
            return []
        seq = obs.get("provider_seq")
        stale = self.highest_seq is not None and seq <= self.highest_seq
        if stale:
            # §2.5 stale events: recorded, cannot regress state. Clarification C8: the only state
            # changes a webhook can make (add positive evidence, mark its own attempt terminal) are
            # monotone, so a stale event may add such facts but never reverts `complete`.
            self._note(obs, "stale (seq %s <= %s)" % (seq, self.highest_seq))
        else:
            self.highest_seq = seq
        event = obs.get("event")
        if event == "committed":
            self._positive(obs, "webhook committed")
        elif event == "aborted":
            self._terminal(obs.get("attempt_id"), obs, "webhook aborted")
        else:
            self._note(obs, "progress only: webhook " + str(event))   # processing, deferred
        return self._after(obs)

    def on_timer(self, obs):
        if obs.get("tag") != "poll":
            return []
        if self._belief == "unresolved":
            return [_status(), _timer(POLL_INTERVAL, "poll")]
        self.polling = False
        return []

    # ---- decision
    def _may_retry(self, obs):
        return True

    def _after(self, obs):
        actions = []
        # Conflict rule (§2.5): positive and terminal negative for the same attempt; the commit wins.
        listed = [c["attempt_id"] for c in self.conflicts]
        for attempt_id in sorted(self.positive):
            if attempt_id in self.terminal and attempt_id not in listed:
                self.conflicts.append({"t": obs.get("t"), "attempt_id": attempt_id,
                                       "positive": list(self.positive[attempt_id]),
                                       "negative": list(self.terminal[attempt_id])})
        if self.positive:
            self._belief = "complete"   # monotone commit: nothing later reverts it
            return actions
        all_terminal = bool(self.attempts) and all(a in self.terminal for a in self.attempts)
        if all_terminal:
            # A definitive negative for the operation: every dispatched attempt is terminal.
            if self.budget_left() and self._may_retry(obs):
                actions.append(_dispatch("all_attempts_terminal"))
                self._belief = "unresolved"
            else:
                self._belief = "failed"
        else:
            self._belief = "unresolved"
        if self.ambiguous and not self.polling and self._belief == "unresolved":
            # Clarification C7: polling starts at the first timeout or error, then every 5 ticks.
            self.polling = True
            actions.extend([_status(), _timer(POLL_INTERVAL, "poll")])
        return actions


class PolicyC(PolicyD):
    """C: D without retries, except after a synchronous `rejected` response that arrives before any
    timeout or error (clarification C12)."""
    name = "C"

    def _may_retry(self, obs):
        return (obs.get("type") == "response" and obs.get("kind") == "rejected" and not self.ambiguous)


class PolicyDI(PolicyD):
    """D+I: D plus, on contract 2 only, one resend with the same op_key and payload if the operation
    is still unresolved after its first timeout and one status poll (clarification C11: evaluated
    once, at the first status reply to a read issued at or after the first timeout, and skipped if
    D's own rule dispatched on that observation). On contract 1 it is exactly D."""
    name = "D+I"

    def __init__(self, idempotent_provider):
        PolicyD.__init__(self)
        self.idempotent_provider = bool(idempotent_provider)
        self.first_timeout_t = None
        self.resend_checked = False

    def on_timeout(self, obs):
        if self.first_timeout_t is None:
            self.first_timeout_t = obs.get("t")
        return PolicyD.on_timeout(self, obs)

    def on_status(self, obs):
        actions = PolicyD.on_status(self, obs)
        if (self.idempotent_provider and not self.resend_checked and self.first_timeout_t is not None
                and obs.get("t") is not None and obs.get("t") >= self.first_timeout_t + 1):
            self.resend_checked = True
            if (self._belief == "unresolved" and self.budget_left()
                    and not any(a.get("type") == "dispatch" for a in actions)):
                actions.append(_dispatch("idempotent_resend"))
                self._note(obs, "idempotent resend (contract 2 guarantees at most one effect)")
        return actions


def make(name, idempotent_provider):
    """Fresh policy object for one operation. `idempotent_provider` is client configuration
    (whether the provider documents contract-2 deduplication), not an observation."""
    if name in ("A", "A-fk"):
        return PolicyA()
    if name == "B":
        return PolicyB()
    if name == "Bw":
        return PolicyBw()
    if name == "C":
        return PolicyC()
    if name == "D":
        return PolicyD()
    if name == "D+I":
        return PolicyDI(idempotent_provider)
    raise KeyError(name)
