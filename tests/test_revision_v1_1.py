"""Revision v1.1: once `complete`, A, B and Bw ignore request-path failure signals (local timeouts;
`error`, `in_progress`, `rejected` responses); webhooks keep 'last terminal-looking event wins'."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arr import policies, validate  # noqa: E402


def committed(d, t):
    return {"type": "webhook", "event": "committed", "provider_seq": 100 * t, "event_id": "ev-c", "op_key": "op-1",
            "attempt_id": d.aid(1), "payload_hash": d.ph, "effect_id": "e1", "t": t}


class RequestPathIgnoredAfterComplete(unittest.TestCase):
    def test_request_path_signals_ignored_once_complete(self):
        for cls in (policies.PolicyA, policies.PolicyB, policies.PolicyBw):
            d = validate.Driver(cls())
            d.feed(committed(d, 3))
            self.assertEqual(d.policy.belief(), "complete")
            acts = d.feed({"type": "timeout", "op_key": "op-1", "attempt_id": d.aid(1), "t": 5})
            for kind in ("error", "in_progress", "rejected"):
                acts += d.feed({"type": "response", "kind": kind, "op_key": "op-1", "attempt_id": d.aid(1), "t": 6})
            self.assertEqual(acts, [], cls.name)
            self.assertEqual((d.k, d.policy.belief()), (1, "complete"), cls.name)

    def test_webhooks_still_last_terminal_looking_event_wins(self):
        for cls, expect in ((policies.PolicyA, "dispatch"), (policies.PolicyB, "status_read"),
                            (policies.PolicyBw, "set_timer")):
            for event in ("aborted", "deferred"):
                d = validate.Driver(cls())
                d.feed(committed(d, 3))
                acts = d.feed({"type": "webhook", "event": event, "provider_seq": 400, "event_id": "ev-x",
                               "op_key": "op-1", "attempt_id": d.aid(1), "t": 4})
                self.assertEqual(d.policy.belief(), "failed", (cls.name, event))
                self.assertEqual([a["type"] for a in acts], [expect], (cls.name, event))

    def test_request_path_signals_still_act_before_completion(self):
        d = validate.Driver(policies.PolicyA())
        d.feed({"type": "timeout", "op_key": "op-1", "attempt_id": d.aid(1), "t": 5})
        self.assertEqual(d.k, 2)


if __name__ == "__main__":
    unittest.main()
