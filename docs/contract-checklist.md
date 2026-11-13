# Provider contract checklist

Answer these questions about the provider your agent calls. Each answer selects a scenario field or a named option (`docs/scenario-format.md`). Encode your provider as a scenario, then run every policy under it:

```
python3 run_sim.py explore --scenario my.json --contract N --policy P
```

The questions are the ones whose answers changed results in the sensitivity analysis (`results/exploratory/sensitivity.md`).

| # | Question | Where it goes | Why it matters (measured) |
|---|---|---|---|
| 1 | Is there an idempotency (dedup) key, and does it require an identical payload? | `--contract 2` (keyed on op_key plus payload hash) or `--contract 1` (none) | Without a key, immediate retry duplicated 12 of 17 core operations and 90 of 120 grid schedules (A, contract 1). With a stable key, policy-caused duplicates disappear. A fresh key per attempt brings them all back (A-fk). |
| 2 | When is the key's record created: when the request is accepted, or only on commit? | option `dedup_record_at`: `acceptance` or `commit` | A record created at commit lets a retry execute while the first attempt is still running (mutation test M3: S05 duplicates under contract 2). |
| 3 | After a failed execution, is the key released, or is the failure replayed to later requests? | option `abort_record`: `release` or `replay_failure` | Under `release`, a provider that breaks its terminal-negative guarantee (S15) causes duplicates even under contract 2. Under `replay_failure` those disappear, but a legitimately failed operation can never be retried with the same key: D and D+I end `failed` in S02 and S06. |
| 4 | Does the status API show work that is accepted but not finished? | option `status_lists_pending` | With pending visibility and a check-then-retry client that re-reads instead of retrying, B's contract-1 duplicates fell from 8 to 5 (core) and from 60 to 40 (grid). |
| 5 | Is there a bound on how stale a status read can be? | `status_lag`: an integer, or `"never"` | The bound decides whether a single stale read misleads a check-then-retry client (in grid G1, B duplicates when L ≥ 4 and the receipt is delayed by W ≥ 8). It also sets the wait a wait-then-verify client needs (`docs/decision-table.md`, row 2). |
| 6 | Which webhook events are *terminal guarantees* ("this attempt will never commit"), and which are progress? Can the provider break a guarantee? | `webhooks`, `deferred_after`, `violation_commit_after`; client option `deferred_is_progress` | Treating a progress event as failure duplicated A's work in S06 and S14. For a monotone reconciler, receipt order and duplication are irrelevant (`docs/monotone-evidence.md`). A broken guarantee (S15) defeats every policy that retries on terminal negatives. |
| 7 | Is there a bound on in-flight time (arrival plus execution)? | `arrive`, `commit_after`; option `horizon` | Without a bound, a lost request is indistinguishable from a slow commit (S08 and S09). C and D leave both unresolved. A bound E_max is what makes wait-then-verify safe (τ ≥ E_max + L_max − T). |
| 8 | Is the dedup window longer than the longest retry sequence? | option `dedup_window` | A window shorter than the time from first dispatch to last retry turns contract 2 back into contract 1 for those retries. Not exercised by the frozen study; set the option to test it. |
| 9 | Do faults persist across retries (a failing dependency, an outage)? | option `retry_fault: copy_first` | Under persistent faults, A and B gain false failures and triple effects. D+I's deduplicated resends can become impossible to close (`results/exploratory/persistent_faults.md`). |
| 10 | Can your client remember its attempt IDs across a restart? | not modelled | C, D and D+I credit only evidence for attempts they dispatched. A restarted client that lost its attempt IDs cannot correlate anything (review item 6). |
