"""Hình cho báo cáo tái tạo Paper A (docs/report_paperA.md).

Chạy:  .venv/bin/python scripts/make_report_figures.py [--no-learning] [--no-gif]
Cần:   trọng số IRL của Mốc 5 (results/moc5_irl/<case>_seed<s>_W.npz) và seed đại diện
       của Mốc 6 (results/moc6/metrics.json). Thời gian: khoảng 2 phút, cộng khoảng 3 phút
       nếu vẽ cả hình quá trình học (vì phải học lại một seed).
Kết quả: results/report/
  <case>_overview.png   6 ô theo kiểu Hình 3–12 của Paper A: quỹ đạo, sai số bearing,
                        kích thước đội hình, bán kính bám ε(t), sai số vận tốc, lực surge
  <case>_yaw.png        góc hướng của follower, M1 so với IRL (Hình 6/16)
  case1_learning.png    Algorithm 2 trên từng follower: ‖W‖, sai số Bellman trên dữ liệu giữ
                        lại, chi phí kiểm định của từng vòng và vòng được chọn (Hình 10/11)
  <case>_animation.gif  ảnh động M1 và IRL chạy cạnh nhau, có đội hình đích p* mờ phía sau
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                          # noqa: E402
import numpy as np                                                       # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter             # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from src import plots                                                    # noqa: E402
from src.baselines.m1_model_based import M1Controller                    # noqa: E402
from src.config import load_case                                         # noqa: E402
from src.high_level.leaders import formation_scale                       # noqa: E402
from src.low_level.augmented_state import BASIS                          # noqa: E402
from src.low_level.basis import LinearBasis                              # noqa: E402
from src.low_level.irl_controller import IRLController                   # noqa: E402
from src.metrics import bearing_error                                    # noqa: E402
from src.sim.runner import run_closed_loop                               # noqa: E402

OUT = ROOT / "results" / "report"
W_DIR = ROOT / "results" / "moc5_irl"
C_M1, C_IRL, C_REF = plots.SV_COLORS[1], plots.SV_COLORS[0], plots.INK


def irl_controller(name, seed, cfg):
    Wz = np.load(W_DIR / f"{name}_seed{seed}_W.npz")
    return IRLController({int(k[2:]): Wz[k] for k in Wz.files}, LinearBasis(BASIS["main"]),
                         cfg["low_level"]["beta_eta"])


def series_of(L):
    F = L["formation"]
    fol = np.asarray(F.followers) - 1
    return {"e": np.array([bearing_error(p, F.bearings) for p in L["p"]]),
            "s": np.array([formation_scale(p, False) for p in L["p"]]),
            "s_star": np.array([formation_scale(p, False) for p in L["p_star"]]),
            "eps": np.linalg.norm(L["p"][:, fol] - L["p_d"], axis=-1).max(axis=1),
            "zups": np.linalg.norm(L["z_ups"], axis=-1).max(axis=1),
            "tau_u": np.abs(L["tau"][:, :, 0]).max(axis=1)}


def draw_formation(ax, F, P, alpha=1.0, lw=1.0, color=None, ms=5):
    for (i, j) in F.bearings:
        ax.plot(*P[[i - 1, j - 1]].T, "-", color=color or plots.MUTED, lw=lw, alpha=alpha)
    for k in range(F.n):
        ax.plot(*P[k], "o", ms=ms, color=color or plots.SV_COLORS[k], alpha=alpha,
                mec="white", mew=0.6)


def overview(name, LM, LI, seed, path):
    F, t = LI["formation"], LI["t"]
    SM, SI = series_of(LM), series_of(LI)
    fig, axs = plt.subplots(2, 3, figsize=(15, 8.2))
    ax = axs[0, 0]
    for k in range(F.n):
        ls = "--" if k < F.nl else "-"
        ax.plot(*LI["p"][:, k].T, ls, color=plots.SV_COLORS[k], lw=1.3, label=f"SV{k + 1}{' (leader)' if k < F.nl else ''}")
        if k >= F.nl:
            ax.plot(*LM["p"][:, k].T, ":", color=plots.SV_COLORS[k], lw=1.0)
    for ts in (0, 10, 21, 32, 40):
        kk = int(np.argmin(np.abs(t - ts)))
        draw_formation(ax, F, LI["p"][kk])
        ax.annotate(f"t = {ts} s", LI["p"][kk, 0], xytext=(6, 6), textcoords="offset points", fontsize=8, color=plots.MUTED)
    ax.set_aspect("equal")
    ax.set_title(f"(a) quỹ đạo: IRL nét liền, M1 chấm (follower)", fontsize=10)
    plots._style(ax, "x (m)", "y (m)")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    panels = [
        (axs[0, 1], "e", "‖g − g*‖ (log)", "(b) sai số bearing (Hình 5)", True, None),
        (axs[0, 2], "s", "s(p) (không 1/n)", "(c) kích thước đội hình (Hình 12)", False, "s_star"),
        (axs[1, 0], "eps", "max_i ‖p_i − p_d,i‖ (m)", "(d) bán kính sai số bám ε(t)", False, None),
        (axs[1, 1], "zups", "max_i ‖z_υ,i‖ (log)", "(e) sai số bám vận tốc (Hình 8)", True, None),
        (axs[1, 2], "tau_u", "max_i |τ_u,i| (N, log)", "(f) lực surge (Hình 9)", True, None),
    ]
    for ax, key, yl, title, logy, ref in panels:
        ax.plot(t, np.maximum(SM[key], 1e-6), color=C_M1, lw=1.4, label="M1 (dựa trên mô hình, [L21])")
        ax.plot(t, np.maximum(SI[key], 1e-6), color=C_IRL, lw=1.4, label=f"IRL (seed {seed})")
        if ref:
            ax.plot(t, SI[ref], ":", color=C_REF, lw=1.4, label="s(p*) mong muốn")
        if logy:
            ax.set_yscale("log")
        ax.set_title(title, fontsize=10)
        plots._style(ax, "Time (s)", yl)
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle(f"{name}: M1 so với IRL (k_v danh định, a_max = 5 m/s², có nhiễu δ)", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def yaw(name, LM, LI, path):
    F, t = LI["formation"], LI["t"]
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.6), sharey=True)
    for ax, L, lab in ((axs[0], LM, "M1"), (axs[1], LI, "IRL")):
        for k in F.followers:
            ax.plot(t, L["psi"][:, k - 1], color=plots.SV_COLORS[k - 1], lw=1.4, label=f"ψ_{k}")
        ax.axhline(F.psi0, ls=":", color=C_REF, lw=1.2, label="ψ₀ = π/4")
        ax.set_title(f"{name}, {lab}: góc hướng của follower (Hình 6/16)", fontsize=10)
        plots._style(ax, "Time (s)", "ψ (rad)")
        ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def learning(path, name="case1", seed=None):
    """Re-train one seed (same seed scheme as run_irl.py --seeds) to get the iteration history."""
    from run_irl import train
    cfg = load_case(ROOT / "config" / f"{name}.yaml")
    followers = list(range(cfg["graph"]["n_leaders"] + 1, cfg["n"] + 1))
    _, hist, _, _ = train(cfg, {}, followers, seed=seed)
    fig, axs = plt.subplots(1, 3, figsize=(15, 3.8))
    for c, (i, h) in enumerate(hist.items()):
        col = plots.SV_COLORS[i - 1]
        it = np.arange(1, len(h["norm_W"]) + 1)
        axs[0].plot(it, h["norm_W"], "-o", ms=3, color=col, label=f"SV{i} ({h['batches']} lô)")
        axs[1].semilogy(it, np.maximum(h["bellman_val"], 1e-12), "-o", ms=3, color=col, label=f"SV{i}")
        J = np.array(h["J_val"], float)
        axs[2].semilogy(it, np.where(np.isfinite(J), J, np.nan), "-o", ms=3, color=col, label=f"SV{i}")
        k = h["picked_iter"]
        axs[2].plot(k, J[k - 1], "*", ms=14, color=col, mec="black", mew=0.6)
        axs[2].axhline(h["J_behaviour_P"], ls=":", color=col, lw=1.2)
    axs[0].set_title("(a) ‖Ŵ‖ theo vòng lặp (Hình 10/18)", fontsize=10)
    axs[1].set_title("(b) sai số Bellman, dữ liệu giữ lại (Hình 11/19)", fontsize=10)
    axs[2].set_title("(c) chi phí kiểm định; ★ vòng được chọn; chấm = phần P\ncủa chính sách hành vi (ngưỡng chấp nhận)", fontsize=10)
    for ax, yl in zip(axs, ("‖Ŵ‖", "RMS Bellman error", "J kiểm định (22)")):
        plots._style(ax, "vòng lặp (lô cuối)", yl)
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle(f"{name}, seed {seed}: Algorithm 2 kèm bước kiểm định không cần mô hình (Mốc 5)", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def animation(name, LM, LI, path, every_s=0.25):
    F, t = LI["formation"], LI["t"]
    idx = np.arange(0, len(t), max(1, int(round(every_s / (t[1] - t[0])))))
    allp = np.concatenate([LM["p"].reshape(-1, 2), LI["p"].reshape(-1, 2)])
    lo, hi = allp.min(0) - 5, allp.max(0) + 5
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    def frame(n):
        k = idx[n]
        for ax, L, lab in ((axs[0], LM, "M1"), (axs[1], LI, "IRL")):
            ax.clear()
            for a in range(F.n):
                ax.plot(*L["p"][:k + 1, a].T, "-", color=plots.SV_COLORS[a], lw=0.8, alpha=0.5)
            draw_formation(ax, F, L["p_star"][k], alpha=0.25, lw=2.5, color=plots.MUTED, ms=9)
            draw_formation(ax, F, L["p"][k])
            ax.set_xlim(lo[0], hi[0])
            ax.set_ylim(lo[1], hi[1])
            ax.set_aspect("equal")
            ax.set_title(f"{name}, {lab}   t = {t[k]:.1f} s   (mờ: đội hình đích p*)", fontsize=10)
            plots._style(ax, "x (m)", "y (m)")
        return []

    anim = FuncAnimation(fig, frame, frames=len(idx), blit=False)
    anim.save(path, writer=PillowWriter(fps=12), dpi=70)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rep = json.loads((ROOT / "results" / "moc6" / "metrics.json").read_text())
    for name in ("case1", "case2"):
        cfg = load_case(ROOT / "config" / f"{name}.yaml")
        seed = rep[name]["representative_seed"]
        LM = run_closed_loop(cfg, M1Controller())
        LI = run_closed_loop(cfg, irl_controller(name, seed, cfg))
        overview(name, LM, LI, seed, OUT / f"{name}_overview.png")
        yaw(name, LM, LI, OUT / f"{name}_yaw.png")
        print(name, "overview + yaw done", flush=True)
        if "--no-gif" not in sys.argv:
            animation(name, LM, LI, OUT / f"{name}_animation.gif")
            print(name, "animation done", flush=True)
    if "--no-learning" not in sys.argv:
        learning(OUT / "case1_learning.png", "case1", rep["case1"]["representative_seed"])
        print("learning done", flush=True)


if __name__ == "__main__":
    main()
