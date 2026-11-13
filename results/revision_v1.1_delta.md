# Revision deltas

Every value that changed between successive frozen runs. Baseline files are byte-for-byte copies of committed results (`git show <commit>:results/<file>`) kept in `baselines/<label>/` and frozen.

## v1.0 -> v1.1

Old: committed v1.0 results (git 924aef2, `baselines/v1.0/`). New: committed v1.1 results (git 622e1f1, `baselines/v1.1/`). Rows are keyed as shown; a cell reads `field: old -> new`. Unchanged rows are omitted.

| file compared | old sha256 |
|---|---|
| summary.csv | 970618fad41f069ebcfe8a3904cce0da7520a9a59853a7182086d961722b9a18 |
| by_policy.csv | 9a2d4aa0ed065677836671b79c4a68156ce7b0ddd07a07acf9b7d352e543170c |
| by_family.csv | 97cf2359067cc8012907647b9cfdff37218509a2a45f0ded2c00c935dd1b7597 |
| grid.csv | 5df1784205b2b27a0b9762182e012efc58084553f2fa45937ca8b5b62cb896cf |

### Core matrix, per operation (`summary.csv`): 0 of 289 rows changed

No value changed.

### Core matrix, per contract x policy (`by_policy.csv`): 0 of 34 rows changed

No value changed.

### Core matrix, per contract x policy x family (`by_family.csv`): 0 of 153 rows changed

No value changed.

### Secondary grid, per schedule (`grid.csv`): 120 of 2040 rows changed

| grid | schedule | contract | policy | changes |
|---|---|---|---|---|
| G1 | G1_L0_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L0_W1 | 1 | B | status_reads: 1 -> 0 |
| G1 | G1_L0_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L0_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L0_W1 | 2 | B | status_reads: 1 -> 0 |
| G1 | G1_L0_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L0_W2 | 1 | B | status_reads: 1 -> 0 |
| G1 | G1_L0_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L0_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L0_W2 | 2 | B | status_reads: 1 -> 0 |
| G1 | G1_L16_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L16_W1 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L16_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L16_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L16_W1 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L16_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L16_W2 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L16_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L16_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L16_W2 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L1_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L1_W1 | 1 | B | status_reads: 1 -> 0 |
| G1 | G1_L1_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L1_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L1_W1 | 2 | B | status_reads: 1 -> 0 |
| G1 | G1_L1_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L1_W2 | 1 | B | status_reads: 1 -> 0 |
| G1 | G1_L1_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L1_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L1_W2 | 2 | B | status_reads: 1 -> 0 |
| G1 | G1_L2_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L2_W1 | 1 | B | status_reads: 1 -> 0 |
| G1 | G1_L2_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L2_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L2_W1 | 2 | B | status_reads: 1 -> 0 |
| G1 | G1_L2_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L2_W2 | 1 | B | status_reads: 1 -> 0 |
| G1 | G1_L2_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L2_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L2_W2 | 2 | B | status_reads: 1 -> 0 |
| G1 | G1_L32_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L32_W1 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L32_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L32_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L32_W1 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L32_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L32_W2 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L32_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L32_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L32_W2 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L4_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L4_W1 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L4_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L4_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L4_W1 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L4_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L4_W2 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L4_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L4_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L4_W2 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L64_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L64_W1 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L64_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L64_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L64_W1 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L64_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L64_W2 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L64_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L64_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L64_W2 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L8_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L8_W1 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L8_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L8_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L8_W1 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L8_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L8_W2 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L8_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_L8_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_L8_W2 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_Lnever_W1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_Lnever_W1 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_Lnever_W1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_Lnever_W1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_Lnever_W1 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_Lnever_W2 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_Lnever_W2 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_Lnever_W2 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G1 | G1_Lnever_W2 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G1 | G1_Lnever_W2 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G2 | G2_E1_L0 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L0 | 1 | B | status_reads: 1 -> 0 |
| G2 | G2_E1_L0 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G2 | G2_E1_L0 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L0 | 2 | B | status_reads: 1 -> 0 |
| G2 | G2_E1_L1 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L1 | 1 | B | status_reads: 1 -> 0 |
| G2 | G2_E1_L1 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G2 | G2_E1_L1 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L1 | 2 | B | status_reads: 1 -> 0 |
| G2 | G2_E1_L16 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L16 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G2 | G2_E1_L16 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G2 | G2_E1_L16 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L16 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G2 | G2_E1_L4 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L4 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G2 | G2_E1_L4 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G2 | G2_E1_L4 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L4 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G2 | G2_E1_L64 | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L64 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G2 | G2_E1_L64 | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G2 | G2_E1_L64 | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_L64 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G2 | G2_E1_Lnever | 1 | A | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_Lnever | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G2 | G2_E1_Lnever | 2 | A | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0 |
| G2 | G2_E1_Lnever | 2 | A-fk | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@5 -> a1@0; commits: a1@2 a2@7 -> a1@2 |
| G2 | G2_E1_Lnever | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; status_reads: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |

### Secondary grid, totals per grid x contract x policy (counts of cells; sums of retries and reads)

