#!/usr/bin/env python3
"""Reproduce the ambiguous-retry recovery pilot (see PROTOCOL.md and README.md).

Frozen study:
    python3 run_sim.py                      # frozen collection: validate, core matrix + grids, exploratory, results/
    python3 run_sim.py --validate           # pre-freeze checks only (V1-V5, unit and mutation tests)
    python3 run_sim.py --freeze --label vX --note "..."   # record SHA-256 hashes in FREEZE.json
    python3 run_sim.py --check-reproducible # V7: run the collection twice in temp dirs, compare every byte
    python3 run_sim.py --show 1 D S04       # readable trace of one frozen cell (contract, policy, scenario or grid id)

Your own provider and policy (no freeze gate, no predictions):
    python3 run_sim.py explore --scenario my.json --contract 1 --policy D [--option key=value ...]
    python3 run_sim.py explore --scenario my.json --policy examples/custom_policy.py:PatientReconciler
    python3 run_sim.py replay --observations recorded.jsonl --policy D

Python 3.9+ standard library only. No randomness, no network. Exit status 0 only if every check passes.
"""
import argparse
import datetime
import glob
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from arr import constants as K  # noqa: E402
from arr import delta, exploratory, metrics, predictions, registry, report, scenarios, validate  # noqa: E402
from arr import options as O  # noqa: E402
from arr.runner import run_cell  # noqa: E402

FREEZE = os.path.join(ROOT, "FREEZE.json")
NOTES = os.path.join(ROOT, "notes", "prediction_explanations.md")
SENS_NOTES = os.path.join(ROOT, "notes", "sensitivity_conclusions.md")
# Baselines: committed results extracted byte-for-byte with `git show <commit>:results/<file>`.
BASELINES = [("v1.0", "924aef2"), ("v1.1", "622e1f1"), ("v1.1.1", "b95a667")]
CURRENT_LABEL = K.STUDY_VERSION

# Freeze groups (review §7): model code and fixtures versus reporting, validation and analysis code.
MODEL_FILES = ["arr/constants.py", "arr/ids.py", "arr/options.py", "arr/policies.py", "arr/provider.py",
               "arr/references.py", "arr/registry.py", "arr/runner.py", "arr/scenarios.py", "arr/sim.py",
               "arr/client.py"]


def bdir(label):
    return os.path.join(ROOT, "baselines", label)


# ------------------------------------------------------------------------------------- freeze
def frozen_files():
    pats = ["PROTOCOL.md", "scenarios/*.json", "scenarios/exploratory/*.json", "baselines/*/*",
            "docs/monotone-evidence.md", "run_sim.py", "arr/*.py", "tests/*.py"]
    out = []
    for pat in pats:
        out += sorted(os.path.relpath(p, ROOT).replace(os.sep, "/") for p in glob.glob(os.path.join(ROOT, pat)))
    return out


def freeze_groups(files):
    model = [f for f in files if f in MODEL_FILES or f.startswith("scenarios/")]
    return {"model_and_fixtures": model, "protocol": ["PROTOCOL.md"],
            "reporting_validation_analysis": [f for f in files if f not in model and f != "PROTOCOL.md"]}


