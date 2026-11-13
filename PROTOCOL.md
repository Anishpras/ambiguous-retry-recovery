# Protocol: Safe retry after an ambiguous tool timeout

Version 1.0 (pre-specification draft, 2026-11-13). Deterministic discrete-event simulation, synthetic CRM workflow, Python standard library only. No randomness is used, so there are no seeds.

## 1. Question

An agent's request to send a message times out, and the provider's status or webhooks are delayed. Which retry policies avoid duplicate external effects while still completing legitimate work? How do the results change when the provider enforces idempotency?

The system under study is the client's **recovery layer**. The tool calls are scripted, and no language model is involved. This is a focused extension of existing work on ambiguous effects. The planned extension is reconciliation under four conditions:

- webhook delay;
- duplicate delivery;
- out-of-order delivery;
- stale negative status reads.

The prior-work report decides whether "extension" or "replication" is the honest label.

## 2. Model

### 2.1 Entities

- **Logical operation.** Each operation has a stable `op_key` and a payload. In this study the action is sending a synthetic message, so the payload holds a contact ID, a template ID and a body hash. `payload_hash` is the SHA-256 of the payload as canonical JSON.
- **Attempt.** Every dispatch creates an attempt with a fresh `attempt_id` = `<op_key>#a<k>`, where k = 1, 2, 3. Each attempt carries the op_key and the payload.
- **Provider.** The provider accepts or rejects attempts, executes them, keeps its own records, answers status reads and emits webhooks.
- **Webhook queue.** The queue delivers provider events to the client according to the scenario's delivery script. Deliveries can be delayed, duplicated, reordered or lost.
- **Private effect ledger.** Used for scoring only. Each entry records `effect_id`, `op_key`, `attempt_id`, `payload_hash` and `commit_time`.
- **Effect IDs** are opaque: the first 12 hex characters of an HMAC of (op_key, attempt_id) under a fixed simulator key. Sequential effect IDs would leak ledger counts to the client.

### 2.2 Time

Time runs in integer ticks, with the first dispatch at t = 0.

**Ordering within a tick:**

1. Provider-side events: arrivals, commits and aborts.
2. Deliveries to the client: responses, status replies and webhooks, in the order they were scheduled. Ties break by a global scheduling counter.
3. Client timers: timeouts and polls.

**Actions the client takes at tick t:**

| Action | When it takes effect |
|---|---|
| A dispatch | arrives at the provider at t + `arrive` (≥ 1) |
| A status read | answered at t + 1, from the provider's records with `record_time` ≤ t − L |

**Constants:**

| Constant | Value |
|---|---|
| Client timeout | T = 5 ticks after dispatch, if no response for that attempt has arrived |
| Dispatch budget | 3 per operation |
| Observation horizon | H = 60 ticks after the operation starts. The client's belief at H is its final answer, and no client action happens after H. |
| Final scoring cutoff | F = 200 ticks |
| Status poll interval (policies C and D) | 5 ticks |
| Dedup window W (contract 2) | 1,000 ticks, which covers the whole experiment |

A response that arrives after its timeout is still delivered, and the client observes it as evidence.

### 2.3 Provider contracts

**Contract 1: no deduplication.** Every accepted attempt executes independently, so repeating an op_key can create another effect.

**Contract 2: deduplication.** It is keyed on op_key and requires an identical payload_hash within W.

- **When it takes effect.** The record is created when the provider *accepts* the first attempt with that key, at arrival and not at commit.
- **A later attempt with the same key and payload:**

  | Record state | Provider's reply | New effect? |
  |---|---|---|
  | pending | `in_progress` | none |
  | committed | `ok` replaying the original `effect_id` | none |
  | aborted | the record is released and the new attempt executes normally | as normal |

- **Same key, different payload:** the provider replies `conflict` and creates no effect.
- **Lost requests.** A request lost before arrival creates no record.
- **Window expiry.** Expiry of the dedup window is not modelled. It would be a separate contract and condition.

### 2.4 Observations and what is authoritative

The policy sees only the following. It never sees the ledger, the scenario script or future events.

| Observation | Content | Authoritative? |
|---|---|---|
| `response: ok` | attempt_id, op_key, payload_hash, effect_id | **positive**, if correlated (§2.5) |
| `response: rejected` | the attempt was refused before execution and will never execute | **terminal negative for that attempt** |
| `response: error` | 5xx-style error | no: the attempt may or may not have executed |
| `response: in_progress` (contract 2) | another attempt with this key is pending | terminal negative for *this* attempt's own effect; says nothing about the earlier attempt |
| `response: conflict` (contract 2) | same key, different payload | terminal negative for this attempt; a client bug |
| timeout (local) | no response by dispatch + T | no |
| `status: found` | effect_id, attempt_id, payload_hash | **positive**, if correlated |
| `status: not_found` | plus `terminal_attempts`, the IDs of attempts the replica shows as aborted | `not_found` itself: **no**, because the replica may be stale (lag L is not shown) or the attempt may still commit. Each listed terminal attempt: **terminal negative for that attempt** |
| `webhook: processing` | provider_seq, attempt_id | no (progress only) |
| `webhook: committed` | provider_seq, attempt_id, payload_hash, effect_id | **positive**, if correlated |
| `webhook: aborted` | provider_seq, attempt_id | **terminal negative for that attempt** |

