"""Figures in the style of Paper A (static PNG, matplotlib).

Colours: fixed categorical order per vessel (SV1..SV6), never cycled; ordered parameter
sweeps use one sequential blue ramp (light -> dark = small -> large). Identity is never
colour-only: legends always present, leaders dashed.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt     # noqa: E402
import numpy as np                  # noqa: E402

SV_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
RAMP = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"


def _style(ax, xlabel, ylabel):
    ax.set_xlabel(xlabel, color=INK)
    ax.set_ylabel(ylabel, color=INK)
    ax.grid(True, color=GRID, linewidth=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED)


def _ls(i, n_leaders):
    return "--" if i <= n_leaders else "-"


def trajectories(log, snapshots, path, title):
    """Fig. 3 / 14 style: paths + formation snapshots (bearing edges drawn)."""
    F, t, P = log["formation"], log["t"], log["p"]
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    for i in range(1, F.n + 1):
        ax.plot(P[:, i - 1, 0], P[:, i - 1, 1], _ls(i, F.nl), color=SV_COLORS[i - 1],
                lw=1.5, label=f"SV {i}" + (" (leader)" if i <= F.nl else ""))
    for ts in snapshots:
        k = int(np.argmin(np.abs(t - ts)))
        for (i, j) in F.bearings:
            ax.plot(*P[k, [i - 1, j - 1]].T, color=INK, lw=0.8, alpha=0.6)
        ax.scatter(P[k, :, 0], P[k, :, 1], c=SV_COLORS[:F.n], s=22, zorder=3,
                   edgecolors="white", linewidths=1.0)
        ax.annotate(f"t = {t[k]:.0f} s", P[k].max(axis=0), xytext=(4, 4),
                    textcoords="offset points", fontsize=8, color=MUTED)
    ax.set_aspect("equal")
    _style(ax, "x (m)", "y (m)")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title(title, fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def series(t, ys, labels, path, ylabel, title, colors=None, styles=None, logy=False, refs=None):
    """Generic time-series figure: one line per entry of ys (each (N,))."""
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    colors = colors or SV_COLORS
    for k, (y, lab) in enumerate(zip(ys, labels)):
        ax.plot(t, y, (styles or ["-"] * len(ys))[k], color=colors[k], lw=1.5, label=lab)
    for y, lab in (refs or []):
        ax.plot(t, y, ":", color=INK, lw=1.2, label=lab)
    if logy:
        ax.set_yscale("log")
    _style(ax, "Time (s)", ylabel)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title(title, fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
