# Ambiguous retry recovery: a deterministic pilot

A small discrete-event simulation of a client's **recovery layer** after an ambiguous tool timeout:
a synthetic CRM "send message" call may or may not have executed, the provider's status replica lags,
and its webhooks are delayed, duplicated, reordered, lost or (in one labelled scenario) wrong. It
compares retry policies A, B, Bw, C, D, D+I, the ablation A-fk and two hidden-state references
(ORACLE-S, ORACLE-O) under two provider contracts (no deduplication; deduplication keyed on a stable
op_key). The design, predictions and every clarification are in `PROTOCOL.md`; all data are synthetic.

## One command

    python3 run_sim.py

Python 3.9+ standard library only; no network, no randomness. It refuses to run unless the source,
fixtures and protocol match the latest entry in `FREEZE.json`, runs validation V1-V6 plus the unit and
mutation tests, runs the core matrix (16 scenarios, 17 operations) and the secondary grids (120
schedules) under both contracts, and exits 0 only if every check passes. Runtime: a few seconds.

Other commands: `--validate` (pre-freeze checks only), `--check-reproducible` (V7: two runs in temp
directories, byte comparison, also against `results/`), `--show <contract> <policy> <scenario>`
(readable trace of one cell; grid IDs such as `G1_L4_W8` work too), `--freeze --label vX --note "..."`.

## Layout

- `arr/` simulator: `sim.py` (event queue, tick phases), `provider.py` (contracts, records, lagged status,
  webhooks, private ledger), `client.py` (runtime: attempt IDs, budget, horizon, timeouts, deep-copied
  observations), `policies.py` (client policies; imports nothing), `references.py` (oracles; simulator side),
  `scenarios.py`, `metrics.py`, `validate.py`, `predictions.py`, `report.py`
- `scenarios/` frozen fixtures: `S00`-`S15` (script, expected effect histories under scripted dispatch times,
  evidence sentence), `grids.json`, `matrix.json`, `sanity_labels.json`
- `tests/` unit tests and mutation tests
- `notes/prediction_explanations.md` hand-written, post-run explanations of prediction mismatches (not frozen)

## Outputs (`results/`)

`headline.md` (contract x policy table), `summary.csv` (one row per contract x policy x scenario x operation),
`by_policy.csv`, `by_family.csv`, `grid.csv`, `grid_tables.md`, `predictions_check.md`, `worked_traces.md`
(S04, S02, S06 as three-column timelines), `ties.csv`, `validation.json`, `run_info.json`, and
`traces/<contract>/<policy>/<scenario>.jsonl` (one event per line: time, phase, event, visibility to the
client, details).
