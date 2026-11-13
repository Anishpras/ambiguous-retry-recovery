#!/usr/bin/env python3
"""Check every number in paper/main.tex against the project's result files.

    python3 paper/check_numbers.py                  check; exits 0 only if every check passes
    python3 paper/check_numbers.py --emit LABEL     print the generated LaTeX rows of one table
    python3 paper/check_numbers.py --write-numbers  rewrite paper/NUMBERS.md from the registry

Standard library only. Nothing in the project is modified except NUMBERS.md (with --write-numbers).

What is checked:
  1. Data tables (outcomes, pooled counts, grid, ablations, sensitivity, Bw boundary, persistent
     faults, predictions) are regenerated from the result files; every generated row must appear
     verbatim in main.tex.
  2. Hand-written table rows (scenarios, grids, traces, escalation): every number in the row must
     appear in the cited line or row of the source file.
  3. Prose numbers: each registry entry gives an exact snippet of main.tex, and every number in that
     snippet is asserted against its source (a CSV cell, a line of a Markdown or JSON file, git log).
  4. Completeness: after removing the checked rows and snippets, no number may remain in the body
     of main.tex (bibliography and the verbatim command block excepted).
  5. Consistency between result files that report the same quantity.
  6. main.tex is pure ASCII and contains no LaTeX comments.
  7. NUMBERS.md is up to date with the registry.
"""
import csv
import datetime
import json
import os
import re
import subprocess
import sys

PAPER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PAPER)
TEX = os.path.join(PAPER, "main.tex")
NUMBERS_MD = os.path.join(PAPER, "NUMBERS.md")

R = "results/"
X = "results/exploratory/"

# --------------------------------------------------------------------------------------------
# Loaders
# --------------------------------------------------------------------------------------------
_cache = {}


def path(rel):
    return os.path.join(ROOT, rel)


def rows(rel):
    if rel not in _cache:
        with open(path(rel), newline="") as f:
            _cache[rel] = list(csv.DictReader(f))
    return _cache[rel]


def lines(rel):
    key = ("lines", rel)
    if key not in _cache:
        with open(path(rel)) as f:
            _cache[key] = f.read().split("\n")
    return _cache[key]


def line(rel, n):
    return lines(rel)[n - 1]


def jload(rel):
    key = ("json", rel)
    if key not in _cache:
        with open(path(rel)) as f:
            _cache[key] = json.load(f)
    return _cache[key]


def one(rel, **kw):
    hits = [r for r in rows(rel) if all(str(r[k]) == str(v) for k, v in kw.items())]
    if len(hits) != 1:
        raise KeyError("%s: %d rows match %r" % (rel, len(hits), kw))
    return hits[0]


def num(s):
    return s.split("/")[0]


TOKEN = re.compile(r"(?<![A-Za-z0-9.\\])\d+(?:\.\d+)*(?:/\d+(?:\.\d+)*)?(?![A-Za-z0-9])")


def tokens(text):
    return TOKEN.findall(text)


def git(*args):
    return subprocess.check_output(["git", "-C", ROOT] + list(args), text=True)


def commit_time(h):
    s = git("show", "-s", "--format=%ct", h).strip()
    return int(s)


# --------------------------------------------------------------------------------------------
# Display names
# --------------------------------------------------------------------------------------------
NAME = {"A": "A", "B": "B", "Bw": "Bw", "C": "C", "D": "D", "D+I": "D+I", "A-fk": "A-fk",
        "ORACLE-S": "ORACLE-S", "ORACLE-O": "ORACLE-O"}
POL1 = ["A", "B", "Bw", "C", "D", "D+I", "ORACLE-S", "ORACLE-O"]
POL2 = ["A", "B", "Bw", "C", "D", "D+I", "A-fk", "ORACLE-S", "ORACLE-O"]
REFS = {"ORACLE-S", "ORACLE-O"}
CORE_OPS = [("S00", "op-1"), ("S01", "op-1"), ("S02", "op-1"), ("S03", "op-1"), ("S04", "op-1"),
            ("S05", "op-1"), ("S06", "op-1"), ("S07", "op-1"), ("S08", "op-1"), ("S09", "op-1"),
            ("S10", "op-1"), ("S11", "op-1"), ("S11", "op-2"), ("S12", "op-1"), ("S13", "op-1"),
            ("S14", "op-1"), ("S15", "op-1")]


def oplabel(s, o):
    return s + "/" + o if s == "S11" else s


# --------------------------------------------------------------------------------------------
# Generated tables. Each generator returns a list of (latex_row, source_description).
# --------------------------------------------------------------------------------------------
def cell_code(r):
    code = "%s%s" % (r["effects_F"], r["belief_H"][0].upper())
    if int(r["effects_F"]) > 1:
        code = "\\textbf{%s}" % code
    if r["dup_cause"] == "contract":
        code += "$^\\dagger$"
    return code


def gen_outcomes():
    out = []
    for s, o in CORE_OPS:
        cells = []
        for c, pols in ((1, POL1), (2, POL2)):
            for p in pols:
                cells.append(cell_code(one(R + "summary.csv", contract=c, policy=p, scenario=s, op=o)))
        row = "%s & %s \\\\" % (oplabel(s, o), " & ".join(cells))
        out.append((row, "results/summary.csv: rows scenario=%s op=%s, every contract x policy; "
                         "columns effects_F, belief_H, dup_cause" % (s, o)))
    return out


def pooled_row(c, p):
    r = one(R + "by_policy.csv", scope="S00-S15", contract=c, policy=p)
    unjust = "n/a" if p in REFS else r["retries_unjustified"]
    if p == "D+I" and c == 2:
        unjust = "%s (+%s)" % (r["retries_unjustified"], r["retries_contract_justified"])
    ttc = "%s/%s (%s)" % (r["ttc_median"], r["ttc_max"], num(r["ttc_coverage"]))
    cells = [NAME[p], num(r["duplicates"]), r["extra_effects"],
             "%s/%s" % (num(r["dup_contract_caused"]), num(r["dup_policy_caused"])),
             num(r["exactly_once"]), num(r["zero_effects"]), num(r["unresolved_H"]),
             num(r["false_failure"]), unjust, r["conflicts"], ttc]
    g = grid_counts(R + "grid.csv", c, p)
    cells.append("%d/%d/%d" % (g["dup"], g["unres"], g["ff"]))
    return " & ".join(cells) + " \\\\"


def gen_pooled():
    out = []
    for c, pols in ((1, POL1), (2, POL2)):
        for p in pols:
            out.append((pooled_row(c, p),
                        "results/by_policy.csv: scope=S00-S15, contract=%d, policy=%s; columns duplicates, "
                        "extra_effects, dup_contract_caused, dup_policy_caused, exactly_once, zero_effects, "
                        "unresolved_H, false_failure, retries_unjustified (retries_contract_justified for D+I), "
                        "conflicts, ttc_median, ttc_max, ttc_coverage; grid column: results/grid.csv rows contract=%d, policy=%s, "
                        "counts of duplicate=1, unresolved=1, false_failure=1 over 120 schedules" % (c, p, c, p)))
    return out


def grid_counts(rel, c, p, grid=None):
    g = [r for r in rows(rel) if r["contract"] == str(c) and r["policy"] == p
         and (grid is None or r["grid"] == grid)]
    return {"n": len(g),
            "dup": sum(int(r["duplicate"]) for r in g),
            "once": sum(1 for r in g if r["effects_F"] == "1"),
            "unres": sum(int(r["unresolved"]) for r in g),
            "ff": sum(int(r["false_failure"]) for r in g),
            "cert": sum(int(r["certified_exactly_once"]) for r in g)}


def gen_grid():
    out = []
    for p in POL2:
        cells = [NAME[p]]
        if p == "A-fk":
            cells += ["--", "--", "--"]
        else:
            g1 = grid_counts(R + "grid.csv", 1, p)
            cells += [str(g1["dup"]), str(g1["unres"]), str(g1["ff"])]
        g2 = grid_counts(R + "grid.csv", 2, p)
        cells += [str(g2["dup"]), str(g2["unres"]), str(g2["ff"])]
        out.append((" & ".join(cells) + " \\\\",
                    "results/grid.csv: rows policy=%s, contract 1 and 2, all 120 schedules; counts of duplicate=1, "
                    "unresolved=1, false_failure=1 (cross-checked against results/grid_tables.md)" % p))
    return out


ABL_NAMES = [("no_provider_seq", "ignore provider\\_seq"),
             ("no_event_id_dedupe", "no event-ID de-duplication"),
             ("no_payload_correlation", "no payload check"),
             ("ignore_webhooks", "ignore every webhook"),
             ("ignore_status", "no status reads")]
ABL_RE = re.compile(r"^\| (C|D) \| (\w+) \(.*\) \| (\d+) of 34 \| (\d+) of 240 \| (\d+) / (\d+) / (\d+) / (\d+) / (\d+) of 17 "
                    r"\| (\d+) / (\d+) / (\d+) / (\d+) / (\d+) of 120 \|$")


def ablation_lines():
    found = {}
    for i, ln in enumerate(lines(X + "ablations.md"), 1):
        m = ABL_RE.match(ln)
        if m:
            found[(m.group(1), m.group(2))] = (i, m.groups())
    return found


def gen_ablations():
    found = ablation_lines()
    out = []
    for p in ("D", "C"):
        for key, label in ABL_NAMES:
            i, g = found[(p, key)]
            row = "%s & %s & %s & %s & %s/%s/%s/%s & %s \\\\" % (p, label, g[2], g[3], g[4], g[5], g[6], g[7], g[11])
            out.append((row, "results/exploratory/ablations.md line %d (policy %s, ablation %s)" % (i, p, key)))
    return out


