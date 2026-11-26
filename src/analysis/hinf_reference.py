"""Model-based reference solutions for linear H-infinity problems (used ONLY by tests, the toy
script and the Mốc 5 sanity check — never by the controller).

System x_dot = A x + B u + E d, cost int e^{-alpha t} (x^T Q x + u^T R u - gamma^2 d^T d).
HJI (30) with V = x^T P x reduces to the discounted game ARE
    (A - alpha/2 I)^T P + P (A - alpha/2 I) + Q - P (B R^{-1} B^T - gamma^{-2} E E^T) P = 0,
u* = -R^{-1} B^T P x,  d* = gamma^{-2} E^T P x   (Eqs. (28)-(29) with grad V = 2 P x).
"""
import numpy as np
from scipy.linalg import solve_continuous_are, solve_continuous_lyapunov, schur


def game_are(A, B, E, Q, R, gamma, alpha):
    """Stabilising solution P via the stable invariant subspace of the Hamiltonian."""
    n = A.shape[0]
    As = A - 0.5 * alpha * np.eye(n)
    S = B @ np.linalg.solve(R, B.T) - E @ E.T / gamma ** 2
    H = np.block([[As, -S], [-Q, -As.T]])
    T, Z, sdim = schur(H, sort="lhp")
    if sdim != n:
        raise ValueError("Hamiltonian has eigenvalues on the imaginary axis (gamma too small?)")
    U1, U2 = Z[:n, :n], Z[n:, :n]
    P = np.real(U2 @ np.linalg.inv(U1))
    return 0.5 * (P + P.T)


def game_are_scipy(A, B, E, Q, R, gamma, alpha):
    """Same via scipy (indefinite R_bar = blkdiag(R, -gamma^2 I)), for cross-checking."""
    n, q = A.shape[0], E.shape[1]
    Bb = np.hstack([B, E])
    Rb = np.block([[R, np.zeros((R.shape[0], q))], [np.zeros((q, R.shape[0])), -gamma ** 2 * np.eye(q)]])
    return solve_continuous_are(A - 0.5 * alpha * np.eye(n), Bb, Q, Rb)


def are_residual(P, A, B, E, Q, R, gamma, alpha):
    As = A - 0.5 * alpha * np.eye(A.shape[0])
    S = B @ np.linalg.solve(R, B.T) - E @ E.T / gamma ** 2
    return As.T @ P + P @ As + Q - P @ S @ P


def gains(P, B, E, R, gamma):
    """K, L with u* = -K x, d* = L x."""
    return np.linalg.solve(R, B.T @ P), E.T @ P / gamma ** 2


def kleinman_game(A, B, E, Q, R, gamma, alpha, K0, L0, n_iter):
    """Model-based simultaneous policy iteration (Algorithm 1 for the linear case):
    evaluate (u = -K x, d = L x) by a Lyapunov equation, then K = R^{-1} B^T P, L = E^T P/gamma^2.
    Returns the list of P_k (k = 1..n_iter)."""
    n = A.shape[0]
    K, L, Ps = np.array(K0, float), np.array(L0, float), []
    for _ in range(n_iter):
        Ac = A - 0.5 * alpha * np.eye(n) - B @ K + E @ L
        P = solve_continuous_lyapunov(Ac.T, -(Q + K.T @ R @ K - gamma ** 2 * L.T @ L))
        Ps.append(P)
        K, L = gains(P, B, E, R, gamma)
    return Ps
