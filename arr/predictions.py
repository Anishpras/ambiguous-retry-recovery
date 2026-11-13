"""PROTOCOL.md §7 (and §10) predictions as executable checks, written before any matrix run.

Original §7 predictions are evaluated on their original scope (S00-S12; policies A, B, C, D, D+I).
Predictions added by the pre-freeze design update are evaluated on the scope they state. Nothing
here is adjusted after the run; mismatches are explained in notes/prediction_explanations.md.
"""
from .metrics import op_label
from .scenarios import ORIGINAL_CORE_IDS

NEW = ("S13", "S14", "S15")


def _fmtset(s):
    return "{" + ", ".join(sorted(s)) + "}" if s else "none"


class Checker(object):
    def __init__(self, rows, cell_index):
        self.rows = rows
        self.cells = cell_index
        self.idx = {(r["contract"], r["policy"], op_label(r)): r for r in rows}
        self.out = []

    def r(self, c, p, label):
        return self.idx[(c, p, label)]

    def dups(self, c, p, scope=None):
        return set(op_label(r) for r in self.rows if r["contract"] == c and r["policy"] == p and r["duplicate"]
                   and (scope is None or r["scenario"] in scope))

    def unres(self, c, p, scope=None):
        return set(op_label(r) for r in self.rows if r["contract"] == c and r["policy"] == p and r["unresolved"]
                   and (scope is None or r["scenario"] in scope))

    def add(self, pid, source, statement, predicted, observed, ok):
        self.out.append({"id": pid, "source": source, "statement": statement, "predicted": predicted,
                         "observed": observed, "verdict": "MATCH" if ok else "MISMATCH"})

    def set_eq(self, pid, source, statement, predicted, observed):
        predicted, observed = set(predicted), set(observed)
        extra, missing = observed - predicted, predicted - observed
        obs = _fmtset(observed)
        if extra or missing:
            obs += " (extra: %s; missing: %s)" % (_fmtset(extra), _fmtset(missing))
        self.add(pid, source, statement, _fmtset(predicted), obs, not extra and not missing)

    def once_complete(self, c, p, label):
        r = self.r(c, p, label)
        return r["effects_F"] == 1 and r["belief_H"] == "complete", "%s: effects F=%d, belief %s" % (
            label, r["effects_F"], r["belief_H"])


