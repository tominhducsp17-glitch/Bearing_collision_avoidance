import sys, itertools, numpy as np
sys.path.insert(0, "/home/d/projects/Paper_1"); sys.path.insert(0, "/home/d/projects/Paper_1/scripts")
from irl_reference import linear_model
from src.analysis.hinf_reference import game_are, gains
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.data_collection import collect, SumOfSines
from src.low_level.offpolicy_irl import OffPolicyHinf
np.set_printoptions(precision=1, suppress=True, linewidth=170)
A, B, E, u0 = linear_model(); Q = np.diag([100.] * 6 + [0.] * 3)
R = np.diag(1 / np.array([1100., 300., 30.]) ** 2)
P = game_are(A, B, E, Q, R, 5.0, 0.1); K, _ = gains(P, B, E, R, 5.0); Wref = -K.T
Kb = np.array([2000., 2000., 200.]); Ki = np.array([4000., 4000., 400.])
rnd = np.random.default_rng(0).random((10 ** 6, 3))
grid = list(itertools.product((3.5, 5.66, 7.5), (-1.0, 0.0, 1.0), (-0.3, 0.0, 0.3)))
parts = []
for s, ups in enumerate(grid):
    rng = np.random.default_rng(s); err0 = rng.uniform(-1, 1, 6) * np.array([2.0, 2.0, 0.3, 1.0, 0.5, 0.3])
    e = SumOfSines(3, 3 * np.array([200., 60., 6.]), n_sines=20, w_min=0.05, w_max=20.0, seed=s)
    # PI behaviour: augment state with integrator (not part of X used by IRL)
    Ia = np.zeros(3)
    def u_fn(t, x, e=e):
        return -Kb * x[3:6] - Ki * x[9:12] + e(t)
    f = lambda t, x, u, d: np.r_[A @ x[:9] + B @ u + E @ d, x[3:6]]
    dfun = lambda t, x: np.array([3., -2.5, 3.]) + 0.1 * rnd[int(t / 1e-3)]
    dat = collect(f, np.r_[err0, ups, np.zeros(3)], u_fn, dfun, 1e-3, 5000, 1)
    dat["X"] = dat["X"][..., :9]
    parts.append(dat)
data = {k: np.concatenate([p[k] for p in parts]) for k in ("t", "X", "U", "D")}
idx = list(range(9))
irl = OffPolicyHinf(QuadraticBasis(idx), LinearBasis(idx), LinearBasis(idx), lambda X: 100 * np.sum(X[..., :6] ** 2, -1), R, 5.0, 0.1).precompute(data)
W0 = np.zeros((9, 3)); W0[3:6] = -np.diag(Kb)
res = irl.run(W0, np.zeros((9, 3)), eps=1e-7, max_iter=60, allow_rank_deficient=True)
print(f"linear-model episodes: rank {res.rank} cond {res.cond:.1e} it {len(res.history)} conv {res.converged} rel err W_a {np.abs(res.W_a - Wref).max() / np.abs(Wref).max():.2e}")
print(res.W_a, "\nref\n", Wref)
