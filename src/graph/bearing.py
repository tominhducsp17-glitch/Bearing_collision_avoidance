"""Bearing geometry, Section 2.1 and Eqs. (6)-(8) of Paper A.

Agent ids are 1-based as in the paper; leaders are listed first.
An edge (i, j) carries the desired bearing g*_ij = (p_j - p_i)/||p_j - p_i||.
The graph is undirected, so g*_ji = -g*_ij and P_{g_ij} = P_{g_ji}.
"""
import numpy as np


def bearing(p_i, p_j):
    """g_ij = (p_j - p_i) / ||p_j - p_i||."""
    d = np.asarray(p_j, float) - np.asarray(p_i, float)
    return d / np.linalg.norm(d)


def projection(g):
    """P_g = I - g g^T for unit g (normalised here for safety). P_g g = 0."""
    g = np.asarray(g, float)
    g = g / np.linalg.norm(g)
    return np.eye(len(g)) - np.outer(g, g)


def bearing_laplacian(n, bearings, dim=2):
    """Eq. (6): B in R^{dn x dn}.
    B_ij = -P_{g_ij} for (i,j) in E,  B_ii = sum_{k in N_i} P_{g_ik},  0 otherwise.
    `bearings`: dict {(i, j): g_ij} with 1-based ids, each undirected edge listed once.
    """
    B = np.zeros((dim * n, dim * n))
    for (i, j), g in bearings.items():
        P = projection(g)
        a, b = (i - 1) * dim, (j - 1) * dim
        B[a:a + dim, a:a + dim] += P
        B[b:b + dim, b:b + dim] += P
        B[a:a + dim, b:b + dim] -= P
        B[b:b + dim, a:a + dim] -= P
    return B


def partition(B, n_leaders, dim=2):
    """Eq. (7): split B into (B_ll, B_lf, B_fl, B_ff); leaders are agents 1..n_l."""
    k = dim * n_leaders
    return B[:k, :k], B[:k, k:], B[k:, :k], B[k:, k:]


def check_ff_invertible(B_ff, tol=1e-9):
    """Uniqueness condition of Section 2.1: B_ff nonsingular (B_ff is symmetric PSD,
    so this is lambda_min > 0). Returns lambda_min; raises if singular."""
    lam_min = float(np.linalg.eigvalsh(B_ff).min())
    if lam_min <= tol:
        raise ValueError(f"B_ff is singular (lambda_min = {lam_min:.3e}): "
                         "augmented formation is not infinitesimally bearing rigid")
    return lam_min


def target_follower_positions(p_leaders, B_fl, B_ff):
    """Eq. (8): p_f* = -B_ff^{-1} B_fl p_l. Inputs/outputs stacked [x1, y1, x2, y2, ...]."""
    return -np.linalg.solve(B_ff, B_fl @ np.asarray(p_leaders, float))


def bearings_from_positions(p, edges, dim=2):
    """g_ij for each edge from stacked positions p (used for checks and metrics)."""
    P = np.asarray(p, float).reshape(-1, dim)
    return {(i, j): bearing(P[i - 1], P[j - 1]) for (i, j) in edges}
