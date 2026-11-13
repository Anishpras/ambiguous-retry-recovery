# Ambiguous retry recovery: a deterministic conformance suite

A small discrete-event simulation of a client's **recovery layer** after an ambiguous tool timeout. A synthetic "send message" call may or may not have executed. The provider's status replica lags, and its webhooks are delayed, duplicated, reordered, lost, or (in one labelled scenario) wrong. All data are synthetic. Python 3.9+ standard library only; no network and no randomness.

**What it is, and is not.** After an independent review, the study is best read as a **small, hand-checkable conformance suite with a sensitivity analysis**.

- **What it replicates.** In a deterministic model, it reproduces known results: naive retries and single stale reads duplicate effects; stable idempotency keys fix that; fresh keys per attempt undo it; and a lost request is indistinguishable from an unacknowledged commit.
- **What it is not.** It is **not** evidence that any policy "beats" another in a rate sense. The counts are over hand-authored cases, and the reconciler's safety follows from its rules (`docs/monotone-evidence.md`).

## 1. The frozen study

```
python3 run_sim.py
```

This single command does the following, and exits 0 only if every check passes:

1. Refuses to run unless the protocol, fixtures, baselines and sources match the latest `FREEZE.json` entry.
2. Runs validation V1–V6 and the unit, property and mutation tests.
3. Runs the core matrix (16 scenarios, 17 operations) and the secondary grids (120 schedules), under both provider contracts, for:
   - the client policies A, B, Bw, C, D and D+I;
   - the ablation A-fk;
   - the references ORACLE-S (a state probe, not a ceiling) and ORACLE-O.
4. Writes `results/`.

It takes about 15 seconds. `python3 run_sim.py --check-reproducible` runs everything twice in temporary directories and compares every byte (V7).

**The record.**

- **Design and history.** `PROTOCOL.md` holds the design, the hand-derived predictions (§7) and every clarification and revision.
- **Pre-specified results.** The v1.1.1 core results are the pre-specified record; they are kept byte-for-byte in `baselines/v1.1.1/`.
- **Revisions.** v1.1, v1.1.1 and v1.2 are post-freeze revisions, logged with their reasons. `results/revision_v1.1_delta.md` and `results/revision_v1.2_delta.md` list every value they changed. v1.2 changed no outcome in the core matrix; only latency reporting and labels changed.
- **Self-attestation.** The freeze is self-attested (no remote, no signed tag).

**Main outputs.**

| File | Contents |
|---|---|
| `results/headline.md` | contract × policy table; counts, not rates |
| `results/summary.csv` | one row per contract × policy × scenario × operation |
| `results/by_policy.csv`, `results/by_family.csv` | aggregates |
| `results/grid.csv`, `results/grid_tables.md` | the secondary grids |
| `results/predictions_check.md` | the §7 predictions against the run; a consistency check, not a confirmation rate |
| `results/worked_traces.md` | S04, S02 and S06 as three-column timelines |
| `results/ties.csv` | same-tick ties and the order applied |
| `results/traces/<contract>/<policy>/<scenario>.jsonl` | full event traces |
| `results/validation.json`, `results/run_info.json` | checks and run metadata |

`python3 run_sim.py --show 1 D S04` prints a readable trace of any cell, including grid IDs such as `G1_L4_W8` and exploratory IDs such as `PF2`.

## 2. Exploratory results (post-review, v1.2)

These are in `results/exploratory/`, labelled exploratory and not pre-specified.

| File | Contents |
|---|---|
| `ablations.md` | C and D with provider_seq, event_id dedupe or payload correlation switched off: no outcome changes in any core or grid cell. Ignoring webhooks or status costs latency and resolution. |
| `sensitivity.md` | every alternative rule from the review as a named option, with which conclusions flip and which survive |
| `persistent_faults.md` | the same fault on all three attempts (lost ack, lost request, abort) |
| `bw_boundary.md` | unit-step grids: wait-then-verify duplicates exactly when L ≥ τ + 4 and the receipt arrives at t ≥ τ + 7 (T = 5, commit at t = 2), i.e. safe when τ ≥ E_max + L_max − T |
| `escalation.md` | for every unresolved operation, the evidence that would resolve it |

## 3. Use it on your own provider

1. **Describe the provider.** Answer the questions in `docs/contract-checklist.md` and write them down as a scenario file (`docs/scenario-format.md`; a fully commented example is `examples/scenario_example.json`).
2. **Run any policy against it.** Built-in policies or your own class both work, with no freeze gate and no predictions:

   ```
   python3 run_sim.py explore --scenario my.json --contract 2 --policy D+I
   python3 run_sim.py explore --scenario my.json --policy examples/custom_policy.py:PatientReconciler
   python3 run_sim.py explore --scenario my.json --policy B --option status_lists_pending=true --option reread_on_pending=true
   ```

3. **Choose a policy.** `docs/decision-table.md` gives a choice for each set of answers. Every row cites the measured result or the argument behind it.
4. **Replay a recorded production trace** (observations only) through a policy, to see what it would have decided (`docs/trace-schema.md`):

   ```
   python3 run_sim.py replay --observations examples/replay_example.jsonl --policy D
   ```

Policies are registered in one place, `arr/registry.py`. A policy is any class with `observe(obs) -> [actions]`, `belief()` and, optionally, `report()`. It sees only deep-copied observation dicts.

## Layout

- **`arr/`**
  - Model: `sim.py` (event queue, tick phases), `provider.py` (contracts, records, lagged status, webhooks, private ledger), `client.py` (runtime: attempt IDs, budget, horizon, timeouts), `policies.py` (client policies; imports nothing), `references.py` (oracles, simulator side), `registry.py`, `options.py`, `scenarios.py`.
  - Analysis: `metrics.py`, `validate.py`, `predictions.py`, `report.py`, `delta.py`, `exploratory.py`.
- **`scenarios/`** frozen fixtures: S00–S15, `grids.json`, `matrix.json`, `sanity_labels.json`, and `exploratory/PF1–PF4`.
- **`baselines/`** byte-exact copies of committed v1.0, v1.1 and v1.1.1 results.
- **`tests/`** validation, property, mutation and command-line tests.
- **`docs/`** checklist, decision table, trace schema, scenario format, monotone-evidence argument.
- **`examples/`** custom policy, commented scenario, replay file.
- **`notes/`** hand-written interpretation, not frozen.
