"""Example of your own policy, for `python3 run_sim.py explore ... --policy examples/custom_policy.py:PatientReconciler`.

A policy is any class with:
    observe(obs: dict) -> list of action dicts   (see docs/trace-schema.md for both vocabularies)
    belief() -> "unresolved" | "complete" | "failed"
    report() -> dict (optional; "conflicts" is read if present)
It is constructed as Class(), Class(options) or Class(idempotent_provider, options). It should import nothing
from the simulator: it sees only the observation dicts the runtime gives it.

PatientReconciler: credits only correlated positives, retries only when every attempt it sent has an
authoritative terminal negative, and polls status with backoff 5, 10, 20, 20, ... ticks.
"""


class PatientReconciler(object):
    def __init__(self, options=None):
        self.op_key = None
        self.payload_hash = None
        self.budget = 0
        self.attempts = []
        self.positive = set()
        self.terminal = set()
        self.polling = False
        self.next_poll = 5

    def belief(self):
        if self.positive:
            return "complete"
        if self.attempts and all(a in self.terminal for a in self.attempts) and len(self.attempts) >= self.budget:
            return "failed"
        return "unresolved"

    def report(self):
        return {"attempts": list(self.attempts), "positive": sorted(self.positive), "terminal": sorted(self.terminal)}

    def _mine(self, obs):
        return obs.get("op_key") == self.op_key and obs.get("attempt_id") in self.attempts

    def _evidence(self, obs):
        kind = obs.get("kind") or obs.get("event") or obs.get("result")
        if kind in ("ok", "committed", "found") and self._mine(obs) and obs.get("payload_hash") == self.payload_hash:
            self.positive.add(obs["attempt_id"])
        elif kind in ("rejected", "in_progress", "conflict", "aborted") and self._mine(obs):
            self.terminal.add(obs["attempt_id"])
        elif kind == "not_found" and obs.get("op_key") == self.op_key:
            self.terminal.update(a for a in obs.get("terminal_attempts", []) if a in self.attempts)

    def observe(self, obs):
        typ = obs["type"]
        if typ == "start":
            self.op_key, self.payload_hash, self.budget = obs["op_key"], obs["payload_hash"], obs["budget"]
            return [{"type": "dispatch"}]
        if typ == "dispatched":
            self.attempts.append(obs["attempt_id"])
            return []
        if typ in ("response", "webhook", "status"):
            self._evidence(obs)
        actions = []
        ambiguous = typ == "timeout" or (typ == "response" and obs.get("kind") == "error")
        if ambiguous and not self.polling and self.belief() == "unresolved":
            self.polling = True
            actions += [{"type": "status_read"}, {"type": "set_timer", "delay": self.next_poll, "tag": "poll"}]
        if typ == "timer" and obs.get("tag") == "poll" and self.belief() == "unresolved":
            self.next_poll = min(self.next_poll * 2, 20)
            actions += [{"type": "status_read"}, {"type": "set_timer", "delay": self.next_poll, "tag": "poll"}]
        if (self.belief() == "unresolved" and self.attempts and all(a in self.terminal for a in self.attempts)
                and len(self.attempts) < self.budget):
            actions.append({"type": "dispatch"})
        return actions
