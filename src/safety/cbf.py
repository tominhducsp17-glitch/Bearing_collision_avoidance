"""Second-order HOCBF for the virtual vessels (double integrators, p_ddot = Pi), Mốc 7.

Pair (i, j), dp = p_i - p_j, dv = v_i - v_j, margin D_ij = d_min + eps_i + eps_j
(PROJECT_CONTEXT §4.2: virtual vessels D apart  =>  real vessels d_min apart):
    h      = ||dp||^2 - D^2
    h_dot  = 2 dp^T dv
    h_ddot = 2 ||dv||^2 + 2 dp^T (Pi_i - Pi_j)
HOCBF ([X21], as used by Paper B (31)-(35) without the time-varying term):
    psi_1 = h_dot + a1 h,   psi_1_dot + a2 psi_1 >= 0
<=> 2 dp^T (Pi_i - Pi_j) >= -2||dv||^2 - (a1 + a2) h_dot - a1 a2 h            (*)
(*) is linear in the accelerations, so the filter is a QP. If j is not a decision variable
(leader, obstacle) its known acceleration a_j moves to the right-hand side.
Forward invariance needs h(0) >= 0 and psi_1(0) >= 0.
"""
import numpy as np


def pair_constraint(dp, dv, D, a1, a2):
    """Return (g, b): constraint g^T (Pi_i - Pi_j) >= b of (*), plus (h, psi_1) for logging."""
    dp, dv = np.asarray(dp, float), np.asarray(dv, float)
    h = dp @ dp - D ** 2
    h_dot = 2.0 * dp @ dv
    b = -2.0 * dv @ dv - (a1 + a2) * h_dot - a1 * a2 * h
    return 2.0 * dp, b, h, h_dot + a1 * h