**Two rules about negatives:**

- **A definitive negative for the operation** exists only when every dispatched attempt has its own terminal negative.
- **A silently lost request** gets no record and no terminal negative. No observation can prove it will not commit.

**Delivery order versus provider order.** `provider_seq` increases per op_key in the provider's emission order. Each emission also has an `event_id`; a duplicated delivery repeats the same event_id. Delivery order can differ from `provider_seq` order.

### 2.5 Correlation and conflict rules (used by policies C and D)

- **Correlation.** Positive evidence counts only if its op_key and payload_hash match the operation and its attempt_id is one the client dispatched.
- **Monotone commit.** Once correlated positive evidence is seen, the operation is `complete`. Later negatives, stale events or `not_found` never revert it, because effects cannot be undone.
- **Terminal attempts.** A terminal negative marks that attempt terminal, and it stays terminal.
- **Duplicates.** A delivery whose event_id was already seen is ignored.
- **Stale events.** A webhook with `provider_seq` ≤ the highest seq already applied for the op is recorded but cannot regress state.
- **Conflict.** A positive and a terminal negative for the *same* attempt are a conflict. The commit wins, the conflict is counted, and the conflicting evidence is listed in the trace.

## 3. Policies

All four policies share the following:

- the same op_key and payload for every dispatch of one operation;
- a budget of 3 dispatches;
- the horizon H;
- each operation is handled independently.

| Policy | Rule |
|---|---|
| **A: immediate retry** | On timeout, `error`, `in_progress` or `rejected`: retry at once if budget remains. On an `ok` response or a `committed` webhook (op_key match only): complete. On an `aborted` webhook: failed, then retry if budget remains. This is operation-level "last terminal-looking event wins"; `processing` is ignored. Budget exhausted with no success: `failed`. |
| **B: status check once** | On every failure signal (timeout, `error`, `in_progress`, `rejected`, `aborted` webhook): one status read. `found` → complete. Anything else, including `not_found` with terminal attempts → retry if budget remains. Success and failure events otherwise as in A. Budget exhausted: `failed`. |
| **C: defer** | Retries only on a *synchronous* `rejected` response, which arrives before any timeout. After a timeout or `error`: never dispatches again. Polls status every 5 ticks and observes webhooks with the §2.5 rules. Final belief: `complete` on correlated positive evidence; `failed` if every attempt is terminal; otherwise `unresolved`. |
| **D: reconcile** | Same evidence rules as C, plus a retry when every dispatched attempt has a terminal negative, no positive evidence exists and budget remains. Ambiguous evidence (timeout, `error`, `not_found`, `processing`) never triggers a retry. |
| **D+I (optional, separately named)** | D, plus: on contract 2 only, if the operation is still unresolved after its first timeout and one status poll, dispatch with the same op_key and payload. The contract guarantees at most one effect. `in_progress` → keep waiting and polling. On contract 1 it behaves exactly as D. Reported separately from the four core policies. |

**C and D are a matched pair.** C is D without retries. Comparing them isolates the retry decision. A and B are simple comparison policies, not straw men; their rules are written above in full.

**Out of scope:** changes in authorisation during recovery. They are left to a follow-up informed by *Permission to Retry*.

## 4. Scenarios (the frozen core matrix)

### 4.1 Defaults

**Nominal attempt.** Arrives at +1, accepted, commits 1 tick after arrival, `ok` response delivered 1 tick after the commit, `committed` webhook delivered 2 ticks after emission, and no `processing` webhook. Every attempt a scenario does not override follows this rule. **Extra retries are generated by this documented rule**, never by randomness.

**Webhook delivery.** Each delivery offset is measured from the emission time. `[]` means lost; `[4, 5]` means delivered twice.

**Status lag** L is per scenario; `never` means records never become visible before F.

### 4.2 Scenarios

Times are for the first attempt, a1, dispatched at t = 0.