def check_all(rows, cell_index):
    k = Checker(rows, cell_index)
    O = set(ORIGINAL_CORE_IDS)
    src = "§7 original (scope S00-S12)"

    # ---------------- original §7, contract 1
    k.set_eq("P01", src, "C1 A duplicates", ["S03", "S04", "S05", "S06", "S07", "S08", "S10", "S11/op-1", "S12"],
             k.dups(1, "A", O))
    k.set_eq("P02", src, "C1 A unresolved: none", [], k.unres(1, "A", O))
    ok, obs = k.once_complete(1, "A", "S09")
    k.add("P03", src, "C1 A completes S09 exactly once", "S09: effects 1, complete", obs, ok)
    k.set_eq("P04", src, "C1 B duplicates", ["S04", "S05", "S07", "S08", "S10", "S11/op-1"], k.dups(1, "B", O))
    k.set_eq("P05", src, "C1 B unresolved: none", [], k.unres(1, "B", O))
    obs = ["%s: %s" % (s, "duplicate" if k.r(1, "B", s)["duplicate"] else "no duplicate") for s in ("S03", "S06", "S12")]
    k.add("P06", src, "C1 B status check prevents duplicates in S03, S06, S12", "no duplicate in each", "; ".join(obs),
          not any(k.r(1, "B", s)["duplicate"] for s in ("S03", "S06", "S12")))
    k.set_eq("P07", src, "C1 C duplicates: none", [], k.dups(1, "C", O))
    k.set_eq("P08", src, "C1 C unresolved", ["S08", "S09", "S10", "S11/op-1"], k.unres(1, "C", O))
    obs = ["%s: effects F=%d, belief %s" % (s, k.r(1, "C", s)["effects_F"], k.r(1, "C", s)["belief_H"]) for s in ("S02", "S06")]
    k.add("P09", src, "C1 C: zero effects with a correct `failed` belief in S02 and S06", "0 effects, failed (both)",
          "; ".join(obs), all(k.r(1, "C", s)["effects_F"] == 0 and k.r(1, "C", s)["belief_H"] == "failed" for s in ("S02", "S06")))
    k.set_eq("P10", src, "C1 D duplicates: none", [], k.dups(1, "D", O))
    k.set_eq("P11", src, "C1 D unresolved", ["S08", "S09", "S10", "S11/op-1"], k.unres(1, "D", O))
    res = [k.once_complete(1, "D", s) for s in ("S02", "S06")]
    k.add("P12", src, "C1 D completes S02 and S06 exactly once", "effects 1, complete (both)",
          "; ".join(x[1] for x in res), all(x[0] for x in res))

    # ---------------- original §7, contract 2
    dup2 = set("%s:%s" % (p, s) for p in ("A", "B", "C", "D", "D+I") for s in k.dups(2, p, O))
    k.set_eq("P13", src, "C2 no policy (A, B, C, D, D+I) has duplicates", [], dup2)
    obs = ["%s: belief %s, effects F=%d" % (p, k.r(2, p, "S10")["belief_H"], k.r(2, p, "S10")["effects_F"]) for p in ("A", "B")]
    k.add("P14", src, "C2 A and B in S10 end `failed` while an effect commits later (false failure)",
          "failed, effects F >= 1 (both)", "; ".join(obs), all(k.r(2, p, "S10")["false_failure"] for p in ("A", "B")))
    res = [k.once_complete(2, "D+I", s) for s in ("S08", "S09", "S11/op-1")]
    k.add("P15a", src, "C2 D+I completes S08, S09, S11/op-1 exactly once", "effects 1, complete (each)",
          "; ".join(x[1] for x in res), all(x[0] for x in res))
    k.set_eq("P15b", src, "C2 D+I leaves only S10 unresolved", ["S10"], k.unres(2, "D+I", O))

    # ---------------- §10 worked timeline (S04, contract 1 unless stated)
    s10 = "§10 worked timeline"
    a = k.r(1, "A", "S04")
    k.add("P16", s10, "C1 A retries at t = 5; second effect at t = 7 (duplicate)", "a2@5, a2 commits at 7",
          "dispatches %s; commits %s" % (a["dispatch_times"], a["commits"]),
          "a2@5" in a["dispatch_times"].split() and "a2@7" in a["commits"].split() and a["duplicate"])
    b = k.r(1, "B", "S04")
    k.add("P17", s10, "C1 B believes `not_found` and retries at t = 6 (duplicate)", "a2@6, duplicate",
          "dispatches %s; commits %s" % (b["dispatch_times"], b["commits"]),
          "a2@6" in b["dispatch_times"].split() and b["duplicate"])
    obs = ["%s: ttc %s, effects F=%d" % (p, k.r(1, p, "S04")["ttc"], k.r(1, p, "S04")["effects_F"]) for p in ("C", "D")]
    k.add("P18", s10, "C1 C and D keep polling and complete at t = 20 via the receipt, exactly once",
          "complete at 20, 1 effect (both)", "; ".join(obs),
          all(k.r(1, p, "S04")["ttc"] == 20 and k.r(1, p, "S04")["exactly_once"] for p in ("C", "D")))
    replay = []
    for p in ("A", "B"):
        sim = k.cells[(2, p, "S04")]
        replay.append(any(e["event"] == "dedup_replay" for e in sim.trace))
    obs = ["%s: retries %d, effects F=%d, replay seen %s" % (p, k.r(2, p, "S04")["retries"], k.r(2, p, "S04")["effects_F"], rp)
           for p, rp in zip(("A", "B"), replay)]
    k.add("P19", s10, "C2 A's and B's retries in S04 are answered with a replay of e1; no duplicate",
          "replay, 1 effect (both)", "; ".join(obs),
          all(replay) and all(k.r(2, p, "S04")["effects_F"] == 1 for p in ("A", "B")))

    # ---------------- design update, contract 1
    du = "§7 design update"
    k.set_eq("U01", du, "C1 Bw duplicates (all scenarios)", ["S08", "S10", "S11/op-1"], k.dups(1, "Bw"))
    k.set_eq("U02", du, "C1 A duplicates in S13-S15", NEW, k.dups(1, "A", NEW))
    k.set_eq("U03a", du, "C1 B duplicates in S13-S15", ["S13", "S15"], k.dups(1, "B", NEW))
    b14 = k.r(1, "B", "S14")
    k.add("U03b", du, "C1 B: S14 once, via its status read", "1 effect, status read, no retry",
          "effects F=%d, status reads %d, retries %d, belief %s" % (b14["effects_F"], b14["status_reads"], b14["retries"],
                                                                     b14["belief_H"]),
          b14["effects_F"] == 1 and b14["status_reads"] >= 1 and b14["retries"] == 0)
    res = [k.once_complete(1, "Bw", s) for s in NEW]
    k.add("U04a", du, "C1 Bw: S13, S14, S15 exactly once", "effects 1, complete (each)", "; ".join(x[1] for x in res),
          all(x[0] for x in res))
    bw15 = k.cells[(1, "Bw", "S15")]
    reads = [e["t"] for e in bw15.trace if e["event"] == "status_read"]
    first = bw15.clients["op-1"].first_complete_t
    k.add("U04b", du, "C1 Bw in S15 sees `committed` at t = 14 before its read", "complete at 14, read after 14",
          "complete at %s; status reads at %s" % (first, reads or "none (wait ended after completion)"),
          first == 14 and all(t > 14 for t in reads))
    k.set_eq("U05a", du, "C1 C duplicates in S13-S15: none", [], k.dups(1, "C", NEW))
    c15 = k.r(1, "C", "S15")
    res = [k.r(1, "C", s)["effects_F"] == 1 for s in NEW]
    k.add("U05b", du, "C1 C: S13, S14, S15 once; S15 ends `complete` with one conflict", "1 effect each; S15 complete, 1 conflict",
          "effects F %s; S15 belief %s, conflicts %d" % ([k.r(1, "C", s)["effects_F"] for s in NEW], c15["belief_H"], c15["conflicts"]),
          all(res) and c15["belief_H"] == "complete" and c15["conflicts"] == 1)
    k.set_eq("U06a", du, "C1 D duplicates in S13-S15", ["S15"], k.dups(1, "D", NEW))
    d15 = k.r(1, "D", "S15")
    k.add("U06b", du, "C1 D: S15 duplicate is contract-caused, with a conflict recorded", "contract-caused, conflict >= 1",
          "cause %s, conflicts %d" % (d15["dup_cause"] or "n/a", d15["conflicts"]),
          d15["dup_cause"] == "contract" and d15["conflicts"] >= 1)
    k.add("U06c", du, "C1 D: S13 and S14 once", "1 effect each",
          "effects F %s" % [k.r(1, "D", s)["effects_F"] for s in ("S13", "S14")],
          all(k.r(1, "D", s)["effects_F"] == 1 for s in ("S13", "S14")))
    k.set_eq("U07", du, "C1 ORACLE-S duplicates (all scenarios)", ["S05", "S10", "S13", "S15"], k.dups(1, "ORACLE-S"))
    k.set_eq("U08a", du, "C1 ORACLE-O duplicates: none", [], k.dups(1, "ORACLE-O"))
    o10 = k.r(1, "ORACLE-O", "S10")
    k.add("U08b", du, "C1 ORACLE-O: S10 unresolved at H", "S10 unresolved",
          "S10 belief %s; all unresolved: %s" % (o10["belief_H"], _fmtset(k.unres(1, "ORACLE-O"))), o10["unresolved"])

    # ---------------- design update, contract 2
    pols = [p for p in ("A", "B", "Bw", "C", "D", "D+I", "ORACLE-S", "ORACLE-O")]
    dup2 = set("%s:%s" % (p, s) for p in pols for s in k.dups(2, p))
    k.set_eq("U09a", du, "C2 duplicates only in S15 for A, B, D and ORACLE-S (all non-ablation policies and references)",
             ["A:S15", "B:S15", "D:S15", "ORACLE-S:S15"], dup2)
    k.set_eq("U09b", du, "C2 A-fk has the same duplicates as A under contract 1", k.dups(1, "A"), k.dups(2, "A-fk"))
    di = k.r(2, "D+I", "S13")
    sim = k.cells[(2, "D+I", "S13")]
    saw_ip = any(e["event"] == "observe" and e["details"]["obs"].get("kind") == "in_progress" for e in sim.trace)
    k.add("U10", du, "C2 D+I completes S13 once: in_progress, then `committed` at t = 10",
          "in_progress seen; complete at 10; 1 effect",
          "in_progress seen %s; complete at %s; effects F=%d" % (saw_ip, di["ttc"], di["effects_F"]),
          saw_ip and di["ttc"] == 10 and di["effects_F"] == 1)

    # ---------------- documented tie (design update §7)
    sim = k.cells[(1, "Bw", "S04")]
    at20 = [(e["phase"], e["details"]["obs"]["type"]) for e in sim.trace
            if e["t"] == 20 and e["event"] == "observe" and e["details"]["obs"]["type"] in ("webhook", "timer")]
    reads20 = [e for e in sim.trace if e["t"] >= 20 and e["event"] == "status_read"]
    k.add("T01", "design update tie note", "S04 under Bw: `committed` webhook and wait timer both at t = 20; webhook first",
          "webhook (delivery) before timer; no read",
          "order at t = 20: %s; status reads at t >= 20: %d" % (at20, len(reads20)),
          [x[1] for x in at20] == ["webhook", "timer"] and not reads20)
    return k.out


