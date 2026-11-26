"""Mốc 4 (PROJECT_CONTEXT §5.4.4-5): Algorithm 2 on linear problems with known solutions.

Reference: discounted game ARE (src/analysis/hinf_reference.py), cross-checked two ways, and
model-based Kleinman iteration (Algorithm 1) iterate by iterate.
"""
import numpy as np
import pytest

from src.analysis.hinf_reference import (game_are, game_are_scipy, are_residual, gains,
                                         kleinman_game)
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.data_collection import collect, SumOfSines
from src.low_level.offpolicy_irl import OffPolicyHinf, RankDeficientError

GAMMA, ALPHA = 5.0, 0.1


def _problem(A, B, E, Q, R, T=0.01, M=1000, n_sub=10, Kb=None, probe_u=1.0, probe_d=1.0,
             d_const=None, seed=0):
    n, m, q = A.shape[0], B.shape[1], E.shape[1]
    Kb = np.zeros((m, n)) if Kb is None else Kb
    eu = SumOfSines(m, probe_u, seed=seed + 1)
    ed = SumOfSines(q, probe_d, seed=seed + 2)
    u_fn = lambda t, x: -Kb @ x + (eu(t) if probe_u else 0.0)
    d_fn = (lambda t, x: np.asarray(d_const, float)) if d_const is not None else \
        (lambda t, x: ed(t) if probe_d else np.zeros(q))
    f = lambda t, x, u, d: A @ x + B @ u + E @ d
    data = collect(f, np.ones(n), u_fn, d_fn, T, M, n_sub)
    idx = list(range(n))
    sig = QuadraticBasis(idx)
    irl = OffPolicyHinf(sig, LinearBasis(idx), LinearBasis(idx),
                        lambda X: np.einsum("...i,ij,...j->...", X, Q, X), R, GAMMA, ALPHA)
    return irl.precompute(data), sig


def _check(irl, sig, A, B, E, Q, R, W_a0=None, W_d0=None, rtol=1e-4, n_kleinman=4):
    n, m, q = A.shape[0], B.shape[1], E.shape[1]
    W_a0 = np.zeros((n, m)) if W_a0 is None else W_a0
    W_d0 = np.zeros((n, q)) if W_d0 is None else W_d0
    res = irl.run(W_a0, W_d0, eps=1e-10, max_iter=40)
    assert res.converged and res.rank == res.n_unknowns
    P = game_are(A, B, E, Q, R, GAMMA, ALPHA)
    K, L = gains(P, B, E, R, GAMMA)
    scale = np.abs(P).max()
    assert np.abs(sig.P_from_weights(res.W_c) - P).max() < rtol * scale
    assert np.abs(res.W_a - (-K.T)).max() < rtol * np.abs(K).max()
    assert np.abs(res.W_d - L.T).max() < rtol * max(np.abs(L).max(), 1e-12) + 1e-9
    # iterate-by-iterate equality with model-based policy iteration
    Pk = kleinman_game(A, B, E, Q, R, GAMMA, ALPHA, -W_a0.T, W_d0.T, n_kleinman)
    for k in range(n_kleinman):
        assert np.abs(sig.P_from_weights(res.history[k]["W_c"]) - Pk[k]).max() < rtol * np.abs(Pk[k]).max()
    return res


# --- reference solver -------------------------------------------------------------------
def test_reference_are_two_ways():
    A = np.array([[0.0, 1.0], [-1.0, -0.5]]); B = np.array([[0.0], [1.0]])
    E = np.array([[0.0], [0.5]]); Q, R = np.eye(2), np.eye(1)
    P = game_are(A, B, E, Q, R, GAMMA, ALPHA)
    assert np.abs(are_residual(P, A, B, E, Q, R, GAMMA, ALPHA)).max() < 1e-12
    assert np.allclose(P, game_are_scipy(A, B, E, Q, R, GAMMA, ALPHA), atol=1e-12)
    Pk = kleinman_game(A, B, E, Q, R, GAMMA, ALPHA, np.zeros((1, 2)), np.zeros((1, 2)), 30)
    assert np.allclose(Pk[-1], P, atol=1e-10)


