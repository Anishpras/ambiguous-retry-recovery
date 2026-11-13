"""The single policy registry (v1.2): every name, role, display label, contract set, runtime key
mode and factory is defined here and nowhere else. `resolve()` also accepts "module:Class" or
"path/to/file.py:Class" for a user's own policy class (see examples/custom_policy.py).
"""
import importlib
import importlib.util
import inspect
import os
import sys

from . import policies

ENTRIES = [
    {"name": "A", "role": "core", "label": "A", "contracts": (1, 2), "kind": "client", "key_mode": "stable",
     "cls": policies.PolicyA},
    {"name": "B", "role": "core", "label": "B", "contracts": (1, 2), "kind": "client", "key_mode": "stable",
     "cls": policies.PolicyB},
    {"name": "Bw", "role": "core", "label": "Bw", "contracts": (1, 2), "kind": "client", "key_mode": "stable",
     "cls": policies.PolicyBw},
    {"name": "C", "role": "core", "label": "C", "contracts": (1, 2), "kind": "client", "key_mode": "stable",
     "cls": policies.PolicyC},
    {"name": "D", "role": "core", "label": "D", "contracts": (1, 2), "kind": "client", "key_mode": "stable",
     "cls": policies.PolicyD},
    {"name": "D+I", "role": "optional", "label": "D+I (optional)", "contracts": (1, 2), "kind": "client",
     "key_mode": "stable", "cls": policies.PolicyDI},
    {"name": "A-fk", "role": "ablation", "label": "A-fk (ablation)", "contracts": (2,), "kind": "client",
     "key_mode": "fresh", "cls": policies.PolicyA},
    # References read hidden state (arr/references.py). L3 (v1.2): ORACLE-S is a state probe, not a ceiling.
    {"name": "ORACLE-S", "role": "state-probe reference", "label": "ORACLE-S (state-probe reference, not a ceiling)",
     "contracts": (1, 2), "kind": "reference", "key_mode": "stable", "cls": None},
    {"name": "ORACLE-O", "role": "reference", "label": "ORACLE-O (outcome-oracle reference)",
     "contracts": (1, 2), "kind": "reference", "key_mode": "stable", "cls": None},
]
BY_NAME = dict((e["name"], e) for e in ENTRIES)
POLICIES = tuple(e["name"] for e in ENTRIES)
ROLE = dict((e["name"], e["role"]) for e in ENTRIES)
LABEL = dict((e["name"], e["label"]) for e in ENTRIES)
CONTRACTS_FOR = dict((e["name"], e["contracts"]) for e in ENTRIES)
REFERENCES = tuple(e["name"] for e in ENTRIES if e["kind"] == "reference")
CLIENT_POLICIES = tuple(e["name"] for e in ENTRIES if e["kind"] == "client")
ORDER = dict((name, i) for i, name in enumerate(POLICIES))


def construct(cls, contract, options):
    """Instantiate a policy class. Registered classes take (options) or, for D+I, (idempotent, options).
    A user class may take (), (options) or (idempotent_provider, options)."""
    if cls is policies.PolicyDI:
        return cls(contract == 2, options)
    try:
        n = len([p for p in inspect.signature(cls).parameters.values()
                 if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)])
    except (TypeError, ValueError):
        n = 1
    if n == 0:
        return cls()
    if n == 1:
        return cls(dict(options))
    return cls(contract == 2, dict(options))


def load_class(spec):
    """'package.module:Class' or 'path/to/file.py:Class' -> class object."""
    target, _, clsname = spec.rpartition(":")
    if not target or not clsname:
        raise ValueError("expected module:Class or file.py:Class, got %r" % spec)
    if target.endswith(".py") or os.sep in target:
        path = os.path.abspath(target)
        name = "user_policy_" + os.path.splitext(os.path.basename(path))[0]
        spec_obj = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec_obj)
        spec_obj.loader.exec_module(module)
    else:
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        module = importlib.import_module(target)
    return getattr(module, clsname)


def resolve(spec):
    """Registry entry for a name, or an ad-hoc entry for a user's class."""
    if spec in BY_NAME:
        return BY_NAME[spec]
    cls = load_class(spec)
    return {"name": spec, "role": "custom", "label": "%s (custom)" % spec, "contracts": (1, 2), "kind": "client",
            "key_mode": "stable", "cls": cls}
