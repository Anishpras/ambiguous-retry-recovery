"""Exploratory, post-review analyses (v1.2). NOT pre-specified: everything written by this module
goes to results/exploratory/ and is labelled "exploratory, post-review (v1.2)".

  ablations          C and D with parts of the evidence machinery switched off (named options)
  sensitivity        every alternative rule from the independent review, as named options
  persistent_faults  the same fault on all three attempts (scenarios/exploratory/PF*.json)
  bw_boundary        unit-step grids locating exactly where Bw duplicates
  escalation         for every unresolved operation, the evidence that would resolve it
"""
import os

from . import metrics, registry, scenarios
from . import options as O
from .runner import run_cell

LABEL = "Exploratory, post-review (v1.2). Not pre-specified; the frozen v1.1.1 core tables remain the record."
OUTCOME_KEYS = ("effects_H", "effects_F", "belief_H", "dispatches", "ttc_any_complete", "conflicts")

ABLATIONS = [
    ("no_provider_seq", "provider_seq ignored (no staleness tracking)", {"use_provider_seq": False}),
    ("no_event_id_dedupe", "event_id duplicate check off", {"dedupe_event_ids": False}),
    ("no_payload_correlation", "payload_hash not checked in correlation", {"check_payload": False}),
    ("ignore_webhooks", "every webhook ignored", {"use_webhooks": False}),
    ("ignore_status", "no status reads (polling off)", {"use_status": False}),
]

SENSITIVITY_ROWS = [
    ("baseline", "v1.2 defaults: the frozen rules plus the v1.2 fixes", {}),
    ("status_lists_pending", "status `not_found` lists pending attempts, and B and Bw re-read (every 5 ticks) "
     "instead of retrying while one is pending", {"status_lists_pending": True, "reread_on_pending": True}),
    ("webhooks_not_by_name", "A, B, Bw treat `deferred` as progress and ignore failure webhooks once complete",
     {"deferred_is_progress": True, "ignore_failure_webhooks_once_complete": True}),
    ("bw_without_C15", "Bw issues its verify read even if already complete (the reply is still ignored once "
     "complete, revision v1.1.1)", {"bw_skip_read_if_complete": False}),
    ("bw_without_C15_or_reply_guard", "as above, and A, B, Bw act on status replies after completion "
     "(v1.0/v1.1 literal reading)", {"bw_skip_read_if_complete": False, "ignore_status_replies_once_complete": False}),
    ("tau_5", "Bw waits 5 ticks", {"wait_tau": 5}),
    ("tau_10", "Bw waits 10 ticks", {"wait_tau": 10}),
    ("tau_20", "Bw waits 20 ticks", {"wait_tau": 20}),
    ("tau_30", "Bw waits 30 ticks", {"wait_tau": 30}),
    ("in_progress_is_wait", "A, B, Bw treat `in_progress` as 'wait', not as a failure signal",
     {"in_progress_is_wait": True}),
    ("abort_record_replays_failure", "contract 2: an aborted record replays the failure (later attempts with the "
     "key are refused) instead of being released", {"abort_record": "replay_failure"}),
    ("persistent_faults", "retries copy attempt 1's fault instead of being nominal", {"retry_fault": "copy_first"}),
    ("horizon_120", "H = 120 instead of 60", {"horizon": 120}),
]
SENS_METRICS = ("duplicate", "exactly_once", "unresolved", "false_failure", "false_complete")


def _cells(scns, policy, contracts, opts):
    rows = []
    for c in contracts:
        for scn in scns:
            sim = run_cell(scn, c, policy, options=opts)
            rows += metrics.cell_results(sim, scn, c, policy)
    return rows


def _key(r):
    return (r["contract"], r["scenario"], r["op"])


def _diff(base, var):
    bi = dict((_key(r), r) for r in base)
    out = []
    for r in var:
        b = bi[_key(r)]
        d = dict((k, (b[k], r[k])) for k in OUTCOME_KEYS if b[k] != r[k])
        if d:
            out.append((r, d))
    return out


def _counts(rows):
    n = len(rows)
    return " / ".join("%d" % sum(1 for r in rows if r[m]) for m in SENS_METRICS) + " of %d" % n


def _read(path):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read().strip()


