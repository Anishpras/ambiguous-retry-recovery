# Ablations of the reconcilers C and D

_Exploratory, post-review (v1.2). Not pre-specified; the frozen v1.1.1 core tables remain the record._

Each ablation is a named policy option (arr/policies.py, POLICY_DEFAULTS). Every core and grid cell is run under both contracts and compared with the unablated policy on effects at H and F, belief at H, dispatches, time to first `complete` and conflicts. Core: 34 operations per policy (16 scenarios x 2 contracts, S11 has two). Grid: 240 schedules per policy (120 x 2 contracts).

| policy | ablation | core operations changed | grid schedules changed | core c1 dup/once/unres/false-fail/false-complete | grid c1 (same) |
|---|---|---|---|---|---|
| D | no_provider_seq (provider_seq ignored (no staleness tracking)) | 0 of 34 | 0 of 240 | 1 / 15 / 4 / 0 / 0 of 17 | 0 / 114 / 16 / 0 / 0 of 120 |
| D | no_event_id_dedupe (event_id duplicate check off) | 0 of 34 | 0 of 240 | 1 / 15 / 4 / 0 / 0 of 17 | 0 / 114 / 16 / 0 / 0 of 120 |
| D | no_payload_correlation (payload_hash not checked in correlation) | 0 of 34 | 0 of 240 | 1 / 15 / 4 / 0 / 0 of 17 | 0 / 114 / 16 / 0 / 0 of 120 |
| D | ignore_webhooks (every webhook ignored) | 8 of 34 | 136 of 240 | 1 / 15 / 4 / 0 / 0 of 17 | 0 / 114 / 41 / 0 / 0 of 120 |
| D | ignore_status (no status reads (polling off)) | 8 of 34 | 58 of 240 | 1 / 14 / 5 / 0 / 0 of 17 | 0 / 114 / 30 / 0 / 0 of 120 |
| C | no_provider_seq (provider_seq ignored (no staleness tracking)) | 0 of 34 | 0 of 240 | 0 / 14 / 4 / 0 / 0 of 17 | 0 / 114 / 16 / 0 / 0 of 120 |
| C | no_event_id_dedupe (event_id duplicate check off) | 0 of 34 | 0 of 240 | 0 / 14 / 4 / 0 / 0 of 17 | 0 / 114 / 16 / 0 / 0 of 120 |
| C | no_payload_correlation (payload_hash not checked in correlation) | 0 of 34 | 0 of 240 | 0 / 14 / 4 / 0 / 0 of 17 | 0 / 114 / 16 / 0 / 0 of 120 |
| C | ignore_webhooks (every webhook ignored) | 8 of 34 | 136 of 240 | 0 / 14 / 4 / 1 / 0 of 17 | 0 / 114 / 41 / 0 / 0 of 120 |
| C | ignore_status (no status reads (polling off)) | 6 of 34 | 58 of 240 | 0 / 14 / 5 / 0 / 0 of 17 | 0 / 114 / 30 / 0 / 0 of 120 |

Baseline (no ablation) core c1 for reference: D 1 / 15 / 4 / 0 / 0 of 17; C 0 / 14 / 4 / 0 / 0 of 17.

## Details

**D, ignore_webhooks: changed core operations**

- c1 S04/op-1: ttc_any_complete 20 -> 36
- c1 S07/op-1: ttc_any_complete 8 -> 36
- c1 S13/op-1: ttc_any_complete 10 -> 11
- c1 S15/op-1: conflicts 1 -> 0; ttc_any_complete 7 -> 9
- c2 S04/op-1: ttc_any_complete 20 -> 36
- c2 S07/op-1: ttc_any_complete 8 -> 36
- c2 S13/op-1: ttc_any_complete 10 -> 11
- c2 S15/op-1: conflicts 1 -> 0; ttc_any_complete 7 -> 9

**D, ignore_webhooks: grid changes by field**: belief_H in 50, ttc_any_complete in 136

**D, ignore_status: changed core operations**

- c1 S02/op-1: belief_H complete -> unresolved; dispatches 2 -> 1; effects_F 1 -> 0; effects_H 1 -> 0; ttc_any_complete 9 -> None
- c1 S03/op-1: ttc_any_complete 6 -> 8
- c1 S06/op-1: ttc_any_complete 9 -> 33
- c1 S12/op-1: ttc_any_complete 4 -> 10
- c2 S02/op-1: belief_H complete -> unresolved; dispatches 2 -> 1; effects_F 1 -> 0; effects_H 1 -> 0; ttc_any_complete 9 -> None
- c2 S03/op-1: ttc_any_complete 6 -> 8
- c2 S06/op-1: ttc_any_complete 9 -> 33
- c2 S12/op-1: ttc_any_complete 4 -> 10

