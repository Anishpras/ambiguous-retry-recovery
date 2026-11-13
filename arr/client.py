"""Client runtime (PROTOCOL.md §2.2, §3).

The runtime, not the policy, assigns attempt IDs, enforces the dispatch budget and the horizon,
fires local timeouts, and hands the policy deep-copied observation dicts. The policy returns
action dicts; nothing else crosses the boundary. Every observation and action list is also
recorded as canonical JSON in io_log, which V4 compares byte for byte between S08 and S09.
"""
import copy

from . import constants as K
from .ids import canonical_json
from .sim import BOOKKEEPING, CLIENT, DELIVERY

BELIEFS = ("unresolved", "complete", "failed")
ACTION_TYPES = ("dispatch", "status_read", "set_timer")


class PolicyClient(object):
    is_reference = False

    def __init__(self, sim, op, policy, policy_name, key_mode="stable"):
        self.sim = sim
        self.logical_op = op["op_key"]
        self.payload = copy.deepcopy(op["payload"])
        self.payload_hash = op["payload_hash"]
        self.start_t = op["start"]
        self.horizon_t = self.start_t + sim.options["horizon"]
        self.policy = policy
        self.policy_name = policy_name
        self.key_mode = key_mode          # "stable" (same op_key every attempt) or "fresh" (A-fk)
        self.attempts = []                # runtime's own dispatch records
        self.responded = set()
        self.io_log = []                  # canonical JSON of every observation and action list (V4)
        self.delivered = []               # observations the policy actually saw, in order
        self.belief = "unresolved"
        self.belief_changes = []
        self.first_complete_t = None
        self.belief_at_H = None
        self.report_at_H = None
        self.violations = []
        self.action_times = []
        self.status_reads = 0
        self.dispatches_after_complete = 0
        self.closed = False
        self._n_conflicts = 0

    # ------------------------------------------------------------------ engine callbacks
    def schedule_initial(self):
        self.sim.schedule(self.start_t, CLIENT, "op_start", self.logical_op)
        self.sim.schedule(self.horizon_t, BOOKKEEPING, "horizon", self.logical_op)

    def start(self):
        self._deliver({"type": "start", "op_key": self.logical_op, "payload": copy.deepcopy(self.payload),
                       "payload_hash": self.payload_hash, "budget": K.BUDGET})

    def deliver_response(self, obs):
        self.responded.add(obs["attempt_id"])
        self._deliver(obs)

    def deliver_status(self, obs):
        self._deliver(obs)

    def deliver_webhook(self, obs):
        self._deliver(obs)

    def on_timeout(self, attempt_id):
        if attempt_id in self.responded:
            self.sim.log("timeout_suppressed", "runtime", False, self.logical_op, attempt_id=attempt_id)
            return
        op_key = [a["op_key"] for a in self.attempts if a["attempt_id"] == attempt_id][0]
        self._deliver({"type": "timeout", "op_key": op_key, "attempt_id": attempt_id})

    def on_timer(self, tag):
        self._deliver({"type": "timer", "tag": tag})

    def close(self):
        self.belief_at_H = self.belief
        self.report_at_H = copy.deepcopy(self.policy.report())
        self.closed = True
        self.sim.log("horizon", "client", True, self.logical_op, belief=self.belief_at_H,
                     conflicts=len(self.report_at_H.get("conflicts", [])))

    # ------------------------------------------------------------------ the policy boundary
    def _deliver(self, obs):
        obs = copy.deepcopy(obs)
        obs["t"] = self.sim.now
        if self.closed or self.sim.now > self.horizon_t or self.sim.now < self.start_t:
            reason = "before_start" if self.sim.now < self.start_t else "after_horizon"
            self.sim.log("not_observed", "client", False, self.logical_op, reason=reason, obs=obs)
            return
        self.sim.log("observe", "client", True, self.logical_op, obs=obs)
        self.delivered.append(obs)
        self.io_log.append(canonical_json(["obs", obs]))
        actions = self.policy.observe(copy.deepcopy(obs))   # the policy gets its own deep copy
        if actions is None:
            actions = []
        if not isinstance(actions, list):
            self.violations.append({"t": self.sim.now, "violation": "actions_not_a_list"})
            actions = []
        actions = copy.deepcopy(actions)
        self.io_log.append(canonical_json(["act", actions]))
        self._refresh()
        for action in actions:
            self._execute(action)

    def _refresh(self):
        b = self.policy.belief()
        if b not in BELIEFS:
            self.violations.append({"t": self.sim.now, "violation": "bad_belief", "value": repr(b)})
            b = "unresolved"
        if b != self.belief:
            self.belief = b
            self.belief_changes.append([self.sim.now, b])
            self.sim.log("belief", "client", True, self.logical_op, belief=b)
        if b == "complete" and self.first_complete_t is None:
            self.first_complete_t = self.sim.now
        conflicts = self.policy.report().get("conflicts", [])
        for c in conflicts[self._n_conflicts:]:
            # Conflict rule (§2.5): the commit wins; the conflicting evidence is listed in the trace.
            self.sim.log("conflict", "client", True, self.logical_op, evidence=copy.deepcopy(c))
        self._n_conflicts = len(conflicts)

    def _execute(self, action):
        t = self.sim.now
        typ = action.get("type") if isinstance(action, dict) else None
        if typ not in ACTION_TYPES:
            self.violations.append({"t": t, "violation": "unknown_action", "action": repr(action)})
            return
        if t > self.horizon_t:
            self.violations.append({"t": t, "violation": "action_after_horizon"})
            return
        self.action_times.append([t, typ])
        if typ == "dispatch":
            if len(self.attempts) >= K.BUDGET:
                self.violations.append({"t": t, "violation": "budget_exceeded"})
                self.sim.log("dispatch_refused", "runtime", True, self.logical_op, reason="budget")
                self._deliver({"type": "dispatch_refused", "reason": "budget"})
                return
            k = len(self.attempts) + 1
            # A-fk ablation: a fresh op_key on every attempt after the first.
            op_key = self.logical_op if (self.key_mode == "stable" or k == 1) else "%s~k%d" % (self.logical_op, k)
            attempt_id = "%s#a%d" % (op_key, k)
            if self.first_complete_t is not None:
                self.dispatches_after_complete += 1
            self.attempts.append({"k": k, "attempt_id": attempt_id, "op_key": op_key, "t": t,
                                  "seen_before": len(self.delivered), "reason": str(action.get("reason", ""))})
            self.sim.log("dispatch", "client", True, self.logical_op, attempt_id=attempt_id, op_key=op_key, k=k,
                         reason=str(action.get("reason", "")))
            self.sim.provider.dispatch(self.logical_op, op_key, k, attempt_id, self.payload)
            self.sim.schedule(t + K.TIMEOUT, CLIENT, "timeout", {"logical_op": self.logical_op,
                                                                 "attempt_id": attempt_id})
            self._deliver({"type": "dispatched", "op_key": op_key, "attempt_id": attempt_id})
        elif typ == "status_read":
            self.status_reads += 1
            obs, hidden = self.sim.provider.status_reply(self.logical_op, self.logical_op, t)
            self.sim.log("status_read", "client", True, self.logical_op)
            self.sim.log("status_snapshot", "provider", False, self.logical_op, reply=obs, **hidden)
            self.sim.schedule(t + 1, DELIVERY, "status", {"logical_op": self.logical_op, "obs": obs})
        else:
            delay, tag = action.get("delay"), action.get("tag")
            if not isinstance(delay, int) or delay < 1 or not isinstance(tag, str):
                self.violations.append({"t": t, "violation": "bad_timer", "action": repr(action)})
                return
            if t + delay > self.horizon_t:
                self.sim.log("timer_not_set", "runtime", False, self.logical_op, tag=tag, reason="after_horizon")
                return
            self.sim.schedule(t + delay, CLIENT, "timer", {"logical_op": self.logical_op, "tag": tag})
            self.sim.log("set_timer", "client", True, self.logical_op, tag=tag, fires_at=t + delay)


