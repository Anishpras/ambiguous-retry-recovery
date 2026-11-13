"""Validation checks V1-V6 (PROTOCOL.md §6). V7 (byte reproducibility) lives in run_sim.py.

Every check function returns a list of {"check", "ok", "detail"} dicts. Functions accept an
injected provider class and/or policy classes so tests/test_mutations.py can show that each
mutant is caught by at least one check.
"""
import ast
import copy
import os
import re

from . import constants as K
from . import ids, policies, scenarios
from .client import PolicyClient
from .provider import Provider
from .runner import effect_history, run_cell, run_scripted
from .sim import Sim

HEX12 = re.compile(r"^[0-9a-f]{12}$")


def result(check, ok, detail=""):
    return {"check": check, "ok": bool(ok), "detail": detail}


def _payload():
    return scenarios.load_json("grids.json")["payload"]


def adhoc(sid, a1=None, lag=1, ops=None, a2=None):
    """A small scenario built in code for contract-basics checks (never part of the matrix)."""
    attempts = {}
    if a1 is not None:
        attempts["1"] = a1
    if a2 is not None:
        attempts["2"] = a2
    scn = {"id": sid, "family": "v2", "status_lag": lag,
           "operations": ops or [{"op_key": "op-1", "start": 0, "payload": _payload(), "attempts": attempts}]}
    return scenarios._finish(scn)


# ---------------------------------------------------------------------------------------- V1
def check_v1(provider_cls=Provider):
    """Oracle checks independent of policies: scripted dispatch times reproduce each fixture's
    expected effect history, under both contracts, with nothing pending at F."""
    out, n, bad = [], 0, []
    for scn in scenarios.load_core():
        for case in scn["oracle"]:
            for c in K.CONTRACTS:
                sim = run_scripted(scn, c, case["dispatches"], provider_cls=provider_cls)
                got = effect_history(sim)
                exp = case["expected_effects"]["contract%d" % c]
                pending = [a.attempt_id for a in sim.provider.attempts.values() if a.state == "pending"]
                n += 1
                if got != exp or pending:
                    bad.append("%s/%s/c%d got %s expected %s pending %s" % (scn["id"], case["case"], c, got, exp, pending))
    out.append(result("V1_oracle_effect_histories", not bad, "%d/%d scripted runs match%s" % (
        n - len(bad), n, ("; " + "; ".join(bad)) if bad else "")))
    return out


# ---------------------------------------------------------------------------------------- V2
class ProbePolicy(object):
    """Validation-only client: dispatches once at start and issues status reads at fixed ticks."""

    def __init__(self, read_times=()):
        self.read_times = list(read_times)
        self.seen = []

    def belief(self):
        return "unresolved"

    def report(self):
        return {}

    def observe(self, obs):
        self.seen.append(obs)
        if obs["type"] == "start":
            return [{"type": "dispatch"}] + [{"type": "set_timer", "delay": t - obs["t"], "tag": "read"}
                                            for t in self.read_times]
        if obs["type"] == "timer":
            return [{"type": "status_read"}]
        return []


def run_probe(scn, contract, read_times=(), provider_cls=Provider):
    sim = Sim(scn, contract, provider_cls)
    probe = ProbePolicy(read_times)
    for op in scn["operations"]:
        sim.add_client(PolicyClient(sim, op, probe if op is scn["operations"][0] else ProbePolicy(), "probe"))
    sim.run()
    return sim, probe


