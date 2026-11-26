"""Simulation loop (Fig. 1 of Paper A). Stage of development: Mốc 2.

mode = "perfect_tracking": each real follower coincides with its virtual vessel
(eta = eta_d, nu = upsilon_d), i.e. the low level is skipped (PROJECT_CONTEXT §5.4.2).
Later milestones add modes "m1" and "irl" with the plant (src/models/vessel.py).

Per step dt (assumptions.md B-15):
 1. leaders: Eq. (9) with beta_s(t) from the schedule object (integrated continuously)
 2. followers: Pi_nom (13) from ACTUAL positions -> SafetyFilter -> Xi (12); omega_d (14)
 3. RK4 with Pi and omega_d held over the step (ZOH); Xi = Eq. (12) is re-evaluated at
    every RK stage, so p_d_ddot = Pi holds exactly within the step
"""
import numpy as np

from src.graph.bearing import bearing_laplacian, partition, check_ff_invertible
from src.high_level.followers import (neighbor_table, compute_nominal_accel, accel_to_Xi,
                                      heading_rate, virtual_vessel_rhs, rot2)
from src.high_level.leaders import centroid_map, leader_velocities, target_formation
from src.high_level.scaling import PiecewiseScaling
from src.safety.base import IdentityFilter, Environment
from src.sim.integrators import rk4_step


class Formation:
    """Static data of a case: graph, gains, schedule. Built from a loaded config."""

    def __init__(self, cfg, k_v=None):
        g = cfg["graph"]
        self.n, self.nl = cfg["n"], g["n_leaders"]
        self.leaders = list(range(1, self.nl + 1))
        self.followers = list(range(self.nl + 1, self.n + 1))
        self.bearings = g["bearings"]
        B = bearing_laplacian(self.n, self.bearings)
        _, _, self.B_fl, self.B_ff = partition(B, self.nl)
        check_ff_invertible(self.B_ff)
        self.C = centroid_map(self.B_fl, self.B_ff)
        self.nb = neighbor_table(self.bearings)
        self.f_nb = {i: [j for j, _ in self.nb[i] if j > self.nl] for i in self.followers}
        self.b = {i: int(any(j <= self.nl for j, _ in self.nb[i])) for i in self.followers}
        hl = cfg["high_level"]
        self.v_c, self.psi0 = hl["v_c"], hl["psi0"]
        self.k_p, self.k_omega = hl["k_p"], hl["k_omega"]
        self.k_v = hl["k_v"] if k_v is None else k_v
        self.schedule = PiecewiseScaling(hl["scaling"])


