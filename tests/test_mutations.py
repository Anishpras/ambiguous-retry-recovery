"""Mutation tests (PROTOCOL.md §6). Each mutant must be caught by at least one check that the
real implementation passes. M5 is an extra mutant added by the implementer (clarification C1)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arr import policies, scenarios, validate  # noqa: E402
from arr.provider import Provider  # noqa: E402
from arr.runner import run_cell  # noqa: E402


# ---- M1: D treats `not_found` as authoritative for every dispatched attempt
class D_NotFoundAuthoritative(policies.PolicyD):
    def on_status(self, obs):
        if obs.get("result") == "not_found":
            for a in self.attempts:
                self.terminal.setdefault(a, []).append("MUTANT not_found")
        return policies.PolicyD.on_status(self, obs)


# ---- M2 (split in v1.2 after the independent review)
# M2a: provider_seq ignored. Not a mutant that should be caught: D's evidence store is monotone and
#      attempt-keyed, so this must change NOTHING. Asserted as a property in tests/test_v1_2.py.
# M2b: attempt correlation ignored: positives credited whatever the attempt; an `aborted` receipt for
#      any attempt marks every dispatched attempt terminal. This must be caught.
class D_IgnoreAttemptCorrelation(policies.PolicyD):
    def _correlated(self, obs):
        return obs.get("op_key") == self.op_key and obs.get("payload_hash") == self.payload_hash

    def _positive(self, obs, label):
        if self._correlated(obs):
            self.positive.setdefault(obs.get("attempt_id"), []).append("MUTANT " + label)

    def _terminal(self, attempt_id, obs, label):
        for a in self.attempts:
            self.terminal.setdefault(a, []).append("MUTANT " + label)


# ---- M3: contract-2 dedup record created at commit instead of acceptance
class DedupAtCommit(Provider):
    def _dedup_on_accept(self, att):
        pass

    def _dedup_on_commit(self, att, eid):
        self.dedup[att.op_key] = {"attempt_id": att.attempt_id, "payload_hash": att.payload_hash,
                                  "state": "committed", "effect_id": eid, "created": self.sim.now}


# ---- M4: sequential effect IDs (still 12 hex characters, so only the leak can catch it)
class SequentialEffectIds(Provider):
    def effect_id(self, op_key, attempt_id):
        return "%012x" % (len(self.ledger) + 1)


# ---- M5: provider_seq as a running per-op count
class CountingSeq(Provider):
    def provider_seq(self, att, event):
        self._count = getattr(self, "_count", {})
        self._count[att.op_key] = self._count.get(att.op_key, 0) + 1
        return self._count[att.op_key]


def effects(scn_id, contract, policy, **kw):
    sim = run_cell(scenarios.load_scenario(scn_id), contract, policy, **kw)
    return len(sim.provider.ledger)


def failing(checks):
    return [c["check"] for c in checks if not c["ok"]]


class MutationTests(unittest.TestCase):
    def test_m1_not_found_authoritative(self):
        self.assertEqual(effects("S04", 1, "D"), 1)
        self.assertEqual(effects("S04", 1, "D", policy_classes={"D": D_NotFoundAuthoritative}), 2)
        self.assertFalse(failing(validate.check_v3()))
        self.assertTrue(failing(validate.check_v3({"D": D_NotFoundAuthoritative})))

    def test_m2b_ignore_attempt_correlation_is_caught(self):
        self.assertFalse(failing(validate.check_v3()))
        caught = failing(validate.check_v3({"D": D_IgnoreAttemptCorrelation}))
        self.assertIn("V3_D_uncorrelated_positives_ignored", caught)

    def test_m3_dedup_record_at_commit(self):
        self.assertFalse(failing(validate.check_v1()))
        caught = failing(validate.check_v1(DedupAtCommit))
        self.assertTrue(caught)
        sim = validate.run_scripted(scenarios.load_scenario("S05"), 2, [{"op": "op-1", "t": 0}, {"op": "op-1", "t": 5}],
                                    provider_cls=DedupAtCommit)
        self.assertEqual(len(sim.provider.ledger), 2)   # duplicates in S05
        # v1.2: the same fault is also available as the named option dedup_record_at=commit
        sim = validate.run_scripted(scenarios.load_scenario("S05"), 2, [{"op": "op-1", "t": 0}, {"op": "op-1", "t": 5}],
                                    options={"dedup_record_at": "commit"})
        self.assertEqual(len(sim.provider.ledger), 2)

    def test_m4_sequential_effect_ids(self):
        twins, _ = validate.check_twins()
        self.assertFalse(failing(twins))
        twins, _ = validate.check_twins(provider_cls=SequentialEffectIds)
        self.assertTrue(failing(twins))

    def test_m5_counting_provider_seq_leaks(self):
        twins, _ = validate.check_twins(provider_cls=CountingSeq)
        self.assertTrue(failing(twins))


if __name__ == "__main__":
    unittest.main()
