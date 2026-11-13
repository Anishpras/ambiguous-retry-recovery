"""Build and run one simulation: scenario x contract x policy (or a scripted dispatch plan)."""
from . import registry
from .client import PolicyClient, ScriptedClient
from .provider import Provider
from .references import ReferenceClient
from .sim import Sim


def run_cell(scenario, contract, policy_name, provider_cls=Provider, policy_classes=None, options=None):
    """Run every operation of `scenario` under one policy.

    `policy_name` is a registry name or "module:Class" / "file.py:Class" (a user's own policy).
    `policy_classes` lets tests substitute mutant classes by name; `provider_cls` a mutant provider;
    `options` sets named options (arr/options.py) on top of the scenario's own."""
    sim = Sim(scenario, contract, provider_cls, options)
    sim.policy_name = policy_name
    entry = registry.resolve(policy_name)
    for op in scenario["operations"]:
        if entry["kind"] == "reference":
            client = ReferenceClient(sim, op, policy_name)
        else:
            cls = (policy_classes or {}).get(policy_name, entry["cls"])
            policy = registry.construct(cls, contract, sim.options)
            client = PolicyClient(sim, op, policy, policy_name, key_mode=entry["key_mode"])
        sim.add_client(client)
    return sim.run()


def run_scripted(scenario, contract, plan, provider_cls=Provider, payload_overrides=None, options=None):
    """Policy-free run: `plan` is a list of {"op": op_key, "t": tick}; dispatches happen at exactly
    those times whatever is observed (V1 oracle checks, V2 contract basics)."""
    sim = Sim(scenario, contract, provider_cls, options)
    sim.policy_name = "scripted"
    times = {}
    for step in plan:
        times.setdefault(step["op"], []).append(step["t"])
    for op in scenario["operations"]:
        if op["op_key"] in times:
            sim.add_client(ScriptedClient(sim, op, sorted(times[op["op_key"]]),
                                          (payload_overrides or {}).get(op["op_key"])))
    return sim.run()


def effect_history(sim, logical_op=None):
    """[[attempt_id, commit_time], ...] sorted by (commit_time, attempt_id)."""
    rows = [[e["attempt_id"], e["commit_time"]] for e in sim.provider.ledger
            if logical_op is None or e["logical_op"] == logical_op]
    return sorted(rows, key=lambda r: (r[1], r[0]))
