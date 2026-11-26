"""Load a case YAML (config/case*.yaml) into plain Python/numpy objects."""
import math
import numpy as np
import yaml

_ALLOWED = {"pi": math.pi, "sqrt": math.sqrt}


def _num(x):
    """Numbers pass through; strings like "pi/4" or "sqrt(2)/2" are evaluated with
    only `pi` and `sqrt` available."""
    if isinstance(x, str):
        return float(eval(x, {"__builtins__": {}}, _ALLOWED))
    return float(x)


def load_case(path):
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    g = cfg["graph"]
    g["bearings"] = {(int(i), int(j)): np.array([_num(c) for c in gij])
                     for i, j, gij in g["bearings"]}
    eta0 = {int(k): np.array([_num(c) for c in v]) for k, v in cfg["initial"]["eta"].items()}
    cfg["initial"]["eta"] = eta0
    cfg["n"] = len(eta0)
    hl = cfg.get("high_level", {})
    if "psi0" in hl:
        hl["psi0"] = _num(hl["psi0"])
    if "v_c" in hl:
        hl["v_c"] = np.array([_num(c) for c in hl["v_c"]])
    return cfg