**D, ignore_status: grid changes by field**: belief_H in 28, ttc_any_complete in 58

**C, ignore_webhooks: changed core operations**

- c1 S04/op-1: ttc_any_complete 20 -> 36
- c1 S07/op-1: ttc_any_complete 8 -> 36
- c1 S13/op-1: ttc_any_complete 10 -> 11
- c1 S15/op-1: belief_H complete -> failed; conflicts 1 -> 0; ttc_any_complete 14 -> None
- c2 S04/op-1: ttc_any_complete 20 -> 36
- c2 S07/op-1: ttc_any_complete 8 -> 36
- c2 S13/op-1: ttc_any_complete 10 -> 11
- c2 S15/op-1: belief_H complete -> failed; conflicts 1 -> 0; ttc_any_complete 14 -> None

**C, ignore_webhooks: grid changes by field**: belief_H in 50, ttc_any_complete in 136

**C, ignore_status: changed core operations**

- c1 S02/op-1: belief_H failed -> unresolved
- c1 S03/op-1: ttc_any_complete 6 -> 8
- c1 S12/op-1: ttc_any_complete 4 -> 10
- c2 S02/op-1: belief_H failed -> unresolved
- c2 S03/op-1: ttc_any_complete 6 -> 8
- c2 S12/op-1: ttc_any_complete 4 -> 10

**C, ignore_status: grid changes by field**: belief_H in 28, ttc_any_complete in 58

## Why order and repeats cannot matter

(From docs/monotone-evidence.md.)

# Why delivery order and repeats cannot change a monotone, attempt-keyed reconciler

**Scope.** This applies to policies C, D and D+I in `arr/policies.py`. Policies A, B and Bw are *not* monotone, and the same argument shows why ordering does matter for them.

## State and decision

After any sequence of observations, the reconciler's decision-relevant state is:

- **A**, the attempts it dispatched (from the runtime's acks);
- **P**, the attempts with correlated positive evidence (`ok`, a `committed` receipt, `found`);
- **N**, the attempts with an authoritative terminal negative (`rejected`, `in_progress` or `conflict` for that attempt, an `aborted` receipt, or a `terminal_attempts` listing);
- a flag recording that something ambiguous (a timeout or `error`) has happened. It only controls when polling starts.

The decision is a function of (A, P, N) and the remaining budget:

- `complete` if P is non-empty;
- otherwise, retry if A ⊆ N and budget remains (D only; C only before any ambiguity);
- otherwise `failed` if A ⊆ N;
- otherwise `unresolved`.

## The argument in three lines

1. **Each observation only adds an element.** It adds an attempt to P or to N. Nothing ever removes one: a commit cannot be undone, and a terminal negative is a provider guarantee that the attempt never commits.
2. **Adding to a set is order-free and repeat-free.** Set union is commutative, associative and idempotent. So the same multiset of deliveries, in any order and with any repeats, yields the same P and N, and hence the same decision.
3. **Sequence numbers and event IDs therefore change nothing.** `provider_seq` (ordering) and `event_id` (de-duplication) can only reorder or drop *repeats* of facts already in the sets, so they cannot change any decision.

The exploratory ablations measure this. With `use_provider_seq` or `dedupe_event_ids` switched off, no core or grid outcome changes for C or D (`results/exploratory/ablations.md`). The test suite asserts it as a property (`tests/test_v1_2.py`).

## What the argument does *not* say

- **Timing still matters.** *When* a fact arrives decides *when* the reconciler can act. Receipt delay changes latency and, past the horizon, whether an operation is resolved at all. Order and repetition do not.
- **It needs monotone facts.** A provider with reversible states (for example `scheduled → cancelled → rescheduled`) emits facts that later facts can contradict. Then ordering matters, and sequence numbers become necessary. No scenario in this study has such a provider.
- **It needs the guarantee to hold.** When a provider breaks its guarantee (S15: `aborted`, then a commit of the same attempt), the attempt lands in both P and N. The commit-wins rule keeps the belief consistent with the ledger and records a conflict. But a retry made while the attempt was only in N can still duplicate the effect, under both contracts if the dedup record was released on abort.
- **Correlation is a separate matter.** Keying evidence by attempt matters: credit is given only to attempts this operation dispatched, with this payload hash. In this model attempt IDs are client-assigned and unique, and the payload never changes, so the payload check is never exercised by the frozen scenarios. It guards against key reuse across different payloads. The attempt check is what the attempt-correlation mutant (M2b) breaks.

## Why A, B and Bw differ

A, B and Bw keep a *single* belief that later events overwrite ("last terminal-looking event wins"). Overwriting is not commutative, so a stale or repeated failure-named receipt can flip a correct `complete` and trigger a retry. This is policy A in S06 (a stale `aborted` at t = 30) and S14 (a late `deferred` at t = 12).
