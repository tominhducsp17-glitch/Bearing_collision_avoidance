"""Phase 1 of Algorithm 2: collect data once with a stable, exploring behaviour policy.

Generic version (Mốc 4, toy problems): system x_dot = f(t, x, u, d), behaviour control
u(t, x) and the actual disturbance d(t, x). The probing signal is a replaceable callable
(PROJECT_CONTEXT §6.4) so that stage 2 can pass it through a CBF filter.

Each interval [t_{j-1}, t_j] of length T is integrated with `n_sub` RK4 sub-steps; u and d are
held constant over each sub-step (ZOH, like the 1 ms controller of the vessel simulation) and
all samples (n_sub + 1 per interval) are kept for the integrals of (57)-(61).
"""
import numpy as np

from src.sim.integrators import rk4_step


class SumOfSines:
    """e(t) = sum_k a_k sin(w_k t + phi_k), independent per channel. Frequencies drawn once
    (fixed, seeded) uniformly in [w_min, w_max]; amplitude per channel `amp`; active for
    t < t_off (e.g. 15 s as in [N24])."""

    def __init__(self, dim, amp, n_sines=10, w_min=0.5, w_max=50.0, t_off=np.inf, seed=0):
        rng = np.random.default_rng(seed)
        self.w = rng.uniform(w_min, w_max, (dim, n_sines))
        self.phi = rng.uniform(0, 2 * np.pi, (dim, n_sines))
        self.amp = np.broadcast_to(np.asarray(amp, float), (dim,)) / np.sqrt(n_sines / 2)
        self.t_off = t_off

    def __call__(self, t):
        if t >= self.t_off:
            return np.zeros(len(self.amp))
        return self.amp * np.sin(self.w * t + self.phi).sum(axis=1)


def collect(f, x0, u_fn, d_fn, T, M, n_sub=10, t0=0.0):
    """Run M intervals of length T. Returns dict with arrays
    t (M, n_sub+1), X (M, n_sub+1, n), U (M, n_sub+1, m), D (M, n_sub+1, q).
    The value of u, d stored at a sample is the value applied on the following sub-step
    (the last sample of an interval repeats the previous one, it carries zero weight in the
    ZOH-consistent integration used downstream)."""
    h = T / n_sub
    x, t = np.asarray(x0, float), t0
    Ts, Xs, Us, Ds = [], [], [], []
    for _ in range(M):
        ts, xs, us, ds = [t], [x.copy()], [], []
        for _ in range(n_sub):
            u, d = u_fn(t, x), d_fn(t, x)
            us.append(u), ds.append(d)
            x = rk4_step(lambda tt, xx: f(tt, xx, u, d), t, x, h)
            t += h
            ts.append(t), xs.append(x.copy())
        us.append(us[-1]), ds.append(ds[-1])
        Ts.append(ts), Xs.append(xs), Us.append(us), Ds.append(ds)
        if not np.all(np.isfinite(x)):
            raise FloatingPointError("behaviour policy did not keep the system bounded")
    return {"t": np.array(Ts), "X": np.array(Xs), "U": np.array(Us), "D": np.array(Ds),
            "T": T, "n_sub": n_sub}
