# Which recovery policy to use

Use this with the answers from `docs/contract-checklist.md`. Every row cites the measurement or the argument behind it.

**What the numbers mean.** The counts are over hand-authored cases, not rates. They show *which mechanisms* produce duplicates or unresolved operations, and where the boundaries are. The policies are defined in `PROTOCOL.md` §3, and the "core", "grid" and exploratory results are in `results/`.

| # | If your provider… | Use | Evidence |
|---|---|---|---|
| 1 | honours a stable idempotency key: record at acceptance, `in_progress` while pending, the original result replayed once committed | **D+I**: reconcile; after an ambiguous signal and one unresolving status poll, resend with the *same* key; treat `in_progress` as "wait" | Contract 2, core: 16/17 exactly once, 0 policy-caused duplicates, 1 unresolved (S10 commits after H) (`results/headline.md`). Grid: 120/120 exactly once, 6 unresolved (G2, E = 96) (`results/exploratory/sensitivity.md`, baseline row). Never rotate keys: A-fk duplicates exactly where A does under contract 1 (12/17, 90/120). |
| 1a | …but persistently loses replies | D+I, and escalate unresolved cases | Its deduplicated resends leave no provider record, so a lost reply can never be closed: PF2, PF3 and PF4 end `unresolved` under contract 2 (`results/exploratory/persistent_faults.md`, `escalation.md`). |
| 1b | …but burns a failed key (`abort_record: replay_failure`) | D+I, plus a *new* key only after an authoritative terminal negative for every attempt (a new operation, not a retry) | With replay-on-abort, D and D+I end `failed` with 0 effects in S02 and S06 (exactly once: D 15 → 14, D+I 16 → 15 under contract 2), and S15's contract-2 duplicates disappear for every policy (sensitivity row `abort_record_replays_failure`). |
| 2 | has no key, but bounds both status staleness (L_max) and in-flight time (E_max) | **Bw** (wait-then-verify) with **τ ≥ E_max + L_max − T** | Unit-step grids: Bw duplicates exactly when L ≥ τ + 4 and the receipt arrives at t ≥ τ + 7, for τ = 5 to 30 (lost ack committing at t = 2, T = 5); and exactly when E + L ≥ 20 for τ = 15 (pending). See `results/exploratory/bw_boundary.md`. A smaller τ fails: τ = 5 gives 7/17 core duplicates and 40/120 grid. |
| 3 | has no key, and its status API lists pending attempts | check-then-retry that **waits while an attempt is pending** (B with `reread_on_pending`), or row 2 | B's contract-1 duplicates fall from 8/17 to 5/17 (core) and from 60/120 to 40/120 (grid). The remaining duplicates come from replicas staler than the wait (S04, S07, S08, S11/op-1) and from S15 (sensitivity row `status_lists_pending`). |
| 4 | has no key and no bounds, but gives authoritative terminal negatives | **D**: retry only when every dispatched attempt has a terminal negative; escalate `unresolved` | 0 policy-caused duplicates by construction (`docs/monotone-evidence.md`). That is an argument, not an empirical finding. Cost: 4/17 core and 16/120 grid unresolved under contract 1. `results/exploratory/escalation.md` lists the evidence that would resolve each one. |
| 5 | sends webhooks | treat only *terminal-guarantee* events as failures, per attempt; never let a late failure event overwrite a confirmed completion; use receipts as a second evidence channel | A's duplicates in S06 and S14 disappear when `deferred` is progress and failure webhooks are ignored once complete (12 → 10). For C and D, ignoring every webhook changes no safety outcome, but raises grid unresolved from 16 to 41 and core latency in S04 and S07 from 20 or 8 ticks to 36 (`results/exploratory/ablations.md`). |
| 6 | replies `in_progress` to a duplicate request | treat it as **wait**, not failure | With `in_progress_is_wait`, the contract-2 false failures of A, B and Bw (1 core, 6 grid) become `unresolved` instead (sensitivity row `in_progress_is_wait`). |
| 7 | may violate its own terminal guarantees | no evidence-based retry is safe; prefer keys that replay failures (row 1b), or do not retry | S15: D, D+I, A, B and ORACLE-S all duplicate under contract 2 with release-on-abort (`results/headline.md`, `predictions_check.md` U09a). |
| 8 | can take longer than your agent's horizon | lengthen the horizon if you can, or escalate | H = 120 resolves S10 for C, D and D+I, and cuts C's and D's grid unresolved from 16 to 7 (sensitivity row `horizon_120`). |
| — | (any) | **avoid** immediate retry without a key, and avoid a single immediate status read | A duplicates 12/17 core and 90/120 grid under contract 1. Under persistent lost acks it commits three times and ends `failed`. B duplicates whenever the replica lags more than the commit-to-read gap (L ≥ 4 in G1) (`results/grid_tables.md`). |

**Not covered.**

- Client restarts that lose attempt IDs.
- Providers with reversible states, where receipt order would matter.
- Rate or prevalence claims of any kind.
- LLM agents.
