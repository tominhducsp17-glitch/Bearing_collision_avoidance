"""Mốc 5: H∞ IRL on the vessel. Encodes the key findings as tests (see findings.md, Mốc 5)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from irl_reference import linear_model                                     # noqa: E402

from src.analysis.hinf_reference import game_are, gains, kleinman_game     # noqa: E402
from src.low_level.augmented_state import build_X, BASIS, Q_prime_fn       # noqa: E402
from src.low_level.basis import QuadraticBasis, LinearBasis                 # noqa: E402
from src.low_level.data_collection import collect, SumOfSines              # noqa: E402
from src.low_level.offpolicy_irl import OffPolicyHinf                       # noqa: E402
from src.sim.episodes import collect_episodes                               # noqa: E402

Q9 = np.diag([100.0] * 6 + [0.0] * 3)
R_NORM = np.diag(1 / np.array([1100.0, 300.0, 30.0]) ** 2)
K_B = np.array([2000.0, 2000.0, 200.0])


def _oracle():
    A, B, E, u0 = linear_model()
    P = game_are(A, B, E, Q9, R_NORM, 5.0, 0.1)
    return A, B, E, u0, -gains(P, B, E, R_NORM, 5.0)[0].T


def test_augmented_state_layout():
    eta, nu = np.array([1.0, 2.0, 0.5]), np.array([3.0, 0.1, 0.2])
    eta_d, ups_d, ups_dd = np.array([0.9, 2.1, 0.4]), np.array([2.9, 0.0, 0.1]), np.array([0.3, -0.2, 0.05])
    X = build_X(eta, nu, eta_d, ups_d, ups_dd, 2.0)
    assert X.shape == (15,)
    assert np.allclose(X[:3], eta - eta_d)
    assert np.allclose(X[6:9], eta_d) and np.allclose(X[9:12], ups_d) and np.allclose(X[12:], ups_dd)
    assert BASIS["main"] == [0, 1, 2, 3, 4, 5, 9, 10, 11] and BASIS["literal"] == list(range(9))


def test_zero_initial_policy_is_not_admissible():
    """Paper A starts Algorithm 2 from W = 0 (tau = 0). On the linearised vessel error system the
    discounted open loop is unstable (backstepping term +beta in z_ups), so policy iteration from
    zero converges to a WRONG (non-stabilising) ARE solution; from the behaviour gains it converges
    (assumptions.md item 8)."""
    A, B, E, u0, _ = _oracle()
    assert np.linalg.eigvals(A - 0.05 * np.eye(9)).real.max() > 0.5
    P = game_are(A, B, E, Q9, R_NORM, 5.0, 0.1)
    zero = kleinman_game(A, B, E, Q9, R_NORM, 5.0, 0.1, np.zeros((3, 9)), np.zeros((3, 9)), 40)[-1]
    K0 = np.hstack([np.zeros((3, 3)), np.diag(K_B), np.zeros((3, 3))])
    beh = kleinman_game(A, B, E, Q9, R_NORM, 5.0, 0.1, K0, np.zeros((3, 9)), 15)[-1]
    assert np.abs(zero - P).max() > 0.5 * np.abs(P).max()
    assert np.abs(beh - P).max() < 1e-8 * np.abs(P).max()


def test_non_autonomous_reference_breaks_learning():
    """Linear model, noise-free: a reference upsilon_d driven by time (not generated inside X)
    violates the assumption behind (45)/(20) and the learned gains are far off."""
    A, B, E, u0, Wref = _oracle()
    e = SumOfSines(3, [200.0, 60.0, 6.0], seed=1)

    def f(t, x, u, d):
        dx = A @ x + B @ u + E @ d
        dx[6:9] = 0.5 * np.array([np.cos(0.7 * t), np.cos(1.1 * t), 0.4 * np.cos(0.9 * t)])
        return dx
    data = collect(f, np.r_[np.zeros(6), u0], lambda t, x: -K_B * x[3:6] + e(t),
                   lambda t, x: np.array([3.0, -2.5, 3.0]), 1e-3, 8000, 1)
    irl = OffPolicyHinf(QuadraticBasis(range(9)), LinearBasis(range(9)), LinearBasis(range(9)),
                        Q_prime_fn(), R_NORM, 5.0, 0.1).precompute(data)
    W0 = np.zeros((9, 3)); W0[3:6] = -np.diag(K_B)
    res = irl.run(W0, np.zeros((9, 3)), eps=1e-6, max_iter=40, allow_rank_deficient=True)
    err = np.abs(res.W_a[3:6] - Wref[3:6]).max() / np.abs(Wref[3:6]).max()
    assert err > 0.1


def test_episodic_vessel_learning_close_to_oracle():
    """Nonlinear vessel, episodic phase 1 (constant-velocity references, omega_d = 0), admissible
    initial policy: the learned z_ups gains match the linearised H∞ solution within 10 %."""
    _, _, _, _, Wref = _oracle()
    grid = [(u, 0.0, 0.0) for u in (5.0, 5.66, 6.3)]
    mk = lambda s: SumOfSines(3, [600.0, 180.0, 18.0], n_sines=20, w_min=0.05, w_max=20.0, seed=s)
    data = collect_episodes(grid, 4.0, mk, K_B, [4000.0, 4000.0, 400.0], [2, 2, 0.3, 1, 0.5, 0.3])
    idx = BASIS["main"]
    irl = OffPolicyHinf(QuadraticBasis(idx), LinearBasis(idx), LinearBasis(idx), Q_prime_fn(),
                        R_NORM, 5.0, 0.1).precompute(data)
    W0 = np.zeros((9, 3)); W0[3:6] = -np.diag(K_B)
    res = irl.run(W0, np.zeros((9, 3)), eps=1e-4, max_iter=60, allow_rank_deficient=True)
    learned, ref = np.diag(res.W_a[3:6]), np.diag(Wref[3:6])
    assert np.all(np.sign(learned) == np.sign(ref))
    assert np.allclose(learned, ref, rtol=0.10)
