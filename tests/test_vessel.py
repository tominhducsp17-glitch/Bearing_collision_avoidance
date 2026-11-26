"""Plant checks (PROJECT_CONTEXT §5.4.3): Eqs. (1)-(2), parameters p. 18."""
import numpy as np
import pytest

from src.models.vessel import M, J, coriolis, damping, vessel_rhs, Disturbance
from src.sim.integrators import rk4_step


def test_mass_matrix_symmetric_positive_definite():
    assert np.allclose(M, M.T)
    assert np.linalg.eigvalsh(M).min() > 0


def test_coriolis_is_skew_symmetric_and_does_no_work():
    rng = np.random.default_rng(1)
    for _ in range(20):
        nu = rng.normal(size=3) * 3
        C = coriolis(nu)
        assert np.allclose(C, -C.T)
        assert abs(nu @ C @ nu) < 1e-9


@pytest.mark.parametrize("u", [-2.0, 0.0, 1.0, 5.66, 8.0, 10.0])
def test_damping_dissipative_in_operating_range(u):
    """nu^T D nu > 0 requires D + D^T > 0. d23, d32 are asymmetric, so check it on a grid
    covering the operating range (|u| <= 10 m/s, |v| <= 2 m/s, |r| <= 1.5 rad/s; cruise
    speed ~5.66 m/s)."""
    for v in np.linspace(-2, 2, 9):
        for r in np.linspace(-1.5, 1.5, 13):
            D = damping(np.array([u, v, r]))
            assert np.linalg.eigvalsh(D + D.T).min() > 0, (u, v, r)


def test_damping_documented_non_dissipative_corners():
    """Documented model limitations (p. 18 as printed / AISMC/D.m), not bugs:
    D + D^T is indefinite (a) at u = 0 with |r| >= 1.75 rad/s, because d23 uses |u|
    (CyberShip II uses |v|), and (b) at very high surge |u| = 20 m/s."""
    for nu in ([0.0, 0.0, 2.0], [20.0, 0.0, 0.0]):
        D = damping(np.array(nu))
        assert np.linalg.eigvalsh(D + D.T).min() < 0


def test_unforced_vessel_decays():
    """No tau, no delta: kinetic energy 0.5 nu^T M nu decreases monotonically to ~0."""
    x = np.array([0.0, 0.0, 0.3, 1.0, 0.5, 0.2])
    f = lambda t, x: vessel_rhs(x, np.zeros(3), np.zeros(3))
    dt, E = 1e-3, []
    for k in range(60_000):
        nu = x[3:]
        E.append(0.5 * nu @ M @ nu)
        x = rk4_step(f, k * dt, x, dt)
    E = np.array(E)
    assert np.all(np.diff(E) <= 1e-12)
    assert E[-1] < 1e-2 * E[0]      # slow: linear surge damping ~0.72/25.8 1/s


def test_kinematics_pure_surge_moves_along_heading():
    x = np.array([0.0, 0.0, np.pi / 4, 2.0, 0.0, 0.0])
    eta_dot = vessel_rhs(x, np.zeros(3), np.zeros(3))[:3]
    assert np.allclose(eta_dot[:2], 2.0 * np.array([1, 1]) / np.sqrt(2))
    assert np.allclose(J(0.3).T @ J(0.3), np.eye(3))


def test_disturbance_reproducible_zoh_and_mean():
    d1, d2 = Disturbance(40.0, seed=7), Disturbance(40.0, seed=7)
    ts = np.arange(0, 40, 1e-3)
    a = np.array([d1(t) for t in ts])
    assert np.allclose(a, np.array([d2(t) for t in ts]))
    # rand part is held over each 1 ms step
    assert np.allclose(d1(0.0101), d1(0.0109), atol=1e-4)   # rand jumps are up to 0.1
    # mean over [0, 40]: deterministic part (analytic means of the slow sinusoids)
    # + 0.05 (mean of 0.1*U[0,1))
    T = 40.0
    ms1, mc1 = (1 - np.cos(0.1 * T)) / (0.1 * T), np.sin(0.1 * T) / (0.1 * T)      # sin/cos(0.1t)
    ms2, mc2 = (1 - np.cos(0.02 * T)) / (0.02 * T), np.sin(0.02 * T) / (0.02 * T)  # sin/cos(0.02t)
    expected = np.array([3 - 0.2 * ms1 + 0.1 * mc2, -2.5 + 0.1 * mc1 + 0.1 * ms2,
                         3 - 0.2 * ms1 - 0.1 * mc2]) + 0.05
    assert np.allclose(a.mean(axis=0), expected, atol=5e-3)
    assert np.allclose(Disturbance(1.0, enabled=False)(0.5), 0)
