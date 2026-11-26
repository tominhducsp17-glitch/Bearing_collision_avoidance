"""Mốc 5: H∞ IRL off-policy trên tàu — huấn luyện (pha 1 + pha 2 của Algorithm 2) rồi triển khai.

Chạy:  .venv/bin/python scripts/run_irl.py [case1|case2|all] [--seeds 10 [--workers 5]]
Kết quả: results/moc5_irl/{<case>_metrics.json, <case>_table.md, *.png, <case>_<variant>_W.npz}

Cấu hình chính (config/*.yaml, low_level): cơ sở [z; upsilon_d], R = diag(1/tau_nom^2),
khởi tạo từ chính sách hành vi, pha 1 nhiều đợt với tham chiếu vận tốc hằng.
Biến thể: basis_literal (X(1..9) đúng chữ), R_identity (R = I như Paper A), init_zero (W = 0 như Paper A).
"""
import copy
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import plots                                                        # noqa: E402
from src.baselines.m1_model_based import M1Controller                        # noqa: E402
from src.config import load_case                                             # noqa: E402
from src.low_level.augmented_state import BASIS, Q_prime_fn                  # noqa: E402
from src.low_level.basis import QuadraticBasis, LinearBasis                  # noqa: E402
from src.low_level.data_collection import SumOfSines                         # noqa: E402
from src.low_level.irl_controller import IRLController                       # noqa: E402
from src.low_level.offpolicy_irl import OffPolicyHinf                        # noqa: E402
from src.metrics import bearing_error, pairwise_min_distance, iae, itae, rmse, settling_time  # noqa: E402
from src.sim.episodes import collect_episodes, validation_cost                                # noqa: E402
from src.sim.runner import run_closed_loop                                   # noqa: E402

OUT = ROOT / "results" / "moc5_irl"
VARIANTS = {
    "main": {},
    "basis_literal": {"basis": "literal"},
    "R_identity": {"R_identity": True},
    "init_zero": {"init_policy": "zero"},
}


def train(cfg, opts, followers, seed=None):
    """Phase 1 + phase 2 of Algorithm 2 for each follower, with the model-free validation and
    acceptance step (Đức 27/11, findings Mốc 5): after every iteration the candidate W_a is
    tried once on the vessel (src.sim.episodes.validation_cost); the iteration with the lowest
    cost is kept, and accepted only if it beats the P part of the behaviour policy. Otherwise
    one more batch of data (new seed, appended) is collected, up to phase1.max_batches.
    seed=None keeps the seeds of the original runs (variants table); an int s uses the seed
    scheme of experiments/moc5/irl_select2.py (10 000 s + ...)."""
    ll = copy.deepcopy(cfg["low_level"])
    ll.update({k: v for k, v in opts.items() if k in ll})
    p1 = ll["phase1"]
    idx = BASIS[ll["basis"]]
    sigma, phi, psi = QuadraticBasis(idx), LinearBasis(idx), LinearBasis(idx)
    R = np.eye(3) if opts.get("R_identity") else np.diag(1.0 / np.asarray(ll["tau_nom"]) ** 2)
    Qf = Q_prime_fn(ll["q"])
    grid = [(u, v, w) for u in p1["u_d"] for v in p1["v_d"] for w in p1["omega_d"]] * p1.get("repeat", 1)
    vcfg = p1.get("validation", {})
    J_of = lambda Wa: validation_cost(Wa, phi, Qf, R, T=vcfg.get("T", 5.0), alpha=ll["alpha"],
                                      beta_eta=ll["beta_eta"], psi0=cfg["high_level"]["psi0"])
    base = 0 if seed is None else 10000 * seed
    W, hist = {}, {}
    for i in followers:
        W_beh = np.zeros((phi.size, 3))                 # P part of the behaviour policy
        for c, k in enumerate((3, 4, 5)):              # z_ups rows (indices 3-5 are in both bases)
            W_beh[idx.index(k), c] = -p1["K_b"][c]
        W_a0 = W_beh if ll["init_policy"] == "behaviour" else np.zeros_like(W_beh)
        J0 = J_of(W_beh)
        parts = []
        for b in range(p1.get("max_batches", 1)):
            mk = lambda s, i=i, b=b: SumOfSines(3, p1["probe_amp"], n_sines=p1["probe_n_sines"],
                                                w_min=p1["probe_band"][0], w_max=p1["probe_band"][1],
                                                seed=base + 1000 * i + 100 * b + s)
            parts.append(collect_episodes(grid, p1["T_episode"], mk, p1["K_b"], p1["K_i"], p1["err_scale"],
                                          seed=base + 100 * i + 37 * b, beta_eta=ll["beta_eta"],
                                          psi0=cfg["high_level"]["psi0"]))
            data = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
            irl = OffPolicyHinf(sigma, phi, psi, Qf, R, ll["gamma"], ll["alpha"]).precompute(data)
            M = len(data["t"])
            val = np.arange(int(0.9 * M), M)           # last 10 % held out
            res = irl.run(W_a0, np.zeros((psi.size, 3)), eps=ll["eps"], max_iter=ll["max_iter"],
                          allow_rank_deficient=True, validation_rows=val)
            if not p1.get("select", True):
                k_best, Js = len(res.history) - 1, [np.nan] * len(res.history)
                break
            Js = [J_of(h["W_a"]) for h in res.history]
            k_best = int(np.argmin(Js))
            if Js[k_best] < J0:
                break
        W[i] = res.history[k_best]["W_a"]
        hist[i] = {"rank": res.rank, "n_unknowns": res.n_unknowns, "cond": res.cond,
                   "converged": res.converged, "iterations": len(res.history),
                   "batches": b + 1, "picked_iter": k_best + 1, "J_val": [float(j) for j in Js],
                   "J_behaviour_P": float(J0), "accepted": bool(Js[k_best] < J0),
                   "norm_W": [h["norm_W"] for h in res.history],
                   "bellman": [h["bellman"] for h in res.history],
                   "bellman_val": [h["bellman_val"] for h in res.history],
                   "dW": [h["dW"] for h in res.history]}
    return W, hist, phi, ll