| grid | contract | policy | cells | changes |
|---|---|---|---|---|
| G1 | 1 | A | 72 | duplicate: 72 -> 54; certified_exactly_once: 0 -> 18; retries: 72 -> 54; retries_unjustified: 72 -> 54; retries_after_complete: 18 -> 0 |
| G1 | 1 | B | 72 | duplicate: 48 -> 36; certified_exactly_once: 24 -> 36; retries: 48 -> 36; retries_unjustified: 48 -> 36; retries_after_complete: 18 -> 6; status_reads: 72 -> 54 |
| G1 | 2 | A | 72 | retries: 72 -> 54; retries_unjustified: 72 -> 54; retries_after_complete: 18 -> 0 |
| G1 | 2 | A-fk | 72 | duplicate: 72 -> 54; certified_exactly_once: 0 -> 18; retries: 72 -> 54; retries_unjustified: 72 -> 54; retries_after_complete: 18 -> 0 |
| G1 | 2 | B | 72 | retries: 48 -> 36; retries_unjustified: 48 -> 36; retries_after_complete: 18 -> 6; status_reads: 72 -> 54 |
| G2 | 1 | A | 42 | duplicate: 42 -> 36; certified_exactly_once: 0 -> 6; retries: 42 -> 36; retries_unjustified: 42 -> 36; retries_after_complete: 6 -> 0 |
| G2 | 1 | B | 42 | duplicate: 38 -> 34; certified_exactly_once: 4 -> 8; retries: 38 -> 34; retries_unjustified: 38 -> 34; retries_after_complete: 8 -> 4; status_reads: 42 -> 36 |
| G2 | 2 | A | 42 | retries: 72 -> 66; retries_unjustified: 72 -> 66; retries_after_complete: 6 -> 0 |
| G2 | 2 | A-fk | 42 | duplicate: 42 -> 36; certified_exactly_once: 0 -> 6; retries: 42 -> 36; retries_unjustified: 42 -> 36; retries_after_complete: 6 -> 0 |
| G2 | 2 | B | 42 | retries: 62 -> 58; retries_unjustified: 62 -> 58; retries_after_complete: 8 -> 4; status_reads: 90 -> 84 |

## v1.1 -> v1.1.1

Old: committed v1.1 results (git 622e1f1, `baselines/v1.1/`). New: this run (v1.1.1). Rows are keyed as shown; a cell reads `field: old -> new`. Unchanged rows are omitted.

| file compared | old sha256 |
|---|---|
| summary.csv | 970618fad41f069ebcfe8a3904cce0da7520a9a59853a7182086d961722b9a18 |
| by_policy.csv | 9a2d4aa0ed065677836671b79c4a68156ce7b0ddd07a07acf9b7d352e543170c |
| by_family.csv | 97cf2359067cc8012907647b9cfdff37218509a2a45f0ded2c00c935dd1b7597 |
| grid.csv | 299d9013c9567b41ae11edbfdab7570f7ef60becd66c690d4b8800f321f3c268 |

### Core matrix, per operation (`summary.csv`): 0 of 289 rows changed

No value changed.

### Core matrix, per contract x policy (`by_policy.csv`): 0 of 34 rows changed

No value changed.

### Core matrix, per contract x policy x family (`by_family.csv`): 0 of 153 rows changed

No value changed.

### Secondary grid, per schedule (`grid.csv`): 20 of 2040 rows changed

| grid | schedule | contract | policy | changes |
|---|---|---|---|---|
| G1 | G1_L16_W4 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L16_W4 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L32_W4 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L32_W4 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L4_W4 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L4_W4 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L64_W4 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L64_W4 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_L8_W4 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_L8_W4 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G1 | G1_Lnever_W4 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@2 a2@8 -> a1@2 |
| G1 | G1_Lnever_W4 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G2 | G2_E3_L16 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@4 a2@8 -> a1@4 |
| G2 | G2_E3_L16 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G2 | G2_E3_L4 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@4 a2@8 -> a1@4 |
| G2 | G2_E3_L4 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G2 | G2_E3_L64 | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@4 a2@8 -> a1@4 |
| G2 | G2_E3_L64 | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |
| G2 | G2_E3_Lnever | 1 | B | effects_H: 2 -> 1; effects_F: 2 -> 1; duplicate: 1 -> 0; dup_cause: policy -> ''; certified_exactly_once: 0 -> 1; retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0; commits: a1@4 a2@8 -> a1@4 |
| G2 | G2_E3_Lnever | 2 | B | retries: 1 -> 0; retries_unjustified: 1 -> 0; retries_after_complete: 1 -> 0; dispatch_times: a1@0 a2@6 -> a1@0 |

### Secondary grid, totals per grid x contract x policy (counts of cells; sums of retries and reads)

| grid | contract | policy | cells | changes |
|---|---|---|---|---|
| G1 | 1 | B | 72 | duplicate: 36 -> 30; certified_exactly_once: 36 -> 42; retries: 36 -> 30; retries_unjustified: 36 -> 30; retries_after_complete: 6 -> 0 |
| G1 | 2 | B | 72 | retries: 36 -> 30; retries_unjustified: 36 -> 30; retries_after_complete: 6 -> 0 |
| G2 | 1 | B | 42 | duplicate: 34 -> 30; certified_exactly_once: 8 -> 12; retries: 34 -> 30; retries_unjustified: 34 -> 30; retries_after_complete: 4 -> 0 |
| G2 | 2 | B | 42 | retries: 58 -> 54; retries_unjustified: 58 -> 54; retries_after_complete: 4 -> 0 |
