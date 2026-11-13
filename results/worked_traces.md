# Worked traces

Generated from the actual run traces (`results/traces/contract1/D/<scenario>.jsonl`). Columns: what the provider knows (hidden), what the client's policy sees or does, and what the private scorer records. Effect IDs are opaque HMACs. Ticks with no events are omitted.

## S04: `not_found` while an effect exists (policy D, contract 1)

Script: commit at t = 2; response lost; `committed` webhook at t = 20; L = 30 (stale `not_found` until t >= 32)

Evidence: At the t = 5 timeout the client has no evidence; status reads issued before t = 32 return non-authoritative `not_found`, and the first positive evidence is the `committed` webhook at t = 20.

| t | Provider knows | Client (policy) sees | Private scorer records |
|---|---|---|---|
| 0 | - | operation op-1 starts; dispatches **a1** | - |
| 1 | a1 arrives and is accepted | - | - |
| 2 | a1 executes and commits effect a77712c198af; emits `committed` (seq 2000) for a1 -> delivery at t = 20; (network) the `ok` response for a1 is lost | - | ledger: a77712c198af (op-1, a1) at t = 2 |
| 5 | replica as of t = -25 shows 0 record(s) -> `not_found`; truth now: effects [a1@2], pending [] | **timeout** for a1 (ambiguous); issues status read | - |
| 6 | - | status reply **`not_found`**, terminal_attempts [] | - |
| 10 | replica as of t = -20 shows 0 record(s) -> `not_found`; truth now: effects [a1@2], pending [] | timer `poll` fires; issues status read | - |
| 11 | - | status reply **`not_found`**, terminal_attempts [] | - |
| 15 | replica as of t = -15 shows 0 record(s) -> `not_found`; truth now: effects [a1@2], pending [] | timer `poll` fires; issues status read | - |
| 16 | - | status reply **`not_found`**, terminal_attempts [] | - |
| 20 | - | webhook `committed` seq 2000 for a1 (ev-e0307a811cf1); belief -> **complete**; timer `poll` fires | - |
| 60 | - | - | H reached: final belief `complete` |

**What every policy did in S04** (from the same run):

| contract | policy | dispatches | commits (t) | belief at H | effects at H / F | outcome |
|---|---|---|---|---|---|---|
| 1 | A | a1@0 a2@5 | a1@2 a2@7 | complete | 2 / 2 | duplicate (policy-caused) |
| 1 | B | a1@0 a2@6 | a1@2 a2@8 | complete | 2 / 2 | duplicate (policy-caused) |
| 1 | Bw | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 1 | C | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 1 | D | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 1 | D+I (optional) | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 1 | ORACLE-S (state-probe reference, not a ceiling) | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 1 | ORACLE-O (outcome-oracle reference) | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 2 | A | a1@0 a2@5 | a1@2 | complete | 1 / 1 | exactly once |
| 2 | B | a1@0 a2@6 | a1@2 | complete | 1 / 1 | exactly once |
| 2 | Bw | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 2 | C | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 2 | D | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 2 | D+I (optional) | a1@0 a2@6 | a1@2 | complete | 1 / 1 | exactly once |
| 2 | A-fk (ablation) | a1@0 a2@5 | a1@2 a2@7 | complete | 2 / 2 | duplicate (policy-caused) |
| 2 | ORACLE-S (state-probe reference, not a ceiling) | a1@0 | a1@2 | complete | 1 / 1 | exactly once |
| 2 | ORACLE-O (outcome-oracle reference) | a1@0 | a1@2 | complete | 1 / 1 | exactly once |

## S02: an authoritative negative enables a useful retry under D (contract 1)

Script: accepted at t = 1, aborted at t = 3; response lost; webhooks lost; L = 1 (status shows a1 terminal from t = 4)

Evidence: Until the t = 5 timeout the client sees nothing; status reads issued at t >= 4 list a1 in `terminal_attempts`, the only authoritative negative, and no response or webhook ever arrives.

| t | Provider knows | Client (policy) sees | Private scorer records |
|---|---|---|---|
| 0 | - | operation op-1 starts; dispatches **a1** | - |
| 1 | a1 arrives and is accepted | - | - |
| 3 | a1 aborts; emits `aborted` (seq 3000) for a1 -> lost; (network) the `error` response for a1 is lost | - | - |
| 5 | replica as of t = 4 shows 2 record(s) -> `not_found`; truth now: effects [], pending [] | **timeout** for a1 (ambiguous); issues status read | - |
| 6 | - | status reply **`not_found`**, terminal_attempts [a1]; dispatches **a2** (all_attempts_terminal) | - |
| 7 | a2 arrives and is accepted | - | - |
| 8 | a2 executes and commits effect 3312b063a674; emits `committed` (seq 8000) for a2 -> delivery at t = 10; sends `ok` response for a2 -> arrives t = 9 | - | ledger: 3312b063a674 (op-1, a2) at t = 8 |
| 9 | - | response `ok` for a2 (effect 3312b063a674); belief -> **complete** | - |
| 10 | - | webhook `committed` seq 8000 for a2 (ev-d426b08e10ac); timer `poll` fires | - |
| 60 | - | - | H reached: final belief `complete` |

