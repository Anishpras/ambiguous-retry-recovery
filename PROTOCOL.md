# Protocol: Safe retry after an ambiguous tool timeout

Version 1.0 (pre-specification draft, 2026-11-13). Deterministic discrete-event simulation, synthetic CRM workflow, Python standard library only. No randomness is used, so there are no seeds.

## 1. Question

An agent's request to send a message times out, and the provider's status or webhooks are delayed. Which retry policies avoid duplicate external effects while still completing legitimate work? How do the results change when the provider enforces idempotency?

The system under study is the client's **recovery layer**. The tool calls are scripted, and no language model is involved.

The core comparison replicates, in a small deterministic model, findings from recent agent-recovery evaluations (LIMBO, RetryBench, Did It Happen?, Permission to Retry, Evidence-Guided Recovery). The extension is provider webhook receipts as recovery evidence (delayed, duplicated, reordered, lost, non-authoritative failure events, and a provider that violates its own terminal-negative guarantee), combined with stale negative status reads. *(Pre-freeze design update; see Revisions.)*

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
| `webhook: deferred` | provider_seq, attempt_id: "temporary failure; the provider will retry internally" | **no** (not authoritative; the attempt may still commit) |
| `webhook: committed` | provider_seq, attempt_id, payload_hash, effect_id | **positive**, if correlated |
| `webhook: aborted` | provider_seq, attempt_id | **terminal negative for that attempt** |

**Terminal negatives are provider guarantees.** Every terminal negative (`rejected`, `aborted`, and each attempt listed in `terminal_attempts`) is a guarantee by the provider that the attempt can never commit later. Scenario S15 is the only place this guarantee is violated, and it is labelled as a contract violation.

