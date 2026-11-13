# Revision deltas

Every value that changed between successive frozen runs. Baseline files are byte-for-byte copies of committed results (`git show <commit>:results/<file>`) kept in `baselines/<label>/` and frozen.

## v1.1.1 -> v1.2

Old: committed v1.1.1 results (git b95a667, `baselines/v1.1.1/`). New: this run (v1.2). Rows are keyed as shown; a cell reads `field: old -> new`. Unchanged rows are omitted.

| file compared | old sha256 |
|---|---|
| summary.csv | 970618fad41f069ebcfe8a3904cce0da7520a9a59853a7182086d961722b9a18 |
| by_policy.csv | 9a2d4aa0ed065677836671b79c4a68156ce7b0ddd07a07acf9b7d352e543170c |
| by_family.csv | 97cf2359067cc8012907647b9cfdff37218509a2a45f0ded2c00c935dd1b7597 |
| grid.csv | 62d19bf8222f4a5692900b31a4d95842bc8c36d998d517260a4ced548586ebf6 |

### Core matrix, per operation (`summary.csv`): 75 of 289 rows changed

Columns added: ttc_any_complete. Columns removed: none.

| contract | policy | scenario | op | changes |
|---|---|---|---|---|
| 1 | A | S03 | op-1 | ttc: 8 -> '' |
| 1 | A | S04 | op-1 | ttc: 8 -> '' |
| 1 | A | S05 | op-1 | ttc: 8 -> '' |
| 1 | A | S06 | op-1 | ttc: 8 -> '' |
| 1 | A | S07 | op-1 | ttc: 8 -> '' |
| 1 | A | S08 | op-1 | ttc: 8 -> '' |
| 1 | A | S10 | op-1 | ttc: 8 -> '' |
| 1 | A | S11 | op-1 | ttc: 8 -> '' |
| 1 | A | S12 | op-1 | ttc: 6 -> '' |
| 1 | A | S13 | op-1 | ttc: 6 -> '' |
| 1 | A | S14 | op-1 | ttc: 4 -> '' |
| 1 | A | S15 | op-1 | ttc: 7 -> '' |
| 1 | B | S04 | op-1 | ttc: 9 -> '' |
| 1 | B | S05 | op-1 | ttc: 9 -> '' |
| 1 | B | S07 | op-1 | ttc: 8 -> '' |
| 1 | B | S08 | op-1 | ttc: 9 -> '' |
| 1 | B | S10 | op-1 | ttc: 9 -> '' |
| 1 | B | S11 | op-1 | ttc: 9 -> '' |
| 1 | B | S13 | op-1 | ttc: 7 -> '' |
| 1 | B | S15 | op-1 | ttc: 8 -> '' |
| 1 | Bw | S08 | op-1 | ttc: 24 -> '' |
| 1 | Bw | S10 | op-1 | ttc: 24 -> '' |
| 1 | Bw | S11 | op-1 | ttc: 24 -> '' |
| 1 | D | S15 | op-1 | ttc: 7 -> '' |
| 1 | D+I | S15 | op-1 | ttc: 7 -> '' |
| 1 | ORACLE-S | S00 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S01 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S02 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S03 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S04 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S05 | op-1 | role: reference -> state-probe reference; ttc: 8 -> '' |
| 1 | ORACLE-S | S06 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S07 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S08 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S09 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S10 | op-1 | role: reference -> state-probe reference; ttc: 8 -> '' |
| 1 | ORACLE-S | S11 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S11 | op-2 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S12 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S13 | op-1 | role: reference -> state-probe reference; ttc: 5 -> '' |
| 1 | ORACLE-S | S14 | op-1 | role: reference -> state-probe reference |
| 1 | ORACLE-S | S15 | op-1 | role: reference -> state-probe reference; ttc: 7 -> '' |
| 2 | A | S15 | op-1 | ttc: 7 -> '' |
| 2 | A-fk | S03 | op-1 | ttc: 8 -> '' |
| 2 | A-fk | S04 | op-1 | ttc: 8 -> '' |
| 2 | A-fk | S05 | op-1 | ttc: 8 -> '' |
| 2 | A-fk | S06 | op-1 | ttc: 8 -> '' |
| 2 | A-fk | S07 | op-1 | ttc: 8 -> '' |
| 2 | A-fk | S08 | op-1 | ttc: 8 -> '' |
| 2 | A-fk | S10 | op-1 | ttc: 8 -> '' |
| 2 | A-fk | S11 | op-1 | ttc: 8 -> '' |
| 2 | A-fk | S12 | op-1 | ttc: 6 -> '' |
| 2 | A-fk | S13 | op-1 | ttc: 6 -> '' |
| 2 | A-fk | S14 | op-1 | ttc: 4 -> '' |
| 2 | A-fk | S15 | op-1 | ttc: 7 -> '' |
| 2 | B | S15 | op-1 | ttc: 8 -> '' |
| 2 | D | S15 | op-1 | ttc: 7 -> '' |
| 2 | D+I | S15 | op-1 | ttc: 7 -> '' |
| 2 | ORACLE-S | S00 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S01 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S02 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S03 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S04 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S05 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S06 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S07 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S08 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S09 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S10 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S11 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S11 | op-2 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S12 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S13 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S14 | op-1 | role: reference -> state-probe reference |
| 2 | ORACLE-S | S15 | op-1 | role: reference -> state-probe reference; ttc: 7 -> '' |

