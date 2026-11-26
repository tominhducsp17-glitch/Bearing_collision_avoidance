"""Mốc 3: backstepping (15)-(17), baseline M1 (62) = [L21] (27), closed loop with the plant."""
import ast
import copy
from pathlib import Path

import numpy as np
import pytest

from src.baselines.m1_model_based import M1Controller
from src.config import load_case
from src.low_level.backstepping import J3, tracking_errors, alpha_v_dot
from src.sim.integrators import rk4_step
from src.sim.runner import run_closed_loop

BETA = 2.0


def test_virtual_velocity_gives_exponential_position_error():
    """If nu = alpha_v (16), then z_eta_dot = J(psi) nu - eta_d_dot = -beta_eta z_eta."""
    rng = np.random.default_rng(3)
    for _ in range(10):
        eta, eta_d, ups_d = rng.normal(size=3), rng.normal(size=3), rng.normal(size=3)
        z, alpha, _ = tracking_errors(eta, np.zeros(3), eta_d, ups_d, BETA)
        z_dot = J3(eta[2]) @ alpha - J3(eta_d[2]) @ ups_d
        assert np.allclose(z_dot, -BETA * z)


def test_alpha_v_dot_matches_finite_difference():
    nu = lambda t: np.array([1 + 0.1 * np.sin(t), 0.2 * np.cos(t), 0.3 * np.sin(2 * t)])
    ups = lambda t: np.array([1.0, 0.1 * np.sin(t), 0.2 * np.cos(t)])
    ups_dot = lambda t: np.array([0.0, 0.1 * np.cos(t), -0.2 * np.sin(t)])
    f = lambda t, x: np.r_[J3(x[2]) @ nu(t), J3(x[5]) @ ups(t)]
    x, t, dt = np.array([0.0, 0.0, 0.3, 0.5, -0.2, 0.1]), 0.0, 1e-4
    alphas, adots = [], []
    for _ in range(2000):
        eta, eta_d = x[:3], x[3:]
        alphas.append(tracking_errors(eta, nu(t), eta_d, ups(t), BETA)[1])
        adots.append(alpha_v_dot(eta, nu(t), eta_d, ups(t), ups_dot(t), BETA))
        x = rk4_step(f, t, x, dt)
        t += dt
    fd = (np.array(alphas[2:]) - np.array(alphas[:-2])) / (2 * dt)
    assert np.allclose(fd, np.array(adots[1:-1]), atol=1e-6)


@pytest.fixture(scope="module")
def case1():
    return load_case("config/case1.yaml")


def test_m1_no_disturbance_tracks(case1):
    L = run_closed_loop(case1, M1Controller(), t_end=15.0, log_every=100, disturbance=False)
    assert np.abs(L["z_eta"][-1]).max() < 0.05
    assert np.abs(L["z_ups"][-1]).max() < 0.05


def test_m1_steady_velocity_error_matches_delta_over_k(case1):
    """M1 does not compensate delta: steady z_ups ≈ M-coupled solution of k z = delta.
    For surge (decoupled): z_u ≈ delta_u / k_u ≈ 3.05/20."""
    L = run_closed_loop(case1, M1Controller(), t_end=20.0, log_every=100)
    k = L["t"] > 17.0          # constant-scale phase
    z_u = L["z_ups"][k, :, 0].mean()
    assert z_u == pytest.approx(3.05 / 20, rel=0.15)


def test_controller_side_does_not_import_plant():
    """PROJECT_CONTEXT §5.2.4: only the plant, the simulators (runner, phase-1 episodes) and the
    baselines may import src.models.vessel (M, C, D)."""
    allowed = {"src/models/vessel.py", "src/sim/runner.py", "src/sim/episodes.py"}
    offenders = []
    for path in Path("src").rglob("*.py"):
        rel = path.as_posix()
        if rel in allowed or rel.startswith("src/baselines/"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "models.vessel" in node.module:
                offenders.append(rel)
            if isinstance(node, ast.Import) and any("models.vessel" in a.name for a in node.names):
                offenders.append(rel)
    assert offenders == []