**Name-based mapping in A and B.** A, B and Bw map any failure-named webhook (`deferred` or `aborted`) to a failure signal. This is the naive, name-based mapping. C and D ignore `deferred` except as progress.

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
| **A: immediate retry** | On timeout, `error`, `in_progress` or `rejected`: retry at once if budget remains. On an `ok` response or a `committed` webhook (op_key match only): complete. On an `aborted` webhook: failed, then retry if budget remains. This is operation-level "last terminal-looking event wins"; `processing` is ignored. Budget exhausted with no success: `failed`. *(Revision v1.1: once the belief is `complete`, request-path failure signals (local timeouts; `error`, `in_progress`, `rejected` responses) are ignored; webhooks are unchanged. B and Bw inherit this. Revision v1.1.1: replies to the policy's own status reads are also ignored once `complete`.)* |
| **B: status check once** | On every failure signal (timeout, `error`, `in_progress`, `rejected`, `aborted` webhook): one status read. `found` → complete. Anything else, including `not_found` with terminal attempts → retry if budget remains. Success and failure events otherwise as in A. Budget exhausted: `failed`. |
| **C: defer** | Retries only on a *synchronous* `rejected` response, which arrives before any timeout. After a timeout or `error`: never dispatches again. Polls status every 5 ticks and observes webhooks with the §2.5 rules. Final belief: `complete` on correlated positive evidence; `failed` if every attempt is terminal; otherwise `unresolved`. |
| **D: reconcile** | Same evidence rules as C, plus a retry when every dispatched attempt has a terminal negative, no positive evidence exists and budget remains. Ambiguous evidence (timeout, `error`, `not_found`, `processing`) never triggers a retry. |
| **D+I (optional, separately named)** | D, plus: on contract 2 only, if the operation is still unresolved after its first timeout and one status poll, dispatch with the same op_key and payload. The contract guarantees at most one effect. `in_progress` → keep waiting and polling. On contract 1 it behaves exactly as D. Reported separately from the four core policies. |
| **Bw: wait-then-verify, τ = 15** | Identical to B, except the single status read is issued 15 ticks after the failure signal. At most one wait is pending at a time; further failure signals during the wait are absorbed. *(Pre-freeze design update.)* |

**References, not client policies** *(pre-freeze design update)*. These are implemented on the simulator side, are allowed to read hidden state, are excluded from V4 and are labelled as references everywhere:

- **ORACLE-S (state oracle).** Acts at the same decision points as A, plus every 5 ticks. If an effect exists in the ledger → complete. Otherwise retry if budget remains. It does not know about in-flight attempts.
- **ORACLE-O (outcome oracle).** Knows whether any dispatched attempt will ever commit before F, from the schedule. If an effect exists → complete. If some dispatched attempt will commit → wait. Otherwise retry if budget remains.

**Ablation A-fk** *(pre-freeze design update)*. A with a fresh op_key on every attempt, reported under contract 2 only. It shows that deduplication needs stable keys.

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
| S13 | webhook harm | non-authoritative failure event before commit: a1 accepted at t = 1; `deferred` (seq 1) emitted at t = 2, delivered at t = 3; the provider retries internally and commits at t = 8; `committed` (seq 2) delivered at t = 10; response lost; L = 1 | 1 effect at t = 8 |
| S14 | webhook harm | stale failure event for the same attempt after commit: a1 accepted at t = 1; `deferred` (seq 1) emitted at t = 2 but delayed to t = 12; a1 commits at t = 3; `ok` response at t = 4; `committed` (seq 2) at t = 6; L = 1 | 1 effect at t = 3 |
| S15 | webhook harm (**contract violation**) | a1 accepted at t = 1; the provider records an abort and emits `aborted` (seq 1) at t = 3, delivered at t = 4; the status replica lists a1 as terminal from t = 4; in violation of its guarantee, the provider then commits a1 at t = 12 and emits `committed` (seq 2), delivered at t = 14; response lost; L = 1. Under contract 2 the released dedup record does not stop a1's late commit, so duplicates can occur under both contracts. | 1 effect at t = 12 |

S13–S15 (family "webhook harm") were added by the pre-freeze design update.

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

**Ledger outcomes** (operations; 14 per contract and policy in S00–S12, 17 with S13–S15):

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

**Added by the pre-freeze design update:**

| Measure | Definition |
|---|---|
| Duplicate cause | *Contract-caused:* every extra effect came from a retry issued only after authoritative negatives covered every earlier attempt. *Policy-caused:* all other duplicates. |
| Unjustified retries (after RetryBench) | retries issued without an authoritative negative covering every outstanding attempt, counted even when no duplicate results. Under contract 2, D+I's retries count as "contract-justified" and are reported separately. |
| Completion categories | certified completion (belief `complete`) and true completion (exactly one effect) reported separately, including "true exactly-once but uncertified". |

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
| V4 | **Hidden-state isolation.** Policies receive deep-copied observation dicts only. The policy module imports nothing from the simulator. Under contract 1, every policy's observation sequence and actions are byte-identical in S08 and S09. The references ORACLE-S and ORACLE-O are excluded. |
| V5 | **Parity.** Every run uses budget 3, H = 60 and F = 200. No dispatch exceeds the budget, and no client action happens after H. |
| V6 | **Sanity labels.** S00 gives exactly one effect and `complete` for every policy and contract. Under contract 2, no policy ever has a duplicate, excluding S15 and A-fk. |
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

### Added after the prior-work review, before any matrix run

These are the study lead's hand derivations, added by the pre-freeze design update. They are not adjusted.

**Contract 1:**

| Policy | Duplicates | Other |
|---|---|---|
| Bw | S08, S10, S11/op-1 | — |
| A | S13, S14, S15 | — |
| B | S13, S15 | S14 once, via its status read |
| Bw | — | S13, S14 and S15 exactly once (in S15 it sees `committed` at t = 14 before its read) |
| C | — | S13, S14 and S15 once. In S15, C ends `complete` with one conflict recorded. |
| D | S15, contract-caused, with a conflict recorded | S13 and S14 once |
| ORACLE-S | S05, S10, S13, S15 | — |
| ORACLE-O | none | S10 unresolved at H |

**Contract 2:**

- No duplicates except in S15 (A, B, D and ORACLE-S) and under A-fk (the same duplicates as A under contract 1).
- D+I completes S13 once: in_progress, then `committed` at t = 10.

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

### Pre-freeze design update (study lead, after prior-work review, before any matrix run)

Applied on 2026-11-13, before the freeze and before any policy × scenario matrix or grid run.

1. **Framing (§1).** The "focused extension" paragraph is replaced: the core comparison is a replication in a small deterministic model of LIMBO, RetryBench, Did It Happen?, Permission to Retry and Evidence-Guided Recovery; the extension is webhook receipts as recovery evidence (including non-authoritative failure events and a provider that violates its terminal-negative guarantee) combined with stale negative status reads.
2. **New webhook type (§2.4).** `webhook: deferred` (provider_seq, attempt_id), not authoritative. A, B and Bw map any failure-named event (`deferred`, `aborted`) to a failure signal (naive, name-based); C and D treat `deferred` as progress only. Every terminal negative is stated to be a provider guarantee; S15 is the only, labelled, violation.
3. **New policies (§3).** Bw (wait-then-verify, τ = 15); references ORACLE-S and ORACLE-O (simulator-side, may read hidden state, excluded from V4, labelled as references); ablation A-fk (fresh op_key per attempt, contract 2 only).
4. **New scenarios (§4.2).** S13, S14, S15, family "webhook harm".
5. **New measures (§5).** Duplicate cause (contract- vs policy-caused), unjustified retries (D+I's contract-2 retries reported separately as contract-justified), completion categories (certified vs true exactly-once).
6. **Predictions (§7).** Added under "Added after the prior-work review, before any matrix run"; the original §7 predictions are unchanged and are checked on their original scope (S00–S12, policies A, B, C, D, D+I).
7. **V4/V6.** V4 excludes the references; V6's "no duplicates under contract 2" excludes S15 and A-fk.
8. **Tie to document.** In S04 under Bw, the `committed` webhook and the wait timer both fall at t = 20, so the webhook wins by the phase rule. (Implementer's note: in §2.2's numbering the webhook is a delivery, phase 2, and the wait timer is a client timer, phase 3; the study lead's note called them phases 1 and 2. The conclusion is the same.)

### Pre-freeze clarifications (implementer, before the freeze)

Each item resolves a detail the protocol leaves open. Code locations are given so a reviewer can check the implementation against the text.

- **C1. provider_seq is clock-derived, not a count** (`arr/provider.py: provider_seq`). The value is 100·t_emit + 10·k + r, with k the attempt index and r = 0, 1, 2, 3 for processing, deferred, committed, aborted. It increases per op_key in emission order (checked on every run), which is all §2.4 requires. A consecutive count leaks hidden state: in S08 a retry's `committed` webhook would carry seq 2 (a1's lost emission took seq 1) but seq 1 in S09, so A, B and Bw would see different bytes in the "indistinguishable twins" and V4 would fail. The protocol's illustrative values "seq 1 / seq 2" therefore appear as, e.g., 110 / 212 in S07. Mutation test M5 (a counting seq) confirms that V4 catches the leak. Residual: a delivered event reveals its own emission tick.
- **C2. Phase 1 uses the scheduling-counter rule too** (`arr/sim.py`). "Arrivals, commits and aborts" is read as the list of phase-1 event types, not as a sub-order. Example tie: in S02 with a resend at t = 2 (oracle case `retry_at_2_tie`), a1's abort and a2's arrival both fall in phase 1 of t = 3. The abort was scheduled first (at t = 1), so it runs first and releases the contract-2 record, and a2 executes. Every same-tick, same-phase, same-operation group in the core matrix is listed in `results/ties.csv`.
- **C3. One response per attempt** (`arr/provider.py: _respond`). It is delivered `after` ticks (default 1) after the provider's decision: the commit or abort for executed attempts, and the arrival for `rejected` and the contract-2 replies (`in_progress`, replayed `ok`, `conflict`). The default response to an abort is `error`; it is never used, because every scripted abort loses its response. S12's `error` replaces a1's `ok`. S15's late commit sends no second response.
- **C4. Contract-2 replies and rejections leave no records.** Contract-2 replies emit no webhook and create no status record. A rejected attempt creates neither a dedup record nor a status record, so `terminal_attempts` lists only attempts the replica shows as aborted (§2.4); a rejection is known to the client only from its synchronous response.
- **C5. Status reads are per op_key.** `found` reports the earliest visible committed record. `terminal_attempts` is sorted. Under L = never no record is ever visible, so `terminal_attempts` is always empty.
- **C6. Webhooks are delivered to every operation of the client** (broadcast), and the policies correlate them (§2.5). Responses and status replies go only to the operation that requested them. This matters only in S11.
- **C7. Polling (C, D, D+I).** It starts at the first `timeout` or `error`, with an immediate status read, and repeats every 5 ticks while the belief is `unresolved`.
- **C8. Stale webhooks** (seq ≤ highest applied). They are recorded and flagged. They may still add monotone facts (correlated positive evidence, or a terminal mark for their own attempt), but they never revert `complete` or a terminal mark.
- **C9. A, B and Bw are applied literally, at operation level.** *(Superseded for request-path signals by Revision v1.1 below; kept as the record of v1.0.)* Every failure signal is acted on whatever the current belief. In particular, a local timeout for an attempt whose response never arrived still triggers A's retry (or B's read) after a `committed` webhook has made the operation `complete`. Budget exhaustion sets `failed` only if the belief is not `complete` (A: "with no success"). To make this reading's effect visible, `retries_after_complete` is reported. It matters when a webhook confirms success before the timeout, e.g. G1 with W ≤ 2 or G2 with E = 1.
- **C10. Horizon.** H = start + 60 per operation (S11's op-2: t = 61). The client acts only at ticks ≤ H. Deliveries after H are logged as not observed. The belief at H is taken after all phases of tick H. F = 200 is absolute. Policy timers that would fire after H are not set. A read issued at t ≤ H whose reply arrives after H is allowed but unobserved.
- **C11. D+I.** The resend is evaluated once, at the first status reply to a read issued at or after the first *timeout* (an `error` response does not count). It dispatches only if the belief is still `unresolved`, budget remains, and D's own rule did not dispatch on that observation.
- **C12. C's retry.** C retries only when a `rejected` response makes every attempt terminal before any timeout or `error` has been observed for the operation.
- **C13. Time to confirmed completion.** It is the first tick at which the belief became `complete` (≤ H), minus the operation start. Coverage counts operations that reached `complete` at least once by H.
- **C14. Scorer-side measures.** Unsupported `complete`, retry justification and duplicate cause are computed by the scorer from the observations the runtime delivered, not from the policy's self-report. The conflict count is taken from the policy's report, as §2.5 asks.
- **C15. Bw's wait is cancelled by success.** When the wait ends and the belief is already `complete`, no status read is issued. This is implied by the study lead's S04 tie note: with the read, Bw would see a stale `not_found` at t = 21 and retry. B's immediate read is unchanged.
- **C16. A, B and Bw map `deferred` exactly like `aborted`.** The belief becomes `failed`, then the policy takes its failure-signal action (name-based mapping).
- **C17. References.**
  - Decision points are A's, plus every 5 ticks from the operation start. A's points are: timeout; `ok`, `error`, `in_progress` and `rejected` responses; and `committed`, `aborted` and `deferred` webhooks of the operation.
  - Decision points in the same tick are coalesced into one decision, because nothing on the provider side changes during phases 2–3 of a tick. Without coalescing, the timeout and the 5-tick point at t = 5 would dispatch twice.
  - Belief: `complete` if an effect exists. Otherwise `failed` if the budget is exhausted and (for ORACLE-O) nothing will commit. Otherwise `unresolved`.
- **C18. How ORACLE-O knows "will commit before F".** It runs a private copy of the provider forward to F with no further client actions (`arr/sim.py: FastForward`), so contract-2 deduplication at future arrivals is taken into account.
- **C19. A-fk keys.** Attempt k ≥ 2 uses op_key `<op_key>~k<k>` and attempt_id `<that key>#a<k>`. The policy matches positives against the keys of its own dispatched attempts. Effects are scored per logical operation.
- **C20. Timing of the new scenario events.** In S13/S14, `deferred` is emitted 1 tick after acceptance. In S15, the violating commit is scheduled 11 ticks after arrival; it neither consults nor restores the released dedup record.
- **C21. Retry justification.** A retry is justified if, when it was dispatched, the client had observed an authoritative terminal negative for every earlier attempt: a `rejected`, `in_progress` or `conflict` response, an `aborted` webhook, or a listing in `terminal_attempts`. A duplicate is contract-caused if every committed retry was justified, and policy-caused otherwise. D+I's unjustified retries under contract 2 are counted separately as contract-justified.
- **C22. What ran before the freeze.**
  - Policy-free or crafted checks: V1 scripted dispatches, V2 contract basics, and V3 crafted sequences.
  - V4: every client policy on S08 and S09 under contract 1. The checks compared bytes; per-cell results were not printed.
  - Mutation tests: D on S04 and S06 under contract 1 (tests M1 and M2 assert that real D yields one effect there).
  - Ad-hoc schedules used to smoke-test the reporting code. One of them reused S15's a1 script and two resembled S13 and S01. Their outcomes were not inspected.
  - No other matrix cell and no grid schedule was run before the freeze.

### Revision v1.1 (post-freeze, study lead)

Applied on 2026-11-13, after the v1.0 collection (commit `924aef2`), and re-frozen as v1.1.

- **What.** Once a policy's belief is `complete`, A, B and Bw ignore *request-path* failure signals: local timeouts, and `error`, `in_progress` and `rejected` responses. Provider webhooks still apply "last terminal-looking event wins" exactly as before; that naive webhook handling is what S06 and S14 test. The change is in `PolicyA.on_timeout` and `PolicyA.on_response` (`arr/policies.py`), inherited by B and Bw, with unit tests in `tests/test_revision_v1_1.py`. Status replies are not request-path failure signals, so B's handling of a `not_found` reply is unchanged. The references, C, D and D+I are untouched. A-fk is policy A, so it changes too.
- **Why.** A client that has already confirmed completion stops its own request path. The literal v1.0 reading (clarification C9) had A and B retrying because their own stale timer fired, which makes them straw men. In v1.0 this produced 24 of A's and 26 of B's contract-1 grid duplicates; the core matrix was unaffected.
- **Results expected to change.** These were derived from the committed v1.0 results before the rerun. The observed changes are listed exhaustively in `results/revision_v1.1_delta.md`, generated by every run from the v1.0 baseline files extracted byte-for-byte from git (`baselines/v1.0/`).
  - **Core matrix: no change.** A scan of the v1.0 traces finds no request-path failure signal reaching A, B or Bw while their belief is `complete`.
  - **A (contracts 1 and 2) and A-fk: 24 grid cells change**, namely G1 with W ∈ {1, 2} and G2 with E = 1. Each loses its retry after completion. Under contract 1 (and for A-fk) those 24 duplicates disappear; under contract 2 only the retry count falls.
  - **B (both contracts): the same 24 cells change.** The post-completion timeout no longer triggers a status read. Under contract 1, the 16 of those cells with L ≥ 4 lose their duplicate.
  - **B keeps 10 contract-1 duplicates after completion**, in G1 with W = 4 and G2 with E = 3, at L ≥ 4. There, B's read was issued at the t = 5 timeout, *before* completion, and its `not_found` reply arrives in the same tick just after the confirming webhook. Status replies are outside the revision.
  - **Bw: no measured value expected to change.** Bw no longer starts a wait on a post-completion timeout, but under C15 it already skipped the read at the end of such a wait.
  - **Predictions: no verdict expected to change.** `results/predictions_check.md` reports match-status changes against the v1.0 run.
- **Supporting changes.** `arr/delta.py` writes the delta. `baselines/v1.0/` holds `summary.csv`, `by_policy.csv`, `by_family.csv`, `grid.csv` and `predictions_check.md` from commit `924aef2`; these files are frozen. `run_sim.py` hashes `baselines/` in FREEZE.json and writes the delta.

### Revision v1.1.1 (post-freeze, study lead)

Applied on 2026-11-13, after the v1.1 run (commit `622e1f1`), and re-frozen as v1.1.1.

- **What.** Once the belief is `complete`, A, B and Bw also ignore replies to their own status reads (`PolicyB.on_status`, inherited by Bw; A never reads status). Webhook handling is unchanged. A unit test was added to `tests/test_revision_v1_1.py`.
- **Why.** It is the same request-path principle as v1.1: status replies answer the client's own requests. The study lead left them out of the v1.1 instruction by oversight. The implementer's v1.1 report had flagged the residual: 10 contract-1 grid cells where B's `not_found` reply, to a read issued before completion, arrived in the same tick just after the confirming webhook and triggered a retry.
- **Results expected to change.** These were derived before the rerun from the committed v1.1 results. The observed changes are listed in the "v1.1 -> v1.1.1" section of `results/revision_v1.1_delta.md`, which compares against `baselines/v1.1/` (byte-for-byte from git `622e1f1`). The file's "v1.0 -> v1.1" section is now computed from the two frozen baselines instead of from the current run; its tables are unchanged.
  - **Core matrix: no change.** No status reply reaches B or Bw while its belief is `complete`, by the same v1.0 trace scan.
  - **B: 10 grid cells change in each contract**, namely G1 with W = 4 and G2 with E = 3, both at L ≥ 4. Under contract 1 they lose their duplicate; under contract 2 they lose a replayed retry.
  - **A and Bw: no change expected.**
  - **Predictions: no verdict expected to change.**
