"""Measures (PROTOCOL.md §5). Everything here is computed by the scorer from the private ledger,
the provider's attempt records and the runtime's record of what the client observed and did; no
measure trusts a policy's self-report except the conflict list (§2.5 asks the policy to count them).
"""
from . import constants as K
from . import registry


def _attempt_label(attempt_id):
    return attempt_id.split("#")[-1]


def _is_positive(obs):
    return ((obs["type"] == "response" and obs.get("kind") == "ok")
            or (obs["type"] == "webhook" and obs.get("event") == "committed")
            or (obs["type"] == "status" and obs.get("result") == "found"))


def correlated_positive(obs, keys, attempt_ids, payload_hash):
    """Scorer-side correlation (§2.5): op_key, payload_hash and a dispatched attempt all match."""
    return (_is_positive(obs) and obs.get("op_key") in keys and obs.get("payload_hash") == payload_hash
            and obs.get("attempt_id") in attempt_ids)


def authoritative_negatives(observations, keys, attempt_ids):
    """Attempts covered by an authoritative terminal negative in these observations: `rejected`,
    `in_progress`, `conflict` responses; `aborted` webhooks; `terminal_attempts` in a status reply.
    (`deferred`, `error`, timeouts and `not_found` itself never cover anything.)"""
    covered = set()
    for obs in observations:
        if obs["type"] == "response" and obs.get("kind") in ("rejected", "in_progress", "conflict"):
            if obs.get("attempt_id") in attempt_ids:
                covered.add(obs["attempt_id"])
        elif obs["type"] == "webhook" and obs.get("event") == "aborted" and obs.get("op_key") in keys:
            if obs.get("attempt_id") in attempt_ids:
                covered.add(obs["attempt_id"])
        elif obs["type"] == "status" and obs.get("result") == "not_found" and obs.get("op_key") in keys:
            covered.update(a for a in obs.get("terminal_attempts", []) if a in attempt_ids)
    return covered


def op_result(sim, client, scenario, contract, policy_name):
    op = client.logical_op
    H = client.horizon_t
    ledger = [e for e in sim.provider.ledger if e["logical_op"] == op]
    attempts = [a for a in sim.provider.attempts.values() if a.logical_op == op]
    effects_H = sum(1 for e in ledger if e["commit_time"] <= H)
    effects_F = sum(1 for e in ledger if e["commit_time"] <= K.FINAL)

    def pending_at(T):
        return sum(1 for a in attempts if a.accepted_t is not None and a.accepted_t <= T
                   and (a.end_t is None or a.end_t > T))

    belief = client.belief_at_H
    keys = set([op] + [a["op_key"] for a in client.attempts])
    ids_all = set(a["attempt_id"] for a in client.attempts)
    supported = any(correlated_positive(o, keys, ids_all, client.payload_hash) for o in client.delivered)

    # Retry justification (design update §5): a retry is justified if, when it was dispatched, the
    # client's observations held an authoritative negative for every earlier attempt.
    retry_class = {}
    for rec in client.attempts[1:]:
        earlier = set(a["attempt_id"] for a in client.attempts if a["k"] < rec["k"])
        covered = authoritative_negatives(client.delivered[:rec["seen_before"]], keys, earlier)
        if earlier <= covered:
            retry_class[rec["attempt_id"]] = "justified"
        elif policy_name == "D+I" and contract == 2:
            retry_class[rec["attempt_id"]] = "contract_justified"
        else:
            retry_class[rec["attempt_id"]] = "unjustified"

    dup_cause = ""
    if effects_F > 1:
        committed_retries = [e["attempt_id"] for e in ledger if e["attempt_id"] in retry_class]
        dup_cause = ("contract" if committed_retries and all(retry_class[a] == "justified" for a in committed_retries)
                     else "policy")

    ttc_any = None
    if client.first_complete_t is not None and client.first_complete_t <= H:
        ttc_any = client.first_complete_t - client.start_t
    report = client.report_at_H or {}
    certified = belief == "complete"
    exactly_once = effects_F == 1
    # Fix H2 (v1.2): time to confirmed completion counts only operations that are certified at H AND
    # exactly-once; the v1.0-v1.1.1 measure (first `complete` of any operation) is kept as ttc_any_complete.
    ttc = ttc_any if (certified and exactly_once) else None
    row = {
        "contract": contract, "policy": policy_name, "role": registry.ROLE.get(policy_name, "custom"),
        "scenario": scenario["id"], "family": scenario["family"], "op": op,
        "effects_H": effects_H, "effects_F": effects_F, "extra_effects": max(0, effects_F - 1),
        "duplicate": effects_F > 1, "dup_cause": dup_cause,
        "exactly_once": exactly_once, "zero_effects": effects_F == 0,
        "pending_H": pending_at(H), "pending_F": pending_at(K.FINAL),
        "belief_H": belief,
        "certified_complete": certified,
        "certified_exactly_once": certified and exactly_once,
        "exactly_once_uncertified": exactly_once and not certified,
        "certified_not_exactly_once": certified and not exactly_once,
        "unsupported_complete": certified and not supported,
        "false_complete": certified and effects_H == 0,
        "false_failure": belief == "failed" and effects_F >= 1,
        "unresolved": belief == "unresolved",
        "dispatches": len(client.attempts), "retries": max(0, len(client.attempts) - 1),
        "retries_justified": sum(1 for v in retry_class.values() if v == "justified"),
        "retries_contract_justified": sum(1 for v in retry_class.values() if v == "contract_justified"),
        "retries_unjustified": sum(1 for v in retry_class.values() if v == "unjustified"),
        "retries_after_complete": client.dispatches_after_complete,
        "status_reads": client.status_reads,
        "conflicts": len(report.get("conflicts", [])),
        "ttc": ttc,
        "ttc_any_complete": ttc_any,
        "dispatch_times": " ".join("%s@%d" % (_attempt_label(a["attempt_id"]), a["t"]) for a in client.attempts),
        "commits": " ".join("%s@%d%s" % (_attempt_label(e["attempt_id"]), e["commit_time"],
                                         "!" if e["violation"] else "") for e in
                            sorted(ledger, key=lambda e: (e["commit_time"], e["attempt_id"]))),
        "violations": len(client.violations),
        "max_action_t_minus_H": max([t for t, _ in client.action_times] or [client.start_t]) - H,
    }
    return row


