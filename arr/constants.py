"""Frozen run constants (PROTOCOL.md §2.2, §3). Every frozen run uses exactly these values (V5).

Policy names, roles and factories live in arr/registry.py (the single policy registry); named
alternative rules (sensitivity options) live in arr/options.py.
"""

TIMEOUT = 5            # client timeout T, ticks after dispatch, if no response for that attempt arrived
BUDGET = 3             # dispatches per logical operation
HORIZON = 60           # H: ticks after the operation starts; belief at H is the final answer
FINAL = 200            # F: final scoring cutoff (absolute tick)
POLL_INTERVAL = 5      # C, D, D+I status poll interval
WAIT_TAU = 15          # Bw wait before its single status read
ORACLE_INTERVAL = 5    # ORACLE-S / ORACLE-O periodic decision points
DEDUP_WINDOW = 1000    # contract 2 window W; covers the whole experiment

CONTRACTS = (1, 2)
FIXTURE_VERSION = "1.0.0"
STUDY_VERSION = "v1.2"

# Fixed simulator key for opaque IDs (§2.1). Not a secret; it only makes IDs non-sequential.
HMAC_KEY = b"arr-pilot/fixed-simulator-key/v1"

PARITY = {"timeout": TIMEOUT, "budget": BUDGET, "horizon": HORIZON, "final": FINAL,
          "poll_interval": POLL_INTERVAL, "wait_tau": WAIT_TAU, "oracle_interval": ORACLE_INTERVAL,
          "dedup_window": DEDUP_WINDOW}

# Environment options (scenario, provider, client). Defaults reproduce the frozen protocol.
ENV_DEFAULTS = {
    "horizon": HORIZON,                 # client horizon H (ticks after the operation start)
    "retry_fault": "nominal",           # "nominal": attempts >= 2 follow the nominal rule;
                                        # "copy_first": every attempt copies attempt 1's fault script
    "status_lists_pending": False,      # status `not_found` also lists attempts the replica shows as pending
    "abort_record": "release",          # contract 2: "release" (an aborted record frees the key) or
                                        # "replay_failure" (later attempts with the key are refused: `rejected`)
    "dedup_record_at": "acceptance",    # contract 2: "acceptance" (protocol) or "commit" (mutant M3 as an option)
    "dedup_window": DEDUP_WINDOW,       # contract 2: ticks a record stays active after creation
}
ENV_CHOICES = {"retry_fault": ("nominal", "copy_first"), "abort_record": ("release", "replay_failure"),
               "dedup_record_at": ("acceptance", "commit")}
