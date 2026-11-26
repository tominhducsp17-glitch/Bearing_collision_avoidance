import sys, numpy as np
sys.path.insert(0, "/home/d/projects/Paper_1"); sys.path.insert(0, "/home/d/projects/Paper_1/scripts")
from irl_reference import linear_model
from src.analysis.hinf_reference import game_are, gains
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.data_collection import collect, SumOfSines
from src.low_level.offpolicy_irl import OffPolicyHinf
A, B, E, u0 = linear_model(); Q = np.diag([100.] * 6 + [0.] * 3)
R = np.diag(1 / np.array([1100., 300., 30.]) ** 2)
P = game_are(A, B, E, Q, R, 5.0, 0.1); K, _ = gains(P, B, E, R, 5.0); Wref = -K.T
Kb = np.array([2000., 2000., 200.]); rnd = np.random.default_rng(0).random((200000, 3))
f = lambda t, x, u, d: A @ x + B @ u + E @ d
dfun = lambda t, x: np.array([3., -2.5, 3.]) + 0.1 * rnd[int(t / 1e-3)]
def learn(data, noise=0.0):
    if noise:
        data = dict(data); X = data["X"].copy()
        X[..., :6] += noise * np.random.default_rng(1).standard_normal(X[..., :6].shape) * np.abs(X[..., :6]).mean((0, 1))
        data["X"] = X
    irl = OffPolicyHinf(QuadraticBasis(range(9)), LinearBasis(range(9)), LinearBasis(range(9)),
                        lambda X: 100 * np.sum(X[..., :6] ** 2, -1), R, 5.0, 0.1).precompute(data)
    res = irl.run(np.zeros((9, 3)), np.zeros((9, 3)), eps=1e-7, max_iter=60, allow_rank_deficient=True)
    return res, np.abs(res.W_a[3:6] - Wref[3:6]).max() / np.abs(Wref[3:6]).max(), np.abs(res.W_a[:3] - Wref[:3]).max() / np.abs(Wref[:3]).max()
def make(ampf, T_col, ref_var):
    e = SumOfSines(3, ampf * np.array([200., 60., 6.]), seed=1)
    # reference variation: upsilon_d driven by its own slow excitation (augment: x[6:9] not constant)
    def f2(t, x, u, d):
        dx = A @ x + B @ u + E @ d
        if ref_var: dx[6:9] = ref_var * np.array([np.cos(0.7 * t), np.cos(1.1 * t), 0.4 * np.cos(0.9 * t)])
        return dx
    return collect(f2, np.r_[np.zeros(6), u0], lambda t, x: -Kb * x[3:6] + e(t), dfun, 1e-3, int(T_col / 1e-3), 1)
for ampf, T_col, rv in ():
    data = make(ampf, T_col, rv)
    for noise in (0.0, 1e-3, 1e-2):
        res, ez, ee = learn(data, noise)
        print(f"amp×{ampf} T={T_col} refvar={rv} noise={noise:g}: rank {res.rank} cond {res.cond:.0e} errZups {ez:.3f} errZeta {ee:.3f}")

print("--- constant reference, probing bands ---")
for wmin, wmax in ((0.5, 50), (0.05, 5), (0.05, 50)):
    for ampf in (1, 10):
        e = SumOfSines(3, ampf * np.array([200., 60., 6.]), n_sines=20, w_min=wmin, w_max=wmax, seed=1)
        data = collect(f, np.r_[np.zeros(6), u0], lambda t, x: -Kb * x[3:6] + e(t), dfun, 1e-3, 30000, 1)
        for noise in (0.0, 1e-3):
            res, ez, ee = learn(data, noise)
            print(f"w in [{wmin},{wmax}] amp×{ampf} noise={noise:g}: rank {res.rank} errZups {ez:.4f} errZeta {ee:.4f}")