**What every policy did in S02** (from the same run):

| contract | policy | dispatches | commits (t) | belief at H | effects at H / F | outcome |
|---|---|---|---|---|---|---|
| 1 | A | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 1 | B | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 1 | Bw | a1@0 a2@21 | a2@23 | complete | 1 / 1 | exactly once |
| 1 | C | a1@0 | none | failed | 0 / 0 | zero effects |
| 1 | D | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 1 | D+I (optional) | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 1 | ORACLE-S (state-probe reference, not a ceiling) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 1 | ORACLE-O (outcome-oracle reference) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 2 | A | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 2 | B | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 2 | Bw | a1@0 a2@21 | a2@23 | complete | 1 / 1 | exactly once |
| 2 | C | a1@0 | none | failed | 0 / 0 | zero effects |
| 2 | D | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 2 | D+I (optional) | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 2 | A-fk (ablation) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 2 | ORACLE-S (state-probe reference, not a ceiling) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 2 | ORACLE-O (outcome-oracle reference) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |

## S06: a stale `aborted` webhook arrives after a later commit (policy D, contract 1)

Script: aborted at t = 3; response lost; `aborted` webhook delayed to t = 30; L = 1. Later attempts nominal.

Evidence: Status reads issued at t >= 4 list a1 in `terminal_attempts` (authoritative negative); the matching `aborted` webhook arrives only at t = 30, after any retry, as a stale receipt.

| t | Provider knows | Client (policy) sees | Private scorer records |
|---|---|---|---|
| 0 | - | operation op-1 starts; dispatches **a1** | - |
| 1 | a1 arrives and is accepted | - | - |
| 3 | a1 aborts; emits `aborted` (seq 3000) for a1 -> delivery at t = 30; (network) the `error` response for a1 is lost | - | - |
| 5 | replica as of t = 4 shows 2 record(s) -> `not_found`; truth now: effects [], pending [] | **timeout** for a1 (ambiguous); issues status read | - |
| 6 | - | status reply **`not_found`**, terminal_attempts [a1]; dispatches **a2** (all_attempts_terminal) | - |
| 7 | a2 arrives and is accepted | - | - |
| 8 | a2 executes and commits effect 3312b063a674; emits `committed` (seq 8000) for a2 -> delivery at t = 10; sends `ok` response for a2 -> arrives t = 9 | - | ledger: 3312b063a674 (op-1, a2) at t = 8 |
| 9 | - | response `ok` for a2 (effect 3312b063a674); belief -> **complete** | - |
| 10 | - | webhook `committed` seq 8000 for a2 (ev-d426b08e10ac); timer `poll` fires | - |
| 30 | - | webhook `aborted` seq 3000 for a1 (ev-7d365e453f67) | - |
| 60 | - | - | H reached: final belief `complete` |

**What every policy did in S06** (from the same run):

| contract | policy | dispatches | commits (t) | belief at H | effects at H / F | outcome |
|---|---|---|---|---|---|---|
| 1 | A | a1@0 a2@5 a3@30 | a2@7 a3@32 | complete | 2 / 2 | duplicate (policy-caused) |
| 1 | B | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 1 | Bw | a1@0 a2@21 | a2@23 | complete | 1 / 1 | exactly once |
| 1 | C | a1@0 | none | failed | 0 / 0 | zero effects |
| 1 | D | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 1 | D+I (optional) | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 1 | ORACLE-S (state-probe reference, not a ceiling) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 1 | ORACLE-O (outcome-oracle reference) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 2 | A | a1@0 a2@5 a3@30 | a2@7 | complete | 1 / 1 | exactly once |
| 2 | B | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 2 | Bw | a1@0 a2@21 | a2@23 | complete | 1 / 1 | exactly once |
| 2 | C | a1@0 | none | failed | 0 / 0 | zero effects |
| 2 | D | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 2 | D+I (optional) | a1@0 a2@6 | a2@8 | complete | 1 / 1 | exactly once |
| 2 | A-fk (ablation) | a1@0 a2@5 a3@30 | a2@7 a3@32 | complete | 2 / 2 | duplicate (policy-caused) |
| 2 | ORACLE-S (state-probe reference, not a ceiling) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |
| 2 | ORACLE-O (outcome-oracle reference) | a1@0 a2@5 | a2@7 | complete | 1 / 1 | exactly once |