def check_v2(provider_cls=Provider):
    out = []
    lost_ack = {"response": None, "webhooks": {"committed": []}}

    # nominal call -> 1 effect
    ok = all(len(effect_history(run_scripted(adhoc("v2a"), c, [{"op": "op-1", "t": 0}], provider_cls))) == 1
             for c in K.CONTRACTS)
    out.append(result("V2_nominal_call_one_effect", ok))

    # committed timeout followed by a resend -> 2 effects (c1), 1 effect (c2) with replayed effect_id
    plan = [{"op": "op-1", "t": 0}, {"op": "op-1", "t": 5}]
    s1 = run_scripted(adhoc("v2b", lost_ack), 1, plan, provider_cls)
    s2 = run_scripted(adhoc("v2b", lost_ack), 2, plan, provider_cls)
    replies = [o for o in s2.clients["op-1"].observed if o["type"] == "response"]
    e1 = s2.provider.ledger[0]["effect_id"] if s2.provider.ledger else None
    ok = (len(s1.provider.ledger) == 2 and len(s2.provider.ledger) == 1 and len(replies) == 1
          and replies[0]["kind"] == "ok" and replies[0]["attempt_id"] == "op-1#a2" and replies[0]["effect_id"] == e1)
    out.append(result("V2_committed_timeout_resend", ok, "c1 effects=%d c2 effects=%d c2 reply=%s" % (
        len(s1.provider.ledger), len(s2.provider.ledger), replies)))

    # contract 2, same key with a different payload -> conflict, no extra effect
    other = dict(_payload(), body_hash="0" * 64)
    s = run_scripted(adhoc("v2c"), 2, plan, provider_cls, payload_overrides={"op-1": {2: other}})
    kinds = [o["kind"] for o in s.clients["op-1"].observed if o["type"] == "response"]
    out.append(result("V2_contract2_payload_mismatch_conflict", len(s.provider.ledger) == 1 and kinds == ["ok", "conflict"],
                      "responses=%s effects=%d" % (kinds, len(s.provider.ledger))))

    # distinct op_keys with the same payload -> 2 effects under both contracts
    ops = [{"op_key": "op-1", "start": 0, "payload": _payload(), "attempts": {}},
           {"op_key": "op-2", "start": 0, "payload": _payload(), "attempts": {}}]
    ok = all(len(run_scripted(adhoc("v2d", ops=ops), c, [{"op": "op-1", "t": 0}, {"op": "op-2", "t": 0}],
                              provider_cls).provider.ledger) == 2 for c in K.CONTRACTS)
    out.append(result("V2_distinct_keys_same_payload_two_effects", ok))

    # contract 2: a retry after an abort executes
    s = run_scripted(adhoc("v2e", {"abort_after": 2, "response": None}), 2,
                     [{"op": "op-1", "t": 0}, {"op": "op-1", "t": 6}], provider_cls)
    out.append(result("V2_contract2_retry_after_abort_executes", effect_history(s) == [["op-1#a2", 8]],
                      str(effect_history(s))))

    # contract 2: a pending record answers in_progress and creates nothing
    s = run_scripted(adhoc("v2f", {"commit_after": 14}), 2, plan, provider_cls)
    kinds = [(o["attempt_id"], o["kind"], o["t"]) for o in s.clients["op-1"].observed if o["type"] == "response"]
    out.append(result("V2_contract2_pending_in_progress", effect_history(s) == [["op-1#a1", 15]]
                      and ("op-1#a2", "in_progress", 7) in kinds, str(kinds)))

    # a request lost before arrival creates no record (contract 2: the retry executes)
    s = run_scripted(adhoc("v2g", {"arrive": None}), 2, plan, provider_cls)
    out.append(result("V2_lost_request_creates_no_record", effect_history(s) == [["op-1#a2", 7]]
                      and not any(r["attempt_id"] == "op-1#a1" for r in s.provider.records), str(effect_history(s))))

    # status reads: answered at t+1 from records with record_time <= t - L; L=never; terminal_attempts
    sim, probe = run_probe(adhoc("v2h", lost_ack, lag=30), 1, read_times=(31, 32))
    st = [(o["t"], o["result"]) for o in probe.seen if o["type"] == "status"]
    ok_lag = st == [(32, "not_found"), (33, "found")]
    sim, probe = run_probe(adhoc("v2i", lost_ack, lag="never"), 1, read_times=(5, 59))
    st_never = [(o["t"], o["result"], o.get("terminal_attempts")) for o in probe.seen if o["type"] == "status"]
    ok_never = st_never == [(6, "not_found", []), (60, "not_found", [])]
    sim, probe = run_probe(adhoc("v2j", {"abort_after": 2, "response": None, "webhooks": {"aborted": []}}, lag=1), 1,
                           read_times=(3, 4))
    st_term = [(o["t"], o.get("terminal_attempts")) for o in probe.seen if o["type"] == "status"]
    ok_term = st_term == [(4, []), (5, ["op-1#a1"])]
    out.append(result("V2_status_lag_and_terminal_attempts", ok_lag and ok_never and ok_term,
                      "L=30 %s; L=never %s; abort %s" % (st, st_never, st_term)))

    # a late response after the timeout is still delivered and observed (S05, single dispatch)
    sim, probe = run_probe(scenarios.load_scenario("S05"), 1)
    seq = [(o["type"], o.get("kind"), o["t"]) for o in probe.seen if o["type"] in ("timeout", "response")]
    out.append(result("V2_late_response_after_timeout_observed", seq == [("timeout", None, 5), ("response", "ok", 16)],
                      str(seq)))

    # per-op provider_seq vs delivery order; duplicate deliveries share event_id (S07)
    sim, probe = run_probe(scenarios.load_scenario("S07"), 1)
    wh = [(o["t"], o["event"], o["provider_seq"], o["event_id"]) for o in probe.seen if o["type"] == "webhook"]
    ok = (len(wh) == 3 and [w[1] for w in wh] == ["committed", "committed", "processing"]
          and wh[0][3] == wh[1][3] and wh[2][2] < wh[0][2])
    out.append(result("V2_seq_vs_delivery_order_and_duplicate_event_ids", ok, str(wh)))

    # deferred is not terminal (S13): the attempt still commits; violation labelled only in S15
    viol = {}
    for scn in scenarios.load_core():
        sim = run_scripted(scn, 1, scn["oracle"][0]["dispatches"], provider_cls)
        viol[scn["id"]] = sum(1 for e in sim.provider.ledger if e["violation"])
    s13 = run_scripted(scenarios.load_scenario("S13"), 1, [{"op": "op-1", "t": 0}], provider_cls)
    ok = effect_history(s13) == [["op-1#a1", 8]] and [k for k, v in viol.items() if v] == ["S15"]
    out.append(result("V2_deferred_not_terminal_and_violation_only_in_S15", ok, "violations=%s" % viol))

    # effect IDs: opaque HMAC of (op_key, attempt_id); per-op seq strictly increasing in emission order
    bad_ids, seq_viol, n = [], [], 0
    for scn in scenarios.load_core():
        for case in scn["oracle"]:
            for c in K.CONTRACTS:
                sim = run_scripted(scn, c, case["dispatches"], provider_cls)
                seq_viol.extend(sim.provider.seq_order_violations)
                for e in sim.provider.ledger:
                    n += 1
                    if not HEX12.match(e["effect_id"]) or e["effect_id"] != ids.effect_id(e["op_key"], e["attempt_id"]):
                        bad_ids.append(e["effect_id"])
    out.append(result("V2_effect_ids_are_opaque_hmacs", not bad_ids, "%d effects checked; bad=%s" % (n, bad_ids[:5])))
    out.append(result("V2_provider_seq_increases_in_emission_order", not seq_viol, str(seq_viol[:5])))
    return out


