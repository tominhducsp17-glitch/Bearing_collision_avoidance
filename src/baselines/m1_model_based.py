"""Baseline M1 (Paper A, Eq. (62)) = model-based formation scaling controller of [L21] (27).

    tau_xi = -k_xi (xi - alpha_xi) - m_xi fbar_xi + m_xi alpha_dot_xi,   xi in {u, v, r}
    fbar_u = -(c13 r + d11 u)/m_u
    fbar_v = -(c23 r + d22 v + d23 r)/m_v
    fbar_r = -(c31 u + c32 v + d32 v + d33 r)/m_r,     m_u, m_v, m_r = m11, m22, m33

alpha = virtual velocity (16) (assumptions.md B-14, interpretation B).
Gains: k = (20, 12, 5) from [L21] (main configuration); Paper A prints zeta = (0.5, 0.7, 0.5)
(variant). Like [L21] (27), the off-diagonal inertia m23 is ignored and delta is not compensated.

**USES THE TRUE MODEL M, C, D** (allowed for this baseline only, PROJECT_CONTEXT §5.2.4).
"""
import numpy as np

from src.low_level.backstepping import tracking_errors, alpha_v_dot
from src.models.vessel import M, coriolis, damping

K_L21 = (20.0, 12.0, 5.0)
ZETA_PAPER_A = (0.5, 0.7, 0.5)


class M1Controller:
    name = "M1"

    def __init__(self, k=K_L21, beta_eta=2.0, full_inertia=False):
        """full_inertia=False: (62)/[L21](27) literally (diagonal m_xi, m23 ignored).
        full_inertia=True: same law with the full M, C, D (exact feedback linearisation,
        tau = M alpha_dot + C nu + D nu - k z_ups), see replication_report.md Mốc 3."""
        self.k = np.asarray(k, float)
        self.beta_eta = beta_eta
        self.m = np.diag(M).copy()
        self.full_inertia = full_inertia

    def tau(self, eta, nu, eta_d, ups_d, ups_d_dot, t=0.0, i=None):
        _, alpha, z_ups = tracking_errors(eta, nu, eta_d, ups_d, self.beta_eta)
        a_dot = alpha_v_dot(eta, nu, eta_d, ups_d, ups_d_dot, self.beta_eta)
        u, v, r = nu
        C, D = coriolis(nu), damping(nu)
        if self.full_inertia:
            return M @ a_dot + C @ nu + D @ nu - self.k * z_ups
        fbar = -np.array([C[0, 2] * r + D[0, 0] * u,
                          C[1, 2] * r + D[1, 1] * v + D[1, 2] * r,
                          C[2, 0] * u + C[2, 1] * v + D[2, 1] * v + D[2, 2] * r]) / self.m
        return -self.k * z_ups - self.m * fbar + self.m * a_dot