| ID | Family | Script for a1 (and provider settings) | True effect history if no retry happens |
|---|---|---|---|
| S00 | control | nominal; L = 1 | 1 effect at t = 2 |
| S01 | auth. negative | rejected at arrival; `rejected` response at t = 2; L = 1 | 0 effects (a retry at t = 2 → commit at t = 4) |
| S02 | auth. negative | accepted at t = 1, aborted at t = 3; response lost; webhooks lost; L = 1 (status shows a1 terminal from t = 4) | 0 effects |
| S03 | lost ack | commit at t = 2; response lost; `committed` webhook at t = 8; L = 1 | 1 effect |
| S04 | lost ack | commit at t = 2; response lost; `committed` webhook at t = 20; L = 30 (stale `not_found` until t ≥ 32) | 1 effect |
| S05 | pending | commit at t = 15; late `ok` response at t = 16; webhook at t = 17; L = 1 | 1 effect at t = 15 |
| S06 | receipt anomaly | aborted at t = 3; response lost; `aborted` webhook delayed to t = 30; L = 1. Later attempts nominal. | 0 effects |
| S07 | receipt anomaly | commit at t = 2; response lost; `processing` (seq 1, emitted t = 1) delivered at t = 12; `committed` (seq 2) delivered at t = 8 and again at t = 9; L = 30 | 1 effect |
| S08 | no confirmation | commit at t = 2; response lost; all webhooks lost; L = never | 1 effect |
| S09 | no confirmation (twin of S08) | request lost before arrival; L = never; nothing observable | 0 effects |
| S10 | pending | commit at t = 90 (after H, before F); response lost; webhook at t = 92; L = 1 | 0 effects at H, 1 at F |
| S11 | validation: distinct ops | op-1: commit at t = 2, response lost, webhooks lost. op-2: starts at t = 1, nominal, identical payload but a different op_key. L = never. | op-1: 1, op-2: 1 |
| S12 | lost ack (error) | commit at t = 2; `error` response at t = 3; `committed` webhook at t = 10; L = 1 | 1 effect |

S08 and S09 are **indistinguishable twins**. Under contract 1 every policy sees byte-identical observations in both, yet the truth differs. Without a provider guarantee, no policy can be both duplicate-free and complete on this pair. Reporting `unresolved` is the only answer that is never wrong.

**Each scenario fixture in `scenarios/` records:**

- the script;
- the expected effect history under a fixed list of scripted dispatch times, for oracle checks independent of the policies (§6, V1);
- a sentence describing the evidence available at each decision point.

### 4.3 Secondary deterministic grid (pre-specified)

The grid explores timing boundaries; it is not a rate estimate.

| Grid | Settings | Count |
|---|---|---|
| G1: lost ack | a1 commits at t = 2, response lost. Status lag L ∈ {0, 1, 2, 4, 8, 16, 32, 64, never}; `committed` webhook delay W ∈ {1, 2, 4, 8, 16, 32, 64, lost} | 72 schedules |
| G2: pending | a1's commit delay E ∈ {1, 3, 6, 12, 24, 48, 96} ticks after arrival; response lost; webhook delay 2; L ∈ {0, 1, 4, 16, 64, never} | 42 schedules |
| G3: never arrived | the request is lost; L ∈ {0, 1, 4, 16, 64, never}, which is irrelevant here | 6 schedules |

All grids run under both contracts and every policy.

## 5. Measures

Reported per policy, contract and scenario family, and per scenario, with counts and denominators.

**Ledger outcomes** (operations; 14 per contract and policy in the core matrix):

| Measure | Definition |
|---|---|
| Duplicates | operations with effects(F) > 1, and the number of extra effects |
| Exactly once | effects(F) = 1 |
| Zero effects | effects(F) = 0 |
| Effects still pending at H | attempts accepted but not yet committed or aborted at H |
| Pending beyond F | attempts still pending at F, reported separately (expected 0) |

**Client belief at H** (complete, failed or unresolved), compared with the ledger separately:

| Measure | Definition |
|---|---|
| Unsupported `complete` | the policy's evidence log holds no correlated positive evidence for the operation |
| Incorrect status: false complete | `complete` while effects(H) = 0 |
| Incorrect status: false failure | `failed` while effects(F) ≥ 1, meaning an effect exists or will exist |
| Unresolved at H | listed with the true effect counts at H and at F |

**Cost and latency:**

| Measure | Definition |
|---|---|
| Retries per operation | dispatches − 1; mean and max |
| Time to confirmed completion | from operation start to the first `complete`, for operations that reach it. Median and max, always shown with coverage (n confirmed / N); no latency figure is given without its coverage. |

**Worked traces** (event by event, marking what the provider knows, what the client sees and what the scorer records):

- S04: `not_found` while an effect exists;
- S02: an authoritative negative enables a useful retry under D;
- S06: a stale `aborted` webhook arrives after a later commit.

## 6. Validation (every run; the run fails if any check fails)

