"""V1-V5 as unit tests, plus a few direct checks of tick ordering and isolation."""
import ast
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arr import constants as K  # noqa: E402
from arr import scenarios, validate  # noqa: E402
from arr.runner import effect_history, run_scripted  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ValidationChecks(unittest.TestCase):
    def assertChecks(self, checks):
        bad = [(c["check"], c["detail"]) for c in checks if not c["ok"]]
        self.assertEqual(bad, [])

    def test_v1(self):
        self.assertChecks(validate.check_v1())

    def test_v2(self):
        self.assertChecks(validate.check_v2())

    def test_v3(self):
        self.assertChecks(validate.check_v3())

    def test_v4_and_v5(self):
        checks, sims = validate.check_v4()
        self.assertChecks(checks + validate.check_v5(sims, "twins"))


class OrderingAndIsolation(unittest.TestCase):
    def test_phase1_tie_resolved_by_scheduling_counter(self):
        # S02 with a resend at t = 2: a1's abort (scheduled at t = 1) and a2's arrival (scheduled
        # at t = 2) both fall in phase 1 of t = 3; the abort runs first and releases the record.
        sim = run_scripted(scenarios.load_scenario("S02"), 2, [{"op": "op-1", "t": 0}, {"op": "op-1", "t": 2}])
        self.assertEqual(effect_history(sim), [["op-1#a2", 4]])
        tie = [x for x in sim.ties if x["t"] == 3 and x["phase"] == 1]
        self.assertEqual(tie[0]["order"], ["abort:a1", "arrival:a2"])

    def test_references_live_outside_the_policy_module(self):
        with open(os.path.join(ROOT, "arr", "policies.py"), encoding="utf-8") as fh:
            names = {n.name for n in ast.walk(ast.parse(fh.read())) if isinstance(n, ast.ClassDef)}
        self.assertFalse(any("Oracle" in n for n in names))

    def test_effect_ids_independent_of_ledger_order(self):
        s08 = run_scripted(scenarios.load_scenario("S08"), 1, [{"op": "op-1", "t": 0}, {"op": "op-1", "t": 5}])
        s09 = run_scripted(scenarios.load_scenario("S09"), 1, [{"op": "op-1", "t": 0}, {"op": "op-1", "t": 5}])
        a2_08 = [e["effect_id"] for e in s08.provider.ledger if e["attempt_id"] == "op-1#a2"]
        a2_09 = [e["effect_id"] for e in s09.provider.ledger if e["attempt_id"] == "op-1#a2"]
        self.assertEqual(a2_08, a2_09)

    def test_constants(self):
        self.assertEqual((K.TIMEOUT, K.BUDGET, K.HORIZON, K.FINAL, K.POLL_INTERVAL, K.WAIT_TAU),
                         (5, 3, 60, 200, 5, 15))


if __name__ == "__main__":
    unittest.main()
