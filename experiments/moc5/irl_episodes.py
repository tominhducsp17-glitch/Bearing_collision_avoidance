import sys, itertools, numpy as np, time
sys.path.insert(0, "/home/d/projects/Paper_1")
from src.models.vessel import vessel_rhs, Disturbance
from src.sim.integrators import rk4_step
from src.high_level.followers import rot2
from src.low_level.augmented_state import build_X, BASIS, Q_prime_fn
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.offpolicy_irl import OffPolicyHinf
from src.low_level.data_collection import SumOfSines
from src.low_level.irl_controller import IRLController
np.set_printoptions(precision=1, suppress=True, linewidth=170)
R = np.diag(1 / np.array([1100., 300., 30.]) ** 2)
Kb = np.array([2000., 2000., 200.]); Ki = np.array([4000., 4000., 400.])
def episode(ups_d, err0, T_ep, seed, amp, dt=1e-3):
    """Single vessel tracking a virtual vessel with CONSTANT body velocity ups_d (autonomous:
    ups_d_dot = 0), behaviour PI + probing, disturbance of Paper A."""
    rng = np.random.default_rng(seed)
    e = SumOfSines(3, amp, n_sines=20, w_min=0.05, w_max=20.0, seed=seed)
    dist = Disturbance(T_ep, dt, seed)
    xd = np.r_[0.0, 0.0, np.pi / 4, ups_d[:2]]
    xs = np.r_[xd[:3] + err0[:3], ups_d + err0[3:]]
    I = np.zeros(3); rec = {"t": [], "X": [], "U": [], "D": []}
    for k in range(int(T_ep / dt)):
        t = k * dt
        X = build_X(xs[:3], xs[3:], xd[:3], ups_d, np.zeros(3), 2.0)
        tau = -Kb * X[3:6] - Ki * I + e(t); I += dt * X[3:6]; d = dist(t)
        rec["t"].append(t); rec["X"].append(X); rec["U"].append(tau); rec["D"].append(d)
        f = lambda tt, xx: np.r_[vessel_rhs(xx[:6], tau, d), rot2(xx[8]) @ xx[9:11], ups_d[2], 0.0, 0.0]
        xx = rk4_step(f, t, np.r_[xs, xd], dt); xs, xd = xx[:6], xx[6:]
    return {k_: np.array(v) for k_, v in rec.items()}
def to_intervals(rec):
    pair = lambda Y: np.stack([Y[:-1], Y[1:]], axis=1)
    U, D = pair(rec["U"]), pair(rec["D"]); U[:, 1] = U[:, 0]; D[:, 1] = D[:, 0]
    return {"t": pair(rec["t"]), "X": pair(rec["X"]), "U": U, "D": D}
def gather(grid, T_ep, amp, seed0=0):
    parts = []
    for s, ups in enumerate(grid):
        rng = np.random.default_rng(seed0 + s)
        err0 = rng.uniform(-1, 1, 6) * np.array([2.0, 2.0, 0.3, 1.0, 0.5, 0.3])
        parts.append(to_intervals(episode(np.array(ups), err0, T_ep, seed0 + s, amp)))
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
if __name__ == "__main__":
    grid = list(itertools.product((3.5, 5.66, 7.5), (-1.0, 0.0, 1.0), (-0.3, 0.0, 0.3)))
    t0 = time.time()
    data = gather(grid, 5.0, 3 * np.array([200., 60., 6.]))
    print(f"{len(grid)} episodes, {len(data['t'])} intervals, {time.time() - t0:.0f} s")
    idx = BASIS["main"]; phi = LinearBasis(idx)
    print("feature std:", data["X"][:, 0][:, idx].std(0).round(3))
    for rc in (None, 1e-6, 1e-4):
        irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Q_prime_fn(), R, 5.0, 0.1, rcond=rc).precompute(data)
        res = irl.run(np.zeros((9, 3)), np.zeros((9, 3)), eps=1e-6, max_iter=60, allow_rank_deficient=True)
        print(f"rcond={rc}: rank {res.rank} cond {res.cond:.1e} it {len(res.history)} conv {res.converged}\n{res.W_a}")
        np.save(f"experiments/moc5/W_ep_{rc}.npy", res.W_a)
