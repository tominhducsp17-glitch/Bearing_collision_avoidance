import sys, copy, numpy as np, itertools
sys.path.insert(0, "/home/d/projects/Paper_1")
from src.config import load_case
from src.sim.runner import run_closed_loop, irl_dataset, Formation
from src.high_level.leaders import target_formation
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.augmented_state import BASIS, Q_prime_fn
from src.low_level.offpolicy_irl import OffPolicyHinf
from src.low_level.irl_controller import IRLController, BehaviourPolicy
from src.low_level.data_collection import SumOfSines
from src.metrics import bearing_error, rmse
cfg = load_case("config/case1.yaml")
R = np.diag(1 / np.array([1100., 300., 30.]) ** 2)
def maintenance_cfg(cfg):
    c = copy.deepcopy(cfg); F = Formation(cfg)
    p_l = np.concatenate([cfg["initial"]["eta"][i][:2] for i in F.leaders])
    ps = target_formation(p_l, F.B_fl, F.B_ff)
    c["initial"]["eta"] = {i: np.r_[ps[i - 1], cfg["high_level"]["psi0"]] for i in range(1, F.n + 1)}
    c["high_level"]["scaling"] = [[0, 1e9, 0.0]]
    return c
cm = maintenance_cfg(cfg)
Kb = np.array([2000., 2000., 200.])
def deploy(W, phi, t_end=40.0):
    try:
        L = run_closed_loop(cfg, IRLController(W, phi), t_end=t_end, log_every=100)
    except FloatingPointError as ex:
        return "DIVERGED " + str(ex)
    F = L["formation"]; t = L["t"]; e = np.array([bearing_error(p, F.bearings) for p in L["p"]]); k = t > 30
    return (f"RMSE {rmse(t, e):.4f} e(40) {e[-1]:.1e} |z_ups|t>30 {np.abs(L['z_ups'][k]).mean((0,1)).round(3)} "
            f"|z_eta|t>30 {np.abs(L['z_eta'][k]).mean((0,1)).round(3)} max|tau| {np.abs(L['tau']).max():.0f} "
            f"effort {np.trapezoid(np.abs(L['tau']).sum((1,2)), t):.3g}")
for ampf, (wmin, wmax), bname in itertools.product((3.0, 10.0), ((0.5, 50.0), (0.05, 20.0)), ("main",)):
    probing = {i: SumOfSines(3, ampf * np.array([200., 60., 6.]), n_sines=20, w_min=wmin, w_max=wmax, seed=10 * i) for i in (3, 4)}
    Lc = run_closed_loop(cm, BehaviourPolicy(Kb, probing), t_end=38.0, log_every=1000, record_irl=True, high_level_uses="virtual")
    idx = BASIS[bname]; phi = LinearBasis(idx); W = {}; info = []
    for a, i in enumerate((3, 4)):
        data = irl_dataset(Lc["irl"], a); keep = data["t"][:, 0] >= 8.0
        data = {k_: (v[keep] if isinstance(v, np.ndarray) else v) for k_, v in data.items()}
        irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Q_prime_fn(), R, 5.0, 0.1).precompute(data)
        res = irl.run(np.zeros((9, 3)), np.zeros((9, 3)), eps=1e-6, max_iter=60, allow_rank_deficient=True)
        W[i] = res.W_a; info.append(f"SV{i} rank{res.rank} it{len(res.history)} {'conv' if res.converged else 'NOCONV'} diag{np.diag(res.W_a[3:6]).round(0)} ff_u{res.W_a[6,0]:.0f}")
    print(f"amp×{ampf} w[{wmin},{wmax}] {bname}: {' | '.join(info)}\n   -> {deploy(W, phi)}", flush=True)