### Core matrix, per contract x policy (`by_policy.csv`): 18 of 34 rows changed

| scope | contract | policy | changes |
|---|---|---|---|
| S00-S12 | 1 | A | ttc_median: 8 -> 5; ttc_coverage: 14/14 -> 5/14 |
| S00-S12 | 1 | B | ttc_median: 9 -> 6; ttc_coverage: 14/14 -> 8/14 |
| S00-S12 | 1 | Bw | ttc_median: 20.5 -> 16; ttc_coverage: 14/14 -> 11/14 |
| S00-S12 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc_coverage: 14/14 -> 12/14 |
| S00-S12 | 2 | A-fk | ttc_median: 8 -> 5; ttc_coverage: 14/14 -> 5/14 |
| S00-S12 | 2 | ORACLE-S | role: reference -> state-probe reference |
| S00-S15 | 1 | A | ttc_median: 8 -> 5; ttc_coverage: 17/17 -> 5/17 |
| S00-S15 | 1 | B | ttc_median: 8 -> 6; ttc_coverage: 17/17 -> 9/17 |
| S00-S15 | 1 | Bw | ttc_median: 16 -> 12; ttc_coverage: 17/17 -> 14/17 |
| S00-S15 | 1 | D | ttc_coverage: 13/17 -> 12/17 |
| S00-S15 | 1 | D+I | ttc_coverage: 13/17 -> 12/17 |
| S00-S15 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc_coverage: 17/17 -> 13/17 |
| S00-S15 | 2 | A | ttc_coverage: 16/17 -> 15/17 |
| S00-S15 | 2 | A-fk | ttc_median: 8 -> 5; ttc_coverage: 17/17 -> 5/17 |
| S00-S15 | 2 | B | ttc_coverage: 16/17 -> 15/17 |
| S00-S15 | 2 | D | ttc_coverage: 13/17 -> 12/17 |
| S00-S15 | 2 | D+I | ttc_coverage: 16/17 -> 15/17 |
| S00-S15 | 2 | ORACLE-S | role: reference -> state-probe reference; ttc_coverage: 16/17 -> 15/17 |

### Core matrix, per contract x policy x family (`by_family.csv`): 47 of 153 rows changed

