"""Mốc 3: chạy kín với plant thật và baseline M1 (62) = [L21] (27).

Chạy:  .venv/bin/python scripts/run_m1.py
Kết quả: results/moc3_m1/{metrics.json, table.md, *.png}
Cấu hình chính: k = (20, 12, 5) của [L21], khối lượng đường chéo (đúng (62)), k_v theo config.
Biến thể: zeta của Paper A; M đầy đủ; k_v = 0.1 của Paper A.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import plots                                                    # noqa: E402
from src.baselines.m1_model_based import M1Controller, ZETA_PAPER_A      # noqa: E402
from src.config import load_case                                         # noqa: E402
from src.high_level.leaders import formation_scale                       # noqa: E402
from src.metrics import (bearing_error, pairwise_min_distance, iae, itae,  # noqa: E402
                         rmse, settling_time)
from src.sim.runner import run_closed_loop                               # noqa: E402

OUT = ROOT / "results" / "moc3_m1"
VARIANTS = {
    "main": dict(ctrl=dict(), k_v=None),
    "zeta_paperA": dict(ctrl=dict(k=ZETA_PAPER_A), k_v=None),
    "full_M": dict(ctrl=dict(full_inertia=True), k_v=None),
    "kv0.1": dict(ctrl=dict(), k_v=0.1),
}


def analyse(L):
    F, t = L["formation"], L["t"]
    e = np.array([bearing_error(p, F.bearings) for p in L["p"]])
    dmin = np.array([pairwise_min_distance(p)[0] for p in L["p"]])
    effort = float(np.trapezoid(np.abs(L["tau"]).sum(axis=(1, 2)), t))
    late = t > 30.0
    return e, dmin, {
        "RMSE": rmse(t, e), "IAE": iae(t, e), "ITAE": itae(t, e),
        "settling_s(e<0.01)": settling_time(t, e, 0.01), "e_final": float(e[-1]),
        "effort_sum_int|tau|": effort,
        "max|tau|": float(np.abs(L["tau"]).max()),
        "d_min (m)": float(dmin.min()), "t_at_d_min": float(t[np.argmin(dmin)]),
        "mean|z_ups| t>30 (u,v,r)": np.abs(L["z_ups"][late]).mean(axis=(0, 1)).round(4).tolist(),
        "max|z_psi|": float(np.abs(L["z_eta"][:, :, 2]).max()),
    }


def figures(name, L, e, dmin, tag):
    F, t = L["formation"], L["t"]
    fol = F.followers
    col = [plots.SV_COLORS[i - 1] for i in fol]
    plots.trajectories(L, [0, 10, 21, 32, 40], OUT / f"{tag}_trajectories.png",
                       f"{name}, M1: trajectories (cf. Fig. 3/14)")
    plots.series(t, [L["psi"][:, i - 1] for i in fol], [f"ψ_{i}" for i in fol],
                 OUT / f"{tag}_yaw.png", "ψ (rad)", f"{name}, M1: follower yaw (cf. Fig. 6/16)",
                 colors=col)
    for c, lab in enumerate(("u", "v", "r")):
        plots.series(t, [L["z_ups"][:, a, c] for a in range(len(fol))],
                     [f"z_υ,{lab} SV{i}" for i in fol], OUT / f"{tag}_zups_{lab}.png",
                     f"z_υ ({lab})", f"{name}, M1: velocity tracking error {lab} (cf. Fig. 8/17)",
                     colors=col)
        plots.series(t, [L["tau"][:, a, c] for a in range(len(fol))],
                     [f"τ_{lab} SV{i}" for i in fol], OUT / f"{tag}_tau_{lab}.png",
                     f"τ_{lab}", f"{name}, M1: control input {lab} (cf. Fig. 9/20)", colors=col)
    s = np.array([formation_scale(p, False) for p in L["p"]])
    s_star = np.array([formation_scale(p, False) for p in L["p_star"]])
    plots.series(t, [s], ["s(p) actual"], OUT / f"{tag}_scale.png", "formation scale (no 1/n)",
                 f"{name}, M1: scale (cf. Fig. 12)", colors=[plots.SV_COLORS[0]],
                 refs=[(s_star, "s(p*) desired")])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    allm = {}
    for name in ("case1", "case2"):
        cfg = load_case(ROOT / "config" / f"{name}.yaml")
        es, ds = {}, {}
        for vname, v in VARIANTS.items():
            L = run_closed_loop(cfg, M1Controller(**v["ctrl"]), k_v=v["k_v"])
            e, dmin, m = analyse(L)
            allm[f"{name}/{vname}"] = m
            es[vname], ds[vname] = e, dmin
            print(name, vname, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in m.items()})
            if vname == "main":
                figures(name, L, e, dmin, f"{name}_main")
                t = L["t"]
        names = list(VARIANTS)
        cols = [plots.SV_COLORS[k] for k in range(len(names))]
        plots.series(t, [np.maximum(es[k], 1e-6) for k in names], names,
                     OUT / f"{name}_variants_bearing_error.png", "‖g − g*‖ (log)",
                     f"{name}: M1 bearing error, main vs variants (cf. Fig. 5)", colors=cols,
                     logy=True)
        plots.series(t, [ds[k] for k in names], names, OUT / f"{name}_variants_min_distance.png",
                     "min_{i≠j} ‖p_i − p_j‖ (m)", f"{name}: M1 closest pair distance", colors=cols)
    (OUT / "metrics.json").write_text(json.dumps(allm, indent=2))
    rows = ["| run | RMSE | IAE | ITAE | xác lập s | Σ∫|τ| | max|τ| | d_min m (t) | |z_υ| t>30 (u, v, r) | max|z_ψ| |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for k, m in allm.items():
        rows.append(f"| {k} | {m['RMSE']:.4f} | {m['IAE']:.3f} | {m['ITAE']:.2f} | "
                    f"{m['settling_s(e<0.01)']:.2f} | {m['effort_sum_int|tau|']:.3g} | "
                    f"{m['max|tau|']:.3g} | {m['d_min (m)']:.2f} ({m['t_at_d_min']:.1f}) | "
                    f"{m['mean|z_ups| t>30 (u,v,r)']} | {m['max|z_psi|']:.2f} |")
    (OUT / "table.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
