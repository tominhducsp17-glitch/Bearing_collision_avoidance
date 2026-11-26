"""Backstepping errors of the low level, Eqs. (15)-(17) of Paper A (as in [N24] (16)-(18)).

    z_eta   = eta - eta_d                                             (15)
    alpha_v = J^T(eta) ( -beta_eta z_eta + J(eta_d) upsilon_d )       (16)  virtual velocity
    z_ups   = nu - alpha_v                                            (17)

Pure kinematics; uses NO vessel parameters (M, C, D), so the model-free controller may import it.
Notation: alpha_v is alpha_i of (16) (renamed, assumptions.md item 15).
"""
import numpy as np


def J3(psi):
    c, s = np.cos(psi), np.sin(psi)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def dJ3(psi):
    """dJ/dpsi."""
    c, s = np.cos(psi), np.sin(psi)
    return np.array([[-s, -c, 0.0], [c, -s, 0.0], [0.0, 0.0, 0.0]])


def tracking_errors(eta, nu, eta_d, ups_d, beta_eta):
    """Eqs. (15)-(17). Returns (z_eta, alpha_v, z_ups). beta_eta: scalar or (3,) diagonal."""
    z_eta = eta - eta_d
    eta_d_dot = J3(eta_d[2]) @ ups_d
    alpha_v = J3(eta[2]).T @ (-beta_eta * z_eta + eta_d_dot)
    return z_eta, alpha_v, nu - alpha_v


def alpha_v_dot(eta, nu, eta_d, ups_d, ups_d_dot, beta_eta):
    """Time derivative of (16) from measured eta, nu and the virtual-vessel signals:
        d/dt J^T(psi) = r dJ^T/dpsi,   z_eta_dot = J(psi) nu - eta_d_dot,
        eta_d_ddot = omega_d dJ(psi_d) ups_d + J(psi_d) ups_d_dot."""
    psi, r = eta[2], nu[2]
    eta_d_dot = J3(eta_d[2]) @ ups_d
    eta_d_ddot = ups_d[2] * dJ3(eta_d[2]) @ ups_d + J3(eta_d[2]) @ ups_d_dot
    w = -beta_eta * (eta - eta_d) + eta_d_dot
    w_dot = -beta_eta * (J3(psi) @ nu - eta_d_dot) + eta_d_ddot
    return r * dJ3(psi).T @ w + J3(psi).T @ w_dot
