"""High level alone, perfect tracking (PROJECT_CONTEXT §5.4.2): Eqs. (9)-(14), (63)."""
import copy

import numpy as np
import pytest

from src.config import load_case
from src.high_level.followers import accel_to_Xi, rot2, S2
from src.high_level.leaders import formation_scale
from src.high_level.scaling import PiecewiseScaling
from src.metrics import bearing_error
from src.safety.base import IdentityFilter
from src.sim.runner import run_perfect_tracking


@pytest.fixture(scope="module")
def case1():
    return load_case("config/case1.yaml")


def test_schedule_eq63():
    s = PiecewiseScaling([[0, 15, 0.073], [15, 25, 0.0], [25, 40, -0.073]])
    assert s.beta_s(0.0) == 0.073 and s.beta_s(15.0) == 0.073
    assert s.beta_s(15.001) == 0.0 and s.beta_s(25.0) == 0.0
    assert s.beta_s(30.0) == -0.073 and s.beta_s(41.0) == 0.0


def test_leaders_centroid_and_scale(case1):
    """Leaders alone (Eq. (9)): c(p*) moves at v_c exactly; s(p*) = s0 exp(int beta)."""
    L = run_perfect_tracking(case1, t_end=20.0, log_every=100)
    t, ps = L["t"], L["p_star"]
    c = ps.mean(axis=1)
    assert np.allclose(c - c[0], t[:, None] * case1["high_level"]["v_c"], atol=1e-8)
    s = np.array([formation_scale(p) for p in ps])
    int_beta = np.where(t <= 15, 0.073 * t, 0.073 * 15)
    # O(dt) error from the RK stage that straddles the jump of beta_s at t = 15 s
    assert np.allclose(s, s[0] * np.exp(int_beta), rtol=1e-4)


def test_virtual_vessel_realises_Pi():
    """Eq. (12) guarantees p_d_ddot = Pi for any psi_d, omega_d, theta_d."""
    rng = np.random.default_rng(0)
    for _ in range(10):
        psi, om, th, Pi = rng.normal(), rng.normal(), rng.normal(size=2), rng.normal(size=2)
        Xi = accel_to_Xi(Pi, psi, om, th)
        p_ddot = om * rot2(psi) @ S2 @ th + rot2(psi) @ Xi       # d/dt (R theta)
        assert np.allclose(p_ddot, Pi)


def test_logged_acceleration_matches_Pi(case1):
    L = run_perfect_tracking(case1, t_end=0.2, log_every=1)
    dt = case1["sim"]["dt"]
    acc = np.diff(L["p_dot"][:, 2:], axis=0) / dt            # followers only
    assert np.allclose(acc, L["Pi"][:-1], atol=1e-6 * np.abs(L["Pi"]).max())


def test_heading_consensus_converges(case1):
    L = run_perfect_tracking(case1, t_end=1.0, log_every=100)
    assert np.allclose(L["psi"][-1], case1["high_level"]["psi0"], atol=1e-6)


def _static(cfg):
    c = copy.deepcopy(cfg)
    c["high_level"]["v_c"] = np.zeros(2)
    c["high_level"]["scaling"] = [[0, 1e9, 0.0]]
    return c


def test_static_leaders_damping_matches_linear_analysis(case1):
    """Static leaders: with k_v = 20 the bearing error dies out; with Paper A's k_v = 0.1
    (zeta ~ 0.01, assumptions.md K2) it is still large after 20 s."""
    cfg = _static(case1)
    for k_v, expect_small in ((20.0, True), (0.1, False)):
        L = run_perfect_tracking(cfg, k_v=k_v, t_end=20.0, log_every=500)
        e_end = bearing_error(L["p"][-1], L["formation"].bearings)
        assert (e_end < 1e-4) == expect_small, (k_v, e_end)


def test_safety_filter_hook_is_used(case1):
    """A filter that zeroes Pi freezes the followers (theta_d(0) = 0): the hook is live."""
    class Zero(IdentityFilter):
        def filter(self, Pi_nom, virtual_states, env, t):
            return {i: np.zeros(2) for i in Pi_nom}, {"zeroed": True}
    L = run_perfect_tracking(case1, safety_filter=Zero(), t_end=1.0, log_every=100)
    assert np.allclose(L["p"][-1, 2:], L["p"][0, 2:])
