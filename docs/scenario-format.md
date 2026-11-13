# Scenario format

A scenario is one JSON file describing a provider's behaviour for one or more logical operations. You run it with:

```
python3 run_sim.py explore --scenario my.json --contract 1|2 --policy NAME|module:Class
```

The frozen fixtures in `scenarios/S00–S15.json` use the same format. Keys starting with `_` are comments and are ignored everywhere.

## Top level

| Key | Meaning |
|---|---|
| `id`, `family`, `title` | Labels. `family` defaults to `custom`. |
| `status_lag` | An integer L, or `"never"`. A status read at tick t is answered at t + 1 from provider records with record_time ≤ t − L. |
| `options` | Named options, listed below. Omitted keys keep the frozen defaults. `--option key=value` on the command line overrides them. |
| `operations` | A list of logical operations. |
| `oracle` | Optional. Scripted dispatch times with expected effect histories, used by V1 for the frozen fixtures. |

## An operation

| Key | Meaning |
|---|---|
| `op_key` | Stable key used for every attempt. Under contract 2 it is the dedup key. |
| `start` | Tick of the first dispatch. The horizon is start + `horizon`. |
| `payload` | Immutable payload; its canonical SHA-256 is the `payload_hash`. |
| `attempts` | `{"1": {...}, "2": {...}}`: per-attempt overrides of the nominal rule. |

## An attempt script

Attempts that are not listed are **nominal**:

- arrives 1 tick after dispatch and is accepted;
- commits 1 tick after arrival;
- an `ok` response arrives 1 tick after the commit;
- a `committed` webhook arrives 2 ticks after emission.

With the option `retry_fault: copy_first`, unlisted attempts copy attempt 1 instead.

| Field | Meaning |
|---|---|
| `arrive` | Ticks from dispatch to arrival (≥ 1), or `null` for lost before arrival (no record, no terminal negative). |
| `decision` | `accept`, or `reject` (refused at arrival; never executes). |
| `commit_after` / `abort_after` | Ticks from arrival to commit or to abort (exactly one of the two). |
| `violation_commit_after` | With an abort: the provider commits anyway this many ticks after arrival, breaking its guarantee (S15). |
| `deferred_after` | An integer or a list: ticks after arrival at which a non-authoritative `deferred` webhook is emitted. |
| `response` | `null` for lost; otherwise `{"kind": "error", "after": 1}`. `kind` overrides the natural reply; `after` is ticks after the provider's decision. |
| `webhooks` | `{event: [delivery offsets after emission]}`. `[]` means emitted but lost; `[6, 7]` means delivered twice; `processing` and `deferred` are emitted only if listed. |

## Options

Defined in `arr/options.py` and `arr/policies.py`.

| Option | Default | Effect |
|---|---|---|
| `horizon` | 60 | Ticks the client has to answer. |
| `retry_fault` | `nominal` | `copy_first`: every retry repeats attempt 1's fault. |
| `status_lists_pending` | false | `not_found` also lists `pending_attempts`. |
| `abort_record` | `release` | Contract 2. `replay_failure`: after an abort, later attempts with the key are refused (`rejected`). |
| `dedup_record_at` | `acceptance` | Contract 2. `commit`: the record appears only at commit (unsafe; mutation test M3). |
| `dedup_window` | 1000 | Contract 2: ticks a record stays active. |
| `wait_tau` | 15 | Bw's wait. |
| `bw_skip_read_if_complete` | true | Bw, clarification C15. |
| `ignore_status_replies_once_complete` | true | A, B, Bw: revision v1.1.1. |
| `deferred_is_progress` | false | A, B, Bw: `deferred` is not a failure. |
| `ignore_failure_webhooks_once_complete` | false | A, B, Bw. |
| `in_progress_is_wait` | false | A, B, Bw: `in_progress` is not a failure. |
| `reread_on_pending` | false | B, Bw: a `not_found` that lists pending attempts means re-read in 5 ticks. |
| `use_provider_seq`, `dedupe_event_ids`, `check_payload`, `use_webhooks`, `use_status` | true | C, D, D+I ablation switches. |

## A fully commented example

This is `examples/scenario_example.json`. It runs as is:

```
python3 run_sim.py explore --scenario examples/scenario_example.json --contract 2 --policy D+I
```

```json
{
  "_comment": "Example scenario for `python3 run_sim.py explore`. Format: docs/scenario-format.md. Every key that starts with an underscore is a comment and is ignored.",
  "id": "EX1",
  "family": "example",
  "title": "Lost acknowledgement; receipt delayed 12 ticks; status lags 8 ticks and lists pending work; a failed key is burned",
  "_status_lag": "Status reads at tick t see provider records with record_time <= t - status_lag. Use \"never\" if status never shows anything before the final cutoff.",
  "status_lag": 8,
  "options": {
    "_comment": "Named options (arr/options.py). Omitted options keep the frozen protocol defaults.",
    "_status_lists_pending": "Does your status API list attempts it has accepted but not finished? true adds pending_attempts to not_found replies.",
    "status_lists_pending": true,
    "_abort_record": "Contract 2 only: after a failed (aborted) execution, is the idempotency key released (release) or does a later request with that key get the stored failure (replay_failure)?",
    "abort_record": "replay_failure",
    "_horizon": "How long (ticks after the operation starts) your agent waits before it must answer.",
    "horizon": 60
  },
  "operations": [
    {
      "_comment": "One logical operation: a stable op_key and an immutable payload. start = tick of the first dispatch.",
      "op_key": "send-welcome-42",
      "start": 0,
      "payload": {
        "contact_id": "ct-0042",
        "template_id": "tpl-welcome-01",
        "body_hash": "cc8ce02372a87ccf18abcb7a6118a132616c906d4385680453885313580f9d95"
      },
      "attempts": {
        "1": {
          "_comment": "Attempt 1 overrides the nominal rule (arrive +1, commit 1 tick after arrival, ok 1 tick after commit, committed receipt 2 ticks after emission). Attempts not listed are nominal unless options.retry_fault is copy_first.",
          "arrive": 1,
          "commit_after": 3,
          "_response": "null = the response is lost; {\"kind\": \"error\", \"after\": 1} would send a 5xx-style error instead of ok.",
          "response": null,
          "_webhooks": "Delivery offsets after each emission: [] = lost, [12, 13] = delivered twice. Add \"processing\" or \"deferred\" (with deferred_after) to emit progress events.",
          "webhooks": {
            "committed": [
              12
            ]
          }
        }
      }
    }
  ]
}
```
