"""Augmented state of the low level, Eqs. (19)-(21) of Paper A.

    X = [z_eta(3); z_ups(3); Omega(9)],
    Omega = [eta_d; upsilon_d; upsilon_d_dot] = [p_d(2); psi_d; theta_d(2); omega_d; theta_d_dot(2); omega_d_dot]

Index map (0-based):   0-2 z_eta | 3-5 z_ups | 6-7 p_d | 8 psi_d | 9-10 theta_d | 11 omega_d
                       12-13 theta_d_dot (= Xi_p) | 14 omega_d_dot
Basis selection (assumptions.md item 10):
    BASIS_MAIN    = [z_eta; z_ups; upsilon_d]  -> indices 0-5, 9-11
    BASIS_LITERAL = X(1..9) of Paper A = [z_eta; z_ups; p_d; psi_d] -> indices 0-8
Uses no vessel parameters.
"""
import numpy as np

from src.low_level.backstepping import tracking_errors

BASIS_MAIN = [0, 1, 2, 3, 4, 5, 9, 10, 11]
BASIS_LITERAL = [0, 1, 2, 3, 4, 5, 6, 7, 8]
BASIS = {"main": BASIS_MAIN, "literal": BASIS_LITERAL}
Z_IDX = list(range(6))


def build_X(eta, nu, eta_d, ups_d, ups_d_dot, beta_eta):
    z_eta, _, z_ups = tracking_errors(eta, nu, eta_d, ups_d, beta_eta)
    return np.concatenate([z_eta, z_ups, eta_d, ups_d, ups_d_dot])


def Q_prime_fn(q=100.0):
    """X^T Q' X with Q' = blkdiag(q I_6, 0_9) (assumptions.md item 1)."""
    return lambda X: q * np.sum(np.asarray(X)[..., :6] ** 2, axis=-1)
