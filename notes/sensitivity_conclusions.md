Written by the implementer after the v1.2 run. This is interpretation, not code or fixtures, so it is not frozen. The core counts are over 17 authored operations per contract, and the grid counts over 120 schedules. They are not rates.

**What survives every row**

- **Immediate retry without deduplication duplicates.** Under contract 1, A duplicates in at least 10 of 17 core operations in every row. The lowest are 10, when webhooks are not handled by name, and 11 under persistent faults. The lost-ack and pending cases (S03, S04, S05, S07, S08, S10, S11/op-1, S12, S13, S15) duplicate in every row.
- **A single stale read misleads.** Under contract 1, B duplicates in at least 5 of 17 core operations in every row. With pending visibility the survivors are S04, S07, S08, S11/op-1 and S15: the replica is staler than the read, or the provider violates its guarantee.
- **Stable keys remove policy-caused duplicates; fresh keys bring them back.** Under contract 2, every duplicate in every row is in S15 (the guarantee violation). A-fk reproduces A's contract-1 duplicates.
- **C and D never cause a duplicate.** They have none in any row except S15, where D's duplicate is contract-caused. This follows from the rules (`docs/monotone-evidence.md`); it is not an empirical finding.
- **S08 and S09 stay indistinguishable.** C and D are unresolved in both in every row; a longer horizon does not help when status never shows anything.
- **Receipt order and duplication are irrelevant to C and D.** The ablations change 0 of 34 core and 0 of 240 grid outcomes.

**What flips or moves**

- **B's duplicate count is a status-API choice.** With pending visibility and re-reading, it falls from 8 to 5 (core) and from 60 to 40 (grid). B and Bw then become `unresolved` in S10 rather than duplicating.
- **A's "webhook harm" is a naming choice.** S06 and S14 duplicate only because A treats a late failure-named event as current. With `deferred` as progress and failure webhooks ignored once complete, A goes from 12 to 10. B and Bw do not change: S13 is not a webhook-harm case for them.
- **Bw's count is a timing choice.**
  - Core: τ = 5 gives 7, τ = 10 gives 4, τ = 15, 20 and 30 give 3.
  - Grid: 40, 34, 27, 26 and 16 respectively.
  - Without C15 and the v1.1.1 reply guard, the core count is 5.
  - With τ = 5, Bw duplicates even under contract 2, in S15: its retry comes after the aborted record has been released.
  - The exact boundary is in `bw_boundary.md`.
- **The contract-2 false failures of A, B, Bw and ORACLE-S (S10) are a rule choice.** They become `unresolved` when `in_progress` means "wait", and disappear with H = 120.
- **"Contract 2 removes duplicates" depends on release-on-abort.** If an aborted record replays the failure, S15's contract-2 duplicates vanish for every policy. But D and D+I then lose S02 and S06: zero effects, `failed`, where they used to complete.
- **Persistent faults change who fails.**
  - A and B gain false failures and triple effects. Under contract 1, A has 4 false failures in the core and 24 in the grid; B has 3 and 14.
  - Bw becomes `unresolved` in 6 core operations.
  - D+I under contract 2 rises from 1 to 4 unresolved (core) and from 6 to 16 (grid): its deduplicated resends whose replies are lost can never be closed.
  - D and C gain no duplicates.
- **A longer horizon (H = 120)** resolves S10 for C, D and D+I, and cuts C's and D's grid unresolved from 16 to 7.

**Reading of the whole table.** The robust conclusions are the replication results (naive retry and stale single reads duplicate; stable keys fix it; fresh keys undo it; the twins are undecidable) and the structural property of monotone reconcilers. Every head-to-head count between D and a baseline moves with at least one equally reasonable rule. The baselines' counts should therefore be read as functions of the provider contract and the client's timing, not as a ranking.