class ScriptedClient(object):
    """Policy-free dispatcher for oracle checks (V1, V2): dispatches at fixed times, reacts to nothing."""
    is_reference = False

    def __init__(self, sim, op, times, payload_overrides=None):
        self.sim = sim
        self.logical_op = op["op_key"]
        self.payload = copy.deepcopy(op["payload"])
        self.times = list(times)
        self.payload_overrides = payload_overrides or {}
        self.attempts = []
        self.observed = []
        self.start_t = op["start"]
        self.horizon_t = self.start_t + sim.options["horizon"]

    def schedule_initial(self):
        for i, t in enumerate(self.times):
            self.sim.schedule(t, CLIENT, "scripted_dispatch", {"logical_op": self.logical_op, "index": i})

    def scripted_dispatch(self, d):
        k = len(self.attempts) + 1
        attempt_id = "%s#a%d" % (self.logical_op, k)
        payload = self.payload_overrides.get(k, self.payload)
        self.attempts.append({"k": k, "attempt_id": attempt_id, "op_key": self.logical_op, "t": self.sim.now})
        self.sim.log("dispatch", "client", True, self.logical_op, attempt_id=attempt_id, k=k, scripted=True)
        self.sim.provider.dispatch(self.logical_op, self.logical_op, k, attempt_id, payload)

    def _record(self, obs):
        obs = copy.deepcopy(obs)
        obs["t"] = self.sim.now
        self.observed.append(obs)

    deliver_response = deliver_status = deliver_webhook = _record

    def status_read(self):
        obs, hidden = self.sim.provider.status_reply(self.logical_op, self.logical_op, self.sim.now)
        self.sim.schedule(self.sim.now + 1, DELIVERY, "status", {"logical_op": self.logical_op, "obs": obs})
        return obs