def run_perfect_tracking(cfg, k_v=None, safety_filter=None, env=None, t_end=None, log_every=10):
    """Mốc 2. Returns a log dict of numpy arrays (sampled every `log_every` steps)."""
    F = Formation(cfg, k_v)
    safety_filter = safety_filter or IdentityFilter()
    env = env or Environment()
    dt = cfg["sim"]["dt"]
    t_end = cfg["sim"]["t_end"] if t_end is None else t_end
    nl, nf = F.nl, len(F.followers)
    eta0 = cfg["initial"]["eta"]

    # state: [p_l (2 nl) | per follower x_d = (p_d(2), psi_d, theta_d(2))], B-7: eta_d(0) = eta(0)
    x = np.concatenate([np.concatenate([eta0[i][:2] for i in F.leaders])] +
                       [np.r_[eta0[i][:2], eta0[i][2], 0.0, 0.0] for i in F.followers])

    def unpack(x):
        p_l = x[:2 * nl].reshape(nl, 2)
        xf = x[2 * nl:].reshape(nf, 5)
        return p_l, xf

    N = int(round(t_end / dt))
    keys = ("t", "p", "p_dot", "psi", "Pi", "omega_d", "p_star")
    log = {k: [] for k in keys}

    for k in range(N + 1):
        t = k * dt
        p_l, xf = unpack(x)
        v_l = leader_velocities(p_l, t, F.v_c, F.schedule, F.C)
        p, p_dot, psi = {}, {}, {}
        for a, i in enumerate(F.leaders):
            p[i], p_dot[i], psi[i] = p_l[a], v_l[a], F.psi0
        for a, i in enumerate(F.followers):
            p[i], psi[i] = xf[a, :2], xf[a, 2]
            p_dot[i] = rot2(xf[a, 2]) @ xf[a, 3:5]

        Pi_nom = {i: compute_nominal_accel(i, p, p_dot, F.nb, F.k_p, F.k_v) for i in F.followers}
        Pi, _ = safety_filter.filter(Pi_nom, {i: xf[a] for a, i in enumerate(F.followers)}, env, t)
        omega = {i: heading_rate(i, psi, F.f_nb, F.b[i], F.psi0, F.k_omega) for i in F.followers}

        if k % log_every == 0:
            log["t"].append(t)
            log["p"].append(np.array([p[i] for i in range(1, F.n + 1)]))
            log["p_dot"].append(np.array([p_dot[i] for i in range(1, F.n + 1)]))
            log["psi"].append(np.array([psi[i] for i in range(1, F.n + 1)]))
            log["Pi"].append(np.array([Pi[i] for i in F.followers]))
            log["omega_d"].append(np.array([omega[i] for i in F.followers]))
            log["p_star"].append(target_formation(p_l, F.B_fl, F.B_ff))
        if k == N:
            break

        def f(tt, xx):
            pl, xff = unpack(xx)
            dl = leader_velocities(pl, tt, F.v_c, F.schedule, F.C).ravel()
            df = [virtual_vessel_rhs(xff[a], accel_to_Xi(Pi[i], xff[a, 2], omega[i], xff[a, 3:5]),
                                     omega[i]) for a, i in enumerate(F.followers)]
            return np.concatenate([dl] + df)

        x = rk4_step(f, t, x, dt)

    out = {k: np.array(v) for k, v in log.items()}
    out["formation"] = F
    return out


# ---------------------------------------------------------------------------------------
# Mốc 3+: closed loop with the real plant (src/models/vessel.py) and a low-level controller
# ---------------------------------------------------------------------------------------
from src.high_level.followers import heading_accel                    # noqa: E402
from src.models.vessel import vessel_rhs, Disturbance                 # noqa: E402
from src.low_level.backstepping import tracking_errors                # noqa: E402


