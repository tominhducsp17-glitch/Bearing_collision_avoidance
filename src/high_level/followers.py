"""High-level trajectory generation for followers, Eqs. (10)-(14) of Paper A.

Virtual vessel of follower i (state p_d, psi_d, theta_d; theta_d is the BODY-frame velocity):
    p_d_dot     = R_p(psi_d) theta_d                                    (10)
    theta_d_dot = Xi_p                                                  (11)
    psi_d_dot   = omega_d                                               (14)
Interface of PROJECT_CONTEXT §6.1:  compute_nominal_accel -> SafetyFilter -> accel_to_Xi
-> virtual_vessel_rhs (integrated by the runner). The filter acts on Pi (earth-frame
acceleration, p_d_ddot = Pi), see assumptions.md B-11.
"""
import numpy as np

from src.graph.bearing import projection

S2 = np.array([[0.0, -1.0], [1.0, 0.0]])     # d/dpsi R_p(psi) = R_p(psi) S2


def rot2(psi):
    c, s = np.cos(psi), np.sin(psi)
    return np.array([[c, -s], [s, c]])


def neighbor_table(bearings):
    """{i: [(j, g*_ij), ...]} for the undirected graph; g*_ji = -g*_ij."""
    nb = {}
    for (i, j), g in bearings.items():
        nb.setdefault(i, []).append((j, np.asarray(g, float)))
        nb.setdefault(j, []).append((i, -np.asarray(g, float)))
    return nb


def compute_nominal_accel(i, p, p_dot, neighbors, k_p, k_v):
    """Eq. (13): Pi_i = -sum_{j in N_i} P_{g*_ij} (k_p (p_i - p_j) + k_v (p_dot_i - p_dot_j)).
    p, p_dot: dicts {agent id: (2,)} of ACTUAL vessel positions / velocities (in Paper A the
    high level uses the real vessels, which is what couples the two levels)."""
    Pi = np.zeros(2)
    for j, g in neighbors[i]:
        Pi -= projection(g) @ (k_p * (p[i] - p[j]) + k_v * (p_dot[i] - p_dot[j]))
    return Pi


def saturate_accel(Pi, a_max):
    """||Pi|| <= a_max (norm saturation, direction kept). a_max = None -> Paper A (no limit).
    Deviation from Paper A chosen by Đức (26/11/2026): Eq. (13) gives ||Pi|| ~ 300 m/s^2 in the
    first second (k_p = 30, initial offsets 10-20 m), which is unphysical and drives the learned
    low level far outside its data (replication_report.md, Mốc 5). Applied to EVERY method."""
    if a_max is None:
        return Pi
    n = np.linalg.norm(Pi)
    return Pi if n <= a_max else Pi * (a_max / n)


def accel_to_Xi(Pi, psi_d, omega_d, theta_d):
    """Eq. (12): Xi_p = R_p^{-1}(psi_d) (Pi - R_p_dot(psi_d) theta_d),
    with R_p_dot = omega_d R_p S2. Guarantees p_d_ddot = Pi."""
    R = rot2(psi_d)
    return R.T @ (Pi - omega_d * R @ S2 @ theta_d)


def heading_rate(i, psi, follower_neighbors, b_i, psi0, k_omega):
    """Eq. (14) in the form of [L21] (6) (assumptions.md item 4):
    omega_d,i = -k_omega [ sum_{j in N_i ∩ V_f} (psi_i - psi_j) + b_i (psi_i - psi0) ],
    psi = VIRTUAL headings psi_d (leaders: psi0); b_i = 1 iff follower i is adjacent to a leader.
    (With actual headings, psi_d integrates a large omega_d while the real vessel lags and
    winds up by ~12 rad in Case 1 -> see replication_report.md, Mốc 3.)"""
    s = sum(psi[i] - psi[j] for j in follower_neighbors[i])
    return -k_omega * (s + b_i * (psi[i] - psi0))


def heading_accel(i, omega, follower_neighbors, b_i, k_omega):
    """d/dt of Eq. (14) with psi_d_dot = omega_d: omega_d_dot (enters upsilon_d_dot in Omega)."""
    s = sum(omega[i] - omega[j] for j in follower_neighbors[i])
    return -k_omega * (s + b_i * omega[i])


def virtual_vessel_rhs(x_d, Xi, omega_d):
    """Eqs. (10), (11), (14). x_d = [p_d(2), psi_d, theta_d(2)]."""
    psi_d, theta_d = x_d[2], x_d[3:5]
    return np.concatenate([rot2(psi_d) @ theta_d, [omega_d], Xi])
