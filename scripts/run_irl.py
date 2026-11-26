"""Mốc 5: H∞ IRL off-policy trên tàu — huấn luyện (pha 1 + pha 2 của Algorithm 2) rồi triển khai.

Chạy:  .venv/bin/python scripts/run_irl.py [case1|case2|all]
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
from src.sim.episodes import collect_episodes                                # noqa: E402
from src.sim.runner import run_closed_loop                                   # noqa: E402

OUT = ROOT / "results" / "moc5_irl"
VARIANTS = {
    "main": {},
    "basis_literal": {"basis": "literal"},
    "R_identity": {"R_identity": True},
    "init_zero": {"init_policy": "zero"},
}


def train(cfg, opts, followers):
    ll = copy.deepcopy(cfg["low_level"])
    ll.update({k: v for k, v in opts.items() if k in ll})
    p1 = ll["phase1"]
    idx = BASIS[ll["basis"]]
    sigma, phi, psi = QuadraticBasis(idx), LinearBasis(idx), LinearBasis(idx)
    R = np.eye(3) if opts.get("R_identity") else np.diag(1.0 / np.asarray(ll["tau_nom"]) ** 2)
    grid = [(u, v, w) for u in p1["u_d"] for v in p1["v_d"] for w in p1["omega_d"]]
    W, hist = {}, {}
    for i in followers:
        mk = lambda s, i=i: SumOfSines(3, p1["probe_amp"], n_sines=p1["probe_n_sines"],
                                      w_min=p1["probe_band"][0], w_max=p1["probe_band"][1],
                                      seed=1000 * i + s)
        data = collect_episodes(grid, p1["T_episode"], mk, p1["K_b"], p1["K_i"], p1["err_scale"],
                                seed=100 * i, beta_eta=ll["beta_eta"], psi0=cfg["high_level"]["psi0"])
        irl = OffPolicyHinf(sigma, phi, psi, Q_prime_fn(ll["q"]), R, ll["gamma"], ll["alpha"]).precompute(data)
        l2 = phi.size
        W_a0 = np.zeros((l2, 3))
        if ll["init_policy"] == "behaviour":
            for c, k in enumerate((3, 4, 5)):          # z_ups rows (indices 3-5 are in both bases)
                W_a0[idx.index(k), c] = -p1["K_b"][c]
        M = len(data["t"])
        val = np.arange(int(0.9 * M), M)               # last 10 % held out
        res = irl.run(W_a0, np.zeros((psi.size, 3)), eps=ll["eps"], max_iter=ll["max_iter"],
                      allow_rank_deficient=True, validation_rows=val)
        W[i] = res.W_a
        hist[i] = {"rank": res.rank, "n_unknowns": res.n_unknowns, "cond": res.cond,
                   "converged": res.converged, "iterations": len(res.history),
                   "norm_W": [h["norm_W"] for h in res.history],
                   "bellman": [h["bellman"] for h in res.history],
                   "bellman_val": [h["bellman_val"] for h in res.history],
                   "dW": [h["dW"] for h in res.history]}
    return W, hist, phi, ll


def evaluate(L):
    F, t = L["formation"], L["t"]
    e = np.array([bearing_error(p, F.bearings) for p in L["p"]])
    dmin = np.array([pairwise_min_distance(p)[0] for p in L["p"]])
    late = t > 30.0
    return e, dmin, {
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
    main(["case1", "case2"] if arg == "all" else [arg])