def run_closed_loop(cfg, controller, k_v=None, beta_eta=2.0, safety_filter=None, env=None,
                    t_end=None, log_every=10, disturbance=True):
    """Followers are real vessels (Eq. (1)) driven by `controller.tau(eta, nu, eta_d, ups_d,
    ups_d_dot)`; their virtual vessels follow Eqs. (10)-(14), whose high-level law (13) uses
    the REAL positions/velocities. Leaders are kinematic (item 13).
    ZOH over each step: Pi, omega_d, tau and delta(t_k) (B-15)."""
    F = Formation(cfg, k_v)
    safety_filter = safety_filter or IdentityFilter()
    env = env or Environment()
    dt = cfg["sim"]["dt"]
    t_end = cfg["sim"]["t_end"] if t_end is None else t_end
    dist = Disturbance(t_end, dt, cfg["sim"]["seed"], enabled=disturbance)
    nl, nf = F.nl, len(F.followers)
    eta0 = cfg["initial"]["eta"]
    # state: [p_l (2nl) | followers: plant (eta 3, nu 3) | virtual x_d (5)], B-7: eta_d(0) = eta(0)
    x = np.concatenate([np.concatenate([eta0[i][:2] for i in F.leaders])] +
                       [np.r_[eta0[i], 0, 0, 0] for i in F.followers] +
                       [np.r_[eta0[i][:2], eta0[i][2], 0.0, 0.0] for i in F.followers])

    def unpack(x):
        p_l = x[:2 * nl].reshape(nl, 2)
        xs = x[2 * nl:2 * nl + 6 * nf].reshape(nf, 6)
        xd = x[2 * nl + 6 * nf:].reshape(nf, 5)
        return p_l, xs, xd

    N = int(round(t_end / dt))
    keys = ("t", "p", "psi", "p_star", "p_d", "psi_d", "z_eta", "z_ups", "tau", "nu", "Pi")
    log = {k: [] for k in keys}
    for k in range(N + 1):
        t = k * dt
        p_l, xs, xd = unpack(x)
        v_l = leader_velocities(p_l, t, F.v_c, F.schedule, F.C)
        p, p_dot, psi, r = {}, {}, {}, {}
        for a, i in enumerate(F.leaders):
            p[i], p_dot[i], psi[i], r[i] = p_l[a], v_l[a], F.psi0, 0.0
        for a, i in enumerate(F.followers):
            eta, nu = xs[a, :3], xs[a, 3:]
            p[i], psi[i], r[i] = eta[:2], eta[2], nu[2]
            p_dot[i] = rot2(eta[2]) @ nu[:2]
        Pi_nom = {i: compute_nominal_accel(i, p, p_dot, F.nb, F.k_p, F.k_v) for i in F.followers}
        Pi, _ = safety_filter.filter(Pi_nom, {i: xd[a] for a, i in enumerate(F.followers)}, env, t)
        psi_v = {**{i: F.psi0 for i in F.leaders},
                 **{i: xd[a, 2] for a, i in enumerate(F.followers)}}           # item 4
        omega = {i: heading_rate(i, psi_v, F.f_nb, F.b[i], F.psi0, F.k_omega) for i in F.followers}
        tau, zs = {}, {}
        for a, i in enumerate(F.followers):
            eta, nu = xs[a, :3], xs[a, 3:]
            eta_d = xd[a, :3]
            ups_d = np.r_[xd[a, 3:5], omega[i]]
            Xi = accel_to_Xi(Pi[i], xd[a, 2], omega[i], xd[a, 3:5])
            ups_d_dot = np.r_[Xi, heading_accel(i, omega, F.f_nb, F.b[i], F.k_omega)]
            tau[i] = controller.tau(eta, nu, eta_d, ups_d, ups_d_dot)
            zs[i] = tracking_errors(eta, nu, eta_d, ups_d, beta_eta)
        delta = dist(t)

        if k % log_every == 0:
            log["t"].append(t)
            log["p"].append(np.array([p[i] for i in range(1, F.n + 1)]))
            log["psi"].append(np.array([psi[i] for i in range(1, F.n + 1)]))
            log["p_star"].append(target_formation(p_l, F.B_fl, F.B_ff))
            log["p_d"].append(xd[:, :2].copy())
            log["psi_d"].append(xd[:, 2].copy())
            log["z_eta"].append(np.array([zs[i][0] for i in F.followers]))
            log["z_ups"].append(np.array([zs[i][2] for i in F.followers]))
            log["tau"].append(np.array([tau[i] for i in F.followers]))
            log["nu"].append(xs[:, 3:].copy())
            log["Pi"].append(np.array([Pi[i] for i in F.followers]))
        if k == N:
            break

        def f(tt, xx):
            pl, xss, xdd = unpack(xx)
            dl = leader_velocities(pl, tt, F.v_c, F.schedule, F.C).ravel()
            ds = [vessel_rhs(xss[a], tau[i], delta) for a, i in enumerate(F.followers)]
            dd = [virtual_vessel_rhs(xdd[a], accel_to_Xi(Pi[i], xdd[a, 2], omega[i], xdd[a, 3:5]),
                                     omega[i]) for a, i in enumerate(F.followers)]
            return np.concatenate([dl] + ds + dd)

        x = rk4_step(f, t, x, dt)
        if not np.all(np.isfinite(x)):
            raise FloatingPointError(f"state diverged at t = {t:.3f} s")

    out = {k: np.array(v) for k, v in log.items()}
    out["formation"] = F
    out["dt_log"] = dt * log_every
    return out