SENS_ITEMS = [
    ("status_lists_pending", "\\code{status\\_lists\\_pending}: status lists pending attempts; B and Bw re-read while one is pending",
     [("B", 1, "duplicate"), ("Bw", 1, "duplicate"), ("B", 2, "false_failure"), ("Bw", 2, "false_failure")]),
    ("webhooks_not_by_name", "\\code{webhooks\\_not\\_by\\_name}: \\code{deferred} is progress; failure receipts ignored once complete",
     [("A", 1, "duplicate"), ("B", 1, "duplicate"), ("Bw", 1, "duplicate")]),
    ("bw_without_C15", "\\code{bw\\_without\\_C15}: Bw reads even if already complete",
     [("Bw", 1, "duplicate")]),
    ("bw_without_C15_or_reply_guard", "\\code{bw\\_without\\_C15\\_or\\_reply\\_guard}: also act on status replies after completion",
     [("B", 1, "duplicate"), ("Bw", 1, "duplicate")]),
    ("tau_5", "\\code{tau\\_5}: Bw waits $\\tau={v}$", [("Bw", 1, "duplicate"), ("Bw", 2, "duplicate")]),
    ("tau_10", "\\code{tau\\_10}: Bw waits $\\tau={v}$", [("Bw", 1, "duplicate")]),
    ("tau_20", "\\code{tau\\_20}: Bw waits $\\tau={v}$", [("Bw", 1, "duplicate"), ("Bw", 2, "false_failure")]),
    ("tau_30", "\\code{tau\\_30}: Bw waits $\\tau={v}$", [("Bw", 1, "duplicate"), ("Bw", 2, "false_failure")]),
    ("in_progress_is_wait", "\\code{in\\_progress\\_is\\_wait}: A, B, Bw wait on \\code{in\\_progress}",
     [("A", 2, "false_failure"), ("B", 2, "false_failure"), ("Bw", 2, "false_failure"), ("A", 2, "unresolved")]),
    ("abort_record_replays_failure", "\\code{abort\\_record=replay\\_failure}: an aborted key refuses later attempts",
     [("A", 2, "duplicate"), ("D", 2, "duplicate"), ("D", 2, "exactly_once"), ("D+I", 2, "exactly_once")]),
    ("persistent_faults", "\\code{retry\\_fault=copy\\_first}: retries repeat the first attempt's fault",
     [("A", 1, "false_failure"), ("B", 1, "false_failure"), ("Bw", 1, "unresolved"), ("D", 1, "duplicate"), ("D+I", 2, "unresolved")]),
    ("horizon_120", "\\code{horizon={v}}: a longer horizon",
     [("D", 1, "unresolved"), ("A", 2, "false_failure")]),
]
FIELD_SHORT = {"duplicate": "dup", "false_failure": "false fail", "unresolved": "unres", "exactly_once": "once"}


def sens(row, p, c, scope):
    return one(X + "sensitivity.csv", row=row, policy=p, contract=c, scope=scope)


def sens_option_value(row):
    opts = sens(row, "A", 1, "core")["options"]
    vals = [kv.split("=")[1] for kv in opts.split() if "=" in kv]
    return vals[0] if vals else ""


def gen_sensitivity():
    out = []
    for row, desc, items in SENS_ITEMS:
        if "{v}" in desc:
            desc = desc.replace("{v}", sens_option_value(row))
        parts = []
        for p, c, f in items:
            b_core, v_core = sens("baseline", p, c, "core")[f], sens(row, p, c, "core")[f]
            b_grid, v_grid = sens("baseline", p, c, "grid")[f], sens(row, p, c, "grid")[f]
            parts.append("%s c%d %s %s$\\to$%s / %s$\\to$%s" % (NAME[p], c, FIELD_SHORT[f], b_core, v_core, b_grid, v_grid))
        out.append(("%s & %s \\\\" % (desc, "; ".join(parts)),
                    "results/exploratory/sensitivity.csv: rows row=baseline and row=%s; policies/contracts/fields %s; scopes core and grid"
                    % (row, ", ".join("%s c%d %s" % it for it in items))))
    return out


def gen_bw():
    out = []
    for r in rows(X + "bw_boundary.csv"):
        if r["grid"] != "lost_ack":
            continue
        exact = "yes" if r["rectangle_exact"] == "1" else "no"
        row = "%s & %s & %s & %s & %s & %s \\\\" % (r["tau"], r["L_star"], r["R_star"], exact,
                                                   r["predicted_L_star"], r["predicted_R_star"])
        out.append((row, "results/exploratory/bw_boundary.csv: row grid=lost_ack, tau=%s; columns L_star, R_star, "
                         "rectangle_exact, predicted_L_star, predicted_R_star" % r["tau"]))
    return out


PF_TITLES = {"PF1": "PF1 lost ack, $L=1$", "PF2": "PF2 lost ack, $L=$ never",
             "PF3": "PF3 lost request, $L=1$", "PF4": "PF4 abort, $L=1$"}


def pf_cell(r):
    code = "%s%s" % (r["effects_F"], r["belief_H"][0].upper())
    if r["duplicate"] == "1":
        code = "\\textbf{%s}" % code
    return code


def gen_pf():
    out = []
    for s in ("PF1", "PF2", "PF3", "PF4"):
        cells = []
        for c in (1, 2):
            for p in ("A", "B", "Bw", "C", "D", "D+I"):
                cells.append(pf_cell(one(X + "persistent_faults.csv", contract=c, policy=p, scenario=s)))
        out.append(("%s & %s \\\\" % (PF_TITLES[s], " & ".join(cells)),
                    "results/exploratory/persistent_faults.csv: rows scenario=%s, policies A..D+I, contracts 1 and 2; "
                    "columns effects_F, belief_H, duplicate (status lag from scenarios/exploratory/%s.json)" % (s, s)))
    return out


PRED_ROW = re.compile(r"^\| (\w+) \| (.+?) \| .* \| \*\*(MATCH|MISMATCH|MATCH \(vacuous\))\*\* \|$")
PRED_GROUPS = [("orig", "Original \\S7, scope S00--S12 (P01--P15b)"),
               ("timeline", "Original worked timeline (P16--P19)"),
               ("update", "Design update (U01--U10)"),
               ("tie", "Design-update tie note (T01)")]


def prediction_rows():
    out = []
    for i, ln in enumerate(lines(R + "predictions_check.md"), 1):
        m = PRED_ROW.match(ln)
        if m:
            out.append((i, m.group(1), m.group(2), m.group(3)))
    return out


def pred_group(pid, src):
    if src.startswith("§7 original"):
        return "orig"
    if src.startswith("§10"):
        return "timeline"
    if src.startswith("§7 design update"):
        return "update"
    if src.startswith("design update tie"):
        return "tie"
    raise ValueError(pid)


def gen_predictions():
    pr = prediction_rows()
    out = []
    tot = [0, 0, 0, 0]
    for g, label in PRED_GROUPS:
        sel = [x for x in pr if pred_group(x[1], x[2]) == g]
        n = len(sel)
        match = sum(1 for x in sel if x[3].startswith("MATCH"))
        vac = sum(1 for x in sel if x[3] == "MATCH (vacuous)")
        mis = sum(1 for x in sel if x[3] == "MISMATCH")
        tot = [tot[0] + n, tot[1] + match, tot[2] + vac, tot[3] + mis]
        out.append(("%s & %d & %d & %d & %d \\\\" % (label, n, match, vac, mis),
                    "results/predictions_check.md lines %d-%d (rows %s to %s); verdict column" %
                    (sel[0][0], sel[-1][0], sel[0][1], sel[-1][1])))
    out.append(("Total & %d & %d & %d & %d \\\\" % tuple(tot),
                "results/predictions_check.md: all %d table rows; also results/run_info.json predictions" % tot[0]))
    return out


GENERATED = {
    "tab:outcomes": gen_outcomes,
    "tab:pooled": gen_pooled,
    "tab:ablations": gen_ablations,
    "tab:sensitivity": gen_sensitivity,
    "tab:bw": gen_bw,
    "tab:pf": gen_pf,
}