| contract | policy | family | changes |
|---|---|---|---|
| 1 | A | distinct_ops | ttc_median: 5.5 -> 3; ttc_max: 8 -> 3; ttc_coverage: 2/2 -> 1/2 |
| 1 | A | lost_ack | ttc_median: 8 -> ''; ttc_max: 8 -> ''; ttc_coverage: 2/2 -> 0/2 |
| 1 | A | lost_ack_error | ttc_median: 6 -> ''; ttc_max: 6 -> ''; ttc_coverage: 1/1 -> 0/1 |
| 1 | A | no_confirmation | ttc_coverage: 2/2 -> 1/2 |
| 1 | A | pending | ttc_median: 8 -> ''; ttc_max: 8 -> ''; ttc_coverage: 2/2 -> 0/2 |
| 1 | A | receipt_anomaly | ttc_median: 8 -> ''; ttc_max: 8 -> ''; ttc_coverage: 2/2 -> 0/2 |
| 1 | A | webhook_harm | ttc_median: 6 -> ''; ttc_max: 7 -> ''; ttc_coverage: 3/3 -> 0/3 |
| 1 | B | distinct_ops | ttc_median: 6 -> 3; ttc_max: 9 -> 3; ttc_coverage: 2/2 -> 1/2 |
| 1 | B | lost_ack | ttc_median: 7.5 -> 6; ttc_max: 9 -> 6; ttc_coverage: 2/2 -> 1/2 |
| 1 | B | no_confirmation | ttc_coverage: 2/2 -> 1/2 |
| 1 | B | pending | ttc_median: 9 -> ''; ttc_max: 9 -> ''; ttc_coverage: 2/2 -> 0/2 |
| 1 | B | receipt_anomaly | ttc_median: 8.5 -> 9; ttc_coverage: 2/2 -> 1/2 |
| 1 | B | webhook_harm | ttc_median: 7 -> 4; ttc_max: 8 -> 4; ttc_coverage: 3/3 -> 1/3 |
| 1 | Bw | distinct_ops | ttc_median: 13.5 -> 3; ttc_max: 24 -> 3; ttc_coverage: 2/2 -> 1/2 |
| 1 | Bw | no_confirmation | ttc_coverage: 2/2 -> 1/2 |
| 1 | Bw | pending | ttc_median: 20 -> 16; ttc_max: 24 -> 16; ttc_coverage: 2/2 -> 1/2 |
| 1 | D | webhook_harm | ttc_coverage: 3/3 -> 2/3 |
| 1 | D+I | webhook_harm | ttc_coverage: 3/3 -> 2/3 |
| 1 | ORACLE-S | auth_negative | role: reference -> state-probe reference |
| 1 | ORACLE-S | control | role: reference -> state-probe reference |
| 1 | ORACLE-S | distinct_ops | role: reference -> state-probe reference |
| 1 | ORACLE-S | lost_ack | role: reference -> state-probe reference |
| 1 | ORACLE-S | lost_ack_error | role: reference -> state-probe reference |
| 1 | ORACLE-S | no_confirmation | role: reference -> state-probe reference |
| 1 | ORACLE-S | pending | role: reference -> state-probe reference; ttc_median: 8 -> ''; ttc_max: 8 -> ''; ttc_coverage: 2/2 -> 0/2 |
| 1 | ORACLE-S | receipt_anomaly | role: reference -> state-probe reference |
| 1 | ORACLE-S | webhook_harm | role: reference -> state-probe reference; ttc_median: 5 -> 4; ttc_max: 7 -> 4; ttc_coverage: 3/3 -> 1/3 |
| 2 | A | webhook_harm | ttc_coverage: 3/3 -> 2/3 |
| 2 | A-fk | distinct_ops | ttc_median: 5.5 -> 3; ttc_max: 8 -> 3; ttc_coverage: 2/2 -> 1/2 |
| 2 | A-fk | lost_ack | ttc_median: 8 -> ''; ttc_max: 8 -> ''; ttc_coverage: 2/2 -> 0/2 |
| 2 | A-fk | lost_ack_error | ttc_median: 6 -> ''; ttc_max: 6 -> ''; ttc_coverage: 1/1 -> 0/1 |
| 2 | A-fk | no_confirmation | ttc_coverage: 2/2 -> 1/2 |
| 2 | A-fk | pending | ttc_median: 8 -> ''; ttc_max: 8 -> ''; ttc_coverage: 2/2 -> 0/2 |
| 2 | A-fk | receipt_anomaly | ttc_median: 8 -> ''; ttc_max: 8 -> ''; ttc_coverage: 2/2 -> 0/2 |
| 2 | A-fk | webhook_harm | ttc_median: 6 -> ''; ttc_max: 7 -> ''; ttc_coverage: 3/3 -> 0/3 |
| 2 | B | webhook_harm | ttc_median: 8 -> 7; ttc_coverage: 3/3 -> 2/3 |
| 2 | D | webhook_harm | ttc_coverage: 3/3 -> 2/3 |
| 2 | D+I | webhook_harm | ttc_coverage: 3/3 -> 2/3 |
| 2 | ORACLE-S | auth_negative | role: reference -> state-probe reference |
| 2 | ORACLE-S | control | role: reference -> state-probe reference |
| 2 | ORACLE-S | distinct_ops | role: reference -> state-probe reference |
| 2 | ORACLE-S | lost_ack | role: reference -> state-probe reference |
| 2 | ORACLE-S | lost_ack_error | role: reference -> state-probe reference |
| 2 | ORACLE-S | no_confirmation | role: reference -> state-probe reference |
| 2 | ORACLE-S | pending | role: reference -> state-probe reference |
| 2 | ORACLE-S | receipt_anomaly | role: reference -> state-probe reference |
| 2 | ORACLE-S | webhook_harm | role: reference -> state-probe reference; ttc_coverage: 3/3 -> 2/3 |

