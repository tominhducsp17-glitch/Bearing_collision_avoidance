"""Deployed model-free H-infinity controller, Eq. (55): tau = W_a^T phi(X).
Also the behaviour policy of phase 1. Neither uses M, C, D."""
import numpy as np

from src.low_level.augmented_state import build_X


class IRLController:
    name = "IRL"

    def __init__(self, W_a, phi, beta_eta=2.0):
        """W_a: dict {follower id: (l2, 3)} (one network per follower) or a single array."""
        self.W_a, self.phi, self.beta_eta = W_a, phi, beta_eta

    def tau(self, eta, nu, eta_d, ups_d, ups_d_dot, t=0.0, i=None):
        X = build_X(eta, nu, eta_d, ups_d, ups_d_dot, self.beta_eta)
        W = self.W_a[i] if isinstance(self.W_a, dict) else self.W_a
        return W.T @ self.phi(X)


class BehaviourPolicy:
    """Phase 1 of Algorithm 2 (assumptions.md §1, K1): stable, exploring, model-free:
        tau = -K_b z_ups - K_i int z_ups dt + e_i(t),   e_i = probing signal (replaceable, §6.4).
    The integral term (K_i > 0) removes the steady offset of z_ups, which otherwise makes the
    z_ups regressors collinear with the (almost constant) upsilon_d features."""
    name = "behaviour"

    def __init__(self, K_b, probing, beta_eta=2.0, K_i=0.0, dt=1e-3):
        self.K_b = np.asarray(K_b, float)
        self.K_i = np.broadcast_to(np.asarray(K_i, float), (3,))
        self.probing = probing            # dict {follower id: callable t -> (3,)}
        self.beta_eta, self.dt = beta_eta, dt
        self._int = {}

    def tau(self, eta, nu, eta_d, ups_d, ups_d_dot, t=0.0, i=None):
        X = build_X(eta, nu, eta_d, ups_d, ups_d_dot, self.beta_eta)
        I = self._int.get(i, np.zeros(3))
        out = -self.K_b * X[3:6] - self.K_i * I + self.probing[i](t)
        self._int[i] = I + self.dt * X[3:6]          # called once per control step
        return out