def cell_results(sim, scenario, contract, policy_name):
    return [op_result(sim, c, scenario, contract, policy_name) for c in sim.client_order]


# ------------------------------------------------------------------ aggregation
def median_str(values):
    if not values:
        return ""
    v = sorted(values)
    n = len(v)
    if n % 2:
        return str(v[n // 2])
    twice = v[n // 2 - 1] + v[n // 2]
    return str(twice // 2) if twice % 2 == 0 else "%d.5" % (twice // 2)


def frac(n, N):
    return "%d/%d" % (n, N)


def op_label(row):
    return row["scenario"] + ("/" + row["op"] if row["scenario"] == "S11" else "")


def aggregate(rows):
    N = len(rows)
    ttcs = [r["ttc"] for r in rows if r["ttc"] is not None]
    retries = [r["retries"] for r in rows]

    def count(key):
        return sum(1 for r in rows if r[key])

    return {
        "ops": N,
        "duplicates": frac(count("duplicate"), N),
        "extra_effects": sum(r["extra_effects"] for r in rows),
        "dup_contract_caused": frac(sum(1 for r in rows if r["dup_cause"] == "contract"), N),
        "dup_policy_caused": frac(sum(1 for r in rows if r["dup_cause"] == "policy"), N),
        "exactly_once": frac(count("exactly_once"), N),
        "zero_effects": frac(count("zero_effects"), N),
        "pending_H": sum(r["pending_H"] for r in rows),
        "pending_F": sum(r["pending_F"] for r in rows),
        "complete_H": frac(sum(1 for r in rows if r["belief_H"] == "complete"), N),
        "failed_H": frac(sum(1 for r in rows if r["belief_H"] == "failed"), N),
        "unresolved_H": frac(count("unresolved"), N),
        "unsupported_complete": frac(count("unsupported_complete"), N),
        "false_complete": frac(count("false_complete"), N),
        "false_failure": frac(count("false_failure"), N),
        "certified_exactly_once": frac(count("certified_exactly_once"), N),
        "exactly_once_uncertified": frac(count("exactly_once_uncertified"), N),
        "certified_not_exactly_once": frac(count("certified_not_exactly_once"), N),
        "retries_mean": "%.2f" % (float(sum(retries)) / N) if N else "",
        "retries_max": max(retries) if retries else 0,
        "retries_unjustified": sum(r["retries_unjustified"] for r in rows),
        "retries_contract_justified": sum(r["retries_contract_justified"] for r in rows),
        "retries_justified": sum(r["retries_justified"] for r in rows),
        "retries_after_complete": sum(r["retries_after_complete"] for r in rows),
        "status_reads": sum(r["status_reads"] for r in rows),
        "conflicts": sum(r["conflicts"] for r in rows),
        "ttc_median": median_str(ttcs),
        "ttc_max": str(max(ttcs)) if ttcs else "",
        "ttc_coverage": frac(len(ttcs), N),   # n = certified and exactly-once operations (H2)
        "duplicate_ops": " ".join(op_label(r) for r in rows if r["duplicate"]),
        "unresolved_ops": " ".join("%s(H%d/F%d)" % (op_label(r), r["effects_H"], r["effects_F"])
                                   for r in rows if r["unresolved"]),
        "false_failure_ops": " ".join(op_label(r) for r in rows if r["false_failure"]),
        "false_complete_ops": " ".join(op_label(r) for r in rows if r["false_complete"]),
    }
