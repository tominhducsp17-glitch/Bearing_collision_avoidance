"""Phase 1 of Algorithm 2 for the vessel: episodic data collection (replication_report.md, Mốc 5).

Why episodes (all found in Mốc 5, see findings.md):
 * The off-policy Bellman equation needs an AUTONOMOUS augmented system (Eq. (20), [M15]):
   the reference must be generated inside X. During the formation transient/scaling the
   reference Omega depends on time, on the neighbours and (via Eq. (13)) on the real vessel
   itself, which breaks this assumption and makes the least squares meaningless.
 * A virtual vessel with CONSTANT body velocity upsilon_d (upsilon_d_dot = 0) is autonomous.
   Several episodes with different constant upsilon_d excite the upsilon_d features; random
   initial errors excite z_eta. omega_d = 0 keeps the earth-frame z_eta consistent with the
   deployment (psi ~ psi0), otherwise the earth-frame policy is not time-invariant on an arc.
 * Behaviour policy (model-free): PI on z_ups + probing. The integral removes the steady
   offset of z_ups, which would make z_ups collinear with the (constant) upsilon_d features.

This module runs the plant (src/models/vessel.py), like the runner: simulator side only.
"""
import numpy as np

from src.high_level.followers import rot2
from src.low_level.augmented_state import build_X
from src.models.vessel import vessel_rhs, Disturbance
from src.sim.integrators import rk4_step


def episode(ups_d, err0, T_ep, probing, K_b, K_i, psi0=np.pi / 4, beta_eta=2.0, dt=1e-3, seed=0):
    """One vessel tracks a virtual vessel with constant body velocity ups_d = (u_d, v_d, omega_d)
    from initial error err0 = (z_eta(3), nu - ups_d (3)). Disturbance delta(t) of Paper A.
    Returns per-step records t, X (augmented state (20)), U (tau), D (delta)."""
    ups_d = np.asarray(ups_d, float)
    dist = Disturbance(T_ep, dt, seed)
    xd = np.r_[0.0, 0.0, psi0, ups_d[:2]]
    xs = np.r_[xd[:3] + err0[:3], ups_d + err0[3:]]
    integ = np.zeros(3)
    N = int(round(T_ep / dt))
    T_, X_, U_, D_ = (np.empty((N,)), np.empty((N, 15)), np.empty((N, 3)), np.empty((N, 3)))
    for k in range(N):
        t = k * dt
        X = build_X(xs[:3], xs[3:], xd[:3], ups_d, np.zeros(3), beta_eta)
        tau = -K_b * X[3:6] - K_i * integ + probing(t)
        integ += dt * X[3:6]
        d = dist(t)
        T_[k], X_[k], U_[k], D_[k] = t, X, tau, d
        f = lambda tt, xx: np.r_[vessel_rhs(xx[:6], tau, d), rot2(xx[8]) @ xx[9:11], ups_d[2], 0.0, 0.0]
        xx = rk4_step(f, t, np.r_[xs, xd], dt)
        xs, xd = xx[:6], xx[6:]
        if not np.all(np.isfinite(xx)):
            raise FloatingPointError("behaviour policy did not keep the vessel bounded")
    return {"t": T_, "X": X_, "U": U_, "D": D_}


def to_intervals(rec):
    """Per-step records -> intervals of one control step (format of offpolicy_irl)."""
    pair = lambda Y: np.stack([Y[:-1], Y[1:]], axis=1)
    U, D = pair(rec["U"]), pair(rec["D"])
    U[:, 1], D[:, 1] = U[:, 0], D[:, 0]
    return {"t": pair(rec["t"]), "X": pair(rec["X"]), "U": U, "D": D}


def collect_episodes(grid, T_ep, make_probing, K_b, K_i, err_scale, seed=0, **kw):
    """Run one episode per entry of `grid` (constant ups_d), random initial error
    uniform in [-err_scale, err_scale]; concatenate the intervals."""
    parts = []
    for s, ups in enumerate(grid):
        rng = np.random.default_rng(seed + s)
        err0 = rng.uniform(-1, 1, 6) * np.asarray(err_scale, float)
        rec = episode(ups, err0, T_ep, make_probing(seed + s), np.asarray(K_b, float),
                      np.asarray(K_i, float), seed=seed + s, **kw)
        parts.append(to_intervals(rec))
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
