"""Mốc 6 (làm gọn): Case 1 và Case 2 với M1 và IRL (trọng số đã học ở Mốc 5, 10 seed).

Chạy:  .venv/bin/python scripts/run_moc6.py   (cần results/moc5_irl/<case>_seed<s>_W.npz,
       tạo bằng scripts/run_irl.py <case> --seeds 10)
Kết quả: results/moc6/{table.md, metrics.json, <case>_eps.npz, *.png}

* Seed đại diện của IRL: seed có eps_max(t >= 5) bằng trung vị dưới trên 10 seed (quy tắc
  cố định, không chọn tay). Bảng báo cả seed đại diện lẫn trung vị [min, max] trên 10 seed.
* <case>_eps.npz lưu eps(t) = max_i ||p_i - p_d,i|| của M1 và của từng seed IRL: đây là
  bán kính sai số bám mà tầng CBF (giai đoạn 2) sẽ dùng.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from src import plots                                                    # noqa: E402
from src.baselines.m1_model_based import M1Controller                    # noqa: E402
from src.config import load_case                                         # noqa: E402
from src.low_level.augmented_state import BASIS                          # noqa: E402
from src.low_level.basis import LinearBasis                              # noqa: E402
from src.low_level.irl_controller import IRLController                   # noqa: E402
from src.metrics import bearing_error, pairwise_min_distance             # noqa: E402
from src.sim.runner import run_closed_loop, Formation                    # noqa: E402
from run_irl import evaluate, tracking_radius                            # noqa: E402

OUT = ROOT / "results" / "moc6"
W_DIR = ROOT / "results" / "moc5_irl"
N_SEEDS = 10
KEYS = ["RMSE", "IAE", "ITAE", "settling_s(e<0.01)", "eps_max t>=5 (m)", "eps_mean t>30 (m)",
        "effort_sum_int|tau|", "max|tau|", "max|tau| t>=0.1", "d_min (m)"]


def _run(name, s):
    cfg = load_case(ROOT / "config" / f"{name}.yaml")
    if s is None:
        ctrl = M1Controller()
    else:
        Wz = np.load(W_DIR / f"{name}_seed{s}_W.npz")
        ctrl = IRLController({int(k[2:]): Wz[k] for k in Wz.files}, LinearBasis(BASIS["main"]),
                             cfg["low_level"]["beta_eta"])
    L = run_closed_loop(cfg, ctrl)
    F = L["formation"]
    _, _, m = evaluate(L)
    m["t_at_d_min"] = float(L["t"][np.argmin([pairwise_min_distance(p)[0] for p in L["p"]])])
    series = {"t": L["t"], "eps": tracking_radius(L),
              "e": np.array([bearing_error(p, F.bearings) for p in L["p"]]),
              "dmin": np.array([pairwise_min_distance(p)[0] for p in L["p"]]),
              "zups": np.linalg.norm(L["z_ups"], axis=-1).max(axis=1),
              "tau": np.abs(L["tau"]).max(axis=1),               # (N, 3): max over followers
              "L": {k: L[k] for k in ("t", "p", "p_star", "psi")} if s is not None else None}
    return m, series


def band(t, Y, path, ylabel, title, m1, rep, logy=False):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.fill_between(t, Y.min(0), Y.max(0), color=plots.SV_COLORS[0], alpha=0.18, lw=0,
                    label=f"IRL, min–max over {len(Y)} seeds")
    ax.plot(t, rep[1], color=plots.SV_COLORS[0], lw=1.5, label=f"IRL, seed {rep[0]} (representative)")
    ax.plot(t, m1, color=plots.SV_COLORS[1], lw=1.5, label="M1 (model-based, [L21])")
    if logy:
        ax.set_yscale("log")
    plots._style(ax, "Time (s)", ylabel)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title(title, fontsize=10, color=plots.INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    allm, rows = {}, []
    with ProcessPoolExecutor(11) as ex:
        for name in ("case1", "case2"):
            futs = {s: ex.submit(_run, name, s) for s in [None] + list(range(N_SEEDS))}
            res = {s: f.result() for s, f in futs.items()}
            m1, S1 = res[None]
            seeds = list(range(N_SEEDS))
            em = np.array([res[s][0]["eps_max t>=5 (m)"] for s in seeds])
            rep = seeds[int(np.argsort(em)[(N_SEEDS - 1) // 2])]          # lower median
            t = S1["t"]
            np.savez(OUT / f"{name}_eps.npz", t=t, M1=S1["eps"], **{f"IRL_seed{s}": res[s][1]["eps"] for s in seeds})
            allm[name] = {"M1": m1, **{f"IRL seed {s}": res[s][0] for s in seeds}, "representative_seed": rep}
            # table
            agg = lambda k: np.array([res[s][0][k] for s in seeds], float)
            f = lambda x: f"{x:.3g}"
            rows += [f"**{name}** (IRL đại diện: seed {rep})", "",
                     "| chỉ số | M1 | IRL seed đại diện | IRL 10 seed: trung vị [min, max] |", "|---|---|---|---|"]
            for k in KEYS:
                a = agg(k)
                rows.append(f"| {k} | {f(m1[k])} | {f(res[rep][0][k])} | {f(np.median(a))} [{f(a.min())}, {f(a.max())}] |")
            for k in ("mean|z_ups| t>30 (u,v,r)", "mean|z_eta| t>30 (x,y,psi)"):
                rows.append(f"| {k} | {m1[k]} | {res[rep][0][k]} | |")
            rows.append("")
            # figures
            Y = lambda key: np.array([res[s][1][key] for s in seeds])
            band(t, Y("e").clip(1e-6), OUT / f"{name}_bearing_error.png", "‖g − g*‖ (log)",
                 f"{name}: bearing error, M1 vs IRL (cf. Fig. 5)", S1["e"].clip(1e-6), (rep, res[rep][1]["e"].clip(1e-6)), logy=True)
            band(t, Y("eps"), OUT / f"{name}_eps.png", "ε(t) = max_i ‖p_i − p_d,i‖ (m)",
                 f"{name}: low-level tracking radius (input to phase 2)", S1["eps"], (rep, res[rep][1]["eps"]))
            band(t, Y("dmin"), OUT / f"{name}_min_distance.png", "min_{i≠j} ‖p_i − p_j‖ (m)",
                 f"{name}: closest-pair distance", S1["dmin"], (rep, res[rep][1]["dmin"]))
            band(t, Y("zups"), OUT / f"{name}_zups.png", "max_i ‖z_υ,i‖", f"{name}: velocity tracking error (cf. Fig. 8/17)",
                 S1["zups"], (rep, res[rep][1]["zups"]), logy=True)
            band(t, Y("tau")[:, :, 0], OUT / f"{name}_tau_u.png", "max_i |τ_u,i| (N)", f"{name}: surge force (cf. Fig. 9/20)",
                 S1["tau"][:, 0], (rep, res[rep][1]["tau"][:, 0]), logy=True)
            Lr = res[rep][1]["L"]
            Lr["formation"] = Formation(load_case(ROOT / "config" / f"{name}.yaml"))
            plots.trajectories(Lr, [0, 10, 21, 32, 40], OUT / f"{name}_irl_trajectories.png",
                               f"{name}, IRL seed {rep}: trajectories (cf. Fig. 3/14)")
            print(name, "done, representative seed", rep, flush=True)
    (OUT / "metrics.json").write_text(json.dumps(allm, indent=2, default=float))
    (OUT / "table.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
