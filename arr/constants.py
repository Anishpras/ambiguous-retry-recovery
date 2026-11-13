"""Frozen run constants (PROTOCOL.md §2.2, §3). Every run uses exactly these values (V5)."""

TIMEOUT = 5            # client timeout T, ticks after dispatch, if no response for that attempt arrived
BUDGET = 3             # dispatches per logical operation
HORIZON = 60           # H: ticks after the operation starts; belief at H is the final answer
FINAL = 200            # F: final scoring cutoff (absolute tick)
POLL_INTERVAL = 5      # C, D, D+I status poll interval
WAIT_TAU = 15          # Bw wait before its single status read
ORACLE_INTERVAL = 5    # ORACLE-S / ORACLE-O periodic decision points
DEDUP_WINDOW = 1000    # contract 2 window W; covers the whole experiment, expiry not modelled

CONTRACTS = (1, 2)
FIXTURE_VERSION = "1.0.0"

# Fixed simulator key for opaque IDs (§2.1). Not a secret; it only makes IDs non-sequential.
HMAC_KEY = b"arr-pilot/fixed-simulator-key/v1"

# Policy names in report order, their role, and the contracts they run under.
POLICIES = ("A", "B", "Bw", "C", "D", "D+I", "A-fk", "ORACLE-S", "ORACLE-O")
ROLE = {
    "A": "core", "B": "core", "Bw": "core", "C": "core", "D": "core",
    "D+I": "optional", "A-fk": "ablation", "ORACLE-S": "reference", "ORACLE-O": "reference",
}
REFERENCES = ("ORACLE-S", "ORACLE-O")
CLIENT_POLICIES = tuple(p for p in POLICIES if p not in REFERENCES)
CONTRACTS_FOR = {p: (1, 2) for p in POLICIES}
CONTRACTS_FOR["A-fk"] = (2,)   # ablation reported under contract 2 only

PARITY = {"timeout": TIMEOUT, "budget": BUDGET, "horizon": HORIZON, "final": FINAL,
          "poll_interval": POLL_INTERVAL, "wait_tau": WAIT_TAU, "oracle_interval": ORACLE_INTERVAL,
          "dedup_window": DEDUP_WINDOW}
