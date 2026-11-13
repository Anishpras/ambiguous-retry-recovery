"""Named options: every alternative rule used by the sensitivity analysis and by `explore` is a
key here, set in a scenario file ("options": {...}), on the command line (--option key=value) or by
the exploratory runner. The defaults reproduce the frozen protocol exactly (V5 checks this).
"""
from . import constants as K
from . import policies

DEFAULTS = dict(K.ENV_DEFAULTS)
DEFAULTS.update(policies.POLICY_DEFAULTS)


def merge(*layers):
    out = dict(DEFAULTS)
    for layer in layers:
        for key, val in (layer or {}).items():
            if key.startswith("_"):
                continue   # comment keys in scenario files
            if key not in DEFAULTS:
                raise KeyError("unknown option %r (known: %s)" % (key, ", ".join(sorted(DEFAULTS))))
            if key in K.ENV_CHOICES and val not in K.ENV_CHOICES[key]:
                raise ValueError("option %s must be one of %s" % (key, K.ENV_CHOICES[key]))
            if isinstance(DEFAULTS[key], bool) and not isinstance(val, bool):
                raise ValueError("option %s must be true or false" % key)
            if isinstance(DEFAULTS[key], int) and not isinstance(DEFAULTS[key], bool) and (
                    not isinstance(val, int) or isinstance(val, bool) or val < 1):
                raise ValueError("option %s must be a positive integer" % key)
            out[key] = val
    return out


def parse_cli(pairs):
    """['key=value', ...] -> dict, with JSON-ish values (true/false/integers/strings)."""
    out = {}
    for pair in pairs or []:
        key, _, raw = pair.partition("=")
        if raw in ("true", "false"):
            val = raw == "true"
        elif raw.lstrip("-").isdigit():
            val = int(raw)
        else:
            val = raw
        out[key.strip()] = val
    return out


def non_default(opts):
    return dict((k, v) for k, v in sorted(opts.items()) if DEFAULTS.get(k) != v)
