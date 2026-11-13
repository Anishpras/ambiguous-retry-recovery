"""Discrete-event engine (PROTOCOL.md §2.2).

Ordering within a tick:
  phase 1  provider-side events: arrivals, commits, aborts (and S13-S15's deferred / late commit)
  phase 2  deliveries to the client: responses, status replies, webhooks
  phase 3  client timers: operation starts, timeouts, polls, waits
  phase 4  bookkeeping: the horizon snapshot of an operation's belief (after all of tick H)
Within a phase, events run in the order they were scheduled: every schedule() call takes the next
value of one global counter, and the heap key is (tick, phase, counter). Pre-freeze clarification C2:
phase 1 uses the same counter rule; "arrivals, commits and aborts" is read as the list of phase-1
event types, not as a sub-order. Same-tick, same-phase, same-operation groups are recorded in
Sim.ties so that every tie the counter resolved can be listed (results/ties.csv).
"""
import heapq

from . import constants as K
from . import options as O
from .provider import Provider

PROVIDER, DELIVERY, CLIENT, BOOKKEEPING = 1, 2, 3, 4
PROVIDER_EVENTS = ("arrival", "commit", "abort", "deferred", "violation_commit")


class Sim(object):
    def __init__(self, scenario, contract, provider_cls=Provider, options=None):
        self.scenario = scenario
        # Named options: defaults, then the scenario file's "options", then the run's (arr/options.py).
        self.options = O.merge(scenario.get("options"), options)
        self.contract = contract
        self.now = 0
        self.phase = 0
        self.cur_n = 0
        self._n = 0
        self._heap = []
        self.trace = []
        self.clients = {}
        self.client_order = []
        self._groups = {}
        self.provider = provider_cls(self, scenario, contract)
        self.config = dict(K.PARITY)
        self.config["horizon"] = self.options["horizon"]
        self.config["wait_tau"] = self.options["wait_tau"]
        self.config["dedup_window"] = self.options["dedup_window"]

    # ------------------------------------------------------------------ scheduling and logging
    def schedule(self, t, phase, kind, data):
        if t < self.now:
            raise ValueError("cannot schedule into the past")
        self._n += 1
        heapq.heappush(self._heap, (t, phase, self._n, kind, data))
        return self._n

    def log(self, name, who, visible, op=None, **details):
        self.trace.append({"t": self.now, "phase": self.phase, "n": self.cur_n, "event": name, "who": who,
                           "visible": bool(visible), "op": op, "details": details})

    def add_client(self, client):
        if client.logical_op in self.clients:
            raise ValueError("duplicate operation " + client.logical_op)
        self.clients[client.logical_op] = client
        self.client_order.append(client)
        client.schedule_initial()

    # ------------------------------------------------------------------ main loop
    def run(self):
        while self._heap:
            t, phase, n, kind, data = heapq.heappop(self._heap)
            if t > K.FINAL:
                break
            self.now, self.phase, self.cur_n = t, phase, n
            self._note_group(t, phase, n, kind, data)
            if kind in PROVIDER_EVENTS:
                getattr(self.provider, "on_" + kind)(data)
            else:
                getattr(self, "_on_" + kind)(data)
        self.now = max(self.now, 0)
        return self

    def _note_group(self, t, phase, n, kind, data):
        if kind in PROVIDER_EVENTS:
            op = self.provider.attempts[data].logical_op
            label = "%s:%s" % (kind, data.split("#")[-1])
        elif kind == "webhook":
            op = self.provider.attempts[data["attempt_id"]].logical_op
            label = "webhook:%s:%s" % (data["event"], data["attempt_id"].split("#")[-1])
        elif kind in ("response", "status"):
            op = data["logical_op"]
            obs = data["obs"]
            label = "%s:%s" % (kind, obs.get("kind") or obs.get("result"))
        elif kind in ("timeout", "timer", "scripted_dispatch"):
            op = data["logical_op"]
            label = "%s:%s" % (kind, data.get("attempt_id", data.get("tag", "")).split("#")[-1])
        else:
            op = data
            label = kind
        self._groups.setdefault((t, phase, op), []).append(label)

    @property
    def ties(self):
        return [{"t": t, "phase": ph, "op": op, "order": labels}
                for (t, ph, op), labels in sorted(self._groups.items()) if len(labels) > 1]

    # ------------------------------------------------------------------ handlers (phases 2-4)
    def _on_response(self, d):
        self.clients[d["logical_op"]].deliver_response(d["obs"])

    def _on_status(self, d):
        self.clients[d["logical_op"]].deliver_status(d["obs"])

    def _on_webhook(self, obs):
        # Pre-freeze clarification C6: webhooks reach every operation of the client; policies must
        # correlate them (§2.5). Responses and status replies go only to the requesting operation.
        for client in self.client_order:
            client.deliver_webhook(obs)

    def _on_op_start(self, op):
        self.clients[op].start()

    def _on_timeout(self, d):
        self.clients[d["logical_op"]].on_timeout(d["attempt_id"])

    def _on_timer(self, d):
        self.clients[d["logical_op"]].on_timer(d["tag"])

    def _on_scripted_dispatch(self, d):
        self.clients[d["logical_op"]].scripted_dispatch(d)

    def _on_horizon(self, op):
        self.clients[op].close()


class FastForward(object):
    """A private copy of the provider run forward to F with no further client actions.

    Used only by the reference ORACLE-O to answer "will any dispatched attempt ever commit before
    F, from the schedule". It sees only phase-1 events already scheduled; deliveries are dropped."""

    def __init__(self, sim):
        self.options = sim.options
        self.now = sim.now
        self.phase = PROVIDER
        self.cur_n = sim.cur_n
        self._n = sim._n
        self._heap = [e for e in sim._heap if e[1] == PROVIDER]
        heapq.heapify(self._heap)
        self.provider = sim.provider.clone(self)

    def schedule(self, t, phase, kind, data):
        if phase == PROVIDER:
            self._n += 1
            heapq.heappush(self._heap, (t, phase, self._n, kind, data))

    def log(self, *args, **kwargs):
        pass

    def run(self):
        while self._heap:
            t, phase, n, kind, data = heapq.heappop(self._heap)
            if t > K.FINAL:
                break
            self.now, self.cur_n = t, n
            getattr(self.provider, "on_" + kind)(data)
        return self.provider.ledger
