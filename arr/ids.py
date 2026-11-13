"""Canonical JSON, payload hashes and opaque identifiers (PROTOCOL.md §2.1)."""
import hashlib
import hmac
import json

from .constants import HMAC_KEY


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_hash(payload):
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _mac(parts):
    return hmac.new(HMAC_KEY, "\x1f".join(parts).encode("utf-8"), hashlib.sha256).hexdigest()


def effect_id(op_key, attempt_id):
    """First 12 hex characters of an HMAC of (op_key, attempt_id). Opaque: it depends only on the
    attempt's own identity, never on how many effects exist, so it leaks no ledger counts."""
    return _mac([op_key, attempt_id])[:12]


def event_id(op_key, attempt_id, event):
    """Opaque webhook emission ID; a duplicated delivery repeats it."""
    return "ev-" + _mac(["event", op_key, attempt_id, event])[:12]
