"""Leader trajectory programming, Eq. (9) of Paper A (as in [L21] Lemma 4).

Leaders are kinematic points with constant heading psi0 (assumptions.md item 13).
Velocity law, with the rotation fixed as in [L21] (3) (assumptions.md B-1):
    p_dot_i = v_c + beta_s(t) (p_i - c(p*)),     theta_i = R_p(psi0)^T p_dot_i   (body frame)
c(p*) is the centroid of the TARGET formation over all n agents (assumptions.md B-2); leaders
can compute it because p_f* = -B_ff^{-1} B_fl p_l (Eq. (8)) depends only on leader positions.
"""
import numpy as np

from src.graph.bearing import target_follower_positions


def target_formation(p_l, B_fl, B_ff):
    """p* = [p_l; p_f*] as an (n, 2) array, Eq. (8)."""
    p_l = np.asarray(p_l, float).reshape(-1, 2)
    p_f = target_follower_positions(p_l.ravel(), B_fl, B_ff).reshape(-1, 2)
    return np.vstack([p_l, p_f])


def centroid_map(B_fl, B_ff):
    """Matrix C (2 x 2n_l) with c(p*) = C p_l (stacked leader positions); Eq. (8) is linear."""
    nl = B_fl.shape[1] // 2
    T = np.vstack([np.eye(2 * nl), -np.linalg.solve(B_ff, B_fl)])      # p* = T p_l
    n = T.shape[0] // 2
    return np.kron(np.ones((1, n)) / n, np.eye(2)) @ T


def leader_velocities(p_l, t, v_c, schedule, C):
    """Eq. (9) in the earth frame: (n_l, 2) array of p_dot_i. C from centroid_map."""
    p_l = np.asarray(p_l, float).reshape(-1, 2)
    c = C @ p_l.ravel()
    return v_c[None, :] + schedule.beta_s(t) * (p_l - c)


def formation_scale(p, normalize=True):
    """s(p) = sqrt(sum_i ||p_i - c(p)||^2 / n) over all agents ([L21] (2)).
    normalize=False drops the 1/n (matches the values read off Fig. 12 of Paper A)."""
    p = np.asarray(p, float).reshape(-1, 2)
    ss = ((p - p.mean(axis=0)) ** 2).sum()
    return np.sqrt(ss / len(p)) if normalize else np.sqrt(ss)