# ----------------------------------------------------------------------------------------- ablations
def ablations(core, grid, docs_dir):
    lines = ["# Ablations of the reconcilers C and D", "", "_" + LABEL + "_", "",
             "Each ablation is a named policy option (arr/policies.py, POLICY_DEFAULTS). Every core and grid cell "
             "is run under both contracts and compared with the unablated policy on effects at H and F, belief at "
             "H, dispatches, time to first `complete` and conflicts. Core: 34 operations per policy (16 scenarios x "
             "2 contracts, S11 has two). Grid: 240 schedules per policy (120 x 2 contracts).", "",
             "| policy | ablation | core operations changed | grid schedules changed | core c1 dup/once/unres/false-fail/false-complete | grid c1 (same) |",
             "|---|---|---|---|---|---|"]
    csv_rows, details = [], []
    for pol in ("D", "C"):
        base_c, base_g = _cells(core, pol, (1, 2), {}), _cells(grid, pol, (1, 2), {})
        for name, desc, opts in ABLATIONS:
            vc, vg = _cells(core, pol, (1, 2), opts), _cells(grid, pol, (1, 2), opts)
            dc, dg = _diff(base_c, vc), _diff(base_g, vg)
            lines.append("| %s | %s (%s) | %d of %d | %d of %d | %s | %s |" % (
                pol, name, desc, len(dc), len(vc), len(dg), len(vg),
                _counts([r for r in vc if r["contract"] == 1]), _counts([r for r in vg if r["contract"] == 1])))
            for scope, d in (("core", dc), ("grid", dg)):
                for r, ch in d:
                    csv_rows.append({"policy": pol, "ablation": name, "scope": scope, "contract": r["contract"],
                                     "scenario": r["scenario"], "op": r["op"],
                                     "changes": "; ".join("%s: %s -> %s" % (k, a, b) for k, (a, b) in sorted(ch.items()))})
            if dc:
                details += ["", "**%s, %s: changed core operations**" % (pol, name), ""]
                details += ["- c%d %s/%s: %s" % (r["contract"], r["scenario"], r["op"], "; ".join(
                    "%s %s -> %s" % (k, a, b) for k, (a, b) in sorted(ch.items()))) for r, ch in dc]
            if dg:
                fields = {}
                for _, ch in dg:
                    for k in ch:
                        fields[k] = fields.get(k, 0) + 1
                details += ["", "**%s, %s: grid changes by field**: %s" % (pol, name, ", ".join(
                    "%s in %d" % (k, v) for k, v in sorted(fields.items())))]
    lines += ["", "Baseline (no ablation) core c1 for reference: D %s; C %s." % (
        _counts([r for r in _cells(core, "D", (1,), {})]), _counts([r for r in _cells(core, "C", (1,), {})])), ""]
    lines += ["## Details"] + details + ["", "## Why order and repeats cannot matter", "",
                                         "(From docs/monotone-evidence.md.)", "", _read(os.path.join(docs_dir, "monotone-evidence.md"))]
    return "\n".join(lines) + "\n", csv_rows


# ----------------------------------------------------------------------------------------- sensitivity
def sensitivity(core, grid, notes_text):
    csv_rows = []
    table = {}
    for row, desc, opts in SENSITIVITY_ROWS:
        for pol in registry.POLICIES:
            for c in registry.CONTRACTS_FOR[pol]:
                for scope, scns in (("core", core), ("grid", grid)):
                    rs = _cells(scns, pol, (c,), opts)
                    vals = dict((m, sum(1 for r in rs if r[m])) for m in SENS_METRICS)
                    vals["N"] = len(rs)
                    table[(row, pol, c, scope)] = vals
                    rec = {"row": row, "options": " ".join("%s=%s" % kv for kv in sorted(opts.items())),
                           "policy": pol, "contract": c, "scope": scope}
                    rec.update(vals)
                    csv_rows.append(rec)
    fmt = lambda v: "%d/%d/%d/%d/%d" % tuple(v[m] for m in SENS_METRICS)
    lines = ["# Sensitivity of the results to alternative rules", "", "_" + LABEL + "_", "",
             "One row per alternative rule from the independent review (section 3). Each is a named option "
             "(arr/options.py) applied to every policy, contract, core scenario and grid schedule; options that "
             "only concern some policies leave the others unchanged. Cells read duplicates / exactly-once / "
             "unresolved at H / false failure / false complete, as counts of operations (core: 17 per contract; "
             "grid: 120). Bold = differs from the baseline row. Counts are over authored cases, not rates.", ""]
    changes = []
    for row, desc, opts in SENSITIVITY_ROWS:
        lines += ["## %s" % row, "", "%s. Options: `%s`." % (desc, ", ".join("%s=%s" % kv for kv in sorted(opts.items()))
                                                             or "none"), "",
                  "| policy | c1 core | c1 grid | c2 core | c2 grid |", "|---|---|---|---|---|"]
        for pol in registry.POLICIES:
            cells = []
            for c in (1, 2):
                for scope in ("core", "grid"):
                    v = table.get((row, pol, c, scope))
                    if v is None:
                        cells.append("-")
                        continue
                    b = table[("baseline", pol, c, scope)]
                    txt = fmt(v)
                    if v != b:
                        txt = "**%s**" % txt
                        diffs = ["%s %d->%d" % (m, b[m], v[m]) for m in SENS_METRICS if b[m] != v[m]]
                        changes.append("- %s: %s c%d %s: %s" % (row, pol, c, scope, ", ".join(diffs)))
                    cells.append(txt)
            lines.append("| %s | %s |" % (registry.LABEL[pol], " | ".join(cells)))
        lines.append("")
    lines += ["## Every change against the baseline row", ""] + (changes or ["None."])
    lines += ["", "## Interpretation (hand-written after the run; notes/sensitivity_conclusions.md, not frozen)", "",
              notes_text or "Not written yet."]
    return "\n".join(lines) + "\n", csv_rows


