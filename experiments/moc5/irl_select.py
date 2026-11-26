import sys, numpy as np, time
sys.path.insert(0, "/home/d/projects/Paper_1")
from src.config import load_case
from src.low_level.augmented_state import BASIS, Q_prime_fn, build_X
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.data_collection import SumOfSines
from src.low_level.irl_controller import IRLController
from src.low_level.offpolicy_irl import OffPolicyHinf
from src.metrics import bearing_error, rmse
from src.sim.episodes import collect_episodes, episode
from src.sim.runner import run_closed_loop
R = np.diag(1 / np.array([1100., 300., 30.]) ** 2)
Kb = np.array([2000., 2000., 200.]); Ki = np.array([4000., 4000., 400.])
idx = BASIS["main"]; phi = LinearBasis(idx); Qf = Q_prime_fn()
W0 = np.zeros((9, 3)); W0[3:6] = -np.diag(Kb)
grid = [(u, 0.0, 0.0) for u in (5.0, 5.66, 6.3)] * 3
cfg = load_case("/home/d/projects/Paper_1/config/case1.yaml")
ERR_VAL = np.array([1.5, -1.5, 0.2, -0.8, 0.4, -0.2])
def val_cost(W, T=5.0, dt=1e-3, alpha=0.1):
    """Model-free validation: run the policy on the real vessel for T s (constant cruise
    reference, fixed initial error, no probing); discounted cost of Paper A (22) without d."""
    try:
        rec = episode((4 * np.sqrt(2), 0.0, 0.0), ERR_VAL, T, lambda t: np.zeros(3), np.zeros(3), np.zeros(3), seed=777,
                      ) if W is None else None
    except FloatingPointError:
        return np.inf
    # custom rollout with policy tau = W^T phi(X)
    from src.models.vessel import vessel_rhs, Disturbance
    from src.sim.integrators import rk4_step
    from src.high_level.followers import rot2
    ups = np.array([4 * np.sqrt(2), 0.0, 0.0]); dist = Disturbance(T, dt, 777)
    xd = np.r_[0.0, 0.0, np.pi / 4, ups[:2]]; xs = np.r_[xd[:3] + ERR_VAL[:3], ups + ERR_VAL[3:]]
    J = 0.0
    for k in range(int(T / dt)):
        t = k * dt
        X = build_X(xs[:3], xs[3:], xd[:3], ups, np.zeros(3), 2.0)
        tau = W.T @ phi(X); d = dist(t)
        J += np.exp(-alpha * t) * (Qf(X) + tau @ R @ tau) * dt
        f = lambda tt, xx: np.r_[vessel_rhs(xx[:6], tau, d), rot2(xx[8]) @ xx[9:11], 0.0, 0.0, 0.0]
        xx = rk4_step(f, t, np.r_[xs, xd], dt); xs, xd = xx[:6], xx[6:]
        if not np.all(np.isfinite(xx)) or np.abs(xx[3:6]).max() > 100:
            return np.inf
    return J
for seed in (0, 2, 3, 4):
    t0 = time.time(); W = {}; info = []
    for i in (3, 4):
        mk = lambda s, i=i: SumOfSines(3, [600., 180., 18.], n_sines=20, w_min=0.05, w_max=20.0, seed=10000 * seed + 1000 * i + s)
        data = collect_episodes(grid, 5.0, mk, Kb, Ki, [2, 2, 0.3, 1, 0.5, 0.3], seed=10000 * seed + 100 * i)
        irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Qf, R, 5.0, 0.1).precompute(data)
        res = irl.run(W0, np.zeros((9, 3)), eps=1e-5, max_iter=40, allow_rank_deficient=True)
        Js = [val_cost(h["W_a"]) for h in res.history]
        k = int(np.argmin(Js)); W[i] = res.history[k]["W_a"]
        info.append(f"SV{i}: pick it {k+1}/{len(Js)} J={Js[k]:.3g} (last {Js[-1]:.3g}) diag{np.diag(W[i][3:6]).round(0).tolist()}")
    try:
        L = run_closed_loop(cfg, IRLController(W, phi), t_end=40.0, log_every=100)
        F = L["formation"]; t = L["t"]; e = np.array([bearing_error(p, F.bearings) for p in L["p"]]); kk = t > 30
        out = f"OK RMSE {rmse(t, e):.4f} |z_ups|t>30 {np.abs(L['z_ups'][kk]).mean((0,1)).round(3).tolist()} max|tau| {np.abs(L['tau']).max():.0f}"
    except FloatingPointError as ex:
        out = f"DIVERGED {ex}"
    print(f"seed {seed}: {' | '.join(info)} -> {out} [{time.time()-t0:.0f}s]", flush=True)