# --- T1: scalar, stable and unstable ----------------------------------------------------
def test_scalar_stable():
    A, B, E, Q, R = (np.array([[-1.0]]), np.array([[1.0]]), np.array([[0.5]]),
                     np.array([[1.0]]), np.eye(1))
    irl, sig = _problem(A, B, E, Q, R)
    _check(irl, sig, A, B, E, Q, R)


def test_scalar_unstable_needs_admissible_initial_policy():
    """a = +1: behaviour policy stabilises (K_b = 3); iteration starts from the admissible
    policy u0 = -K_b x (assumptions.md item 8 fallback)."""
    A, B, E, Q, R = (np.array([[1.0]]), np.array([[1.0]]), np.array([[0.5]]),
                     np.array([[1.0]]), np.eye(1))
    Kb = np.array([[3.0]])
    irl, sig = _problem(A, B, E, Q, R, Kb=Kb)
    _check(irl, sig, A, B, E, Q, R, W_a0=-Kb.T)


# --- T2: 2-D with disturbance, two interval lengths ---------------------------------------
@pytest.mark.parametrize("T,M", [(0.01, 1000), (0.001, 5000)])
def test_2d_matches_are(T, M):
    A = np.array([[0.0, 1.0], [-1.0, -0.5]]); B = np.array([[0.0], [1.0]])
    E = np.array([[0.0], [0.5]]); Q, R = np.eye(2), np.eye(1)
    irl, sig = _problem(A, B, E, Q, R, T=T, M=M)
    res = _check(irl, sig, A, B, E, Q, R)
    assert len(res.history) <= 10


def test_3d_two_inputs_two_disturbances():
    A = np.array([[-0.5, 1.0, 0.0], [0.0, -0.3, 1.0], [0.2, 0.0, -1.0]])
    B = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    E = np.array([[0.3, 0.0], [0.0, 0.0], [0.0, 0.5]])
    Q, R = np.diag([10.0, 1.0, 1.0]), np.diag([1.0, 2.0])
    irl, sig = _problem(A, B, E, Q, R, M=2000)
    _check(irl, sig, A, B, E, Q, R)


# --- excitation diagnostics (§5.4.5) ------------------------------------------------------
def test_no_probing_is_detected():
    A = np.array([[0.0, 1.0], [-1.0, -0.5]]); B = np.array([[0.0], [1.0]])
    E = np.array([[0.0], [0.5]]); Q, R = np.eye(2), np.eye(1)
    irl, _ = _problem(A, B, E, Q, R, probe_u=0.0, probe_d=0.0)
    with pytest.raises(RankDeficientError):
        irl.run(np.zeros((2, 1)), np.zeros((2, 1)))


def test_constant_multichannel_disturbance_is_rank_deficient():
    """assumptions.md B-6: with W_d^(0) = 0 and d ≈ constant vector c, the columns of the
    disturber block are c_a * int(psi_b): proportional across channels a -> rank loss."""
    A = np.array([[-0.5, 1.0], [0.0, -1.0]]); B = np.eye(2)
    E = np.diag([0.3, 0.5]); Q, R = np.eye(2), np.eye(2)
    irl, _ = _problem(A, B, E, Q, R, d_const=[3.0, -2.5])
    with pytest.raises(RankDeficientError):
        irl.run(np.zeros((2, 2)), np.zeros((2, 2)))


def test_held_out_bellman_residual_small():
    A = np.array([[0.0, 1.0], [-1.0, -0.5]]); B = np.array([[0.0], [1.0]])
    E = np.array([[0.0], [0.5]]); Q, R = np.eye(2), np.eye(1)
    irl, _ = _problem(A, B, E, Q, R)
    res = irl.run(np.zeros((2, 1)), np.zeros((2, 1)), eps=1e-10, validation_rows=np.arange(800, 1000))
    fit_rms = res.history[-1]["bellman"] / np.sqrt(800)
    assert res.history[-1]["bellman_val"] < 10 * fit_rms + 1e-9