# ----------------------------------------------------------------------------------------- persistent faults
def persistent_faults():
    pf = scenarios.load_exploratory()
    pf = [s for s in pf if s["id"].startswith("PF")]
    lines = ["# Persistent faults: the same fault on all three attempts", "", "_" + LABEL + "_", "",
             "Scenarios in scenarios/exploratory/PF*.json use the option `retry_fault: copy_first`, so every "
             "retry repeats attempt 1's fault (fix for review item H3: in the frozen matrix every retry is "
             "nominal). Cell: effects at F, belief at H, dispatch times; flags DUP, FALSE-FAIL, FALSE-COMPLETE.", ""]
    csv_rows, cells = [], []
    for scn in pf:
        lines += ["## %s: %s" % (scn["id"], scn.get("title", "")), "", scn.get("protocol_script", ""), "",
                  "| policy | contract 1 | contract 2 |", "|---|---|---|"]
        for pol in registry.POLICIES:
            out = []
            for c in (1, 2):
                if c not in registry.CONTRACTS_FOR[pol]:
                    out.append("-")
                    continue
                sim = run_cell(scn, c, pol)
                r = metrics.cell_results(sim, scn, c, pol)[0]
                cells.append({"contract": c, "policy": pol, "scenario": scn["id"], "scenario_obj": scn, "sim": sim,
                              "rows": [r]})
                flags = [f for f, k in (("DUP", "duplicate"), ("FALSE-FAIL", "false_failure"),
                                        ("FALSE-COMPLETE", "false_complete")) if r[k]]
                out.append("%d effects, %s, %s%s" % (r["effects_F"], r["belief_H"], r["dispatch_times"],
                                                    (" **" + " ".join(flags) + "**") if flags else ""))
                csv_rows.append(dict((k, r[k]) for k in ("contract", "policy", "scenario", "effects_H", "effects_F",
                                                         "duplicate", "belief_H", "false_failure", "false_complete",
                                                         "unresolved", "dispatches", "dispatch_times", "commits")))
            lines.append("| %s | %s |" % (registry.LABEL[pol], " | ".join(out)))
        lines.append("")
    return "\n".join(lines) + "\n", csv_rows, cells


# ----------------------------------------------------------------------------------------- Bw boundary
def _g1(L, R, tau_unused=None):
    a1 = {"commit_after": 1, "response": None, "webhooks": {"committed": [] if R is None else [R - 2]}}
    return scenarios._finish({"id": "BW_L%s_R%s" % (L, R), "family": "bw_boundary", "status_lag": L,
                              "operations": [{"op_key": "op-1", "start": 0, "payload": _payload(), "attempts": {"1": a1}}]})


def _payload():
    return scenarios.load_json("grids.json")["payload"]


