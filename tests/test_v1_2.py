"""v1.2 (post-review) tests: monotone-evidence property (M2a), fixes L4 and M1, the registry, options,
and the explore / replay commands."""
import io
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from arr import metrics, options, policies, registry, scenarios, validate  # noqa: E402
from arr.runner import run_cell  # noqa: E402

KEYS = ("effects_H", "effects_F", "belief_H", "dispatches", "ttc_any_complete", "conflicts")


def outcomes(policy, opts=None):
    out = []
    for scn in scenarios.load_core() + scenarios.build_grids():
        for c in (1, 2):
            sim = run_cell(scn, c, policy, options=opts)
            out += [tuple(r[k] for k in KEYS) for r in metrics.cell_results(sim, scn, c, policy)]
    return out


class MonotoneEvidenceProperty(unittest.TestCase):
    """M2a and the event-id half of H1: for a monotone, attempt-keyed reconciler, ignoring provider_seq or
    event_id de-duplication changes no outcome in any core or grid cell (docs/monotone-evidence.md)."""

    def test_seq_and_dedupe_irrelevant_for_C_and_D(self):
        for pol in ("C", "D"):
            base = outcomes(pol)
            self.assertEqual(base, outcomes(pol, {"use_provider_seq": False}), pol)
            self.assertEqual(base, outcomes(pol, {"dedupe_event_ids": False}), pol)


class Fixes(unittest.TestCase):
    def test_L4_bw_unresolved_while_verify_pending(self):
        d = validate.Driver(policies.PolicyBw())
        d.feed({"type": "webhook", "event": "deferred", "provider_seq": 2000, "event_id": "ev-d", "op_key": "op-1",
                "attempt_id": d.aid(1), "t": 3})
        self.assertEqual(d.policy.belief(), "unresolved")
        self.assertTrue(d.policy.waiting)
        d = validate.Driver(policies.PolicyA())
        d.feed({"type": "webhook", "event": "deferred", "provider_seq": 2000, "event_id": "ev-d", "op_key": "op-1",
                "attempt_id": d.aid(1), "t": 3})
        self.assertEqual(d.policy.belief(), "failed")   # A unchanged

    def test_M1_di_resends_after_error_in_scenario(self):
        # the review's P4: commit, `error` response, webhooks lost, L = never, contract 2
        scn = validate.adhoc("p4", {"response": {"kind": "error"}, "webhooks": {"committed": []}}, lag="never")
        r = metrics.cell_results(run_cell(scn, 2, "D+I"), scn, 2, "D+I")[0]
        self.assertEqual((r["effects_F"], r["belief_H"]), (1, "complete"))


class RegistryAndOptions(unittest.TestCase):
    def test_single_registry(self):
        self.assertEqual(registry.POLICIES, ("A", "B", "Bw", "C", "D", "D+I", "A-fk", "ORACLE-S", "ORACLE-O"))
        self.assertIn("not a ceiling", registry.LABEL["ORACLE-S"])
        cls = registry.resolve(os.path.join(ROOT, "examples", "custom_policy.py") + ":PatientReconciler")["cls"]
        self.assertTrue(hasattr(registry.construct(cls, 1, options.DEFAULTS), "observe"))

    def test_options_validated_and_defaults_frozen(self):
        with self.assertRaises(KeyError):
            options.merge({"no_such_option": 1})
        with self.assertRaises(ValueError):
            options.merge({"abort_record": "explode"})
        self.assertEqual(options.DEFAULTS["horizon"], 60)
        self.assertEqual(options.DEFAULTS["wait_tau"], 15)

    def test_copy_first_repeats_attempt_one(self):
        op = scenarios.load_scenario("S09")["operations"][0]
        self.assertIsNone(scenarios.resolve_attempt(op, 3, "copy_first")["arrive"])
        self.assertEqual(scenarios.resolve_attempt(op, 3)["arrive"], 1)


class CommandLine(unittest.TestCase):
    def run_cmd(self, *args):
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "run_sim.py")] + list(args), cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.returncode, proc.stdout.decode("utf-8")

    def test_explore_builtin_and_custom(self):
        scn = os.path.join(ROOT, "examples", "scenario_example.json")
        code, out = self.run_cmd("explore", "--scenario", scn, "--contract", "2", "--policy", "D+I", "--quiet")
        self.assertEqual(code, 0, out)
        self.assertIn("metrics op=", out)
        code, out = self.run_cmd("explore", "--scenario", scn, "--policy",
                                 os.path.join(ROOT, "examples", "custom_policy.py") + ":PatientReconciler")
        self.assertEqual(code, 0, out)
        self.assertIn("(custom)", out)

    def test_replay(self):
        code, out = self.run_cmd("replay", "--observations", os.path.join(ROOT, "examples", "replay_example.jsonl"),
                                 "--policy", "D")
        self.assertEqual(code, 0, out)
        self.assertIn("final belief: complete", out)


if __name__ == "__main__":
    unittest.main()
