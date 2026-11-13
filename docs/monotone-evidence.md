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
