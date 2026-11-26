import sys, numpy as np
sys.path.insert(0, "/home/d/projects/Paper_1")
from src.low_level.augmented_state import BASIS, Q_prime_fn
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.data_collection import SumOfSines
from src.low_level.offpolicy_irl import OffPolicyHinf
from src.sim.episodes import collect_episodes
R = np.diag(1 / np.array([1100., 300., 30.]) ** 2)
Kb = np.array([2000., 2000., 200.]); Ki = np.array([4000., 4000., 400.])
idx = BASIS["main"]; phi = LinearBasis(idx)
W0 = np.zeros((9, 3)); W0[3:6] = -np.diag(Kb)
base_amp, base_err = np.array([600., 180., 18.]), np.array([2, 2, 0.3, 1, 0.5, 0.3])
for gname, grid in (("u in {5.3,5.66,6.0}", [(u, 0.0, 0.0) for u in (5.3, 5.66, 6.0)] * 3),):
    for sc in (1.0, 0.3, 0.1, 0.03):
        out = []
        for seed in (0, 2, 3):
            for i in (3, 4):
                mk = lambda s: SumOfSines(3, sc * base_amp, n_sines=20, w_min=0.05, w_max=20.0, seed=10000 * seed + 1000 * i + s)
                data = collect_episodes(grid, 5.0, mk, Kb, Ki, sc * base_err, seed=10000 * seed + 100 * i)
                irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Q_prime_fn(), R, 5.0, 0.1).precompute(data)
                r1, r2 = irl.regression(W0, np.zeros((9, 3))); W, _, _ = irl.solve_ls(r1, r2)
                mis = np.linalg.norm(r1 @ W - r2) / np.linalg.norm(r2)
                res = irl.run(W0, np.zeros((9, 3)), eps=1e-5, max_iter=60, allow_rank_deficient=True)
                d = np.diag(res.W_a[3:6])
                out.append(f"s{seed}SV{i}:{'OK ' if np.all(d < 0) else 'FLIP'}{mis:.0e}")
        print(f"{gname} scale {sc}: {' '.join(out)}", flush=True)
