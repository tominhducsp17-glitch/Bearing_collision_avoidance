import sys, itertools, json, numpy as np, time
sys.path.insert(0, "/home/d/projects/Paper_1")
from src.config import load_case
from src.low_level.augmented_state import BASIS, Q_prime_fn
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.data_collection import SumOfSines
from src.low_level.irl_controller import IRLController
from src.low_level.offpolicy_irl import OffPolicyHinf
from src.metrics import bearing_error, rmse
from src.sim.episodes import collect_episodes
from src.sim.runner import run_closed_loop
cfg = load_case("/home/d/projects/Paper_1/config/case1.yaml")
R = np.diag(1 / np.array([1100., 300., 30.]) ** 2)
Kb = np.array([2000., 2000., 200.]); Ki = np.array([4000., 4000., 400.])
idx = BASIS["main"]; phi = LinearBasis(idx)
W0 = np.zeros((9, 3)); W0[3:6] = -np.diag(Kb)
grids = {"narrow": [(u, v, 0.0) for u in (5.0, 5.66, 6.3) for v in (-0.3, 0.0, 0.3)],
         "wide": [(u, v, 0.0) for u in (2.0, 3.5, 5.0, 5.66, 6.3, 7.5) for v in (-0.6, 0.0, 0.6)]}
for (gname, grid), relax, seed in itertools.product(grids.items(), (1.0, 0.5), (0, 1, 2)):
    t0 = time.time(); W = {}; lrn = []
    for i in (3, 4):
        mk = lambda s, i=i: SumOfSines(3, [600., 180., 18.], n_sines=20, w_min=0.05, w_max=20.0, seed=10000 * seed + 1000 * i + s)
        data = collect_episodes(grid, 5.0, mk, Kb, Ki, [2, 2, 0.3, 1, 0.5, 0.3], seed=10000 * seed + 100 * i)
        irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Q_prime_fn(), R, 5.0, 0.1).precompute(data)
        res = irl.run(W0, np.zeros((9, 3)), eps=1e-4, max_iter=80, allow_rank_deficient=True, relax=relax)
        W[i] = res.W_a; lrn.append(f"SV{i}:{len(res.history)}{'✓' if res.converged else '✗'} diag{np.diag(res.W_a[3:6]).round(0).tolist()}")
    try:
        L = run_closed_loop(cfg, IRLController(W, phi), t_end=40.0, log_every=100)
        F = L["formation"]; t = L["t"]; e = np.array([bearing_error(p, F.bearings) for p in L["p"]]); k = t > 30
        out = f"OK RMSE {rmse(t, e):.4f} |z_ups|t>30 {np.abs(L['z_ups'][k]).mean((0,1)).round(3).tolist()} |z_eta|t>30 {np.abs(L['z_eta'][k]).mean((0,1)).round(3).tolist()} max|tau| {np.abs(L['tau']).max():.0f}"
    except FloatingPointError as ex:
        out = f"DIVERGED {ex}"
    print(f"{gname} relax={relax} seed={seed}: {' | '.join(lrn)} -> {out} [{time.time()-t0:.0f}s]", flush=True)