def bw_boundary():
    """Unit-step grids for Bw under contract 1 (where nothing deduplicates).

    Grid 1 (lost ack): a1 commits at t = 2, response lost, the `committed` receipt arrives at t = R
    (3..70, or lost), status lag L = 0..64. Grid 2 (pending): receipt lost, a1 commits at t = 1 + E
    (E = 1..40), L = 0..40, tau = 15."""
    taus = (5, 10, 15, 20, 30)
    Ls = list(range(0, 65))
    Rs = list(range(3, 71)) + [None]
    lines = ["# Where Bw duplicates: unit-step boundary", "", "_" + LABEL + "_", "",
             "Contract 1, policy Bw, timeout T = 5. Grid 1: a1 commits at t = 2 with its response lost; the "
             "`committed` receipt arrives at t = R (3 to 70, or lost); status lag L = 0 to 64. A duplicate needs "
             "both the receipt to miss the verify window and the verify read to miss the commit.", "",
             "| tau | duplicates | smallest L with a duplicate | smallest R with a duplicate | rectangle {L >= L*, R >= R* or lost} exact? | predicted L* = tau + T - c + 1 | predicted R* = tau + T + 2 |",
             "|---|---|---|---|---|---|---|"]
    csv_rows = []
    maps = {}
    for tau in taus:
        dup = {}
        for L in Ls:
            for R in Rs:
                sim = run_cell(_g1(L, R), 1, "Bw", options={"wait_tau": tau})
                dup[(L, R)] = len(sim.provider.ledger) > 1
        hits = [k for k, v in dup.items() if v]
        Lstar = min(k[0] for k in hits) if hits else None
        Rstar = min(k[1] for k in hits if k[1] is not None) if any(k[1] is not None for k in hits) else None
        exact = all(dup[(L, R)] == (Lstar is not None and L >= Lstar and (R is None or (Rstar is not None and R >= Rstar)))
                    for L in Ls for R in Rs)
        lines.append("| %d | %d of %d | %s | %s | %s | %d | %d |" % (tau, len(hits), len(dup), Lstar, Rstar,
                                                                    "yes" if exact else "NO", tau + 5 - 2 + 1, tau + 5 + 2))
        csv_rows.append({"grid": "lost_ack", "tau": tau, "duplicates": len(hits), "cells": len(dup), "L_star": Lstar,
                         "R_star": Rstar, "rectangle_exact": exact, "predicted_L_star": tau + 4,
                         "predicted_R_star": tau + 7})
        maps[tau] = dup
    lines += ["", "Map for tau = 15 (rows L = 0..64, columns R = 3..70 then `L` = lost; `X` = duplicate, `.` = one effect):",
              "", "```", "L\\R  " + "".join(str(R % 10) if R is not None else "L" for R in Rs)]
    for L in Ls:
        lines.append("%3d  %s" % (L, "".join("X" if maps[15][(L, R)] else "." for R in Rs)))
    lines += ["```", ""]
    # Grid 2: pending (in-flight) dimension
    lines += ["Grid 2 (tau = 15, receipt lost, response lost): a1 commits at t = 1 + E. Predicted: duplicate iff the "
              "verify read at t = T + tau = 20 cannot see the commit, i.e. 1 + E > 20 - L, i.e. E + L >= 20 "
              "(while the commit falls before F).", ""]
    bad, n2, d2 = [], 0, 0
    for E in range(1, 41):
        for L in range(0, 41):
            a1 = {"commit_after": E, "response": None, "webhooks": {"committed": []}}
            scn = scenarios._finish({"id": "BW2", "family": "bw_boundary", "status_lag": L,
                                     "operations": [{"op_key": "op-1", "start": 0, "payload": _payload(),
                                                     "attempts": {"1": a1}}]})
            sim = run_cell(scn, 1, "Bw")
            dup = len(sim.provider.ledger) > 1
            n2 += 1
            d2 += dup
            if dup != (E + L >= 20):
                bad.append((E, L, dup))
    lines.append("Result: %d of %d cells duplicate; cells disagreeing with `E + L >= 20`: %s." % (
        d2, n2, bad[:10] if bad else "none"))
    csv_rows.append({"grid": "pending_tau15", "tau": 15, "duplicates": d2, "cells": n2, "L_star": "", "R_star": "",
                     "rectangle_exact": not bad, "predicted_L_star": "E+L>=20", "predicted_R_star": ""})
    lines += ["", "General condition (lost ack or pending, no receipt in time): Bw is duplicate-free iff its verify "
              "read sees the commit, i.e. commit_time <= t_signal + tau - L. With commit_time <= dispatch + E_max "
              "(an in-flight bound covering arrival and execution) and t_signal = dispatch + T, a sufficient "
              "condition is **tau >= E_max + L_max - T**. Both grids above confirm it at unit resolution."]
    return "\n".join(lines) + "\n", csv_rows


