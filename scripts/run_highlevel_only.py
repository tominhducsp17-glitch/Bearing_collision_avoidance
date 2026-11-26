"""Mốc 2: tầng cao riêng, tàu thật bám hoàn hảo tàu ảo. Quét k_v cho từng case.

Chạy:  .venv/bin/python scripts/run_highlevel_only.py
Kết quả: results/moc2_highlevel/{metrics.json, sweep.md, *.png}
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import plots                                                # noqa: E402
from src.config import load_case                                     # noqa: E402
from src.high_level.leaders import formation_scale                   # noqa: E402
from src.metrics import (bearing_error, pairwise_min_distance, iae,  # noqa: E402
                         itae, rmse, settling_time)
from src.sim.runner import run_perfect_tracking                      # noqa: E402

K_V = [0.1, 5.0, 10.0, 20.0, 40.0]
OUT = ROOT / "results" / "moc2_highlevel"


def analyse(L):
    F, t = L["formation"], L["t"]
    e = np.array([bearing_error(p, F.bearings) for p in L["p"]])
    dmin = np.array([pairwise_min_distance(p)[0] for p in L["p"]])
    return t, e, dmin, {
        "settling_s(e<0.01)": settling_time(t, e, 0.01),
        "IAE": iae(t, e), "ITAE": itae(t, e), "RMSE": rmse(t, e),
        "e_final": float(e[-1]),
        "max|Pi| (m/s^2)": float(np.abs(L["Pi"]).max()),
        "max|Pi| after 1 s": float(np.abs(L["Pi"][t > 1.0]).max()),
        "d_min (m)": float(dmin.min()), "t_at_d_min (s)": float(t[np.argmin(dmin)]),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    allm = {}
    for name in ("case1", "case2"):
        cfg = load_case(ROOT / "config" / f"{name}.yaml")
        res = {}
        for kv in K_V:
            L = run_perfect_tracking(cfg, k_v=kv)
            t, e, dmin, m = analyse(L)
            res[kv] = (L, e, dmin)
            allm[f"{name}/k_v={kv:g}"] = m
            print(name, f"k_v={kv:g}", {k: round(v, 4) for k, v in m.items()})
        # sweep figures (ordered k_v -> sequential ramp)
        t = res[K_V[0]][0]["t"]
        cols = plots.RAMP[1:1 + len(K_V)]
        plots.series(t, [np.maximum(res[k][1], 1e-6) for k in K_V], [f"k_v = {k:g}" for k in K_V],
                     OUT / f"{name}_sweep_bearing_error.png", "‖g − g*‖ (log)",
                     f"{name}: bearing error vs k_v (k_p = 30, perfect tracking)", colors=cols,
                     logy=True)
        plots.series(t, [res[k][2] for k in K_V], [f"k_v = {k:g}" for k in K_V],
                     OUT / f"{name}_sweep_min_distance.png", "min_{i≠j} ‖p_i − p_j‖ (m)",
                     f"{name}: closest pair distance vs k_v", colors=cols)
        # detailed figures: chosen k_v (config) and Paper A's k_v = 0.1
        for kv in (cfg["high_level"]["k_v"], 0.1):
            L, e, dmin = res[kv]
            tag = f"{name}_kv{kv:g}"
            plots.trajectories(L, [0, 10, 21, 32, 40], OUT / f"{tag}_trajectories.png",
                               f"{name}, k_v = {kv:g}: trajectories (cf. Fig. 3/14)")
            F = L["formation"]
            plots.series(L["t"], [L["psi"][:, i - 1] for i in F.followers],
                         [f"ψ_{i}" for i in F.followers], OUT / f"{tag}_yaw.png", "ψ (rad)",
                         f"{name}, k_v = {kv:g}: follower yaw (cf. Fig. 6/16)",
                         colors=[plots.SV_COLORS[i - 1] for i in F.followers])
            s = [formation_scale(p, False) for p in L["p"]]
            s_star = [formation_scale(p, False) for p in L["p_star"]]
            plots.series(L["t"], [np.array(s)], ["s(p) actual"], OUT / f"{tag}_scale.png",
                         "formation scale (no 1/n)", f"{name}, k_v = {kv:g}: scale (cf. Fig. 12)",
                         colors=[plots.SV_COLORS[0]], refs=[(np.array(s_star), "s(p*) desired")])
    (OUT / "metrics.json").write_text(json.dumps(allm, indent=2))
    lines = ["| run | settling (e<0.01) s | RMSE | IAE | e(40) | max‖Π‖ | max‖Π‖ (t>1 s) | d_min m (at t) |",
             "|---|---|---|---|---|---|---|---|"]
    for k, m in allm.items():
        lines.append(f"| {k} | {m['settling_s(e<0.01)']:.2f} | {m['RMSE']:.4f} | {m['IAE']:.3f} | "
                     f"{m['e_final']:.2e} | {m['max|Pi| (m/s^2)']:.0f} | {m['max|Pi| after 1 s']:.2f} | "
                     f"{m['d_min (m)']:.2f} ({m['t_at_d_min (s)']:.1f}) |")
    (OUT / "sweep.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