# --------------------------------------------------------------------------------------------
# Tokenising the paper
# --------------------------------------------------------------------------------------------
WORDS = {"two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8",
         "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
         "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
         "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "hundred": "100"}
WORD_RE = re.compile(r"\b(" + "|".join(WORDS) + r")\b", re.I)
NAME_PATTERNS = [
    r"\\(?:ref|label|cite|url|eqref)\{[^}]*\}",
    r"\\begin\{tabular\}\{(?:[^{}]|\{[^{}]*\})*\}",
    r"\*\{\d+\}",
    r"\\setlength\{[^}]*\}\{[^}]*\}",
    r"\\multicolumn\{\d+\}",
    r"\\cmidrule(?:\([^)]*\))?\{[^}]*\}",
    r"-(?:\{\})?-contract \d",
    r"[Cc]ontracts \d and \d",
    r"[Cc]ontract \d",
    r"contract-\d",
    r"op-\d",
    r"SHA-256",
]
NUMTOK = re.compile(r"(?<![A-Za-z0-9.\\])\d+(?:\.\d+)*(?:/\d+(?:\.\d+)*)?(?![A-Za-z0-9]|\.\d)")


def strip_names(text):
    out = []
    for ln in text.split("\n"):
        for pat in NAME_PATTERNS:
            ln = re.sub(pat, " ", ln)
        out.append(ln)
    return "\n".join(out)


def paper_tokens(text):
    """Numbers in a piece of the paper: digit tokens plus cardinal number words (as digit strings)."""
    s = strip_names(text)
    toks = NUMTOK.findall(s)
    toks += [WORDS[w.lower()] for w in WORD_RE.findall(s)]
    return toks


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def tex():
    with open(TEX) as f:
        return f.read()


def body_of(t):
    return t.split("\\begin{document}", 1)[1].split("\\begin{thebibliography}", 1)[0]


# --------------------------------------------------------------------------------------------
# Source accessors used by the registry. Each returns (value, locator).
# --------------------------------------------------------------------------------------------
def bp(field, c, p, scope="S00-S15", whole=False):
    r = one(R + "by_policy.csv", scope=scope, contract=c, policy=p)
    v = r[field] if whole else num(r[field])
    return v, "results/by_policy.csv: scope=%s, contract=%s, policy=%s; column %s" % (scope, c, p, field)


def sm(field, c, p, s, op="op-1"):
    r = one(R + "summary.csv", contract=c, policy=p, scenario=s, op=op)
    return r[field], "results/summary.csv: contract=%s, policy=%s, scenario=%s, op=%s; column %s" % (c, p, s, op, field)


def at(field, c, p, s, attempt):
    """Time of an attempt in summary.csv dispatch_times or commits (e.g. 'a2@7')."""
    v, loc = sm(field, c, p, s)
    m = re.search(r"\b%s@(\d+)" % attempt, v)
    return (m.group(1) if m else None), loc + " (%s in '%s')" % (attempt, v)


def gcount(key, c, p, grid=None, rel=R + "grid.csv"):
    g = grid_counts(rel, c, p, grid)
    return str(g[key]), "%s: rows contract=%s, policy=%s%s; count of %s" % (
        rel, c, p, (", grid=" + grid) if grid else "", {"dup": "duplicate=1", "unres": "unresolved=1",
                                                         "ff": "false_failure=1", "n": "rows", "once": "effects_F=1"}[key])


def nsched(grid=None):
    sch = {r["schedule"] for r in rows(R + "grid.csv") if grid is None or r["grid"] == grid}
    return str(len(sch)), "results/grid.csv: number of distinct schedules%s" % ((" in " + grid) if grid else "")


def sensv(field, row, p, c, scope):
    return sens(row, p, c, scope)[field], "results/exploratory/sensitivity.csv: row=%s, policy=%s, contract=%s, scope=%s; column %s" % (row, p, c, scope, field)


def sens_ext(field, p, c, scope, fn):
    vals = [int(r[field]) for r in rows(X + "sensitivity.csv") if r["policy"] == p and r["contract"] == str(c) and r["scope"] == scope]
    return str(fn(vals)), "results/exploratory/sensitivity.csv: %s of column %s over all 13 rows, policy=%s, contract=%s, scope=%s" % (fn.__name__, field, p, c, scope)


def sens_ext_many(field, pols, contracts, scope, fn):
    vals = [int(r[field]) for r in rows(X + "sensitivity.csv") if r["policy"] in pols and r["contract"] in [str(c) for c in contracts] and r["scope"] == scope]
    return str(fn(vals)), "results/exploratory/sensitivity.csv: %s of column %s over all rows, policies %s, contracts %s, scope=%s" % (fn.__name__, field, "/".join(pols), contracts, scope)


def bwv(field, tau):
    r = one(X + "bw_boundary.csv", grid="lost_ack", tau=tau)
    return r[field], "results/exploratory/bw_boundary.csv: grid=lost_ack, tau=%s; column %s" % (tau, field)


def bw_offset(field):
    offs = {int(r[field]) - int(r["tau"]) for r in rows(X + "bw_boundary.csv") if r["grid"] == "lost_ack"}
    assert len(offs) == 1, offs
    return str(offs.pop()), "results/exploratory/bw_boundary.csv: %s - tau, identical in every lost_ack row (tau = 5, 10, 15, 20, 30)" % field


def pfv(field, c, p, s):
    r = one(X + "persistent_faults.csv", contract=c, policy=p, scenario=s)
    return r[field], "results/exploratory/persistent_faults.csv: contract=%s, policy=%s, scenario=%s; column %s" % (c, p, s, field)


def info(*keys):
    d = jload(R + "run_info.json")
    for k in keys:
        d = d[k]
    return str(d), "results/run_info.json: %s" % ".".join(keys)


def findline(rel, needle, nth=0):
    hits = [i for i, ln in enumerate(lines(rel), 1) if needle in ln]
    if len(hits) <= nth:
        raise KeyError("%s: %r not found" % (rel, needle))
    return hits[nth]


def intext(exp, rel, needle, nth=0):
    """exp must appear as a number token in the line of rel that contains needle."""
    n = findline(rel, needle, nth)
    ln = line(rel, n)
    ok = exp in NUMTOK.findall(ln) or exp in [WORDS.get(w.lower()) for w in WORD_RE.findall(ln)] or \
        (exp == "2" and "twice" in ln)
    return (exp if ok else "not in line"), "%s line %d (%s)" % (rel, n, needle)


def abl_group(policy, key, idx):
    i, g = ablation_lines()[(policy, key)]
    return g[idx], "results/exploratory/ablations.md line %d (policy %s, ablation %s)" % (i, policy, key)


def abl_change(policy, key, contract, scenario, which):
    r = one(X + "ablations.csv", policy=policy, ablation=key, scope="core", contract=contract, scenario=scenario)
    m = re.search(r"ttc_any_complete: (\d+) -> (\d+)", r["changes"])
    return m.group(which), "results/exploratory/ablations.csv: policy=%s, ablation=%s, core, contract=%s, scenario=%s ('%s')" % (
        policy, key, contract, scenario, r["changes"])


def abl_count(policy, key, contract, scope="core"):
    n = sum(1 for r in rows(X + "ablations.csv") if r["policy"] == policy and r["ablation"] == key and r["scope"] == scope and r["contract"] == str(contract))
    return str(n), "results/exploratory/ablations.csv: count of rows policy=%s, ablation=%s, scope=%s, contract=%s" % (policy, key, scope, contract)


def validation(check, pattern):
    for r in jload(R + "validation.json"):
        if r["check"] == check:
            m = re.search(pattern, r["detail"])
            return m.group(1), "results/validation.json: check %s, detail '%s'" % (check, r["detail"][:60])
    raise KeyError(check)


def nvalidation():
    v = jload(R + "validation.json")
    assert all(r["ok"] for r in v)
    return str(len(v)), "results/validation.json: number of checks (all ok)"


def minutes(h1, h2, how):
    d = (commit_time(h2) - commit_time(h1)) / 60.0
    v = int(d) if how == "floor" else int(round(d))
    return str(v), "git log: commit %s to commit %s = %.2f minutes (%s)" % (h1, h2, d, how)


def baseline_grid(label, p):
    rel = "baselines/%s/grid.csv" % label
    return gcount("dup", 1, p, rel=rel)


def nclarifications():
    n = sum(1 for ln in lines("PROTOCOL.md") if re.match(r"^- \*\*C\d+\.", ln))
    return str(n), "PROTOCOL.md: number of clarification items '- **C<n>.' (C1-C22)"


def pred_counts(group, what):
    pr = prediction_rows()
    sel = [x for x in pr if group == "all" or pred_group(x[1], x[2]) in group]
    if what == "rows":
        v = len(sel)
    elif what == "match":
        v = sum(1 for x in sel if x[3].startswith("MATCH"))
    return str(v), "results/predictions_check.md: %s of rows in group %s" % (what, group)


def roles(pred):
    pols = jload(R + "run_info.json")["policies"]
    n = sum(1 for k, v in pols.items() if pred(v["role"]))
    return str(n), "results/run_info.json: policies with role " + ("core/optional" if pred("core") else "reference/state-probe reference")


def contributions_items():
    t = tex()
    blk = t.split("\\paragraph{Contributions.}", 1)[1].split("\\end{enumerate}", 1)[0]
    return str(blk.count("\\item")), "main.tex: number of items in the Contributions list (structural)"


def escal_core(c, p):
    n = sum(1 for r in rows(X + "escalation.csv") if r["source"] == "core" and r["contract"] == str(c) and r["policy"] == p)
    return str(n), "results/exploratory/escalation.csv: count of rows source=core, contract=%s, policy=%s" % (c, p)


def escal_truth(scenario, pattern):
    r = one(X + "escalation.csv", source="core", contract=1, policy="D", scenario=scenario)
    m = re.search(pattern, r["hidden_truth"])
    return m.group(1), "results/exploratory/escalation.csv: source=core, contract=1, policy=D, scenario=%s; hidden_truth '%s'" % (scenario, r["hidden_truth"])


def escal_new_categories():
    cats = {}
    for ln in lines(X + "escalation.md"):
        m = re.match(r"^\| (core|grid|persistent_fault) \| [^|]+ \| ([^|]+) \| \d+ \|$", ln)
        if m:
            cats.setdefault(m.group(1), set()).add(m.group(2).strip())
    new = cats["persistent_fault"] - cats["core"] - cats["grid"]
    return str(len(new)), "results/exploratory/escalation.md: categories found only under persistent_fault: %s" % sorted(new)


def npf():
    return str(len({r["scenario"] for r in rows(X + "persistent_faults.csv")})), "results/exploratory/persistent_faults.csv: distinct scenarios"


def post_freeze_revisions():
    labels = [h["label"] for h in jload("FREEZE.json")["history"]]
    n = sum(1 for l in labels if l.startswith("v1.1"))
    return str(n), "FREEZE.json: history labels before the review-driven v1.2 (%s)" % ", ".join(l for l in labels if l.startswith("v1.1"))


def false_complete_max():
    v = max(int(num(r["false_complete"])) for r in rows(R + "by_policy.csv"))
    g = max(int(r["false_complete"]) for r in rows(R + "grid.csv"))
    return str(max(v, g)), "results/by_policy.csv and results/grid.csv: maximum of false_complete over all rows"


def ops17():
    return bp("ops", 1, "A", whole=True)


def nscen():
    return str(len(jload("scenarios/matrix.json")["scenarios"])), "scenarios/matrix.json: number of scenarios"


def grid_rows_policy(p):
    return str(sum(1 for r in rows(R + "grid.csv") if r["policy"] == p)), "results/grid.csv: rows with policy=%s (both contracts)" % p


# --------------------------------------------------------------------------------------------
# Registry of prose numbers. Each entry: (id, exact snippet of main.tex, [(expected, getter)], count)
# Every number in the snippet must be matched by one check.
# --------------------------------------------------------------------------------------------
def C(exp, getter, *args):
    return (str(exp), lambda: getter(*args))


def L(exp, rel, needle, nth=0):
    return (str(exp), lambda: intext(str(exp), rel, needle, nth))


P = "PROTOCOL.md"
WT = R + "worked_traces.md"

REGISTRY = [
    ("abs-size", "Its 16 scripted scenarios (17 operations) and 120 timing schedules",
     [C(16, nscen), C(17, ops17), C(120, nsched)]),
    ("abs-contracts", "under two explicit provider contracts", [C(2, lambda: (str(len(jload(R + "run_info.json")["contracts"])), "results/run_info.json: contracts"))]),
    ("abs-five", "It adds five things.", [C(5, contributions_items)]),
    ("bw-offsets", "status lag is at least $\\tau+4$ ticks and the receipt arrives at $t \\geq \\tau+7$",
     [C(4, bw_offset, "L_star"), C(7, bw_offset, "R_star")], 2),
    ("intro-size", "suite with two explicit provider contracts. A synthetic ``send message'' call is driven through 16 scripted scenarios (17 operations) and 120 timing schedules. Six client policies, one ablation and two references",
     [C(2, lambda: (str(len(jload(R + "run_info.json")["contracts"])), "results/run_info.json: contracts")), C(16, nscen), C(17, ops17), C(120, nsched),
      C(6, roles, lambda r: r in ("core", "optional")), C(2, roles, lambda r: "reference" in r)]),
    ("contrib-webhooks", "ignoring them raises the unresolved grid schedules from 16 to 41 of 120. Handling failure-named receipts by name makes an immediate-retry client duplicate in 2 scenarios",
     [C(16, sensv, "unresolved", "baseline", "D", 1, "grid"), C(41, abl_group, "D", "ignore_webhooks", 11), C(120, nsched),
      C(2, lambda: (str(int(sens("baseline", "A", 1, "core")["duplicate"]) - int(sens("webhooks_not_by_name", "A", 1, "core")["duplicate"])),
                    "results/exploratory/sensitivity.csv: A c1 core duplicate, row baseline minus row webhooks_not_by_name"))]),
    ("model-k", "for $k = 1, 2, 3$", [L(1, P, "k = 1, 2, 3"), L(2, P, "k = 1, 2, 3"), L(3, P, "k = 1, 2, 3")]),
    ("model-hmac", "the first 12 hex characters of an HMAC", [L(12, P, "first 12 hex characters")]),
    ("model-t0", "from the first dispatch at $t=0$", [L(0, P, "with the first dispatch at t = 0")]),
    ("model-read", "is answered at $t+1$", [L(1, P, "| A status read | answered at t + 1")]),
    ("model-nominal", "it arrives 1 tick after dispatch, commits 1 tick after arrival, and its \\code{ok} response arrives 1 tick after the commit and its \\code{committed} receipt 2 ticks after emission",
     [L(1, P, "**Nominal attempt.**"), L(1, P, "**Nominal attempt.**"), L(1, P, "**Nominal attempt.**"), L(2, P, "**Nominal attempt.**")]),
    ("model-constants", "the client timeout is $T=5$ ticks after dispatch; the budget is 3 dispatches per operation; the horizon is $H=60$ ticks after the operation starts, and the belief at $H$ is final; the scoring cutoff is $F=200$; C, D and D+I poll status every 5 ticks; the contract-2 deduplication window is 1000 ticks, longer than the experiment; and Bw waits $\\tau=15$ ticks.",
     [C(5, info, "constants", "timeout"), C(3, info, "constants", "budget"), C(60, info, "constants", "horizon"), C(200, info, "constants", "final"),
      C(5, info, "constants", "poll_interval"), C(1000, info, "constants", "dedup_window"), C(15, info, "constants", "wait_tau")]),
    ("policies-budget", "a budget of 3 and the horizon $H$", [C(3, info, "constants", "budget")]),
    ("policies-bw", "the read is issued $\\tau=15$ ticks after the failure signal", [C(15, info, "constants", "wait_tau")]),
    ("policies-c", "polls status every 5 ticks and applies the rules above", [C(5, info, "constants", "poll_interval")]),
    ("policies-os", "Acts at A's decision points and every 5 ticks", [C(5, info, "constants", "oracle_interval")]),
    ("method-n", "lists the 16 scenarios", [C(16, nscen)]),
    ("method-g1", "G1 (lost ack: commit at $t=2$, response lost) crosses $L \\in \\{0, 1, 2, 4, 8, 16, 32, 64, \\text{never}\\}$ with receipt delays $W \\in \\{1, 2, 4, 8, 16, 32, 64, \\text{lost}\\}$: 72 schedules.",
     [L(v, P, "| G1: lost ack |") for v in (2, 0, 1, 2, 4, 8, 16, 32, 64, 1, 2, 4, 8, 16, 32, 64)] + [C(72, nsched, "G1")]),
    ("method-g2", "G2 (pending) crosses commit delays $E \\in \\{1, 3, 6, 12, 24, 48, 96\\}$ with $L \\in \\{0, 1, 4, 16, 64, \\text{never}\\}$, response lost, receipt delay 2: 42 schedules.",
     [L(v, P, "| G2: pending |") for v in (1, 3, 6, 12, 24, 48, 96, 0, 1, 4, 16, 64, 2)] + [C(42, nsched, "G2")]),
    ("method-g3", "G3 loses the request, for the same 6 lags.", [C(6, nsched, "G3")]),
    ("method-cells", "272 core cells with 289 operations, and 2040 grid cells",
     [C(272, info, "runs", "core_matrix"), C(289, info, "runs", "operations_core"), C(2040, info, "runs", "grids")]),
    ("scen-caption", "a1, dispatched at $t=0$", [L(0, P, "Times are for the first attempt, a1, dispatched at t = 0")]),
    ("valid", "Every run executes 61 checks and fails if any fails: 78 policy-free scripted runs",
     [C(61, nvalidation), C(78, validation, "V1_oracle_effect_histories", r"(\d+)/")]),
    ("valid-resend", "gives 2 effects under contract 1 and 1 under contract 2",
     [C(2, validation, "V2_committed_timeout_resend", r"c1 effects=(\d+)"), C(1, validation, "V2_committed_timeout_resend", r"c2 effects=(\d+)")]),
    ("valid-tests", "and 25 unit, property and mutation tests", [C(25, validation, "unit_and_mutation_tests", r"ran=(\d+)")]),
    ("valid-twice", "compares every output byte across two runs", [L(2, "README.md", "runs everything twice")]),
    ("use-twice", "the second compares every byte across two runs", [L(2, "README.md", "runs everything twice")]),
    ("hist-22", "committed 22 minutes before any code", [C(22, minutes, "8dc59af", "2ab9c6f", "floor")], 2),
    ("hist-clar", "and all 22 implementation clarifications", [C(22, nclarifications)]),
    ("hist-span", "the whole recorded history spans about 67 minutes", [C(67, minutes, "8dc59af", "d11234a", "round")]),
    ("hist-grid", "contract-1 grid duplicates fell from 114 to 90 for A, and from 86 to 70 and then 60 for B",
     [C(114, baseline_grid, "v1.0", "A"), C(90, baseline_grid, "v1.1", "A"), C(86, baseline_grid, "v1.0", "B"),
      C(70, baseline_grid, "v1.1", "B"), C(60, baseline_grid, "v1.1.1", "B")]),
    ("hist-caption", "Grid duplicates are contract-1 counts over the 120 grid schedules.", [C(120, nsched)]),
    ("hist-row-v11", "grid duplicates A 114$\\to$90, B 86$\\to$70",
     [C(114, baseline_grid, "v1.0", "A"), C(90, baseline_grid, "v1.1", "A"), C(86, baseline_grid, "v1.0", "B"), C(70, baseline_grid, "v1.1", "B")]),
    ("hist-row-v111", "grid duplicates B 70$\\to$60", [C(70, baseline_grid, "v1.1", "B"), C(60, baseline_grid, "v1.1.1", "B")]),
    ("res-intro", "the outcome of each of the 17 operations for every policy and contract; Table~\\ref{tab:pooled} totals them and the 120 grid schedules",
     [C(17, ops17), C(120, nsched)]),
    ("pooled-caption-17", "counts of the 17 authored operations per row", [C(17, ops17)]),
    ("pooled-caption-120", "false failures over the 120 grid schedules", [C(120, nsched)]),
    ("pooled-caption-fc", "False complete is 0 everywhere.", [C(0, false_complete_max)]),
    ("rep-a", "immediate retry (A) duplicates 12 of 17 operations", [C(12, bp, "duplicates", 1, "A"), C(17, ops17)]),
    ("rep-b", "A single immediate status read (B) duplicates 8:", [C(8, bp, "duplicates", 1, "B")]),
    ("rep-grid", "In the grid, A duplicates 90 of 120 schedules and B 60.",
     [C(90, gcount, "dup", 1, "A"), C(120, nsched), C(60, gcount, "dup", 1, "B")]),
    ("rep-afk", "A-fk duplicates the same 12 operations and 90 schedules as A under contract 1",
     [C(12, bp, "duplicates", 2, "A-fk"), C(90, gcount, "dup", 2, "A-fk")]),
    ("d-240", "D's 240 grid cells", [C(240, grid_rows_policy, "D")]),
    ("d-cost", "it leaves 4 of 17 core operations and 16 of 120 grid schedules unresolved at $H$",
     [C(4, bp, "unresolved_H", 1, "D"), C(17, ops17), C(16, gcount, "unres", 1, "D"), C(120, nsched)]),
    ("lat", "A's median time to confirmed completion of 5 ticks covers 5 operations and D's median of 7 covers 12",
     [C(5, bp, "ttc_median", 1, "A", "S00-S15", True), C(5, bp, "ttc_coverage", 1, "A"), C(7, bp, "ttc_median", 1, "D", "S00-S15", True), C(12, bp, "ttc_coverage", 1, "D")]),
    ("os", "it duplicates 4 core operations (S05, S10, S13, S15) and 30 grid schedules", [C(4, bp, "duplicates", 1, "ORACLE-S"), C(30, gcount, "dup", 1, "ORACLE-S")]),
    ("tr-s04", "In S04, A retries at $t=5$, and B, believing the stale \\code{not\\_found}, at $t=6$; both duplicate, with second effects at $t=7$ and $t=8$.",
     [C(5, at, "dispatch_times", 1, "A", "S04", "a2"), C(6, at, "dispatch_times", 1, "B", "S04", "a2"), C(7, at, "commits", 1, "A", "S04", "a2"), C(8, at, "commits", 1, "B", "S04", "a2")]),
    ("tr-bw", "Bw's verify timer and the receipt both fall at $t=20$", [C(20, sm, "ttc_any_complete", 1, "Bw", "S04")]),
    ("tr-s06", "In S06, A retries at the timeout ($t=5$, effect at $t=7$) and again when the stale \\code{aborted} receipt arrives at $t=30$, because its last terminal-looking event wins; a second effect commits at $t=32$.",
     [C(5, at, "dispatch_times", 1, "A", "S06", "a2"), C(7, at, "commits", 1, "A", "S06", "a2"), C(30, at, "dispatch_times", 1, "A", "S06", "a3"), C(32, at, "commits", 1, "A", "S06", "a3")]),
    ("abl-caption", "over both contracts (34 core operations, 240 grid schedules)", [L(34, X + "ablations.md", "| D | no_provider_seq"), L(240, X + "ablations.md", "| D | no_provider_seq")]),
    ("abl-caption-17", "(duplicates, exactly once, unresolved, false failures, of 17)", [L(17, X + "ablations.md", "| D | no_provider_seq")]),
    ("abl-none", "changes none of the 34 core operations and none of the 240 grid schedules",
     [L(34, X + "ablations.md", "| C | no_payload_correlation"), L(240, X + "ablations.md", "| C | no_payload_correlation")]),
    ("abl-latency", "delays confirmation in four scenarios (S04 from 20 to 36 ticks, S07 from 8 to 36, S13 from 10 to 11, S15 from 7 to 9), and raises the unresolved grid schedules from 16 to 41 of 120",
     [C(4, abl_count, "D", "ignore_webhooks", 1),
      C(20, abl_change, "D", "ignore_webhooks", 1, "S04", 1), C(36, abl_change, "D", "ignore_webhooks", 1, "S04", 2),
      C(8, abl_change, "D", "ignore_webhooks", 1, "S07", 1), C(36, abl_change, "D", "ignore_webhooks", 1, "S07", 2),
      C(10, abl_change, "D", "ignore_webhooks", 1, "S13", 1), C(11, abl_change, "D", "ignore_webhooks", 1, "S13", 2),
      C(7, abl_change, "D", "ignore_webhooks", 1, "S15", 1), C(9, abl_change, "D", "ignore_webhooks", 1, "S15", 2),
      C(16, abl_group, "D", "no_provider_seq", 11), C(41, abl_group, "D", "ignore_webhooks", 11), C(120, nsched)]),
    ("abl-status", "Ignoring status instead raises the grid count to 30", [C(30, abl_group, "D", "ignore_status", 11)]),
    ("name-2", "harms the immediate-retry client in 2 scenarios",
     [C(2, lambda: (str(int(sens("baseline", "A", 1, "core")["duplicate"]) - int(sens("webhooks_not_by_name", "A", 1, "core")["duplicate"])),
                    "results/exploratory/sensitivity.csv: A c1 core duplicate, row baseline minus row webhooks_not_by_name"))]),
    ("name-s14", "In S14 a \\code{deferred} receipt arrives at $t=12$, after A confirmed completion at $t=4$; A's belief flips to failed and a second effect commits at $t=14$.",
     [C(12, at, "dispatch_times", 1, "A", "S14", "a2"), C(4, sm, "ttc_any_complete", 1, "A", "S14"), C(14, at, "commits", 1, "A", "S14", "a2")]),
    ("name-1210", "A's contract-1 duplicates fall from 12 to 10",
     [C(12, sensv, "duplicate", "baseline", "A", 1, "core"), C(10, sensv, "duplicate", "webhooks_not_by_name", "A", 1, "core")]),
    ("name-family", "receipt-specific harm for A in 2 scenarios",
     [C(2, lambda: (str(int(sens("baseline", "A", 1, "core")["duplicate"]) - int(sens("webhooks_not_by_name", "A", 1, "core")["duplicate"])),
                    "results/exploratory/sensitivity.csv: A c1 core duplicate, row baseline minus row webhooks_not_by_name"))]),
    ("s15", "by receipt at $t=4$ and in the status listing, and then commits a1 at $t=12$. D retries at $t=4$; a2 commits at $t=6$ and D confirms completion at $t=7$. At $t=14$ the \\code{committed} receipt for a1 arrives, D records a conflict (the commit wins), and the ledger holds 2 effects.",
     [L(4, P, "| S15 | webhook harm"), C(12, at, "commits", 1, "D", "S15", "a1"), C(4, at, "dispatch_times", 1, "D", "S15", "a2"),
      C(6, at, "commits", 1, "D", "S15", "a2"), C(7, sm, "ttc_any_complete", 1, "D", "S15"), L(14, P, "| S15 | webhook harm"),
      C(2, sm, "effects_F", 1, "D", "S15")]),
    ("sens-caption", "for the 17 core operations and then the 120 grid schedules", [C(17, ops17), C(120, nsched)]),
    ("surv-ab", "A duplicates at least 10 of 17 core operations and 90 of 120 grid schedules in every row, and B at least 5 and 40",
     [C(10, sens_ext, "duplicate", "A", 1, "core", min), C(17, ops17), C(90, sens_ext, "duplicate", "A", 1, "grid", min), C(120, nsched),
      C(5, sens_ext, "duplicate", "B", 1, "core", min), C(40, sens_ext, "duplicate", "B", 1, "grid", min)]),
    ("surv-c2", "duplicates a grid schedule or more than 1 core operation in any row",
     [C(1, sens_ext_many, "duplicate", ["A", "B", "Bw", "C", "D", "D+I"], [2], "core", max)]),
    ("surv-cd", "C and D leave at least 3 of 17 core operations unresolved in every row",
     [C(3, sens_ext_many, "unresolved", ["C", "D"], [1, 2], "core", min), C(17, ops17)]),
    ("moves-tau5", "with $\\tau=5$ Bw duplicates even under contract 2", [C(5, lambda: (sens_option_value("tau_5"), "results/exploratory/sensitivity.csv: options column of row tau_5"))]),
    ("bw-3", "its 3 contract-1 core duplicates rest on fine timing", [C(3, bp, "duplicates", 1, "Bw")]),
    ("bw-grid", "a1 commits at $t=2$ with its response lost, the receipt arrives at $t=R$ for $R$ from 3 to 70 or never, and $L$ runs from 0 to 64",
     [L(v, X + "bw_boundary.md", "Grid 1: a1 commits at t = 2") for v in (2, 3, 70, 0, 64)]),
    ("bw-formula", "with $L^* = \\tau + T - c + 1$ and $R^* = \\tau + T + 2$ as derived from the timing rules, where $c=2$ is the commit time",
     [L(1, X + "bw_boundary.md", "predicted L* = tau + T - c + 1"), L(2, X + "bw_boundary.md", "predicted L* = tau + T - c + 1"),
      L(2, X + "bw_boundary.md", "Grid 1: a1 commits at t = 2")]),
    ("bw-T", "with $T=5$, $L \\geq \\tau+4$ and $R \\geq \\tau+7$. For the frozen $\\tau=15$, Bw duplicates exactly when $L \\geq 19$ and the receipt arrives at $t \\geq 22$.",
     [C(5, info, "constants", "timeout"), C(4, bw_offset, "L_star"), C(7, bw_offset, "R_star"), C(15, info, "constants", "wait_tau"),
      C(19, bwv, "L_star", 15), C(22, bwv, "R_star", 15)]),
    ("bw-s04", "S04 (receipt at $t=20$, $L=30$) lies 2 ticks on the safe side",
     [L(20, P, "| S04 | lost ack"), L(30, P, "| S04 | lost ack"),
      C(2, lambda: (str(int(bwv("R_star", 15)[0]) - 20), "results/exploratory/bw_boundary.csv: R_star at tau=15 minus S04's receipt time 20"))]),
    ("bw-pending", "with the receipt lost and the commit at $t=1+E$, Bw ($\\tau=15$) duplicates exactly when $E+L \\geq 20$",
     [L(1, X + "bw_boundary.md", "a1 commits at t = 1 + E"), L(15, X + "bw_boundary.md", "a1 commits at t = 1 + E"),
      C(20, lambda: (re.search(r"(\d+)", one(X + "bw_boundary.csv", grid="pending_tau15")["predicted_L_star"]).group(1)
                     if one(X + "bw_boundary.csv", grid="pending_tau15")["rectangle_exact"] == "1" else "inexact",
                     "results/exploratory/bw_boundary.csv: grid=pending_tau15, predicted 'E+L>=20', rectangle_exact=1"))]),
    ("pf-attempt1", "repeats attempt 1's fault on every retry", [L(1, X + "persistent_faults.md", "repeats attempt 1's fault")]),
    ("pf-three", "Under persistent lost acknowledgements A commits three times", [C(3, pfv, "effects_F", 1, "A", "PF1")]),
    ("pf-three-bw", "Bw also commits three times in PF2", [C(3, pfv, "effects_F", 1, "Bw", "PF2")]),
    ("pf-caption", "the same fault on all three attempts", [C(3, info, "constants", "budget")]),
    ("esc-four", "D+I the same four under contract 1", [C(4, escal_core, 1, "D+I")]),
    ("esc-truth", "S08 and S11/op-1 (a1 committed at $t=2$) need a correlated positive that never comes; S10 (a1 commits at $t=90$)",
     [C(2, escal_truth, "S08", r"committed@(\d+)"), C(90, escal_truth, "S10", r"@(\d+)")]),
    ("esc-grid", "4 G1 schedules lacking a positive, 6 G2 schedules committing after $H$ and the 6 G3 schedules",
     [C(4, gcount, "unres", 1, "D", "G1"), C(6, gcount, "unres", 1, "D", "G2"), C(6, gcount, "unres", 1, "D", "G3")]),
    ("pred", "All 20 rows of the original protocol match (16 from its prediction section, scoped to S00--S12, and 4 from its worked timeline), as do 16 of the 17 design-update rows and the 1 tie-note row. That 37 of 38 rows match",
     [C(20, pred_counts, ("orig", "timeline"), "match"), C(16, pred_counts, ("orig",), "rows"), C(4, pred_counts, ("timeline",), "rows"),
      C(16, pred_counts, ("update",), "match"), C(17, pred_counts, ("update",), "rows"), C(1, pred_counts, ("tie",), "match"),
      C(37, info, "predictions", "match"), C(38, info, "predictions", "total")]),
    ("lim-cases", "The 16 core scenarios, 120 grid schedules and 4 persistent-fault scenarios", [C(16, nscen), C(120, nsched), C(4, npf)]),
    ("lim-d", "1 of 17 core operations and 6 of 120 grid schedules",
     [C(1, bp, "zero_effects", 1, "D"), C(17, ops17), C(6, nsched, "G3"), C(120, nsched)]),
    ("lim-revisions", "two revisions were made after results were visible", [C(2, post_freeze_revisions)]),
    ("avail", "exits 0 only if every check passes; it takes about 15 seconds (CPython 3.13.7, macOS, arm64)",
     [L(0, "README.md", "exits 0 only if every check passes"), L(15, "README.md", "It takes about 15 seconds"), C("3.13.7", info, "python_version")]),
]

# Hand-written table rows: every number in the row must appear in the cited source line(s).
ROWCHECKS = [
    ("tab:scenarios", "S00 &", [(P, "| S00 | control |")]),
    ("tab:scenarios", "S01 &", [(P, "| S01 | auth. negative |")]),
    ("tab:scenarios", "S02 &", [(P, "| S02 | auth. negative |")]),
    ("tab:scenarios", "S03 &", [(P, "| S03 | lost ack |")]),
    ("tab:scenarios", "S04 &", [(P, "| S04 | lost ack |")]),
    ("tab:scenarios", "S05 &", [(P, "| S05 | pending |")]),
    ("tab:scenarios", "S06 &", [(P, "| S06 | receipt anomaly |")]),
    ("tab:scenarios", "S07 &", [(P, "| S07 | receipt anomaly |")]),
    ("tab:scenarios", "S08 &", [(P, "| S08 | no confirmation |")]),
    ("tab:scenarios", "S09 &", [(P, "| S09 | no confirmation")]),
    ("tab:scenarios", "S10 &", [(P, "| S10 | pending |")]),
    ("tab:scenarios", "S11 &", [(P, "| S11 | validation: distinct ops |")]),
    ("tab:scenarios", "S12 &", [(P, "| S12 | lost ack (error) |")]),
    ("tab:scenarios", "S13 &", [(P, "| S13 | webhook harm |")]),
    ("tab:scenarios", "S14 &", [(P, "| S14 | webhook harm |")]),
    ("tab:scenarios", "S15 &", [(P, "| S15 | webhook harm (")]),
    ("tab:traces", "0 & -- & dispatches a1 & -- \\\\", [(WT, "| 0 | - | operation op-1 starts; dispatches **a1** | - |")]),
    ("tab:traces", "1 & a1 arrives and is accepted & -- & -- \\\\", [(WT, "| 1 | a1 arrives and is accepted | - | - |")]),
    ("tab:traces", "2 & a1 commits;", [(WT, "| 2 | a1 executes and commits effect")]),
    ("tab:traces", "5 & replica (lag 30)", [(WT, "| 5 | replica as of t = -25"), (WT, "L = 30 (stale")]),
    ("tab:traces", "6 & -- & \\code{not\\_found}, no terminal", [(WT, "| 6 | - | status reply **`not_found`**, terminal_attempts [] |")]),
    ("tab:traces", "10, 15 & --", [(WT, "| 10 | replica as of t = -20"), (WT, "| 11 | - | status reply"), (WT, "| 15 | replica as of t = -15"), (WT, "| 16 | - | status reply")]),
    ("tab:traces", "20 & -- & \\code{committed} receipt", [(WT, "| 20 | - | webhook `committed` seq 2000")]),
    ("tab:traces", "3 & a1 aborts;", [(WT, "| 3 | a1 aborts; emits `aborted` (seq 3000) for a1 -> lost"), (WT, "| 3 | a1 aborts; emits `aborted` (seq 3000) for a1 -> delivery at t = 30")]),
    ("tab:traces", "5 & replica (as of", [(WT, "| 5 | replica as of t = 4 shows 2 record(s)")]),
    ("tab:traces", "6 & -- & \\code{not\\_found} with a1 terminal", [(WT, "| 6 | - | status reply **`not_found`**, terminal_attempts [a1]")]),
    ("tab:traces", "8 & a2 commits", [(WT, "| 8 | a2 executes and commits effect")]),
    ("tab:traces", "9 & -- & \\code{ok} for a2", [(WT, "| 9 | - | response `ok` for a2")]),
    ("tab:traces", "30 & -- & S06 only", [(WT, "| 30 | - | webhook `aborted` seq 3000 for a1")]),
]


# --------------------------------------------------------------------------------------------
# Claims about named operations in the prose (not numbers, but load-bearing).
# --------------------------------------------------------------------------------------------
def ops_set(field, c, p, scope="S00-S15"):
    v = one(R + "by_policy.csv", scope=scope, contract=c, policy=p)[field]
    return set(re.sub(r"\(H\d/F\d\)", "", v).split())


CLAIMS = [
    ("A c1 duplicates: lost acks, pending, S06, S14, S15",
     lambda: ops_set("duplicate_ops", 1, "A") == {"S03", "S04", "S05", "S06", "S07", "S08", "S10", "S11/op-1", "S12", "S13", "S14", "S15"}),
    ("B c1 duplicates: S04, S07, S08, S11/op-1 (stale), S05, S10, S13 (pending), S15",
     lambda: ops_set("duplicate_ops", 1, "B") == {"S04", "S05", "S07", "S08", "S10", "S11/op-1", "S13", "S15"}),
    ("A and B c2: only duplicate is S15", lambda: ops_set("duplicate_ops", 2, "A") == {"S15"} and ops_set("duplicate_ops", 2, "B") == {"S15"}),
    ("A-fk c2 duplicates = A c1 duplicates", lambda: ops_set("duplicate_ops", 2, "A-fk") == ops_set("duplicate_ops", 1, "A")),
    ("C, D unresolved = S08, S09, S10, S11/op-1 under both contracts; D+I c1 same; D+I c2 = S10; ORACLE-O = S10",
     lambda: all(ops_set("unresolved_ops", c, p) == {"S08", "S09", "S10", "S11/op-1"} for c in (1, 2) for p in ("C", "D"))
     and ops_set("unresolved_ops", 1, "D+I") == {"S08", "S09", "S10", "S11/op-1"} and ops_set("unresolved_ops", 2, "D+I") == {"S10"}
     and all(ops_set("unresolved_ops", c, "ORACLE-O") == {"S10"} for c in (1, 2))),
    ("contract-2 S15 duplicates: A, B, D, D+I, ORACLE-S (and A-fk); not Bw, C, ORACLE-O",
     lambda: {p for p in POL2 if "S15" in ops_set("duplicate_ops", 2, p)} == {"A", "B", "D", "D+I", "ORACLE-S", "A-fk"}),
    ("contract-1 S15 duplicates include A, B, D, D+I, ORACLE-S; not Bw, C, ORACLE-O",
     lambda: {p for p in POL1 if "S15" in ops_set("duplicate_ops", 1, p)} == {"A", "B", "D", "D+I", "ORACLE-S"}),
    ("D and D+I S15 duplicates are contract-caused",
     lambda: all(sm("dup_cause", c, p, "S15")[0] == "contract" for c in (1, 2) for p in ("D", "D+I"))),
    ("contract-2 false failures in S10 for A, B, Bw (and ORACLE-S)",
     lambda: {p for p in POL2 if ops_set("false_failure_ops", 2, p)} == {"A", "B", "Bw", "ORACLE-S"}
     and all(ops_set("false_failure_ops", 2, p) == {"S10"} for p in ("A", "B", "Bw", "ORACLE-S"))),
    ("ORACLE-S c1 duplicates S05, S10, S13, S15", lambda: ops_set("duplicate_ops", 1, "ORACLE-S") == {"S05", "S10", "S13", "S15"}),
    ("Bw c1 duplicates S08, S10, S11/op-1", lambda: ops_set("duplicate_ops", 1, "Bw") == {"S08", "S10", "S11/op-1"}),
    ("C ends failed with 0 effects in S02 and S06; D completes them exactly once",
     lambda: all(sm("belief_H", c, "C", s)[0] == "failed" and sm("effects_F", c, "C", s)[0] == "0" and sm("effects_F", c, "D", s)[0] == "1"
                 and sm("belief_H", c, "D", s)[0] == "complete" for c in (1, 2) for s in ("S02", "S06"))),
    ("S07 gives every policy the same effects and belief as S04",
     lambda: all(sm("effects_F", c, p, "S07")[0] == sm("effects_F", c, p, "S04")[0] and sm("belief_H", c, p, "S07")[0] == sm("belief_H", c, p, "S04")[0]
                 for c, pols in ((1, POL1), (2, POL2)) for p in pols)),
    ("D records a conflict in S15 (both contracts); C ends complete there", lambda: all(sm("conflicts", c, "D", "S15")[0] == "1" and sm("belief_H", c, "C", "S15")[0] == "complete" for c in (1, 2))),
    ("Bw S04 contract 1: no status read, exactly once", lambda: sm("status_reads", 1, "Bw", "S04")[0] == "0" and sm("effects_F", 1, "Bw", "S04")[0] == "1"),
    ("A and B S04 contract 2: retry replayed, exactly once", lambda: all(sm("effects_F", 2, p, "S04")[0] == "1" and sm("retries", 2, p, "S04")[0] == "1" for p in ("A", "B"))),
    ("D ignore_webhooks: no core belief or effect change; C ignore_webhooks: false failure in S15",
     lambda: all("belief_H" not in r["changes"] and "effects" not in r["changes"] for r in rows(X + "ablations.csv")
                 if r["policy"] == "D" and r["ablation"] == "ignore_webhooks" and r["scope"] == "core")
     and "belief_H: complete -> failed" in one(X + "ablations.csv", policy="C", ablation="ignore_webhooks", scope="core", contract=1, scenario="S15")["changes"]),
    ("D ignore_status loses S02 (both contracts)",
     lambda: all("effects_F: 1 -> 0" in one(X + "ablations.csv", policy="D", ablation="ignore_status", scope="core", contract=c, scenario="S02")["changes"] for c in (1, 2))),
    ("webhooks_not_by_name changes nothing for B and Bw", lambda: all(sensv(f, "webhooks_not_by_name", p, c, s)[0] == sensv(f, "baseline", p, c, s)[0]
                                                                     for p in ("B", "Bw") for c in (1, 2) for s in ("core", "grid") for f in ("duplicate", "exactly_once", "unresolved", "false_failure"))),
    ("A-fk c2 equals A c1 in every sensitivity row",
     lambda: all(sensv(f, r, "A-fk", 2, s)[0] == sensv(f, r, "A", 1, s)[0] for r in {x["row"] for x in rows(X + "sensitivity.csv")}
                 for s in ("core", "grid") for f in ("duplicate", "exactly_once", "unresolved", "false_failure"))),
    ("C never duplicates; D duplicates at most 1 core op and 0 grid cells, in every sensitivity row",
     lambda: all(int(r["duplicate"]) == 0 for r in rows(X + "sensitivity.csv") if r["policy"] == "C")
     and all(int(r["duplicate"]) <= (1 if r["scope"] == "core" else 0) for r in rows(X + "sensitivity.csv") if r["policy"] == "D")),
    ("no client policy except A-fk duplicates a grid schedule under contract 2 in any row",
     lambda: all(int(r["duplicate"]) == 0 for r in rows(X + "sensitivity.csv") if r["contract"] == "2" and r["scope"] == "grid" and r["policy"] in ("A", "B", "Bw", "C", "D", "D+I"))),
    ("abort_record=replay_failure removes every contract-2 core duplicate",
     lambda: all(int(r["duplicate"]) == 0 for r in rows(X + "sensitivity.csv") if r["row"] == "abort_record_replays_failure" and r["contract"] == "2" and r["policy"] != "A-fk")),
    ("sensitivity.md states D and D+I lose S02 and S06 under replay_failure",
     lambda: any("D and D+I then lose S02 and S06" in ln for ln in lines(X + "sensitivity.md"))),
    ("horizon_120 resolves S10 for C and D: unresolved 4 -> 3", lambda: all(sensv("unresolved", "horizon_120", p, c, "core")[0] == "3" for p in ("C", "D") for c in (1, 2))),
    ("persistent faults: B c1 PF2 3 effects failed; A c2 PF1/PF2 1 effect failed; D+I c2 unresolved in PF2-PF4; C, D never duplicate",
     lambda: pfv("effects_F", 1, "B", "PF2")[0] == "3" and pfv("belief_H", 1, "B", "PF2")[0] == "failed"
     and all(pfv("belief_H", 2, p, s)[0] == "failed" and pfv("false_failure", 2, p, s)[0] == "1" for p in ("A",) for s in ("PF1", "PF2"))
     and all(pfv("belief_H", 2, "D+I", s)[0] == "unresolved" for s in ("PF2", "PF3", "PF4"))
     and all(r["duplicate"] == "0" for r in rows(X + "persistent_faults.csv") if r["policy"] in ("C", "D"))),
    ("PF titles: status lags of PF1-PF4 are 1, never, 1, 1",
     lambda: [jload("scenarios/exploratory/%s.json" % s)["status_lag"] for s in ("PF1", "PF2", "PF3", "PF4")] == [1, "never", 1, 1]),
    ("U04b vacuous, U09a mismatch",
     lambda: {x[1]: x[3] for x in prediction_rows()}["U04b"] == "MATCH (vacuous)" and {x[1]: x[3] for x in prediction_rows()}["U09a"] == "MISMATCH"),
    ("v1.2 changed no core outcome against v1.1.1",
     lambda: all(all(a[k] == b[k] for k in ("effects_H", "effects_F", "duplicate", "dup_cause", "belief_H", "unresolved", "false_failure", "false_complete", "dispatch_times", "commits"))
                 for a, b in zip(rows("baselines/v1.1.1/summary.csv"), rows(R + "summary.csv")))),
    ("v1.1 and v1.1.1 changed no core cell", lambda: rows("baselines/v1.0/summary.csv") == rows("baselines/v1.1/summary.csv") == rows("baselines/v1.1.1/summary.csv")),
    ("v1.1 and v1.1.1 changed nothing for C or D in the grid",
     lambda: all([r for r in rows("baselines/%s/grid.csv" % lab) if r["policy"] in ("C", "D")] ==
                 [r for r in rows("baselines/v1.0/grid.csv") if r["policy"] in ("C", "D")] for lab in ("v1.1", "v1.1.1"))),
    ("commits cited in the history table exist",
     lambda: all(subprocess.call(["git", "-C", ROOT, "cat-file", "-e", h + "^{commit}"]) == 0 for h in
                 ("8dc59af", "2ab9c6f", "3f6cb9c", "924aef2", "2b2d5e0", "47289f8", "622e1f1", "6ae14a9", "7da9ec8", "b95a667",
                  "9d4021c", "bc1fea0", "0b01478", "4ffb5ce", "d11234a"))),
    ("original predictions (8dc59af) are unchanged in the current protocol; design update, U predictions and C22 first appear in 2ab9c6f",
     lambda: all(ln in lines("PROTOCOL.md") for ln in git("show", "8dc59af:PROTOCOL.md").split("## 7. Pre-specified predictions")[1].split("## 8.")[0].split("\n")
                 if ln.startswith("| A |") or ln.startswith("| B |") or ln.startswith("| C |") or ln.startswith("| D |") or ln.startswith("- "))
     and "Added after the prior-work review" not in git("show", "8dc59af:PROTOCOL.md") and "Bw" not in git("show", "8dc59af:PROTOCOL.md")
     and "Added after the prior-work review" in git("show", "2ab9c6f:PROTOCOL.md") and "**C22." in git("show", "2ab9c6f:PROTOCOL.md")
     and "U01" in git("show", "2ab9c6f:arr/predictions.py")),
    ("freeze is current and matches", lambda: jload(R + "run_info.json")["freeze"]["label"] == "v1.2.2" and jload(R + "run_info.json")["freeze"]["matches"] is True),
]


# --------------------------------------------------------------------------------------------
# Consistency between result files that report the same quantity
# --------------------------------------------------------------------------------------------
def consistency():
    problems = []
    bpr = {(r["scope"], r["contract"], r["policy"]): r for r in rows(R + "by_policy.csv")}
    # sensitivity baseline = by_policy (core) and grid.csv (grid)
    for r in rows(X + "sensitivity.csv"):
        if r["row"] != "baseline":
            continue
        c, p = r["contract"], r["policy"]
        if r["scope"] == "core":
            b = bpr[("S00-S15", c, p)]
            for fs, fb in (("duplicate", "duplicates"), ("exactly_once", "exactly_once"), ("unresolved", "unresolved_H"),
                           ("false_failure", "false_failure"), ("false_complete", "false_complete")):
                if r[fs] != num(b[fb]):
                    problems.append("sensitivity baseline vs by_policy: %s c%s %s %s != %s" % (p, c, fs, r[fs], b[fb]))
        else:
            g = grid_counts(R + "grid.csv", c, p)
            for fs, k in (("duplicate", "dup"), ("exactly_once", "once"), ("unresolved", "unres"), ("false_failure", "ff")):
                if int(r[fs]) != g[k]:
                    problems.append("sensitivity baseline vs grid.csv: %s c%s %s %s != %s" % (p, c, fs, r[fs], g[k]))
    # headline.md (S00-S15 table) vs by_policy.csv
    lab = {"A": "A", "B": "B", "Bw": "Bw", "C": "C", "D": "D", "D+I (optional)": "D+I", "A-fk (ablation)": "A-fk",
           "ORACLE-S (state-probe reference, not a ceiling)": "ORACLE-S", "ORACLE-O (outcome-oracle reference)": "ORACLE-O"}
    scope = None
    for ln in lines(R + "headline.md"):
        if ln.startswith("## Scope S00-S15"):
            scope = "S00-S15"
        elif ln.startswith("## Scope S00-S12"):
            scope = "S00-S12"
        elif ln.startswith("## "):
            scope = None
        m = re.match(r"^\| (\d) \| (.+?) \| (\d+/\d+) \[(\d+); (\d+)c/(\d+)p\] \| (\d+/\d+) \| (\d+/\d+) \| (\d+/\d+) \| (\d+/\d+) \| (\d+/\d+) \|.*\| ([\d.]+) / (\d+) \((\d+/\d+)\) \|$", ln)
        if scope and m:
            c, p = m.group(1), lab[m.group(2)]
            b = bpr[(scope, c, p)]
            exp = [b["duplicates"], b["extra_effects"], num(b["dup_contract_caused"]), num(b["dup_policy_caused"]), b["exactly_once"],
                   b["zero_effects"], b["unresolved_H"], b["false_complete"], b["false_failure"], b["ttc_median"], b["ttc_max"], b["ttc_coverage"]]
            if list(m.groups()[2:]) != exp:
                problems.append("headline.md vs by_policy.csv: %s c%s %s" % (scope, c, p))
    # grid_tables.md summary vs grid.csv
    gl = {"A": "A", "B": "B", "Bw": "Bw", "C": "C", "D": "D", "D+I (optional)": "D+I", "A-fk (ablation)": "A-fk",
          "ORACLE-S (state-probe reference, not a ceiling)": "ORACLE-S", "ORACLE-O (outcome-oracle reference)": "ORACLE-O"}
    for ln in lines(R + "grid_tables.md"):
        m = re.match(r"^\| (G\d) \| (\d) \| (.+?) \| (\d+)/\d+ \| (\d+)/\d+ \| (\d+)/\d+ \| (\d+)/\d+ \|", ln)
        if m:
            g, c, p = m.group(1), m.group(2), gl[m.group(3)]
            cnt = grid_counts(R + "grid.csv", c, p, g)
            got = [int(x) for x in m.groups()[3:]]
            if got != [cnt["dup"], cnt["cert"], cnt["unres"], cnt["ff"]]:
                problems.append("grid_tables.md vs grid.csv: %s c%s %s" % (g, c, p))
    # ablations.md: seq/dedupe/payload rows equal the sensitivity baseline (contract 1)
    for (p, key), (i, g) in ablation_lines().items():
        if key in ("no_provider_seq", "no_event_id_dedupe", "no_payload_correlation"):
            core = [sens("baseline", p, 1, "core")[f] for f in ("duplicate", "exactly_once", "unresolved", "false_failure", "false_complete")]
            grid = [sens("baseline", p, 1, "grid")[f] for f in ("duplicate", "exactly_once", "unresolved", "false_failure", "false_complete")]
            if list(g[4:9]) != core or list(g[9:14]) != grid:
                problems.append("ablations.md line %d vs sensitivity baseline (%s)" % (i, p))
            if g[2] != "0" or g[3] != "0":
                problems.append("ablations.md line %d: %s %s changed cells" % (i, p, key))
    # bw_boundary.md table vs csv
    for ln in lines(X + "bw_boundary.md"):
        m = re.match(r"^\| (\d+) \| (\d+) of (\d+) \| (\d+) \| (\d+) \| (yes|no) \| (\d+) \| (\d+) \|$", ln)
        if m:
            r = one(X + "bw_boundary.csv", grid="lost_ack", tau=m.group(1))
            if [m.group(2), m.group(3), m.group(4), m.group(5), m.group(7), m.group(8)] != [r["duplicates"], r["cells"], r["L_star"], r["R_star"], r["predicted_L_star"], r["predicted_R_star"]]:
                problems.append("bw_boundary.md vs csv: tau %s" % m.group(1))
    # predictions: run_info vs predictions_check.md
    pr = prediction_rows()
    ri = jload(R + "run_info.json")["predictions"]
    if (ri["total"], ri["match"], ri["vacuous"]) != (len(pr), sum(1 for x in pr if x[3].startswith("MATCH")), sum(1 for x in pr if "vacuous" in x[3])):
        problems.append("run_info.json predictions vs predictions_check.md")
    # escalation core rows vs by_policy unresolved_ops
    for c in (1, 2):
        for p in POL2:
            if (("S00-S15", str(c), p)) not in bpr:
                continue
            esc = {r["scenario"] + ("/" + r["op"] if r["scenario"] == "S11" else "") for r in rows(X + "escalation.csv")
                   if r["source"] == "core" and r["contract"] == str(c) and r["policy"] == p}
            if esc != ops_set("unresolved_ops", c, p):
                problems.append("escalation.csv vs by_policy unresolved_ops: c%d %s" % (c, p))
    # run_info runs vs summary/grid row counts
    if jload(R + "run_info.json")["runs"]["operations_core"] != len(rows(R + "summary.csv")):
        problems.append("run_info operations_core vs summary.csv rows")
    if jload(R + "run_info.json")["runs"]["grids"] != len(rows(R + "grid.csv")):
        problems.append("run_info grids vs grid.csv rows")
    return problems


# --------------------------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------------------------
def table_block(t, label):
    i = t.index("\\label{%s}" % label)
    s = t.index("\\begin{tabular}", i)
    e = t.index("\\end{tabular}", s)
    return t[s:e]


def run_checks():
    fails = []
    notes = []
    t = tex()
    # 6. ASCII and comments
    bad = [i for i, ch in enumerate(t) if ord(ch) > 127]
    if bad:
        fails.append("main.tex has %d non-ASCII characters (first at offset %d)" % (len(bad), bad[0]))
    if re.search(r"(?<!\\)%", t):
        fails.append("main.tex contains an unescaped % (LaTeX comment)")
    body = norm(body_of(t))
    remaining = body
    # 1. generated tables
    ngen = 0
    for label, gen in GENERATED.items():
        blk = norm(table_block(t, label))
        for row, src in gen():
            r = norm(row)
            if r not in blk:
                fails.append("%s: generated row not found in main.tex: %s" % (label, row[:90]))
            else:
                blk = blk.replace(r, "", 1)
                remaining = remaining.replace(r, " ", 1)
                ngen += 1
    # 2. hand-written rows
    nrow = 0
    for label, key, sources in ROWCHECKS:
        blk = table_block(t, label)
        cand = [ln.strip() for ln in blk.split("\n") if ln.strip().startswith(key)]
        if label == "tab:traces" and key in ("0 & -- & dispatches a1 & -- \\\\", "1 & a1 arrives and is accepted & -- & -- \\\\"):
            want = 2
        else:
            want = 1
        if len(cand) != want:
            fails.append("%s: expected %d row(s) starting %r, found %d" % (label, want, key, len(cand)))
            continue
        allowed = []
        for rel, needle in sources:
            try:
                allowed += NUMTOK.findall(line(rel, findline(rel, needle)))
            except KeyError as e:
                fails.append(str(e))
        for row in cand:
            for tok in paper_tokens(row):
                if tok not in allowed:
                    fails.append("%s row %r: number %s not in source %s" % (label, key, tok, sources))
            remaining = remaining.replace(norm(row), " ", 1)
            nrow += 1
    # 3. registry
    nnum = 0
    for entry in REGISTRY:
        eid, snip, checks = entry[0], entry[1], entry[2]
        count = entry[3] if len(entry) > 3 else 1
        sn = norm(snip)
        found = body.count(sn)
        if found != count:
            fails.append("%s: snippet found %d times, expected %d: %r" % (eid, found, count, snip[:80]))
            continue
        toks = paper_tokens(sn)
        exps = [e for e, g in checks]
        if sorted(toks) != sorted(exps):
            fails.append("%s: numbers in snippet %s do not match the checked numbers %s" % (eid, toks, exps))
        for exp, g in checks:
            try:
                val, loc = g()
            except Exception as e:
                fails.append("%s: source error for %s: %r" % (eid, exp, e))
                continue
            if str(val) != exp:
                fails.append("%s: paper says %s, source says %s (%s)" % (eid, exp, val, loc))
            nnum += 1
        remaining = remaining.replace(sn, " ")
    # 4. completeness
    remaining = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", " ", remaining)
    left = []
    for piece in re.split(r"(?<=\\\\)|\. ", remaining):
        for tok in paper_tokens(piece):
            left.append((tok, norm(piece)[:100]))
    for tok, ctx in left:
        fails.append("uncovered number %s in: %s" % (tok, ctx))
    # 5. claims and consistency
    for name, fn in CLAIMS:
        try:
            ok = fn()
        except Exception as e:
            ok = False
            name += " (error %r)" % e
        if not ok:
            fails.append("claim failed: " + name)
    for p in consistency():
        fails.append("inconsistent result files: " + p)
    # 7. NUMBERS.md up to date
    if not os.path.exists(NUMBERS_MD) or open(NUMBERS_MD).read() != numbers_md():
        fails.append("paper/NUMBERS.md is missing or out of date (run with --write-numbers)")
    notes.append("generated table rows: %d" % ngen)
    notes.append("hand-written table rows: %d" % nrow)
    notes.append("prose numbers asserted: %d (in %d snippets)" % (nnum, len(REGISTRY)))
    notes.append("claims: %d; consistency checks across result files" % len(CLAIMS))
    return fails, notes


# --------------------------------------------------------------------------------------------
# NUMBERS.md
# --------------------------------------------------------------------------------------------
def md_escape(s):
    return s.replace("|", "\\|").replace("\n", " ")


def numbers_md():
    out = ["# Number provenance for paper/main.tex", "",
           "Generated by `python3 paper/check_numbers.py --write-numbers`; checked by `python3 paper/check_numbers.py`, "
           "which re-reads every source below and fails if any number in the paper differs, or if any number in the "
           "body of the paper is not covered by this file. Paths are relative to the repository root. "
           "Excluded: the bibliography, and the command lines in the verbatim block (their arguments are examples, not results).", ""]
    out += ["## 1. Data tables (every row regenerated from the result files and compared verbatim)", ""]
    for label, gen in GENERATED.items():
        out += ["### %s" % label, "", "| Row in main.tex | Source (file, row and columns) |", "|---|---|"]
        for row, src in gen():
            out.append("| `%s` | %s |" % (md_escape(row.replace(" \\\\", "")), md_escape(src)))
        out.append("")
    out += ["## 2. Hand-written table rows (every number in the row must occur in the cited source line)", "",
            "| Table | Row starts with | Source lines |", "|---|---|---|"]
    for label, key, sources in ROWCHECKS:
        locs = "; ".join("%s line %d" % (rel, findline(rel, needle)) for rel, needle in sources)
        out.append("| %s | `%s` | %s |" % (label, md_escape(key.replace(" \\\\", "")), locs))
    out += ["", "## 3. Numbers in the text, captions and other cells", "",
            "| ID | Snippet of main.tex | Number | Source |", "|---|---|---|---|"]
    for entry in REGISTRY:
        eid, snip, checks = entry[0], entry[1], entry[2]
        for exp, g in checks:
            val, loc = g()
            out.append("| %s | %s | %s | %s |" % (eid, md_escape(snip if len(snip) < 120 else snip[:117] + "..."), exp, md_escape(loc)))
    out += ["", "## 4. Claims about named operations (asserted, not numbers)", ""]
    for name, fn in CLAIMS:
        out.append("- " + name)
    out.append("")
    return "\n".join(out)


def main(argv):
    if len(argv) > 1 and argv[1] == "--emit":
        for row, src in GENERATED[argv[2]]():
            print(row)
        return 0
    if len(argv) > 1 and argv[1] == "--write-numbers":
        with open(NUMBERS_MD, "w") as f:
            f.write(numbers_md())
        print("wrote", NUMBERS_MD)
        return 0
    fails, notes = run_checks()
    for n in notes:
        print(n)
    if fails:
        print("FAILED: %d problem(s)" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASS: every number in paper/main.tex matches its source")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