### Secondary grid, per schedule (`grid.csv`): 507 of 2040 rows changed

| grid | schedule | contract | policy | changes |
|---|---|---|---|---|
| G1 | G1_L0_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L0_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L0_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L0_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L0_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_L0_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_L0_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L0_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L0_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L0_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L0_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_L0_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L0_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L0_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L16_W16 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L16_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L16_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L16_W32 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L16_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L16_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_L16_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_L16_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L16_W64 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L16_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L16_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L16_W8 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L16_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L16_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_L16_Wlost | 1 | B | ttc: 9 -> '' |
| G1 | G1_L16_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L16_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L16_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L1_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L1_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L1_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L1_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_L1_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_L1_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L1_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L1_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L1_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L1_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_L1_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L1_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L1_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L2_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L2_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L2_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L2_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_L2_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_L2_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L2_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L2_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L2_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L2_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_L2_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L2_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L2_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L32_W16 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L32_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L32_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L32_W32 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L32_W32 | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_L32_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L32_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_L32_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_L32_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L32_W64 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L32_W64 | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_L32_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L32_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L32_W8 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L32_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L32_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_L32_Wlost | 1 | B | ttc: 9 -> '' |
| G1 | G1_L32_Wlost | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_L32_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L32_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L32_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L4_W16 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L4_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L4_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L4_W32 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L4_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L4_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_L4_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_L4_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L4_W64 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L4_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L4_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L4_W8 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L4_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L4_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_L4_Wlost | 1 | B | ttc: 9 -> '' |
| G1 | G1_L4_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L4_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L4_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L64_W16 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L64_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L64_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L64_W32 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L64_W32 | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_L64_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L64_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_L64_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_L64_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L64_W64 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L64_W64 | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_L64_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L64_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L64_W8 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L64_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L64_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_L64_Wlost | 1 | B | ttc: 9 -> '' |
| G1 | G1_L64_Wlost | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_L64_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L64_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L64_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L8_W16 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L8_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L8_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L8_W32 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L8_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L8_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_L8_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_L8_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L8_W64 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L8_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L8_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_L8_W8 | 1 | B | ttc: 9 -> '' |
| G1 | G1_L8_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L8_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_L8_Wlost | 1 | B | ttc: 9 -> '' |
| G1 | G1_L8_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_L8_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_L8_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W16 | 1 | A | ttc: 8 -> '' |
| G1 | G1_Lnever_W16 | 1 | B | ttc: 9 -> '' |
| G1 | G1_Lnever_W16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W16 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_Lnever_W16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W2 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W2 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W32 | 1 | A | ttc: 8 -> '' |
| G1 | G1_Lnever_W32 | 1 | B | ttc: 9 -> '' |
| G1 | G1_Lnever_W32 | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_Lnever_W32 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W32 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_Lnever_W32 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W4 | 1 | A | ttc: 6 -> '' |
| G1 | G1_Lnever_W4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W4 | 2 | A-fk | ttc: 6 -> '' |
| G1 | G1_Lnever_W4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W64 | 1 | A | ttc: 8 -> '' |
| G1 | G1_Lnever_W64 | 1 | B | ttc: 9 -> '' |
| G1 | G1_Lnever_W64 | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_Lnever_W64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W64 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_Lnever_W64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W8 | 1 | A | ttc: 8 -> '' |
| G1 | G1_Lnever_W8 | 1 | B | ttc: 9 -> '' |
| G1 | G1_Lnever_W8 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_W8 | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_Lnever_W8 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_Wlost | 1 | A | ttc: 8 -> '' |
| G1 | G1_Lnever_Wlost | 1 | B | ttc: 9 -> '' |
| G1 | G1_Lnever_Wlost | 1 | Bw | ttc: 24 -> '' |
| G1 | G1_Lnever_Wlost | 1 | ORACLE-S | role: reference -> state-probe reference |
| G1 | G1_Lnever_Wlost | 2 | A-fk | ttc: 8 -> '' |
| G1 | G1_Lnever_Wlost | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E12_L0 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E12_L0 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E12_L0 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E12_L0 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E12_L0 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E12_L1 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E12_L1 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E12_L1 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E12_L1 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E12_L1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E12_L16 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E12_L16 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E12_L16 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E12_L16 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E12_L16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E12_L4 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E12_L4 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E12_L4 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E12_L4 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E12_L4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E12_L64 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E12_L64 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E12_L64 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E12_L64 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E12_L64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E12_Lnever | 1 | A | ttc: 8 -> '' |
| G2 | G2_E12_Lnever | 1 | B | ttc: 9 -> '' |
| G2 | G2_E12_Lnever | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E12_Lnever | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E12_Lnever | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L0 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L0 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_L64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_Lnever | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E1_Lnever | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E24_L0 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E24_L0 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E24_L0 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E24_L0 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E24_L0 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E24_L0 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E24_L1 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E24_L1 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E24_L1 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E24_L1 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E24_L1 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E24_L1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E24_L16 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E24_L16 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E24_L16 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E24_L16 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E24_L16 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E24_L16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E24_L4 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E24_L4 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E24_L4 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E24_L4 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E24_L4 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E24_L4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E24_L64 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E24_L64 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E24_L64 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E24_L64 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E24_L64 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E24_L64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E24_Lnever | 1 | A | ttc: 8 -> '' |
| G2 | G2_E24_Lnever | 1 | B | ttc: 9 -> '' |
| G2 | G2_E24_Lnever | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E24_Lnever | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E24_Lnever | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E24_Lnever | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L0 | 1 | A | ttc: 6 -> '' |
| G2 | G2_E3_L0 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L0 | 2 | A-fk | ttc: 6 -> '' |
| G2 | G2_E3_L0 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L1 | 1 | A | ttc: 6 -> '' |
| G2 | G2_E3_L1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L1 | 2 | A-fk | ttc: 6 -> '' |
| G2 | G2_E3_L1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L16 | 1 | A | ttc: 6 -> '' |
| G2 | G2_E3_L16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L16 | 2 | A-fk | ttc: 6 -> '' |
| G2 | G2_E3_L16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L4 | 1 | A | ttc: 6 -> '' |
| G2 | G2_E3_L4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L4 | 2 | A-fk | ttc: 6 -> '' |
| G2 | G2_E3_L4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L64 | 1 | A | ttc: 6 -> '' |
| G2 | G2_E3_L64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_L64 | 2 | A-fk | ttc: 6 -> '' |
| G2 | G2_E3_L64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_Lnever | 1 | A | ttc: 6 -> '' |
| G2 | G2_E3_Lnever | 1 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E3_Lnever | 2 | A-fk | ttc: 6 -> '' |
| G2 | G2_E3_Lnever | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E48_L0 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E48_L0 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E48_L0 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E48_L0 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E48_L0 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E48_L0 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E48_L1 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E48_L1 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E48_L1 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E48_L1 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E48_L1 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E48_L1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E48_L16 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E48_L16 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E48_L16 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E48_L16 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E48_L16 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E48_L16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E48_L4 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E48_L4 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E48_L4 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E48_L4 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E48_L4 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E48_L4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E48_L64 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E48_L64 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E48_L64 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E48_L64 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E48_L64 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E48_L64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E48_Lnever | 1 | A | ttc: 8 -> '' |
| G2 | G2_E48_Lnever | 1 | B | ttc: 9 -> '' |
| G2 | G2_E48_Lnever | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E48_Lnever | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E48_Lnever | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E48_Lnever | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E6_L0 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E6_L0 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E6_L0 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E6_L0 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E6_L0 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E6_L1 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E6_L1 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E6_L1 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E6_L1 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E6_L1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E6_L16 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E6_L16 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E6_L16 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E6_L16 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E6_L16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E6_L4 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E6_L4 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E6_L4 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E6_L4 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E6_L4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E6_L64 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E6_L64 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E6_L64 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E6_L64 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E6_L64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E6_Lnever | 1 | A | ttc: 8 -> '' |
| G2 | G2_E6_Lnever | 1 | B | ttc: 9 -> '' |
| G2 | G2_E6_Lnever | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E6_Lnever | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E6_Lnever | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E96_L0 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E96_L0 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E96_L0 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E96_L0 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E96_L0 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E96_L0 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E96_L1 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E96_L1 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E96_L1 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E96_L1 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E96_L1 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E96_L1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E96_L16 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E96_L16 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E96_L16 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E96_L16 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E96_L16 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E96_L16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E96_L4 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E96_L4 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E96_L4 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E96_L4 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E96_L4 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E96_L4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E96_L64 | 1 | A | ttc: 8 -> '' |
| G2 | G2_E96_L64 | 1 | B | ttc: 9 -> '' |
| G2 | G2_E96_L64 | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E96_L64 | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E96_L64 | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E96_L64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G2 | G2_E96_Lnever | 1 | A | ttc: 8 -> '' |
| G2 | G2_E96_Lnever | 1 | B | ttc: 9 -> '' |
| G2 | G2_E96_Lnever | 1 | Bw | ttc: 24 -> '' |
| G2 | G2_E96_Lnever | 1 | ORACLE-S | role: reference -> state-probe reference; ttc: 8 -> '' |
| G2 | G2_E96_Lnever | 2 | A-fk | ttc: 8 -> '' |
| G2 | G2_E96_Lnever | 2 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L0 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L0 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L1 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L1 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L16 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L16 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L4 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L4 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L64 | 1 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_L64 | 2 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_Lnever | 1 | ORACLE-S | role: reference -> state-probe reference |
| G3 | G3_Lnever | 2 | ORACLE-S | role: reference -> state-probe reference |

### Secondary grid, totals per grid x contract x policy (counts of cells; sums of retries and reads)

No value changed.