def tracking_radius(L):
    """epsilon(t) = max_i ||p_i - p_d,i|| over followers (tracking-error radius for phase 2)."""
    fol = np.asarray(L["formation"].followers) - 1
    return np.linalg.norm(L["p"][:, fol] - L["p_d"], axis=-1).max(axis=1)


# Pass criterion of Mốc 5 (Đức 27/11), fixed BEFORE the sweep: full 40 s without divergence,
# and the tracking radius stays bounded: eps(t) <= EPS_PASS for t >= 5 s.
EPS_PASS = 1.0


def seed_sweep(name, n_seeds, workers):
    """Mốc 5 'done' check: train + deploy the main configuration for n_seeds data seeds."""
    from concurrent.futures import ProcessPoolExecutor
    cfg = load_case(ROOT / "config" / f"{name}.yaml")
    followers = list(range(cfg["graph"]["n_leaders"] + 1, cfg["n"] + 1))
    Lm = run_closed_loop(cfg, M1Controller())
    rows = {"M1": evaluate(Lm)[2]}
    print(name, "M1", json.dumps(rows["M1"], default=float), flush=True)
    with ProcessPoolExecutor(workers) as ex:
        futs = {s: ex.submit(_one_seed, name, s, followers) for s in range(n_seeds)}
        for s, fu in futs.items():
            rows[f"seed {s}"] = r = fu.result()
            np.savez(OUT / f"{name}_seed{s}_W.npz", **r.pop("_W"))
            print(name, f"seed {s}", json.dumps(r, default=float)[:900], flush=True)
    n_pass = sum(r["pass"] for k, r in rows.items() if k != "M1")
    (OUT / f"{name}_seeds.json").write_text(json.dumps(rows, indent=2, default=float))
    lines = [f"Pass: {n_pass}/{n_seeds} (criterion: 40 s without divergence and eps(t) <= {EPS_PASS} m for t >= 5 s)", "",
             "| run | pass | RMSE | eps_max t≥5 | eps_mean t>30 | max|τ| | |z_υ| t>30 (u,v,r) | per SV: lô, vòng chọn, J/J_hv, chấp nhận |",
             "|---|---|---|---|---|---|---|---|"]
    for k, m in rows.items():
        lr = "; ".join(f"{sv}: {v['batches']}, {v['picked_iter']}, {v['J_ratio']:.2f}, {'✓' if v['accepted'] else '✗'}"
                       for sv, v in m.get("learning", {}).items())
        if "diverged" in m:
            lines.append(f"| {k} | ✗ | **phân kỳ** ({m['diverged']}) | | | | | {lr} |")
            continue
        lines.append(f"| {k} | {'✓' if m.get('pass', True) else '✗'} | {m['RMSE']:.4f} | {m['eps_max t>=5 (m)']:.3f} | "
                     f"{m['eps_mean t>30 (m)']:.4f} | {m['max|tau|']:.3g} | {m['mean|z_ups| t>30 (u,v,r)']} | {lr} |")
    (OUT / f"{name}_seeds_table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


def _one_seed(name, s, followers):
    cfg = load_case(ROOT / "config" / f"{name}.yaml")
    t0 = time.time()
    W, hist, phi, ll = train(cfg, {}, followers, seed=s)
    learn = {f"SV{i}": {"batches": h["batches"], "picked_iter": h["picked_iter"], "iterations": h["iterations"],
                        "J_ratio": min(h["J_val"]) / h["J_behaviour_P"], "accepted": h["accepted"]}
             for i, h in hist.items()}
    try:
        L = run_closed_loop(cfg, IRLController(W, phi, ll["beta_eta"]))
        m = evaluate(L)[2]
        m["pass"] = bool(np.isfinite(m["eps_max t>=5 (m)"]) and m["eps_max t>=5 (m)"] <= EPS_PASS)
    except FloatingPointError as ex:
        m = {"diverged": str(ex), "pass": False}
    m["learning"], m["time_s"], m["_W"] = learn, time.time() - t0, {f"SV{i}": W[i] for i in W}
    return m


def evaluate(L):
    F, t = L["formation"], L["t"]
    e = np.array([bearing_error(p, F.bearings) for p in L["p"]])
    dmin = np.array([pairwise_min_distance(p)[0] for p in L["p"]])
    late = t > 30.0
    eps_t = tracking_radius(L)
    return e, dmin, {
        "eps_max t>=5 (m)": float(eps_t[t >= 5.0].max()), "eps_mean t>30 (m)": float(eps_t[late].mean()),
        "RMSE": rmse(t, e), "IAE": iae(t, e), "ITAE": itae(t, e),
        "settling_s(e<0.01)": settling_time(t, e, 0.01),
        "effort_sum_int|tau|": float(np.trapezoid(np.abs(L["tau"]).sum(axis=(1, 2)), t)),
        "max|tau|": float(np.abs(L["tau"]).max()),
        "d_min (m)": float(dmin.min()),
        "mean|z_ups| t>30 (u,v,r)": np.abs(L["z_ups"][late]).mean(axis=(0, 1)).round(4).tolist(),
        "mean|z_eta| t>30 (x,y,psi)": np.abs(L["z_eta"][late]).mean(axis=(0, 1)).round(4).tolist(),
        "max|z_psi|": float(np.abs(L["z_eta"][:, :, 2]).max()),
    }


def figures(name, L, hist, tag):
    F, t = L["formation"], L["t"]
    fol = F.followers
    col = [plots.SV_COLORS[i - 1] for i in fol]
    plots.trajectories(L, [0, 10, 21, 32, 40], OUT / f"{tag}_trajectories.png",
                       f"{name}, IRL: trajectories (cf. Fig. 3/14)")
    plots.series(t, [L["psi"][:, i - 1] for i in fol], [f"ψ_{i}" for i in fol], OUT / f"{tag}_yaw.png",
                 "ψ (rad)", f"{name}, IRL: follower yaw (cf. Fig. 6/16)", colors=col)
    for c, lab in enumerate(("u", "v", "r")):
        plots.series(t, [L["z_ups"][:, a, c] for a in range(len(fol))], [f"z_υ,{lab} SV{i}" for i in fol],
                     OUT / f"{tag}_zups_{lab}.png", f"z_υ ({lab})",
                     f"{name}, IRL: velocity tracking error {lab} (cf. Fig. 8/17)", colors=col)
        plots.series(t, [L["tau"][:, a, c] for a in range(len(fol))], [f"τ_{lab} SV{i}" for i in fol],
                     OUT / f"{tag}_tau_{lab}.png", f"τ_{lab}", f"{name}, IRL: control input {lab} (cf. Fig. 9/20)",
                     colors=col)
    n_it = max(len(h["norm_W"]) for h in hist.values())
    pad = lambda v: np.r_[v, [v[-1]] * (n_it - len(v))]
    it = np.arange(1, n_it + 1)
    plots.series(it, [pad(hist[i]["norm_W"]) for i in fol], [f"‖W_{i}‖" for i in fol], OUT / f"{tag}_weights.png",
                 "‖Ŵ‖", f"{name}: weight convergence over iterations (cf. Fig. 10/18)", colors=col)
    plots.series(it, [np.maximum(pad(hist[i]["bellman_val"]), 1e-12) for i in fol], [f"SV{i} (held-out)" for i in fol],
                 OUT / f"{tag}_bellman.png", "RMS Bellman error (log)",
                 f"{name}: Bellman error on held-out intervals (cf. Fig. 11/19)", colors=col, logy=True)


def main(cases):
    OUT.mkdir(parents=True, exist_ok=True)
    for name in cases:
        cfg = load_case(ROOT / "config" / f"{name}.yaml")
        followers = list(range(cfg["graph"]["n_leaders"] + 1, cfg["n"] + 1))
        allm, es, ds = {}, {}, {}
        t0 = time.time()
        Lm = run_closed_loop(cfg, M1Controller())
        es["M1"], ds["M1"], allm["M1 (main, [L21])"] = evaluate(Lm)
        for vname, opts in VARIANTS.items():
            W, hist, phi, ll = train(cfg, opts, followers)
            np.savez(OUT / f"{name}_{vname}_W.npz", **{f"SV{i}": W[i] for i in W})
            summ = {f"SV{i}": {k: hist[i][k] for k in ("rank", "n_unknowns", "cond", "converged", "iterations")}
                    | {"bellman_val_last": hist[i]["bellman_val"][-1]} for i in W}
            try:
                L = run_closed_loop(cfg, IRLController(W, phi, ll["beta_eta"]))
                e, dmin, m = evaluate(L)
                es[f"IRL {vname}"], ds[f"IRL {vname}"] = e, dmin
                if vname == "main":
                    figures(name, L, hist, f"{name}_irl_main")
                    t = L["t"]
            except FloatingPointError as ex:
                m = {"diverged": str(ex)}
            m["learning"] = summ
            allm[f"IRL {vname}"] = m
            print(name, vname, json.dumps(m, default=float)[:600], f"[{time.time() - t0:.0f} s]", flush=True)
        names = list(es)
        cols = [plots.SV_COLORS[k % 6] for k in range(len(names))]
        plots.series(Lm["t"], [np.maximum(es[k], 1e-6) for k in names], names,
                     OUT / f"{name}_bearing_error_irl_vs_m1.png", "‖g − g*‖ (log)",
                     f"{name}: bearing error, IRL vs M1 (cf. Fig. 5)", colors=cols, logy=True)
        (OUT / f"{name}_metrics.json").write_text(json.dumps(allm, indent=2, default=float))
        rows = ["| run | RMSE | IAE | ITAE | Σ∫|τ| | max|τ| | d_min | |z_υ| t>30 (u,v,r) | |z_η| t>30 (x,y,ψ) | học (hạng, vòng, hội tụ) |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for k, m in allm.items():
            lr = m.get("learning", {})
            lstr = "; ".join(f"{s}: {v['rank']}/{v['n_unknowns']}, {v['iterations']}, {'✓' if v['converged'] else '✗'}"
                             for s, v in lr.items())
            if "diverged" in m:
                rows.append(f"| {k} | **phân kỳ** ({m['diverged']}) | | | | | | | | {lstr} |")
                continue
            rows.append(f"| {k} | {m['RMSE']:.4f} | {m['IAE']:.3f} | {m['ITAE']:.2f} | {m['effort_sum_int|tau|']:.3g} | "
                        f"{m['max|tau|']:.3g} | {m['d_min (m)']:.2f} | {m['mean|z_ups| t>30 (u,v,r)']} | "
                        f"{m['mean|z_eta| t>30 (x,y,psi)']} | {lstr} |")
        (OUT / f"{name}_table.md").write_text("\n".join(rows) + "\n")
        print("\n".join(rows), flush=True)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    cases = ["case1", "case2"] if arg == "all" else [arg]
    if "--seeds" in sys.argv:                     # run_irl.py case1 --seeds 10 [--workers 5]
        n = int(sys.argv[sys.argv.index("--seeds") + 1])
        w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 5
        OUT.mkdir(parents=True, exist_ok=True)
        for c in cases:
            seed_sweep(c, n, w)
    else:
        main(cases)
