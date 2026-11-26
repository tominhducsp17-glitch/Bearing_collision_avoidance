"""Bearing geometry checks (PROJECT_CONTEXT §5.4.1): Eqs. (6)-(8)."""
import numpy as np
import pytest

from src.config import load_case
from src.graph.bearing import (projection, bearing_laplacian, partition, check_ff_invertible,
                               target_follower_positions, bearings_from_positions)

TARGETS = {  # expected p* (Section 4): square side 9 (Case 1), rectangle 18 x 9 (Case 2)
    "case1": {3: (1, 0), 4: (1, -9)},
    "case2": {3: (1, 0), 4: (1, -9), 5: (-8, 0), 6: (-8, -9)},
}
LAMBDA_MIN = {"case1": 0.145, "case2": 0.039}


def _setup(name):
    cfg = load_case(f"config/{name}.yaml")
    n, nl = cfg["n"], cfg["graph"]["n_leaders"]
    B = bearing_laplacian(n, cfg["graph"]["bearings"])
    p_l = np.concatenate([cfg["initial"]["eta"][i][:2] for i in range(1, nl + 1)])
    return cfg, n, nl, B, p_l


def test_projection_properties():
    g = np.array([0.6, 0.8])
    P = projection(g)
    assert np.allclose(P @ g, 0)
    assert np.allclose(P @ P, P) and np.allclose(P, P.T)
    assert np.allclose(projection(-g), P)


@pytest.mark.parametrize("name", ["case1", "case2"])
def test_laplacian_structure(name):
    cfg, n, nl, B, p_l = _setup(name)
    assert np.allclose(B, B.T)
    assert np.linalg.eigvalsh(B).min() > -1e-12
    ones = np.kron(np.ones(n), np.eye(2))           # translation null space
    assert np.allclose(B @ ones.T, 0)


@pytest.mark.parametrize("name", ["case1", "case2"])
def test_ff_invertible_and_target_positions(name):
    cfg, n, nl, B, p_l = _setup(name)
    _, _, B_fl, B_ff = partition(B, nl)
    lam = check_ff_invertible(B_ff)
    assert lam == pytest.approx(LAMBDA_MIN[name], abs=1e-3)
    p_f = target_follower_positions(p_l, B_fl, B_ff).reshape(-1, 2)
    for k, i in enumerate(range(nl + 1, n + 1)):
        assert np.allclose(p_f[k], TARGETS[name][i], atol=1e-9)
    # B p* = 0 (Section 3), and bearings of p* reproduce g* of the config
    p_star = np.concatenate([p_l, p_f.ravel()])
    assert np.allclose(B @ p_star, 0, atol=1e-9)
    assert np.allclose(B @ (3.0 * p_star + np.tile([5.0, -2.0], n)), 0, atol=1e-8)  # scale + shift
    g = bearings_from_positions(p_star, cfg["graph"]["bearings"].keys())
    for e, g_star in cfg["graph"]["bearings"].items():
        assert np.allclose(g[e], g_star, atol=1e-12), e


def test_singular_B_ff_is_detected():
    # follower 3 linked only to leader 1: its position along g*_31 is undetermined
    B = bearing_laplacian(3, {(3, 1): np.array([1.0, 0.0]), (1, 2): np.array([0.0, 1.0])})
    with pytest.raises(ValueError):
        check_ff_invertible(partition(B, 2)[3])