# ---------------------------------------------------------------------------------------- V3
PH = None  # payload hash used by crafted sequences (set lazily)


class Driver(object):
    """Feeds crafted observation sequences to a policy object, acking dispatches like the runtime."""

    def __init__(self, policy, op="op-1"):
        self.policy = policy
        self.op = op
        self.k = 0
        self.dispatch_times = []
        self.ph = scenarios.ids.payload_hash(_payload())
        self.feed({"type": "start", "op_key": op, "payload": _payload(), "payload_hash": self.ph,
                   "budget": K.BUDGET, "t": 0})

    def feed(self, obs):
        actions = self.policy.observe(copy.deepcopy(obs)) or []
        for a in actions:
            if a["type"] == "dispatch":
                self.k += 1
                self.dispatch_times.append(obs.get("t"))
                self.policy.observe({"type": "dispatched", "op_key": self.op,
                                     "attempt_id": "%s#a%d" % (self.op, self.k), "t": obs.get("t")})
        return actions

    def aid(self, k):
        return "%s#a%d" % (self.op, k)

    def committed(self, k, t, seq, event_id=None, op=None, ph=None, attempt=None):
        return {"type": "webhook", "event": "committed", "provider_seq": seq, "t": t,
                "event_id": event_id or "ev-c%d-%d" % (k, seq), "op_key": op or self.op,
                "attempt_id": attempt or self.aid(k), "payload_hash": ph or self.ph, "effect_id": "e%d" % k}

    def aborted(self, k, t, seq, event_id=None):
        return {"type": "webhook", "event": "aborted", "provider_seq": seq, "t": t,
                "event_id": event_id or "ev-a%d-%d" % (k, seq), "op_key": self.op, "attempt_id": self.aid(k)}

    def timeout(self, k, t):
        return {"type": "timeout", "op_key": self.op, "attempt_id": self.aid(k), "t": t}

    def not_found(self, t, terminal=()):
        return {"type": "status", "result": "not_found", "op_key": self.op, "terminal_attempts": list(terminal), "t": t}


