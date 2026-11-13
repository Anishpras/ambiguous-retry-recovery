# Predictions check

PROTOCOL.md §7 (original and design-update additions) and the §10 worked timeline, checked against the frozen run. Predictions were written by hand before any matrix run and are not adjusted. Original §7 predictions use their original scope (S00-S12; policies A, B, C, D, D+I).

**37 of 38 predictions match.**

| id | source | prediction | predicted | observed | verdict |
|---|---|---|---|---|---|
| P01 | §7 original (scope S00-S12) | C1 A duplicates | {S03, S04, S05, S06, S07, S08, S10, S11/op-1, S12} | {S03, S04, S05, S06, S07, S08, S10, S11/op-1, S12} | **MATCH** |
| P02 | §7 original (scope S00-S12) | C1 A unresolved: none | none | none | **MATCH** |
| P03 | §7 original (scope S00-S12) | C1 A completes S09 exactly once | S09: effects 1, complete | S09: effects F=1, belief complete | **MATCH** |
| P04 | §7 original (scope S00-S12) | C1 B duplicates | {S04, S05, S07, S08, S10, S11/op-1} | {S04, S05, S07, S08, S10, S11/op-1} | **MATCH** |
| P05 | §7 original (scope S00-S12) | C1 B unresolved: none | none | none | **MATCH** |
| P06 | §7 original (scope S00-S12) | C1 B status check prevents duplicates in S03, S06, S12 | no duplicate in each | S03: no duplicate; S06: no duplicate; S12: no duplicate | **MATCH** |
| P07 | §7 original (scope S00-S12) | C1 C duplicates: none | none | none | **MATCH** |
| P08 | §7 original (scope S00-S12) | C1 C unresolved | {S08, S09, S10, S11/op-1} | {S08, S09, S10, S11/op-1} | **MATCH** |
| P09 | §7 original (scope S00-S12) | C1 C: zero effects with a correct `failed` belief in S02 and S06 | 0 effects, failed (both) | S02: effects F=0, belief failed; S06: effects F=0, belief failed | **MATCH** |
| P10 | §7 original (scope S00-S12) | C1 D duplicates: none | none | none | **MATCH** |
| P11 | §7 original (scope S00-S12) | C1 D unresolved | {S08, S09, S10, S11/op-1} | {S08, S09, S10, S11/op-1} | **MATCH** |
| P12 | §7 original (scope S00-S12) | C1 D completes S02 and S06 exactly once | effects 1, complete (both) | S02: effects F=1, belief complete; S06: effects F=1, belief complete | **MATCH** |
| P13 | §7 original (scope S00-S12) | C2 no policy (A, B, C, D, D+I) has duplicates | none | none | **MATCH** |
| P14 | §7 original (scope S00-S12) | C2 A and B in S10 end `failed` while an effect commits later (false failure) | failed, effects F >= 1 (both) | A: belief failed, effects F=1; B: belief failed, effects F=1 | **MATCH** |
| P15a | §7 original (scope S00-S12) | C2 D+I completes S08, S09, S11/op-1 exactly once | effects 1, complete (each) | S08: effects F=1, belief complete; S09: effects F=1, belief complete; S11/op-1: effects F=1, belief complete | **MATCH** |
| P15b | §7 original (scope S00-S12) | C2 D+I leaves only S10 unresolved | {S10} | {S10} | **MATCH** |
| P16 | §10 worked timeline | C1 A retries at t = 5; second effect at t = 7 (duplicate) | a2@5, a2 commits at 7 | dispatches a1@0 a2@5; commits a1@2 a2@7 | **MATCH** |
| P17 | §10 worked timeline | C1 B believes `not_found` and retries at t = 6 (duplicate) | a2@6, duplicate | dispatches a1@0 a2@6; commits a1@2 a2@8 | **MATCH** |
| P18 | §10 worked timeline | C1 C and D keep polling and complete at t = 20 via the receipt, exactly once | complete at 20, 1 effect (both) | C: ttc 20, effects F=1; D: ttc 20, effects F=1 | **MATCH** |
| P19 | §10 worked timeline | C2 A's and B's retries in S04 are answered with a replay of e1; no duplicate | replay, 1 effect (both) | A: retries 1, effects F=1, replay seen True; B: retries 1, effects F=1, replay seen True | **MATCH** |
| U01 | §7 design update | C1 Bw duplicates (all scenarios) | {S08, S10, S11/op-1} | {S08, S10, S11/op-1} | **MATCH** |
| U02 | §7 design update | C1 A duplicates in S13-S15 | {S13, S14, S15} | {S13, S14, S15} | **MATCH** |
| U03a | §7 design update | C1 B duplicates in S13-S15 | {S13, S15} | {S13, S15} | **MATCH** |
| U03b | §7 design update | C1 B: S14 once, via its status read | 1 effect, status read, no retry | effects F=1, status reads 1, retries 0, belief complete | **MATCH** |
| U04a | §7 design update | C1 Bw: S13, S14, S15 exactly once | effects 1, complete (each) | S13: effects F=1, belief complete; S14: effects F=1, belief complete; S15: effects F=1, belief complete | **MATCH** |
| U04b | §7 design update | C1 Bw in S15 sees `committed` at t = 14 before its read | complete at 14, read after 14 | complete at 14; status reads at none (wait ended after completion) | **MATCH** |
| U05a | §7 design update | C1 C duplicates in S13-S15: none | none | none | **MATCH** |
| U05b | §7 design update | C1 C: S13, S14, S15 once; S15 ends `complete` with one conflict | 1 effect each; S15 complete, 1 conflict | effects F [1, 1, 1]; S15 belief complete, conflicts 1 | **MATCH** |
| U06a | §7 design update | C1 D duplicates in S13-S15 | {S15} | {S15} | **MATCH** |
| U06b | §7 design update | C1 D: S15 duplicate is contract-caused, with a conflict recorded | contract-caused, conflict >= 1 | cause contract, conflicts 1 | **MATCH** |
| U06c | §7 design update | C1 D: S13 and S14 once | 1 effect each | effects F [1, 1] | **MATCH** |
| U07 | §7 design update | C1 ORACLE-S duplicates (all scenarios) | {S05, S10, S13, S15} | {S05, S10, S13, S15} | **MATCH** |
| U08a | §7 design update | C1 ORACLE-O duplicates: none | none | none | **MATCH** |
| U08b | §7 design update | C1 ORACLE-O: S10 unresolved at H | S10 unresolved | S10 belief unresolved; all unresolved: {S10} | **MATCH** |
| U09a | §7 design update | C2 duplicates only in S15 for A, B, D and ORACLE-S (all non-ablation policies and references) | {A:S15, B:S15, D:S15, ORACLE-S:S15} | {A:S15, B:S15, D+I:S15, D:S15, ORACLE-S:S15} (extra: {D+I:S15}; missing: none) | **MISMATCH** |
| U09b | §7 design update | C2 A-fk has the same duplicates as A under contract 1 | {S03, S04, S05, S06, S07, S08, S10, S11/op-1, S12, S13, S14, S15} | {S03, S04, S05, S06, S07, S08, S10, S11/op-1, S12, S13, S14, S15} | **MATCH** |
| U10 | §7 design update | C2 D+I completes S13 once: in_progress, then `committed` at t = 10 | in_progress seen; complete at 10; 1 effect | in_progress seen True; complete at 10; effects F=1 | **MATCH** |
| T01 | design update tie note | S04 under Bw: `committed` webhook and wait timer both at t = 20; webhook first | webhook (delivery) before timer; no read | order at t = 20: [(2, 'webhook'), (3, 'timer')]; status reads at t >= 20: 0 | **MATCH** |

