"""Revision delta: every value that changed between a baseline run and the current run.

The baseline files in baselines/v1.0/ were extracted byte-for-byte from git commit 924aef2
(`git show 924aef2:results/<file>`), the committed v1.0 results. The comparison is deterministic.
"""
import csv
import hashlib
import io
import os

FILES = [
    ("summary.csv", ("contract", "policy", "scenario", "op"), "Core matrix, per operation"),
    ("by_policy.csv", ("scope", "contract", "policy"), "Core matrix, per contract x policy"),
    ("by_family.csv", ("contract", "policy", "family"), "Core matrix, per contract x policy x family"),
    ("grid.csv", ("grid", "schedule", "contract", "policy"), "Secondary grid, per schedule"),
]
GRID_AGG = ("duplicate", "certified_exactly_once", "unresolved", "false_failure", "retries", "retries_unjustified",
            "retries_after_complete", "status_reads")


def _read(text):
    return list(csv.DictReader(io.StringIO(text)))


def _index(rows, key):
    return {tuple(r[k] for k in key): r for r in rows}


def _grid_aggregates(rows):
    out = {}
    for r in rows:
        k = (r["grid"], r["contract"], r["policy"])
        agg = out.setdefault(k, dict((f, 0) for f in GRID_AGG))
        agg["n"] = agg.get("n", 0) + 1
        for f in GRID_AGG:
            agg[f] += int(r[f]) if r[f] not in ("", None) else 0
    return out


def delta_section(old_dir, new_dir, old_label, new_label, old_source, new_source):
    """One section: every value that differs between two result sets."""
    lines = ["## %s -> %s" % (old_label, new_label), "",
             "Old: %s. New: %s. Rows are keyed as shown; a cell reads `field: old -> new`. Unchanged rows are "
             "omitted." % (old_source, new_source), "", "| file compared | old sha256 |", "|---|---|"]
    for name, _, _ in FILES:
        with open(os.path.join(old_dir, name), "rb") as fh:
            lines.append("| %s | %s |" % (name, hashlib.sha256(fh.read()).hexdigest()))
    lines.append("")
    tables = {}
    for name, key, title in FILES:
        with open(os.path.join(old_dir, name), encoding="utf-8") as fh:
            old = _read(fh.read())
        with open(os.path.join(new_dir, name), encoding="utf-8") as fh:
            new = _read(fh.read())
        tables[name] = (old, new)
        oi, ni = _index(old, key), _index(new, key)
        changed = []
        for k in sorted(set(oi) | set(ni), key=lambda x: [(0, int(v)) if v.isdigit() else (1, v) for v in x]):
            if k not in oi or k not in ni:
                changed.append((k, "row %s" % ("added" if k not in oi else "removed")))
                continue
            diffs = ["%s: %s -> %s" % (f, oi[k][f] or "''", ni[k].get(f, "") or "''")
                     for f in oi[k] if oi[k][f] != ni[k].get(f)]
            if diffs:
                changed.append((k, "; ".join(diffs)))
        lines += ["### %s (`%s`): %d of %d rows changed" % (title, name, len(changed), len(old)), ""]
        if changed:
            lines += ["| %s | changes |" % " | ".join(key), "|" + "---|" * (len(key) + 1)]
            lines += ["| %s | %s |" % (" | ".join(k), d) for k, d in changed]
        else:
            lines.append("No value changed.")
        lines.append("")
    old, new = tables["grid.csv"]
    oa, na = _grid_aggregates(old), _grid_aggregates(new)
    rows = []
    for k in sorted(set(oa) | set(na), key=lambda x: (x[0], int(x[1]), x[2])):
        diffs = ["%s: %s -> %s" % (f, oa.get(k, {}).get(f), na.get(k, {}).get(f))
                 for f in GRID_AGG if oa.get(k, {}).get(f) != na.get(k, {}).get(f)]
        if diffs:
            rows.append("| %s | %s | %s | %s | %s |" % (k[0], k[1], k[2], na.get(k, oa.get(k))["n"], "; ".join(diffs)))
    lines += ["### Secondary grid, totals per grid x contract x policy (counts of cells; sums of retries and reads)", ""]
    if rows:
        lines += ["| grid | contract | policy | cells | changes |", "|---|---|---|---|---|"] + rows
    else:
        lines.append("No value changed.")
    lines.append("")
    return lines


def delta_md(sections):
    """`sections`: list of (old_dir, new_dir, old_label, new_label, old_source, new_source)."""
    lines = ["# Revision deltas", "",
             "Every value that changed between successive frozen runs. Baseline files are byte-for-byte copies of "
             "committed results (`git show <commit>:results/<file>`) kept in `baselines/<label>/` and frozen.", ""]
    for sec in sections:
        lines += delta_section(*sec)
    return "\n".join(lines).rstrip("\n") + "\n"


def baseline_verdicts(baseline_dir):
    """id -> verdict from the baseline predictions_check.md table."""
    path = os.path.join(baseline_dir, "predictions_check.md")
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 6 and cells[5].strip("*") in ("MATCH", "MISMATCH"):
                out[cells[0]] = cells[5].strip("*")
    return out