def _cls(policy_classes, name):
    if policy_classes and name in policy_classes:
        return policy_classes[name]
    return {"C": policies.PolicyC, "D": policies.PolicyD, "D+I": policies.PolicyDI}[name]


def _new(policy_classes, name):
    cls = _cls(policy_classes, name)
    return cls(True) if name == "D+I" else cls()


def check_v3(policy_classes=None):
    out = []
    for name in ("C", "D", "D+I"):
        # (a) a delayed older receipt (lower seq, attempt already terminal) cannot overturn a commit
        d = Driver(_new(policy_classes, name))
        d.feed(d.timeout(1, 5))
        d.feed(d.not_found(6, [d.aid(1)]))                  # a1 terminal; D/D+I retry, C fails
        if name == "C":
            d.feed(d.committed(1, 8, 211))                  # crafted: C gets a positive for a1 (conflict path)
            ok = d.policy.belief() == "complete"
        else:
            d.feed(d.committed(2, 8, 821))
            before = d.k
            d.feed(d.aborted(1, 30, 312))                   # stale, for an attempt already terminal
            d.feed(d.aborted(2, 31, 100))                   # lower seq, for the committed attempt
            ok = d.policy.belief() == "complete" and d.k == before
        out.append(result("V3_%s_older_receipt_cannot_overturn_commit" % name, ok,
                          "belief=%s dispatches=%d" % (d.policy.belief(), d.k)))

        # (b) duplicate deliveries are idempotent
        d = Driver(_new(policy_classes, name))
        d.feed(d.timeout(1, 5))
        ab = d.aborted(1, 6, 312, event_id="ev-dup")
        d.feed(ab)
        after_first = (d.policy.belief(), d.k, sorted(d.policy.terminal))
        d.feed(dict(ab, t=7))
        after_second = (d.policy.belief(), d.k, sorted(d.policy.terminal))
        out.append(result("V3_%s_duplicate_delivery_idempotent" % name, after_first == after_second,
                          "%s vs %s" % (after_first, after_second)))

        # (c) uncorrelated positives (other op_key, other payload_hash, undispatched attempt) are ignored
        d = Driver(_new(policy_classes, name))
        d.feed(d.timeout(1, 5))
        d.feed(d.committed(1, 6, 211, op="op-2", attempt="op-2#a1"))
        d.feed(d.committed(1, 7, 212, ph="f" * 64))
        d.feed(d.committed(9, 8, 213, attempt="op-1#a9"))
        d.feed({"type": "response", "kind": "ok", "op_key": "op-1", "attempt_id": d.aid(1), "payload_hash": "f" * 64,
                "effect_id": "e1", "t": 9})
        d.feed({"type": "status", "result": "found", "op_key": "op-1", "attempt_id": d.aid(1), "payload_hash": "f" * 64,
                "effect_id": "e1", "t": 10})
        out.append(result("V3_%s_uncorrelated_positives_ignored" % name,
                          d.policy.belief() == "unresolved" and d.k == (2 if name == "D+I" else 1),
                          "belief=%s dispatches=%d" % (d.policy.belief(), d.k)))

        # (d) conflict rule: positive + terminal negative for the same attempt -> commit wins, counted
        d = Driver(_new(policy_classes, name))
        d.feed(d.committed(1, 4, 211))
        d.feed(d.aborted(1, 5, 312))
        conf = d.policy.report()["conflicts"]
        out.append(result("V3_%s_conflict_rule" % name, d.policy.belief() == "complete" and len(conf) == 1
                          and conf[0]["attempt_id"] == d.aid(1) and d.k == 1, str(conf)))

        # (e) not_found never reverts complete, and alone never triggers a retry
        d = Driver(_new(policy_classes, name))
        d.feed(d.timeout(1, 5))
        d.feed(d.not_found(6))
        no_retry = d.k == (2 if name == "D+I" else 1)
        d.feed(d.committed(1, 8, 211))
        d.feed(d.not_found(11))
        out.append(result("V3_%s_not_found_not_authoritative" % name, no_retry and d.policy.belief() == "complete",
                          "dispatches=%d belief=%s" % (d.k, d.policy.belief())))

        # (f) deferred is progress only (design update)
        d = Driver(_new(policy_classes, name))
        d.feed({"type": "webhook", "event": "deferred", "provider_seq": 211, "event_id": "ev-def", "op_key": "op-1",
                "attempt_id": d.aid(1), "t": 3})
        out.append(result("V3_%s_deferred_is_progress_only" % name,
                          d.k == 1 and d.policy.belief() == "unresolved" and not d.policy.terminal,
                          "dispatches=%d" % d.k))

    # (g) all attempts terminal: D retries, C (after a timeout) does not and ends failed
    d = Driver(_new(policy_classes, "D"))
    d.feed(d.timeout(1, 5))
    d.feed(d.not_found(6, [d.aid(1)]))
    c = Driver(_new(policy_classes, "C"))
    c.feed(c.timeout(1, 5))
    c.feed(c.not_found(6, [c.aid(1)]))
    out.append(result("V3_all_terminal_retry_D_not_C", d.k == 2 and c.k == 1 and c.policy.belief() == "failed",
                      "D dispatches=%d C dispatches=%d C belief=%s" % (d.k, c.k, c.policy.belief())))

    # (h) D+I: in_progress is terminal for the resend only; keep waiting, then complete on a1's commit
    d = Driver(_new(policy_classes, "D+I"))
    d.feed(d.timeout(1, 5))
    d.feed(d.not_found(6))
    d.feed({"type": "response", "kind": "in_progress", "op_key": "op-1", "attempt_id": d.aid(2), "t": 8})
    mid = (d.k, d.policy.belief())
    d.feed(d.committed(1, 10, 1012))
    out.append(result("V3_DI_in_progress_keeps_waiting", mid == (2, "unresolved") and d.policy.belief() == "complete",
                      "after in_progress=%s final=%s" % (mid, d.policy.belief())))
    return out