def predictions_md(checks, notes_text, base_verdicts=()):
    n_ok = sum(1 for c in checks if c["verdict"] == "MATCH")
    lines = ["# Predictions check", "",
             "PROTOCOL.md §7 (original and design-update additions) and the §10 worked timeline, checked against "
             "the frozen run. Predictions were written by hand before any matrix run and are not adjusted. "
             "Original §7 predictions use their original scope (S00-S12; policies A, B, C, D, D+I).", "",
             "**%d of %d predictions match.**" % (n_ok, len(checks)), "",
             "| id | source | prediction | predicted | observed | verdict |", "|---|---|---|---|---|---|"]
    for c in checks:
        lines.append("| %s | %s | %s | %s | %s | **%s** |" % (c["id"], c["source"], c["statement"], c["predicted"],
                                                              c["observed"], c["verdict"]))
    for base_label, verdicts in base_verdicts:
        if not verdicts:
            continue
        changed = ["%s (%s -> %s)" % (c["id"], verdicts.get(c["id"], "absent"), c["verdict"])
                   for c in checks if verdicts.get(c["id"]) != c["verdict"]]
        lines += ["", "## Match-status changes since %s" % base_label, "",
                  ("Changed: " + "; ".join(changed) + ".") if changed else
                  "None: every prediction has the same verdict as in the %s run (%d predictions compared)."
                  % (base_label, len(checks))]
    lines += ["", "## Explanations of mismatches", ""]
    mism = [c["id"] for c in checks if c["verdict"] != "MATCH"]
    if not mism:
        lines.append("None.")
    elif notes_text:
        lines.append(notes_text.strip())
    else:
        lines.append("Mismatches %s have no written explanation yet (notes/prediction_explanations.md is absent)."
                     % ", ".join(mism))
    return "\n".join(lines) + "\n"
