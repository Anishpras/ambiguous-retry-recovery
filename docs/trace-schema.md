# Trace and observation schema

There are two JSONL vocabularies:

1. **Simulator traces**, in `results/traces/<contract>/<policy>/<scenario>.jsonl`. These record everything that happened, including hidden provider state.
2. **Observations**: the only thing a policy ever sees. `run_sim.py replay` accepts either a file of observations or a simulator trace; from a trace it uses the `observe` events.

All values are deterministic and every line is canonical JSON with sorted keys.

## 1. Simulator trace lines

| Field | Meaning |
|---|---|
| `t` | integer tick |
| `phase` | 1 provider events, 2 deliveries to the client, 3 client timers (start, timeout, poll, wait), 4 bookkeeping (horizon snapshot) |
| `n` | global scheduling counter of the event being processed; it breaks ties within a tick and phase |
| `event` | event name (table below) |
| `who` | `provider`, `network`, `client`, `runtime` or `scorer` |
| `visible` | `true` if the client could see it: its own actions, and deliveries it observed within the horizon |
| `op` | logical operation (op_key of the first attempt) |
| `details` | event-specific fields |

| Event | Who | Details |
|---|---|---|
| `request_sent` / `request_lost` | network | `attempt_id`, `arrives_at` |
| `arrival_accepted` / `arrival_rejected` | provider | `attempt_id`, `dedup_record` |
| `dedup_in_progress` / `dedup_replay` / `dedup_conflict` / `dedup_replay_failure` | provider | `attempt_id`, `record_attempt`, `effect_id` |
| `deferred`, `abort`, `commit`, `commit_after_abort` | provider | `attempt_id`, `effect_id` |
| `webhook_emitted` / `webhook_lost` | provider / network | `event`, `attempt_id`, `provider_seq`, `event_id`, `deliveries` |
| `response_sent` / `response_lost` | provider / network | `attempt_id`, `kind`, `arrives_at` |
| `status_snapshot` | provider | `cutoff` (t − L, or null for "never"), `visible_records`, `reply`, plus the truth: `true_effects_now`, `true_pending_now` |
| `ledger_entry` | scorer | `effect_id`, `attempt_id`, `commit_time`, `violation` |
| `observe` / `not_observed` | client | `obs`: the observation, as below. `not_observed` means it was delivered after H. |
| `dispatch`, `status_read`, `set_timer` | client | the client's actions, with `attempt_id` and `reason` for dispatches |
| `belief`, `conflict`, `horizon` | client | belief changes; conflicting evidence (§2.5); final belief at H |
| `timeout_suppressed`, `timer_not_set`, `dispatch_refused` | runtime | runtime bookkeeping |

## 2. Observations (policy input; replay input)

Every observation carries `type` and `t`.

| `type` | Fields | Authoritative? |
|---|---|---|
| `start` | `op_key`, `payload`, `payload_hash`, `budget` | — |
| `dispatched` | `op_key`, `attempt_id`: the runtime's acknowledgement of a dispatch, carrying the attempt ID it assigned | — |
| `response` | `kind` ∈ `ok`, `rejected`, `error`, `in_progress`, `conflict`; `op_key`, `attempt_id`; for `ok` also `payload_hash`, `effect_id` | `ok` positive (if correlated); `rejected`, `in_progress`, `conflict` terminal for that attempt; `error` no |
| `timeout` | `op_key`, `attempt_id` | no |
| `status` | `result` ∈ `found`, `not_found`; `op_key`; `found`: `effect_id`, `attempt_id`, `payload_hash`; `not_found`: `terminal_attempts` (and `pending_attempts` with option `status_lists_pending`) | `found` positive; each terminal attempt terminal; `not_found` itself no |
| `webhook` | `event` ∈ `processing`, `deferred`, `committed`, `aborted`; `event_id`, `provider_seq`, `op_key`, `attempt_id`; `committed` also `payload_hash`, `effect_id` | `committed` positive; `aborted` terminal; others progress |
| `timer` | `tag` (`poll`, `verify`, `reread`, or your own) | — |

## 3. Actions (policy output)

| Action | Meaning |
|---|---|
| `{"type": "dispatch"}` | The runtime assigns `attempt_id` (`<op_key>#a<k>`) and enforces the budget of 3. An optional `reason` is logged. |
| `{"type": "status_read"}` | Answered at t + 1 from records with record_time ≤ t − L. |
| `{"type": "set_timer", "delay": d, "tag": s}` | Returns as a `timer` observation at t + d, if t + d ≤ H. |

## 4. Replaying a recorded production trace

Convert your client log to one observation per line, using these mappings:

| In your log | Observation |
|---|---|
| request sent | a `dispatched` line with your attempt ID |
| HTTP reply | a `response` line (2xx with a result → `ok`; 409 or an idempotency "in progress" reply → `in_progress`; a refusal before execution → `rejected`; 5xx → `error`) |
| client timeout | a `timeout` line |
| status API answer | a `status` line |
| webhook | a `webhook` line |

Start the file with a `start` line. Then run:

```
python3 run_sim.py replay --observations my.jsonl --policy D
```

Each recorded observation is fed to the policy in order, and the command prints the actions the policy would have taken and its belief. The recording does not change in response: if the policy would have dispatched where your client did not, later lines still describe what really happened. See `examples/replay_example.jsonl`.