# ---------------------------------------------------------------------------------------- V4
FORBIDDEN_NAMES = {"__import__", "eval", "exec", "compile", "open", "globals", "locals", "vars", "getattr",
                   "setattr", "delattr", "__builtins__", "input", "breakpoint", "memoryview", "type"}
ALLOWED_DUNDERS = {"__init__"}


def check_policy_module_static(path=None):
    path = path or os.path.join(scenarios.ROOT, "arr", "policies.py")
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if not (isinstance(node, ast.ImportFrom) and node.module == "__future__"):
                problems.append("import at line %d" % node.lineno)
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            problems.append("name %s at line %d" % (node.id, node.lineno))
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr not in ALLOWED_DUNDERS:
            problems.append("attribute %s at line %d" % (node.attr, node.lineno))
    return [result("V4_policy_module_imports_nothing", not problems, "; ".join(problems))]


class HostileD(policies.PolicyD):
    """V4 probe: mutates every observation it receives and keeps references to mutate them later."""

    def __init__(self):
        policies.PolicyD.__init__(self)
        self.kept = []

    def observe(self, obs):
        actions = policies.PolicyD.observe(self, obs)
        for old in self.kept:
            old.clear()
        obs["t"] = -1
        for v in obs.values():
            if isinstance(v, list):
                v.append("tampered")
        self.kept.append(obs)
        return actions


def check_deep_copy():
    # An ad-hoc schedule outside the matrix: abort, duplicated aborted webhook, late processing.
    scn = adhoc("v4", {"abort_after": 2, "response": None, "webhooks": {"processing": [8], "aborted": [2, 5]}}, lag=4)
    a = run_cell(scn, 1, "D")
    b = run_cell(scn, 1, "D", policy_classes={"D": HostileD})
    same = a.trace == b.trace and a.clients["op-1"].io_log == b.clients["op-1"].io_log
    return [result("V4_policies_receive_deep_copies", same, "hostile mutation of observations left the run unchanged"
                   if same else "trace differs after hostile mutation")]