## Explanations of mismatches

Written by the implementer after the v1.0 collection run. This file is interpretation, not code or fixtures, so it is not frozen; `run_sim.py` copies it into `results/predictions_check.md`.

**U09a: D+I duplicates in S15 under contract 2. Cause: a prediction error, not an implementation bug.**

- **The prediction.** The design-update prediction lists the contract-2 duplicates as "only in S15 (A, B, D and ORACLE-S)". It does not mention D+I.
- **Why D+I behaves like D here.** D+I is D plus one idempotent resend, so it inherits D's retry rule. In S15, the `aborted` webhook for a1 arrives at t = 4. It is an authoritative terminal negative, and it covers the only dispatched attempt. D's rule therefore dispatches a2 at t = 4, under D+I exactly as under D.
- **Why that retry executes.** a1's abort at t = 3 released the contract-2 dedup record. a2 therefore executes and commits at t = 6.
- **Where the duplicate comes from.** The provider then violates its guarantee and commits a1 at t = 12, giving two effects. The duplicate is contract-caused (a2 was a justified retry), and D+I records the conflict for a1 when the `committed` webhook arrives at t = 14.
- **Why D+I's own resend is not involved.** D+I's resend fires at t = 6, on the first status reply after the t = 5 timeout. That reply's replica was cut off at t = 4, so it shows only a1 as terminal; a2 is still in flight and the operation is unresolved. The resend a3 is answered with a replay of a2's effect, so it adds no effect.
- **Conclusion.** Both D and D+I duplicate in S15 for the same reason. The trace is in `results/traces/contract2/D+I/S15.jsonl`; `python3 run_sim.py --show 2 D+I S15` prints it.
- **Disclosure.** The implementer noticed this omission by hand while applying the design update, before the freeze. As instructed, the prediction was not adjusted.

Every other prediction matches. Three of the matches depend on implementation clarifications:

- **U04b and T01 (Bw).** These rely on clarification C15: Bw issues no status read when the belief is already `complete` at the end of its wait. In S15, Bw becomes `complete` at t = 14 and its wait (started at t = 4) ends at t = 19, so no read is issued at all. The prediction text "before its read" assumed a read would follow. That detail differs from the expectation, but the predicted outcome (exactly once, `complete` at t = 14) holds.
- **P06, P16 and P17 (A and B).** These rely on clarification C9, the literal reading of A and B: failure signals are acted on whatever the current belief.
  - In the core matrix this reading changes no outcome. A scan of the traces finds no timeout, `error`, `in_progress`, `rejected` or `not_found` reaching A, B or Bw while their belief is `complete`.
  - A's two dispatches after completion (S06 at t = 30, S14 at t = 12) are triggered by failure-named webhooks. Those retries are behaviour that §3 specifies ("last terminal-looking event wins"), not a consequence of C9.
  - The reading does matter in the grids: under contract 1, 24 of A's and 26 of B's grid duplicates follow a retry made after a webhook had already confirmed completion. See `results/grid_tables.md` and the `retries_after_complete` column.