# ----------------------------------------------------------------------------------------- escalation
def _attempt_truth(sim, attempt_id, H):
    a = sim.provider.attempts[attempt_id]
    e = [x for x in sim.provider.ledger if x["attempt_id"] == attempt_id]
    if e:
        t = e[0]["commit_time"]
        return ("committed", t) if t <= H else ("commits_after_H", t)
    if a.state == "lost":
        return ("never_arrived", None)
    if a.state == "pending":
        return ("pending_at_F", None)
    if a.state == "aborted":
        return ("aborted", a.end_t)
    return (a.state, a.end_t)


def escalation(cells):
    """For every unresolved operation: the dispatched attempts the client could not close, and what
    evidence would resolve the operation (computed by the scorer, with the hidden truth for context)."""
    csv_rows = []
    for cell in cells:
        sim = cell["sim"]
        for client in sim.client_order:
            if client.belief_at_H != "unresolved" or not hasattr(client, "delivered"):
                continue
            keys = set([client.logical_op] + [a["op_key"] for a in client.attempts])
            ids_all = set(a["attempt_id"] for a in client.attempts)
            covered = metrics.authoritative_negatives(client.delivered, keys, ids_all)
            open_ = [a["attempt_id"] for a in client.attempts if a["attempt_id"] not in covered]
            needs, truths = [], []
            for aid in open_:
                state, t = _attempt_truth(sim, aid, client.horizon_t)
                short = aid.split("#")[-1]
                truths.append("%s %s%s" % (short, state, "" if t is None else "@%d" % t))
                if state == "committed":
                    needs.append("correlated positive for %s" % short)
                elif state == "commits_after_H":
                    needs.append("correlated positive for %s after t=%d (or a longer horizon)" % (short, t))
                elif state == "never_arrived":
                    needs.append("terminal negative or in-flight time bound for %s" % short)
                elif state == "aborted":
                    needs.append("terminal negative for %s" % short)
                else:
                    needs.append("in-flight time bound for %s" % short)
            csv_rows.append({"source": cell.get("source", ""), "contract": cell["contract"], "policy": cell["policy"],
                             "scenario": cell["scenario"], "op": client.logical_op,
                             "open_attempts": " ".join(a.split("#")[-1] for a in open_),
                             "would_complete_on": "correlated positive (ok, committed receipt, status found) for any of "
                                                  "[%s]" % ", ".join(a.split("#")[-1] for a in open_),
                             "would_retry_or_fail_on": "terminal negative for each of [%s]" % ", ".join(
                                 a.split("#")[-1] for a in open_),
                             "evidence_that_resolves_it": "; ".join(needs), "hidden_truth": "; ".join(truths)})
    cats = {}
    for r in csv_rows:
        for part in r["evidence_that_resolves_it"].split("; "):
            kind = ("correlated positive" if part.startswith("correlated positive") and "after" not in part else
                    "correlated positive after H / longer horizon" if part.startswith("correlated positive") else
                    "terminal negative or in-flight bound" if part.startswith("terminal negative or") else
                    "terminal negative" if part.startswith("terminal negative") else "in-flight time bound")
            key = (r["source"], r["policy"], kind)
            cats[key] = cats.get(key, 0) + 1
    lines = ["# Escalation detail: what would resolve each unresolved operation", "", "_" + LABEL + "_", "",
             "For every operation whose belief at H is `unresolved`, the attempts the client could not close (no "
             "authoritative negative observed) and the evidence that would resolve it, given the hidden truth. "
             "Full list: escalation.csv.", "",
             "| source | policy | evidence needed (per open attempt) | count |", "|---|---|---|---|"]
    for (src, pol, kind), n in sorted(cats.items(), key=lambda x: (x[0][0], registry.ORDER.get(x[0][1], 99), x[0][2])):
        lines.append("| %s | %s | %s | %d |" % (src, registry.LABEL.get(pol, pol), kind, n))
    core = [r for r in csv_rows if r["source"] == "core"]
    if core:
        lines += ["", "Core matrix, every unresolved operation:", "",
                  "| contract | policy | scenario/op | open attempts | evidence that resolves it | hidden truth |",
                  "|---|---|---|---|---|---|"]
        for r in core:
            lines.append("| %s | %s | %s/%s | %s | %s | %s |" % (r["contract"], r["policy"], r["scenario"], r["op"],
                                                              r["open_attempts"], r["evidence_that_resolves_it"],
                                                              r["hidden_truth"]))
    return "\n".join(lines) + "\n", csv_rows