def io_bytes(sim):
    return "\n".join("\n".join(c.io_log) for c in sim.client_order).encode("utf-8")


def check_twins(provider_cls=Provider, policy_classes=None, names=K.CLIENT_POLICIES):
    """Under contract 1 every client policy's observation sequence and actions are byte-identical
    in S08 and S09 (the references are excluded)."""
    s08, s09 = scenarios.load_scenario("S08"), scenarios.load_scenario("S09")
    out, sims = [], []
    for name in names:
        a = run_cell(s08, 1, name, provider_cls=provider_cls, policy_classes=policy_classes)
        b = run_cell(s09, 1, name, provider_cls=provider_cls, policy_classes=policy_classes)
        sims += [a, b]
        ba, bb = io_bytes(a), io_bytes(b)
        detail = "%d bytes" % len(ba)
        if ba != bb:
            la, lb = ba.split(b"\n"), bb.split(b"\n")
            i = next((i for i in range(min(len(la), len(lb))) if la[i] != lb[i]), min(len(la), len(lb)))
            detail = "first difference at line %d: %s | %s" % (i, la[i][:160] if i < len(la) else b"<end>",
                                                                lb[i][:160] if i < len(lb) else b"<end>")
        out.append(result("V4_S08_S09_identical_%s" % name, ba == bb, detail))
    return out, sims


def check_v4(provider_cls=Provider, policy_classes=None):
    out = check_policy_module_static() + check_deep_copy()
    twins, sims = check_twins(provider_cls, policy_classes)
    out += twins
    ledger_ids = [e["effect_id"] for s in sims for e in s.provider.ledger]
    out.append(result("V4_effect_ids_opaque_format", all(HEX12.match(x) for x in ledger_ids),
                      "%d effect IDs" % len(ledger_ids)))
    return out, sims


# ---------------------------------------------------------------------------------------- V5
def check_v5(sims, label):
    problems = []
    if policies.POLL_INTERVAL != K.POLL_INTERVAL or policies.WAIT_TAU != K.WAIT_TAU:
        problems.append("policy constants differ from run constants")
    for sim in sims:
        if sim.config != K.PARITY:
            problems.append("config differs")
        for c in sim.client_order:
            if not hasattr(c, "action_times"):
                continue
            if len(c.attempts) > K.BUDGET or c.violations:
                problems.append("%s/%s: dispatches=%d violations=%s" % (sim.scenario["id"], c.logical_op,
                                                                          len(c.attempts), c.violations))
            late = [t for t, _ in c.action_times if t > c.horizon_t]
            if late:
                problems.append("%s/%s: actions after H at %s" % (sim.scenario["id"], c.logical_op, late))
    return [result("V5_parity_%s" % label, not problems, "%d runs; %s" % (len(sims), "; ".join(problems[:5])))]


# ---------------------------------------------------------------------------------------- V6
def check_v6(rows, sanity):
    lab = sanity["V6"]
    ctrl = lab["control"]
    s00 = [r for r in rows if r["scenario"] == ctrl["scenario"]]
    bad = ["%s/c%d" % (r["policy"], r["contract"]) for r in s00
           if r["effects_F"] != ctrl["effects_F"] or r["belief_H"] != ctrl["belief_H"]]
    out = [result("V6_S00_one_effect_and_complete_everywhere", s00 and not bad,
                  "%d S00 runs; failing %s" % (len(s00), bad))]
    rule = lab["contract2_no_duplicates"]
    dups = ["%s/%s/%s" % (r["policy"], r["scenario"], r["op"]) for r in rows
            if r["contract"] == rule["contract"] and r["duplicate"]
            and r["scenario"] not in rule["exclude_scenarios"] and r["policy"] not in rule["exclude_policies"]]
    n = sum(1 for r in rows if r["contract"] == rule["contract"])
    out.append(result("V6_contract2_no_duplicates_except_S15_and_A-fk", not dups,
                      "%d contract-2 operations checked; duplicates: %s" % (n, dups)))
    return out


# ---------------------------------------------------------------------------------------- bundles
def prefreeze_checks():
    """V1-V5 as allowed before the freeze (no matrix or grid run)."""
    out = check_v1() + check_v2() + check_v3()
    v4, sims = check_v4()
    out += v4
    out += check_v5(sims, "twin_runs")
    return out
