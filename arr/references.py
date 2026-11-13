"""Reference strategies ORACLE-S and ORACLE-O (pre-freeze design update, PROTOCOL.md §3).

These are NOT client policies. They are implemented on the simulator side and read hidden state
through an OracleView; they are excluded from V4 and labelled "reference" in every output. They
still dispatch through the ordinary client runtime, so attempt IDs, the budget and the horizon are
enforced exactly as for the policies.

Decision points: the same as A (timeout; `ok`, `error`, `in_progress`, `rejected` responses;
`committed`, `aborted`, `deferred` webhooks for the operation) plus every ORACLE_INTERVAL ticks from
the operation start. Clarification C16: decision points falling in the same tick are coalesced into
one decision (nothing on the provider side changes within phases 2-3 of a tick).
"""
from . import constants as K
from .client import PolicyClient
from .sim import FastForward

DECISION_RESPONSES = ("ok", "error", "in_progress", "rejected")
DECISION_WEBHOOKS = ("committed", "aborted", "deferred")


class OracleView(object):
    """Hidden-state access for references only."""

    def __init__(self, sim, client):
        self._sim = sim
        self._client = client

    def effect_exists(self):
        op = self._client.logical_op
        return any(e["logical_op"] == op and e["commit_time"] <= self._sim.now for e in self._sim.provider.ledger)

    def will_commit(self):
        """Will any dispatched attempt commit in the future (before F), with no further client
        action? Answered by running a private copy of the provider forward (clarification C17)."""
        ids = set(a["attempt_id"] for a in self._client.attempts)
        now = self._sim.now
        ledger = FastForward(self._sim).run()
        return any(e["attempt_id"] in ids and e["commit_time"] > now for e in ledger)


class _Reference(object):
    name = "?"
    outcome_oracle = False

    def __init__(self, view):
        self.view = view
        self.op_key = None
        self.budget = 0
        self.attempts = []
        self.keys = []
        self._belief = "unresolved"
        self.last_decision_t = None
        self.decisions = []

    def belief(self):
        return self._belief

    def report(self):
        return {"belief": self._belief, "attempts": list(self.attempts), "decisions": [list(d) for d in self.decisions]}

    def observe(self, obs):
        kind = obs.get("type")
        t = obs.get("t")
        if kind == "start":
            self.op_key = obs["op_key"]
            self.budget = obs["budget"]
            self.keys = [self.op_key]
            self.last_decision_t = t
            return [{"type": "dispatch"}, {"type": "set_timer", "delay": K.ORACLE_INTERVAL, "tag": "oracle"}]
        if kind == "dispatched":
            self.attempts.append(obs["attempt_id"])
            self.keys.append(obs["op_key"])
            return []
        actions = []
        decide = False
        if kind == "timer" and obs.get("tag") == "oracle":
            actions.append({"type": "set_timer", "delay": K.ORACLE_INTERVAL, "tag": "oracle"})
            decide = True
        elif kind == "timeout":
            decide = True
        elif kind == "response" and obs.get("op_key") in self.keys and obs.get("kind") in DECISION_RESPONSES:
            decide = True
        elif kind == "webhook" and obs.get("op_key") in self.keys and obs.get("event") in DECISION_WEBHOOKS:
            decide = True
        if decide and self.last_decision_t != t:
            self.last_decision_t = t
            actions.extend(self._decide(t))
        return actions

    def _decide(self, t):
        if self.view.effect_exists():
            self._belief = "complete"
            self.decisions.append([t, "effect exists"])
            return []
        if self.outcome_oracle and self.view.will_commit():
            self._belief = "unresolved"
            self.decisions.append([t, "a dispatched attempt will commit: wait"])
            return []
        if len(self.attempts) < self.budget:
            self._belief = "unresolved"
            self.decisions.append([t, "no effect: retry"])
            return [{"type": "dispatch"}]
        self._belief = "failed"
        self.decisions.append([t, "no effect, budget exhausted"])
        return []


class OracleS(_Reference):
    """State oracle: knows whether an effect exists now; does not know about in-flight attempts."""
    name = "ORACLE-S"


class OracleO(_Reference):
    """Outcome oracle: also knows whether any dispatched attempt will ever commit before F."""
    name = "ORACLE-O"
    outcome_oracle = True


class ReferenceClient(PolicyClient):
    is_reference = True

    def __init__(self, sim, op, name):
        cls = {"ORACLE-S": OracleS, "ORACLE-O": OracleO}[name]
        PolicyClient.__init__(self, sim, op, None, name)
        self.policy = cls(OracleView(sim, self))
