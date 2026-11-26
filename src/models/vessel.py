"""Plant: 3-DOF fully actuated surface vessel, Eqs. (1)-(2) of Paper A.

    eta_dot = J(psi) nu                         eta = [x, y, psi]  (earth frame)
    M nu_dot = -C(nu) nu - D(nu) nu + tau + delta(t)   nu = [u, v, r]  (body frame)

Numerical values: p. 18 of Paper A, implemented exactly as in the authors' reference
code (`AISMC/C.m`, `AISMC/D.m`; see docs/reference_code_notes.md §2). In particular
d11 uses u^2 and d22, d23, d32 use |u| (not |v| as in CyberShip II).

ONLY the simulator (sim/runner.py) and the model-based baseline M1 may import this
module. The proposed controller must not (checked by tests/test_separation.py).
"""
import numpy as np

# --- Inertia, p. 18 -------------------------------------------------------------
M = np.array([[25.8, 0.0, 0.0],
              [0.0, 33.8, 1.0948],
              [0.0, 1.0948, 2.76]])
M_INV = np.linalg.inv(M)


def rot2(psi):
    """R_p(psi) = J_p(psi) in Eq. (2): 2x2 rotation, body -> earth."""
    c, s = np.cos(psi), np.sin(psi)
    return np.array([[c, -s], [s, c]])


def J(psi):
    """Eq. (2): J(eta) = blkdiag(R_p(psi), 1)."""
    out = np.eye(3)
    out[:2, :2] = rot2(psi)
    return out


def coriolis(nu):
    """C(nu), p. 18: c13 = -33.8 v - 1.0948 r, c23 = 25.8 u, c31 = -c13, c32 = -c23."""
    u, v, r = nu
    c13 = -33.8 * v - 1.0948 * r
    c23 = 25.8 * u
    return np.array([[0.0, 0.0, c13],
                     [0.0, 0.0, c23],
                     [-c13, -c23, 0.0]])


def damping(nu):
    """D(nu), p. 18 (as in AISMC/D.m)."""
    u, v, r = nu
    au, av, ar = abs(u), abs(v), abs(r)
    d11 = 0.7225 + 1.3274 * au + 5.8664 * u ** 2
    d22 = 0.8612 + 36.2823 * au + 0.805 * ar
    d23 = -0.1079 + 0.845 * au + 3.45 * ar
    d32 = -0.1052 - 5.0437 * au - 0.13 * ar
    d33 = 1.9 - 0.08 * av + 0.75 * ar
    return np.array([[d11, 0.0, 0.0],
                     [0.0, d22, d23],
                     [0.0, d32, d33]])


def vessel_rhs(x, tau, delta):
    """Eq. (1) as a first-order ODE. x = [eta(3), nu(3)] -> x_dot."""
    eta, nu = x[:3], x[3:]
    eta_dot = J(eta[2]) @ nu
    nu_dot = M_INV @ (-coriolis(nu) @ nu - damping(nu) @ nu + tau + delta)
    return np.concatenate([eta_dot, nu_dot])


class Disturbance:
    """delta(t), p. 18:
        [ 3   - 0.2 sin(0.1t) + 0.1 cos(0.02t) + 0.1 rand
         -2.5 + 0.1 cos(0.1t) + 0.1 sin(0.02t) + 0.1 rand
          3   - 0.2 sin(0.1t) - 0.1 cos(0.02t) + 0.1 rand ]
    rand ~ U[0,1), redrawn every `dt_hold` seconds and held constant in between
    (zero-order hold, mimicking Simulink evaluating rand(1) once per 1 ms step;
    assumptions.md B-15). Pre-generated from `seed` -> fully reproducible.
    `enabled=False` gives delta = 0 (for tests).
    """

    def __init__(self, t_end, dt_hold=1e-3, seed=0, enabled=True):
        self.dt_hold = dt_hold
        self.enabled = enabled
        n = int(np.ceil(t_end / dt_hold)) + 2
        self._rand = np.random.default_rng(seed).random((n, 3))

    def __call__(self, t):
        if not self.enabled:
            return np.zeros(3)
        k = min(int(np.floor(t / self.dt_hold + 1e-9)), len(self._rand) - 1)
        r = self._rand[k]
        return np.array([
            3.0 - 0.2 * np.sin(0.1 * t) + 0.1 * np.cos(0.02 * t) + 0.1 * r[0],
            -2.5 + 0.1 * np.cos(0.1 * t) + 0.1 * np.sin(0.02 * t) + 0.1 * r[1],
            3.0 - 0.2 * np.sin(0.1 * t) - 0.1 * np.cos(0.02 * t) + 0.1 * r[2],
        ])