| # | Check |
|---|---|
| V1 | **Oracle checks independent of policies.** For each scenario, scripted dispatch times with no policy reproduce the expected effect history in the fixture, under both contracts. |
| V2 | **Contract basics.** A nominal call gives 1 effect. A committed timeout followed by a resend gives 2 effects under contract 1 and 1 under contract 2. Contract 2 with a payload mismatch gives `conflict` and no extra effect. Distinct op_keys with the same payload give 2 effects under both contracts. Under contract 2, a retry after an abort executes. |
| V3 | **Reconciliation rules.** Unit tests with crafted observation sequences. A delayed older receipt (lower seq, or for an attempt already terminal) cannot overturn a commit. Duplicate deliveries are idempotent. Uncorrelated positives (other op_key or payload_hash) are ignored. The conflict rule holds. |
| V4 | **Hidden-state isolation.** Policies receive deep-copied observation dicts only. The policy module imports nothing from the simulator. Under contract 1, every policy's observation sequence and actions are byte-identical in S08 and S09. |
| V5 | **Parity.** Every run uses budget 3, H = 60 and F = 200. No dispatch exceeds the budget, and no client action happens after H. |
| V6 | **Sanity labels.** S00 gives exactly one effect and `complete` for every policy and contract. Under contract 2, no policy ever has a duplicate. |
| V7 | **Reproducibility.** `python3 run_sim.py --check-reproducible` runs everything twice in temp directories and compares every output byte. |

**Mutation tests** (in `tests/`). Each mutant must be caught by at least one test:

- D treating `not_found` as authoritative (duplicates in S04);
- D ignoring provider_seq and attempt correlation (S06);
- a contract-2 dedup record created at commit instead of acceptance (duplicates in S05);
- sequential effect IDs (V4 fails).

## 7. Pre-specified predictions

These are derived by hand from the rules above before any run. Deviations are reported and explained, not silently fixed.

**Contract 1:**

| Policy | Duplicates | Unresolved | Other |
|---|---|---|---|
| A | S03, S04, S05, S06, S07, S08, S10, S11/op-1, S12 (9 of 14 operations) | none | completes S09 exactly once |
| B | S04, S05, S07, S08, S10, S11/op-1 (6) | none | the status check prevents duplicates in S03, S06 and S12 |
| C | none | S08, S09, S10, S11/op-1 | zero effects with a correct `failed` belief in S02 and S06 |
| D | none | S08, S09, S10, S11/op-1 | completes S02 and S06 exactly once through authoritative negatives |

**Contract 2:**

- no policy has duplicates;
- A and B in S10 end `failed` while an effect commits later (false failure);
- D+I completes S08, S09 and S11/op-1 exactly once, and leaves only S10 unresolved.

## 8. Freeze

`python3 run_sim.py --freeze` records SHA-256 hashes of these files in `FREEZE.json` before results are collected:

- this protocol;
- the scenario fixtures (the matrix and the sanity labels);
- every source file.

The collecting run refuses to start unless the hashes match. Post-freeze changes are logged under "Revisions" with their reasons and re-frozen under a new label. The freeze is self-attested.

## 9. Outputs

**Command:** `python3 run_sim.py` exits 0 only if every validation check passes.

**Traces:** `results/traces/<contract>/<policy>/<scenario>.jsonl`, one event per line. Each line records the time, the event, whether the client could see it, and its details.

**Summaries:**

- `results/summary.csv`: one row per contract × policy × scenario × operation;
- `results/by_family.csv` and `results/by_policy.csv`;
- `results/grid.csv` and `results/grid_tables.md`.

**Comparison and worked traces:**

- `results/predictions_check.md`: §7 predictions against observed results;
- `results/worked_traces.md`.

**Run metadata:** `results/run_info.json` records the interpreter, platform, fixture version, constants, file hashes and freeze status.

## 10. Worked timeline: a request that commits but times out (S04, contract 1)

| t | Provider knows | Client (policy) sees | Private scorer records |
|---|---|---|---|
| 0 | — | dispatches a1 for op-1 | — |
| 1 | a1 arrives and is accepted | — | — |
| 2 | a1 executes and commits effect e1. It emits `committed` (seq 1) and sends `ok` | — | ledger: e1 (op-1, a1) at t = 2 |
| 3 | — | (the `ok` response is lost) | — |
| 5 | — | **timeout**: ambiguous | — |
| 5→6 | the replica is 30 ticks behind and shows nothing | status read: **`not_found`** (not authoritative) | — |
| 20 | — | `committed` webhook (seq 1, a1, e1) | — |

**What each policy does next:**

| Policy | Action | Outcome |
|---|---|---|
| A | retries at t = 5 | a second effect at t = 7: **duplicate** |
| B | believes `not_found` and retries at t = 6 | **duplicate** |
| C, D | treat `not_found` as non-authoritative, keep polling, see the receipt at t = 20 | `complete`, **exactly once** |

Under contract 2, A's and B's retries are answered with a replay of e1, so no duplicate occurs.

## Revisions

None yet.
