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
grid = [(u, 0.0, 0.0) for u in (5.0, 5.66, 6.3)] * 3
seed, i = 0, 4
mk = lambda s: SumOfSines(3, [600., 180., 18.], n_sines=20, w_min=0.05, w_max=20.0, seed=10000 * seed + 1000 * i + s)
data = collect_episodes(grid, 5.0, mk, Kb, Ki, [2, 2, 0.3, 1, 0.5, 0.3], seed=10000 * seed + 100 * i)
irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Q_prime_fn(), R, 5.0, 0.1).precompute(data)
res = irl.run(W0, np.zeros((9, 3)), eps=1e-6, max_iter=12, allow_rank_deficient=True)
for k, h in enumerate(res.history):
    print(k + 1, "diag z_ups->tau", np.diag(h["W_a"][3:6]).round(0), "z_psi->tau_r %.0f" % h["W_a"][2, 2], "ff_u %.0f" % h["W_a"][6, 0], "bellman %.3g" % h["bellman"])
# residual of the behaviour-policy evaluation alone: how well does a quadratic V explain data?
r1, r2 = irl.regression(W0, np.zeros((9, 3)))
W, rank, cond = irl.solve_ls(r1, r2)
print("rank", rank, "cond %.1e" % cond, "relative LS residual %.2e" % (np.linalg.norm(r1 @ W - r2) / np.linalg.norm(r2)))
