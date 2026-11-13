#!/usr/bin/env python3
"""Reproduce the ambiguous-retry recovery pilot (see PROTOCOL.md).

    python3 run_sim.py                      # frozen collection: validate, run matrix + grids, write results/
    python3 run_sim.py --validate           # pre-freeze checks only (V1-V5, unit and mutation tests)
    python3 run_sim.py --freeze --label v1.0 --note "..."   # record SHA-256 hashes in FREEZE.json
    python3 run_sim.py --check-reproducible # V7: run the collection twice in temp dirs, compare every byte
    python3 run_sim.py --show 1 D S04       # readable trace of one cell (contract, policy, scenario or grid id)

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
from arr import metrics, predictions, report, scenarios, validate  # noqa: E402
from arr.runner import run_cell  # noqa: E402

FREEZE = os.path.join(ROOT, "FREEZE.json")
NOTES = os.path.join(ROOT, "notes", "prediction_explanations.md")


# ------------------------------------------------------------------------------------- freeze
def frozen_files():
    pats = ["PROTOCOL.md", "scenarios/*.json", "run_sim.py", "arr/*.py", "tests/*.py"]
    out = []
    for pat in pats:
        out += sorted(os.path.relpath(p, ROOT).replace(os.sep, "/") for p in glob.glob(os.path.join(ROOT, pat)))
    return out


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
        detail += "; " + "; ".join(str(t) for t, _ in res.failures + res.errors)
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
def run_matrix():
    cells = []
    for c in K.CONTRACTS:
        for p in K.POLICIES:
            if c not in K.CONTRACTS_FOR[p]:
                continue
            for scn in scenarios.load_core():
                sim = run_cell(scn, c, p)
                cells.append({"contract": c, "policy": p, "scenario": scn["id"], "scenario_obj": scn, "sim": sim,
                              "rows": metrics.cell_results(sim, scn, c, p)})
    return cells


def run_grids():
    cells = []
    grid_scns = scenarios.build_grids()
    for c in K.CONTRACTS:
        for p in K.POLICIES:
            if c not in K.CONTRACTS_FOR[p]:
                continue
            for scn in grid_scns:
                sim = run_cell(scn, c, p)
                cells.append({"contract": c, "policy": p, "scenario": scn["id"], "scenario_obj": scn, "sim": sim,
                              "rows": metrics.cell_results(sim, scn, c, p)})
    return cells


def collect(out):
    frz = freeze_status()
    if not frz["matches"]:
        print("REFUSING TO COLLECT: the current files do not match the latest FREEZE.json entry.")
        print("  freeze=%s mismatched=%s not_covered=%s" % (frz.get("label"), frz["mismatched"], frz["not_covered"]))
        return 2
    checks = prefreeze()
    if not all(c["ok"] for c in checks):
        print("PRE-RUN VALIDATION FAILED; not collecting.")
        print_checks(checks)
        return 1

    cells = run_matrix()
    gcells = run_grids()
    rows = report.sort_rows([r for cell in cells for r in cell["rows"]])
    grows = report.grid_rows(gcells)   # generation order: contract, policy, grid axis order
    cell_index = {(cl["contract"], cl["policy"], cl["scenario"]): cl["sim"] for cl in cells}

    # ---- post-run checks on every run: V4 on the matrix runs, V5 parity, V6 sanity labels
    for p in K.CLIENT_POLICIES:
        if 1 in K.CONTRACTS_FOR[p]:
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
    notes = ""
    if os.path.exists(NOTES):
        with open(NOTES, encoding="utf-8") as fh:
            notes = fh.read()

    # ---- outputs
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
    report.write_text(os.path.join(out, "predictions_check.md"), predictions.predictions_md(preds, notes))
    report.write_text(os.path.join(out, "worked_traces.md"), report.worked_traces_md(cell_index, rows))
    ties = [dict(contract=cl["contract"], policy=cl["policy"], scenario=cl["scenario"], t=x["t"], phase=x["phase"],
                 op=x["op"], order=" > ".join(x["order"])) for cl in cells for x in cl["sim"].ties]
    report.write_text(os.path.join(out, "ties.csv"),
                      report.csv_text(ties, ["contract", "policy", "scenario", "t", "phase", "op", "order"]))
    report.write_text(os.path.join(out, "validation.json"), json.dumps(checks, indent=2) + "\n")
    run_info = {
        "command": "python3 run_sim.py",
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "fixture_version": K.FIXTURE_VERSION,
        "constants": K.PARITY,
        "contracts": list(K.CONTRACTS),
        "policies": {p: {"role": K.ROLE[p], "contracts": list(K.CONTRACTS_FOR[p])} for p in K.POLICIES},
        "runs": {"core_matrix": len(cells), "grids": len(gcells),
                 "operations_core": len(rows), "operations_grid": len(grows)},
        "sha256": {f: sha256(f) for f in frozen_files()},
        "freeze": frz,
        "prediction_notes_sha256": hashlib.sha256(notes.encode("utf-8")).hexdigest() if notes else None,
        "validation_all_ok": all(c["ok"] for c in checks),
        "predictions": {"match": sum(1 for p in preds if p["verdict"] == "MATCH"), "total": len(preds)},
    }
    report.write_text(os.path.join(out, "run_info.json"), json.dumps(run_info, indent=2, sort_keys=True) + "\n")

    # ---- console
    print("Ambiguous retry recovery pilot | fixtures v%s | Python %s | freeze %s" % (
        K.FIXTURE_VERSION, platform.python_version(), frz["label"]))
    print("%d core cells (%d operations), %d grid cells" % (len(cells), len(rows), len(gcells)))
    print()
    fmt = "%-3s %-9s %-7s %-6s %-6s %-6s %-6s %-6s %-6s %s"
    print(fmt % ("c", "policy", "dup", "once", "zero", "unres", "f.comp", "f.fail", "retry", "ttc med/max (cov)"))
    for r in pol:
        if r["scope"] != "S00-S15":
            continue
        print(fmt % (r["contract"], r["policy"], r["duplicates"], r["exactly_once"], r["zero_effects"], r["unresolved_H"],
                     r["false_complete"], r["false_failure"], r["retries_mean"],
                     "%s/%s (%s)" % (r["ttc_median"] or "-", r["ttc_max"] or "-", r["ttc_coverage"])))
    print()
    print("Predictions: %d/%d match (results/predictions_check.md)" % (run_info["predictions"]["match"], len(preds)))
    ok = print_checks(checks)
    print("Results written to %s" % out)
    return 0 if ok else 1


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


# ------------------------------------------------------------------------------------- show
def show(contract, policy, sid):
    scn = scenarios.load_scenario(sid)
    sim = run_cell(scn, int(contract), policy)
    print("%s | contract %s | policy %s%s" % (sid, contract, policy,
                                              " (REFERENCE: reads hidden state)" if policy in K.REFERENCES else ""))
    if "protocol_script" in scn:
        print("script: " + scn["protocol_script"])
    print("freeze: %s" % ("matches " + str(freeze_status()["label"]) if freeze_status()["matches"] else "NOT a frozen run"))
    for e in sim.trace:
        d = report.describe(e)
        if d is None:
            continue
        col, text = d
        print("t=%3d ph%d %-8s %s%s" % (e["t"], e["phase"], col, "   " if e["visible"] else "[h]", text.replace("**", "")))
    for r in metrics.cell_results(sim, scn, int(contract), policy):
        print("result %s: effects H=%d F=%d belief=%s dispatches=%s commits=%s" % (
            r["op"], r["effects_H"], r["effects_F"], r["belief_H"], r["dispatch_times"], r["commits"]))
    return 0


# ------------------------------------------------------------------------------------- main
def main(argv=None):
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
        data["history"].append({
            "label": label,
            "frozen_at_utc": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
            "fixture_version": K.FIXTURE_VERSION,
            "note": args.note,
            "sha256": {f: sha256(f) for f in frozen_files()},
        })
        with open(FREEZE, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(data, indent=2) + "\n")
        print("Appended freeze entry %s (%d files) to FREEZE.json" % (label, len(frozen_files())))
        return 0
    if args.check_reproducible:
        return check_reproducible()
    return collect(os.path.abspath(args.out))


if __name__ == "__main__":
    sys.exit(main())