def sha256(rel):
    with open(os.path.join(ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_freeze():
    if not os.path.exists(FREEZE):
        return {"history": []}
    with open(FREEZE, encoding="utf-8") as fh:
        return json.load(fh)


def freeze_status():
    hist = load_freeze()["history"]
    if not hist:
        return {"frozen": False, "matches": False, "label": None, "mismatched": [], "not_covered": []}
    last = hist[-1]
    files = frozen_files()
    mismatched = sorted(f for f, h in last["sha256"].items()
                        if not os.path.exists(os.path.join(ROOT, f)) or sha256(f) != h)
    not_covered = sorted(f for f in files if f not in last["sha256"])
    return {"frozen": True, "label": last["label"], "frozen_at_utc": last["frozen_at_utc"],
            "matches": not mismatched and not not_covered, "mismatched": mismatched, "not_covered": not_covered}


# ------------------------------------------------------------------------------------- checks
def unit_tests():
    suite = unittest.TestLoader().discover(os.path.join(ROOT, "tests"), top_level_dir=ROOT)
    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    detail = "ran=%d failures=%d errors=%d" % (res.testsRun, len(res.failures), len(res.errors))
    if not res.wasSuccessful():
        detail += "; " + "; ".join("%s: %s" % (t, tb.strip().splitlines()[-1]) for t, tb in res.failures + res.errors)
    return [validate.result("unit_and_mutation_tests", res.wasSuccessful(), detail)]


def prefreeze():
    return validate.prefreeze_checks() + unit_tests()


def print_checks(checks):
    n_ok = sum(c["ok"] for c in checks)
    for c in checks:
        if not c["ok"]:
            print("  FAIL", c["check"], c["detail"])
    print("Validation: %d/%d checks passed" % (n_ok, len(checks)))
    return n_ok == len(checks)


# ------------------------------------------------------------------------------------- collection
def run_cells(scns, source):
    cells = []
    for c in K.CONTRACTS:
        for p in registry.POLICIES:
            if c not in registry.CONTRACTS_FOR[p]:
                continue
            for scn in scns:
                sim = run_cell(scn, c, p)
                cells.append({"contract": c, "policy": p, "scenario": scn["id"], "scenario_obj": scn, "sim": sim,
                              "rows": metrics.cell_results(sim, scn, c, p), "source": source})
    return cells


def collect(out):
    frz = freeze_status()
    if not frz["matches"]:
        print("REFUSING TO COLLECT: the current files do not match the latest FREEZE.json entry.")
        print("  freeze=%s mismatched=%s not_covered=%s" % (frz.get("label"), frz["mismatched"], frz["not_covered"]))
        print("  (Use `python3 run_sim.py explore ...` to run your own scenarios without the freeze gate.)")
        return 2
    checks = prefreeze()
    if not all(c["ok"] for c in checks):
        print("PRE-RUN VALIDATION FAILED; not collecting.")
        print_checks(checks)
        return 1

    core = scenarios.load_core()
    grid = scenarios.build_grids()
    cells = run_cells(core, "core")
    gcells = run_cells(grid, "grid")
    rows = report.sort_rows([r for cell in cells for r in cell["rows"]])
    grows = report.grid_rows(gcells)   # generation order: contract, policy, grid axis order
    cell_index = {(cl["contract"], cl["policy"], cl["scenario"]): cl["sim"] for cl in cells}

    # ---- post-run checks on every run: V4 on the matrix runs, V5 parity, V6 sanity labels
    for p in registry.CLIENT_POLICIES:
        if 1 in registry.CONTRACTS_FOR[p]:
            same = validate.io_bytes(cell_index[(1, p, "S08")]) == validate.io_bytes(cell_index[(1, p, "S09")])
            checks.append(validate.result("V4_matrix_S08_S09_identical_%s" % p, same))
    checks += validate.check_v5([cl["sim"] for cl in cells], "core_matrix")
    checks += validate.check_v5([cl["sim"] for cl in gcells], "grids")
    sanity = scenarios.load_json("sanity_labels.json")
    checks += validate.check_v6(rows + grows, sanity)
    seqv = [v for cl in cells + gcells for v in cl["sim"].provider.seq_order_violations]
    checks.append(validate.result("V2_provider_seq_increases_in_emission_order_all_runs", not seqv, str(seqv[:3])))
    pend = sum(r["pending_F"] for r in rows + grows)
    checks.append(validate.result("pending_beyond_F_is_zero", pend == 0, "pending at F: %d" % pend))

    preds = predictions.check_all(rows, cell_index)
    notes = read(NOTES)

    # ---- frozen-study outputs
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    report.write_traces(out, cells)
    report.write_text(os.path.join(out, "summary.csv"), report.csv_text(rows, report.SUMMARY_FIELDS))
    pol = report.by_policy_rows(rows)
    report.write_text(os.path.join(out, "by_policy.csv"),
                      report.csv_text(pol, ["scope", "contract", "policy", "role"] + report.AGG_FIELDS))
    report.write_text(os.path.join(out, "by_family.csv"),
                      report.csv_text(report.by_family_rows(rows), ["contract", "policy", "role", "family"] + report.AGG_FIELDS))
    report.write_text(os.path.join(out, "headline.md"), report.headline_md(pol))
    report.write_text(os.path.join(out, "grid.csv"), report.csv_text(grows, report.GRID_FIELDS))
    report.write_text(os.path.join(out, "grid_tables.md"),
                      report.grid_tables_md(grows, scenarios.load_json("grids.json")["grids"]))
    base_verdicts = [(label, delta.baseline_verdicts(bdir(label))) for label, _ in BASELINES]
    report.write_text(os.path.join(out, "predictions_check.md"), predictions.predictions_md(preds, notes, base_verdicts))
    report.write_text(os.path.join(out, "worked_traces.md"), report.worked_traces_md(cell_index, rows))
    ties = [dict(contract=cl["contract"], policy=cl["policy"], scenario=cl["scenario"], t=x["t"], phase=x["phase"],
                 op=x["op"], order=" > ".join(x["order"])) for cl in cells for x in cl["sim"].ties]
    report.write_text(os.path.join(out, "ties.csv"),
                      report.csv_text(ties, ["contract", "policy", "scenario", "t", "phase", "op", "order"]))
    src = "committed %s results (git %s, `baselines/%s/`)"
    b = dict((label, (commit, bdir(label))) for label, commit in BASELINES)
    report.write_text(os.path.join(out, "revision_v1.1_delta.md"), delta.delta_md([
        (b["v1.0"][1], b["v1.1"][1], "v1.0", "v1.1", src % ("v1.0", b["v1.0"][0], "v1.0"), src % ("v1.1", b["v1.1"][0], "v1.1")),
        (b["v1.1"][1], b["v1.1.1"][1], "v1.1", "v1.1.1", src % ("v1.1", b["v1.1"][0], "v1.1"),
         src % ("v1.1.1", b["v1.1.1"][0], "v1.1.1"))]))
    report.write_text(os.path.join(out, "revision_v1.2_delta.md"), delta.delta_md([
        (b["v1.1.1"][1], out, "v1.1.1", CURRENT_LABEL, src % ("v1.1.1", b["v1.1.1"][0], "v1.1.1"),
         "this run (%s)" % CURRENT_LABEL)]))

    # ---- exploratory, post-review (v1.2) outputs
    ex = os.path.join(out, "exploratory")
    md, rows_ab = exploratory.ablations(core, grid, os.path.join(ROOT, "docs"))
    report.write_text(os.path.join(ex, "ablations.md"), md)
    report.write_text(os.path.join(ex, "ablations.csv"),
                      report.csv_text(rows_ab, ["policy", "ablation", "scope", "contract", "scenario", "op", "changes"]))
    md, rows_s = exploratory.sensitivity(core, grid, read(SENS_NOTES))
    report.write_text(os.path.join(ex, "sensitivity.md"), md)
    report.write_text(os.path.join(ex, "sensitivity.csv"), report.csv_text(
        rows_s, ["row", "options", "policy", "contract", "scope", "N"] + list(exploratory.SENS_METRICS)))
    md, rows_pf, pf_cells = exploratory.persistent_faults()
    report.write_text(os.path.join(ex, "persistent_faults.md"), md)
    report.write_text(os.path.join(ex, "persistent_faults.csv"), report.csv_text(rows_pf, list(rows_pf[0].keys())))
    md, rows_bw = exploratory.bw_boundary()
    report.write_text(os.path.join(ex, "bw_boundary.md"), md)
    report.write_text(os.path.join(ex, "bw_boundary.csv"), report.csv_text(rows_bw, list(rows_bw[0].keys())))
    for cl in pf_cells:
        cl["source"] = "persistent_fault"
    md, rows_esc = exploratory.escalation(cells + gcells + pf_cells)
    report.write_text(os.path.join(ex, "escalation.md"), md)
    report.write_text(os.path.join(ex, "escalation.csv"), report.csv_text(
        rows_esc, ["source", "contract", "policy", "scenario", "op", "open_attempts", "would_complete_on",
                   "would_retry_or_fail_on", "evidence_that_resolves_it", "hidden_truth"]))

    report.write_text(os.path.join(out, "validation.json"), json.dumps(checks, indent=2) + "\n")
    run_info = {
        "command": "python3 run_sim.py",
        "study_version": CURRENT_LABEL,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "fixture_version": K.FIXTURE_VERSION,
        "constants": K.PARITY,
        "default_options": O.DEFAULTS,
        "contracts": list(K.CONTRACTS),
        "policies": dict((p, {"role": registry.ROLE[p], "label": registry.LABEL[p],
                              "contracts": list(registry.CONTRACTS_FOR[p])}) for p in registry.POLICIES),
        "runs": {"core_matrix": len(cells), "grids": len(gcells),
                 "operations_core": len(rows), "operations_grid": len(grows)},
        "sha256": dict((f, sha256(f)) for f in frozen_files()),
        "freeze": frz,
        "unfrozen_inputs_sha256": dict((os.path.relpath(p, ROOT), hashlib.sha256(read(p).encode("utf-8")).hexdigest())
                                       for p in (NOTES, SENS_NOTES) if os.path.exists(p)),
        "validation_all_ok": all(c["ok"] for c in checks),
        "predictions": {"match": sum(1 for p in preds if p["verdict"].startswith("MATCH")),
                        "vacuous": sum(1 for p in preds if p["verdict"] == "MATCH (vacuous)"), "total": len(preds)},
    }
    report.write_text(os.path.join(out, "run_info.json"), json.dumps(run_info, indent=2, sort_keys=True) + "\n")

    # ---- console
    print("Ambiguous retry recovery pilot %s | fixtures v%s | Python %s | freeze %s" % (
        CURRENT_LABEL, K.FIXTURE_VERSION, platform.python_version(), frz["label"]))
    print("%d core cells (%d operations), %d grid cells; exploratory outputs in %s" % (
        len(cells), len(rows), len(gcells), ex))
    print()
    fmt = "%-3s %-9s %-7s %-6s %-6s %-6s %-6s %-6s %-6s %s"
    print(fmt % ("c", "policy", "dup", "once", "zero", "unres", "f.comp", "f.fail", "retry",
                 "ttc med/max (certified & once)"))
    for r in pol:
        if r["scope"] != "S00-S15":
            continue
        print(fmt % (r["contract"], r["policy"], r["duplicates"], r["exactly_once"], r["zero_effects"], r["unresolved_H"],
                     r["false_complete"], r["false_failure"], r["retries_mean"],
                     "%s/%s (%s)" % (r["ttc_median"] or "-", r["ttc_max"] or "-", r["ttc_coverage"])))
    print()
    print("Predictions: %d/%d match, %d vacuously (results/predictions_check.md); counts are over authored cases, "
          "not rates" % (run_info["predictions"]["match"], len(preds), run_info["predictions"]["vacuous"]))
    ok = print_checks(checks)
    print("Results written to %s" % out)
    return 0 if ok else 1


def read(path):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ------------------------------------------------------------------------------------- V7
def tree(d):
    out = {}
    for base, _, files in os.walk(d):
        for f in files:
            p = os.path.join(base, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, d).replace(os.sep, "/")] = fh.read()
    return out


def check_reproducible():
    tmp = tempfile.mkdtemp(prefix="arr-repro-")
    try:
        trees, codes = [], []
        for i in (1, 2):
            d = os.path.join(tmp, "run%d" % i)
            proc = subprocess.run([sys.executable, os.path.join(ROOT, "run_sim.py"), "--out", d],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
            codes.append(proc.returncode)
            trees.append(tree(d) if os.path.isdir(d) else {})
        a, b = trees
        diff = sorted(f for f in set(a) | set(b) if a.get(f) != b.get(f))
        print("V7 run 1 vs run 2: %d files, %d differ; exit codes %s" % (len(a), len(diff), codes))
        for f in diff[:10]:
            print("  differs:", f)
        ok = not diff and a and codes == [0, 0]
        res_dir = os.path.join(ROOT, "results")
        if os.path.isdir(res_dir):
            r = tree(res_dir)
            rdiff = sorted(f for f in set(a) | set(r) if a.get(f) != r.get(f))
            print("results/ vs run 1: %d files, %d differ%s" % (len(r), len(rdiff),
                                                               (": " + ", ".join(rdiff[:10])) if rdiff else ""))
            ok = ok and not rdiff
        print("V7 reproducibility: %s" % ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp)


# ------------------------------------------------------------------------------------- show / explore / replay
def print_trace(sim):
    for e in sim.trace:
        d = report.describe(e)
        if d is None:
            continue
        col, text = d
        print("t=%3d ph%d %-8s %s%s" % (e["t"], e["phase"], col, "   " if e["visible"] else "[h]", text.replace("**", "")))


def print_rows(rows):
    keys = ["op", "effects_H", "effects_F", "duplicate", "belief_H", "unsupported_complete", "false_complete",
            "false_failure", "dispatches", "retries_unjustified", "status_reads", "conflicts", "ttc",
            "ttc_any_complete", "dispatch_times", "commits"]
    for r in rows:
        print("metrics " + " ".join("%s=%s" % (k, report._fmt(r[k])) for k in keys))


def show(contract, policy, sid):
    scn = scenarios.load_scenario(sid)
    sim = run_cell(scn, int(contract), policy)
    print("%s | contract %s | policy %s" % (sid, contract, registry.LABEL.get(policy, policy)))
    if "protocol_script" in scn:
        print("script: " + scn["protocol_script"])
    print("freeze: %s" % ("matches " + str(freeze_status()["label"]) if freeze_status()["matches"] else "NOT a frozen run"))
    print_trace(sim)
    print_rows(metrics.cell_results(sim, scn, int(contract), policy))
    return 0


def explore(argv):
    ap = argparse.ArgumentParser(prog="run_sim.py explore",
                                 description="Run one scenario file under one policy, outside the frozen study.")
    ap.add_argument("--scenario", required=True, help="scenario JSON (docs/scenario-format.md)")
    ap.add_argument("--contract", type=int, default=1, choices=(1, 2))
    ap.add_argument("--policy", required=True,
                    help="registry name (%s) or module:Class or path/file.py:Class" % ", ".join(registry.POLICIES))
    ap.add_argument("--option", action="append", default=[], metavar="KEY=VALUE",
                    help="named option (arr/options.py), repeatable; overrides the scenario's own options")
    ap.add_argument("--quiet", action="store_true", help="metrics row only")
    args = ap.parse_args(argv)
    scn = scenarios.load_file(args.scenario)
    opts = O.parse_cli(args.option)
    sim = run_cell(scn, args.contract, args.policy, options=opts)
    print("EXPLORATORY run (not part of the frozen study) | scenario %s | contract %d | policy %s" % (
        scn.get("id", args.scenario), args.contract, registry.resolve(args.policy)["label"]))
    print("options (non-default): %s" % (json.dumps(O.non_default(sim.options), sort_keys=True)))
    if not args.quiet:
        print_trace(sim)
    print_rows(metrics.cell_results(sim, scn, args.contract, args.policy))
    for c in sim.client_order:
        if getattr(c, "violations", None):
            print("runtime violations for %s: %s" % (c.logical_op, c.violations))
    return 0


def replay(argv):
    ap = argparse.ArgumentParser(prog="run_sim.py replay",
                                 description="Feed recorded observations to a policy and print its decisions "
                                             "(docs/trace-schema.md).")
    ap.add_argument("--observations", required=True,
                    help="JSONL: one observation per line, or a trace from results/traces/ (observe events are used)")
    ap.add_argument("--policy", required=True, help="registry client policy name or module:Class / file.py:Class")
    ap.add_argument("--contract", type=int, default=1, choices=(1, 2),
                    help="tells D+I whether the provider deduplicates")
    ap.add_argument("--op", default=None, help="operation to replay when the file holds several (default: first)")
    ap.add_argument("--option", action="append", default=[], metavar="KEY=VALUE")
    args = ap.parse_args(argv)
    entry = registry.resolve(args.policy)
    if entry["kind"] != "client":
        print("replay needs a client policy; references read hidden state that a recording does not contain")
        return 2
    obs_list = []
    with open(args.observations, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if "event" in rec and "details" in rec:   # a simulator trace line
                if rec["event"] != "observe":
                    continue
                if args.op is None:
                    args.op = rec["op"]
                if rec["op"] != args.op:
                    continue
                obs_list.append(rec["details"]["obs"])
            else:
                obs_list.append(rec)
    policy = registry.construct(entry["cls"], args.contract, O.merge(O.parse_cli(args.option)))
    print("REPLAY of %d recorded observations to policy %s (contract %d). Recorded observations are fed as-is; a "
          "decision that differs from what the recording did cannot change later observations." % (
              len(obs_list), entry["label"], args.contract))
    for obs in obs_list:
        actions = policy.observe(json.loads(json.dumps(obs))) or []
        print("t=%-4s %-60s -> %-40s belief=%s" % (obs.get("t", "?"), summarize(obs)[:60],
                                                   ", ".join(action_text(a) for a in actions) or "-", policy.belief()))
    print("final belief: %s" % policy.belief())
    rep = policy.report() if hasattr(policy, "report") else {}
    if rep.get("conflicts"):
        print("conflicts: %s" % rep["conflicts"])
    return 0


def summarize(o):
    typ = o.get("type")
    if typ == "response":
        return "response %s %s" % (o.get("kind"), o.get("attempt_id"))
    if typ == "webhook":
        return "webhook %s %s seq=%s" % (o.get("event"), o.get("attempt_id"), o.get("provider_seq"))
    if typ == "status":
        return "status %s %s" % (o.get("result"), o.get("terminal_attempts", o.get("attempt_id", "")))
    if typ in ("timeout", "dispatched"):
        return "%s %s" % (typ, o.get("attempt_id"))
    if typ == "timer":
        return "timer %s" % o.get("tag")
    return str(typ)


def action_text(a):
    if a.get("type") == "set_timer":
        return "timer %s +%s" % (a.get("tag"), a.get("delay"))
    return a.get("type", "?") + (" (%s)" % a["reason"] if a.get("reason") else "")


# ------------------------------------------------------------------------------------- main
def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "explore":
        return explore(argv[1:])
    if argv and argv[0] == "replay":
        return replay(argv[1:])
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "results"))
    ap.add_argument("--validate", action="store_true", help="pre-freeze checks only; writes nothing")
    ap.add_argument("--freeze", action="store_true", help="append the current hashes to FREEZE.json")
    ap.add_argument("--label", default=None)
    ap.add_argument("--note", default="")
    ap.add_argument("--check-reproducible", action="store_true")
    ap.add_argument("--show", nargs=3, metavar=("CONTRACT", "POLICY", "SCENARIO"))
    args = ap.parse_args(argv)

    if args.show:
        return show(*args.show)
    if args.validate:
        return 0 if print_checks(prefreeze()) else 1
    if args.freeze:
        if not print_checks(prefreeze()):
            print("Not freezing: validation failed.")
            return 1
        data = load_freeze()
        label = args.label or "v1.0"
        if any(h["label"] == label for h in data["history"]):
            print("label %s already used" % label)
            return 1
        files = frozen_files()
        data["history"].append({
            "label": label,
            "frozen_at_utc": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
            "fixture_version": K.FIXTURE_VERSION,
            "note": args.note,
            "groups": freeze_groups(files),
            "sha256": dict((f, sha256(f)) for f in files),
        })
        with open(FREEZE, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(data, indent=2) + "\n")
        print("Appended freeze entry %s (%d files) to FREEZE.json" % (label, len(files)))
        return 0
    if args.check_reproducible:
        return check_reproducible()
    return collect(os.path.abspath(args.out))


if __name__ == "__main__":
    sys.exit(main())
