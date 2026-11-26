import sys, numpy as np
sys.path.insert(0, "/home/d/projects/Paper_1")
import src.sim.episodes as EP
from src.models.vessel import coriolis, damping, J, M_INV, vessel_rhs
from src.low_level.augmented_state import BASIS, Q_prime_fn
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.data_collection import SumOfSines
from src.low_level.offpolicy_irl import OffPolicyHinf
R = np.diag(1 / np.array([1100., 300., 30.]) ** 2)
Kb = np.array([2000., 2000., 200.]); Ki = np.array([4000., 4000., 400.])
idx = BASIS["main"]; phi = LinearBasis(idx)
W0 = np.zeros((9, 3)); W0[3:6] = -np.diag(Kb)
u0 = np.array([4 * np.sqrt(2), 0, 0]); Nnu = lambda nu: (coriolis(nu) + damping(nu)) @ nu
A_N = np.column_stack([(Nnu(u0 + 1e-6 * e) - Nnu(u0 - 1e-6 * e)) / 2e-6 for e in np.eye(3)])
def affine_rhs(x, tau, d):
    return np.concatenate([J(x[2]) @ x[3:], M_INV @ (-(Nnu(u0) + A_N @ (x[3:] - u0)) + tau + d)])
grid = [(u0[0], 0.0, 0.0)] * 6
for pname, rhs in (("affine drag", affine_rhs), ("true vessel", vessel_rhs)):
    EP.vessel_rhs = rhs
    for dist_on in (True, False):
        EP.Disturbance.__init__.__defaults__ = (1e-3, 0, dist_on)
        out = []
        for seed in (0, 2):
            mk = lambda s: SumOfSines(3, [600., 180., 18.], n_sines=20, w_min=0.05, w_max=20.0, seed=1000 * seed + s)
            data = EP.collect_episodes(grid, 5.0, mk, Kb, Ki, [2, 2, 0.3, 1, 0.5, 0.3], seed=100 * seed)
            irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Q_prime_fn(), R, 5.0, 0.1).precompute(data)
            r1, r2 = irl.regression(W0, np.zeros((9, 3))); W, _, _ = irl.solve_ls(r1, r2)
            out.append(f"seed{seed} misfit {np.linalg.norm(r1 @ W - r2) / np.linalg.norm(r2):.1e}")
        print(pname, "disturbance", dist_on, " | ".join(out), flush=True)
