"""Mốc 7: CBF giữa các tàu, kịch bản S0 (k_v = 0.1 của Paper A), docs/PLAN_phase2.md.

Chạy:  .venv/bin/python scripts/run_moc7.py      (cần trọng số IRL của Mốc 5)
Kết quả: results/moc7/{table.md, metrics.json, *.png}

Mỗi case: M1 và IRL (10 seed), không lọc và có lọc CBF-QP (src/safety/qp_filter.py).
Thêm lượt kiểm "k_v danh định + CBF": không có xung đột thì bộ lọc phải gần như không can thiệp.
Kiểm (đặt trước khi chạy):
  (a) khoảng cách thật nhỏ nhất giữa mọi cặp tàu >= d_min;
  (b) tàu ảo giữ đúng biên D_ij = d_min + eps_i + eps_j (eps_leader = 0);
  (c) eps thật <= eps giả định của tầng thấp (nếu sai thì (a) không còn được bảo đảm).
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
from src.metrics import bearing_error, rmse                              # noqa: E402
from src.safety.qp_filter import CBFFilter                               # noqa: E402
from src.sim.runner import run_closed_loop, Formation                    # noqa: E402

OUT = ROOT / "results" / "moc7"
W_DIR = ROOT / "results" / "moc5_irl"
N_SEEDS = 10
KV_S0 = 0.1


def pair_distances(P):
    """P: (N, n, 2) -> (N, n, n) distances."""
    return np.linalg.norm(P[:, :, None] - P[:, None], axis=-1)


def _run(name, ctrl_name, seed, cbf, k_v):
    cfg = load_case(ROOT / "config" / f"{name}.yaml")
    sc = cfg["safety"]
    eps_assumed = sc["eps"][ctrl_name]
    if ctrl_name == "M1":
        ctrl = M1Controller()
    else:
        Wz = np.load(W_DIR / f"{name}_seed{seed}_W.npz")
        ctrl = IRLController({int(k[2:]): Wz[k] for k in Wz.files}, LinearBasis(BASIS["main"]),
                             cfg["low_level"]["beta_eta"])
    filt = CBFFilter(sc["d_min"], eps_assumed, sc["alpha1"], sc["alpha2"], cfg["high_level"]["a_max"]) if cbf else None
    out = {"case": name, "ctrl": ctrl_name, "seed": seed, "cbf": cbf, "k_v": k_v}
    try:
        L = run_closed_loop(cfg, ctrl, k_v=k_v, safety_filter=filt)
    except FloatingPointError as ex:
        return out | {"diverged": str(ex)}, None
    F, t = L["formation"], L["t"]
    fol = np.asarray(F.followers) - 1
    n = F.n
    iu = np.triu_indices(n, 1)
    Dr = pair_distances(L["p"])[:, iu[0], iu[1]]                       # real
    Pv = L["p"].copy()
    Pv[:, fol] = L["p_d"]
    Dv = pair_distances(Pv)[:, iu[0], iu[1]]                           # virtual (leaders exact)
    eps_i = np.array([eps_assumed if k in fol else 0.0 for k in range(n)])
    D_req = sc["d_min"] + eps_i[iu[0]] + eps_i[iu[1]]
    is_ll = (iu[0] < F.nl) & (iu[1] < F.nl)                            # leader-leader: not filtered
    eps_t = np.linalg.norm(L["p"][:, fol] - L["p_d"], axis=-1).max(axis=1)
    e = np.array([bearing_error(p, F.bearings) for p in L["p"]])
    dPi = np.linalg.norm(L["Pi"] - L["Pi_nom"], axis=-1).max(axis=1)
    k_min = np.unravel_index(Dr.argmin(), Dr.shape)
    pairs = [(int(a) + 1, int(b) + 1) for a, b in zip(*iu)]
    out |= {
        "d_real_min": float(Dr.min()), "t_d_real_min": float(t[k_min[0]]), "pair": pairs[k_min[1]],
        "virtual_margin_min": float((Dv - D_req)[:, ~is_ll].min()),
        "eps_max": float(eps_t.max()), "eps_assumed": eps_assumed,
        "RMSE": rmse(t, e), "e_final": float(e[-1]),
        "max|Pi-Pi_nom|": float(dPi.max()), "mean|Pi-Pi_nom|": float(dPi.mean()),
        "effort": float(np.trapezoid(np.abs(L["tau"]).sum(axis=(1, 2)), t)),
        "qp_steps": L["cbf_counts"]["qp_solved"], "infeasible": L["cbf_counts"]["infeasible"],
    }
    out["ok_a"] = out["d_real_min"] >= sc["d_min"]
    out["ok_b"] = out["virtual_margin_min"] >= -1e-3 if cbf else None
    out["ok_c"] = out["eps_max"] <= eps_assumed
    series = {"t": t, "d_real": Dr.min(axis=1), "e": e, "dPi": dPi, "eps": eps_t,
              "p": L["p"], "p_star": L["p_star"], "psi": L["psi"]}
    return out, series


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name in ("case1", "case2"):
        kv_nom = load_case(ROOT / "config" / f"{name}.yaml")["high_level"]["k_v"]
        for cbf in (False, True):
            jobs.append((name, "M1", None, cbf, KV_S0))
            jobs += [(name, "IRL", s, cbf, KV_S0) for s in range(N_SEEDS)]
        jobs += [(name, "M1", None, True, kv_nom), (name, "IRL", 1, True, kv_nom)]
    with ProcessPoolExecutor(12) as ex:
        res = dict(zip(jobs, ex.map(_run, *zip(*jobs))))
    rows_all = [r for r, _ in res.values()]
    (OUT / "metrics.json").write_text(json.dumps(rows_all, indent=2, default=float))

    f = lambda x: "—" if x is None else (f"{x:.3g}" if isinstance(x, float) else str(x))
    ok = lambda b: "—" if b is None else ("✓" if b else "✗")
    lines = ["| case | tầng thấp | k_v | CBF | d thật min (m) [cặp, t] | lề tàu ảo min (m) | ε thật / giả định | RMSE | max‖Π−Π_nom‖ | bước QP / vô nghiệm | (a) (b) (c) |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in ("case1", "case2"):
        kv_nom = load_case(ROOT / "config" / f"{name}.yaml")["high_level"]["k_v"]
        for cbf, kv in ((False, KV_S0), (True, KV_S0), (True, kv_nom)):
            for ctrl in ("M1", "IRL"):
                rs = [r for r in rows_all if r["case"] == name and r["ctrl"] == ctrl and r["cbf"] == cbf and r["k_v"] == kv]
                if not rs:
                    continue
                good = [r for r in rs if "diverged" not in r]
                lab = f"| {name} | {ctrl}{'' if len(rs) == 1 else f' ({len(good)}/{len(rs)} không phân kỳ)'} | {kv} | {'có' if cbf else 'không'} |"
                if not good:
                    lines.append(lab + " phân kỳ | | | | | | |")
                    continue
                if len(good) == 1:
                    r = good[0]
                    lines.append(lab + f" {r['d_real_min']:.3f} [{r['pair']}, {r['t_d_real_min']:.1f}] | {f(r['virtual_margin_min'])} | "
                                 f"{r['eps_max']:.3f} / {r['eps_assumed']} | {r['RMSE']:.4f} | {r['max|Pi-Pi_nom|']:.3g} | "
                                 f"{r['qp_steps']} / {r['infeasible']} | {ok(r['ok_a'])} {ok(r['ok_b'])} {ok(r['ok_c'])} |")
                else:
                    g = lambda k: np.array([r[k] for r in good], float)
                    rng = lambda k: f"{np.median(g(k)):.3g} [{g(k).min():.3g}, {g(k).max():.3g}]"
                    cnt = lambda k: f"{sum(bool(r[k]) for r in good)}/{len(good)}" if good[0][k] is not None else "—"
                    lines.append(lab + f" {rng('d_real_min')} | {rng('virtual_margin_min')} | {rng('eps_max')} / {good[0]['eps_assumed']} | "
                                 f"{rng('RMSE')} | {rng('max|Pi-Pi_nom|')} | {int(np.median(g('qp_steps')))} / {int(g('infeasible').sum())} | "
                                 f"{cnt('ok_a')} {cnt('ok_b')} {cnt('ok_c')} |")
    lines += ["", "Nhóm IRL: trung vị [min, max] trên các seed không phân kỳ; (a)(b)(c) đếm số seed đạt.",
              "(a) d thật ≥ d_min; (b) tàu ảo giữ biên D_ij; (c) ε thật ≤ ε giả định."]
    (OUT / "table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)

    # figures: M1 and IRL seed 1, S0 without / with CBF
    for name in ("case1", "case2"):
        F = Formation(load_case(ROOT / "config" / f"{name}.yaml"))
        S = {(c, cbf): res[(name, c, None if c == "M1" else 1, cbf, KV_S0)][1] for c in ("M1", "IRL") for cbf in (False, True)}
        S = {k: v for k, v in S.items() if v is not None}
        keys = list(S)
        labs = [f"{c}, {'CBF' if cbf else 'no filter'}" for c, cbf in keys]
        cols = [plots.SV_COLORS[{"M1": 1, "IRL": 0}[c]] for c, _ in keys]
        sty = ["-" if cbf else "--" for _, cbf in keys]
        t = S[keys[0]]["t"]
        d_min = load_case(ROOT / "config" / f"{name}.yaml")["safety"]["d_min"]
        plots.series(t, [S[k]["d_real"] for k in keys], labs, OUT / f"{name}_S0_min_distance.png",
                     "min_{i≠j} ‖p_i − p_j‖ (m)", f"{name}, S0 (k_v = 0.1): closest pair, real vessels",
                     colors=cols, styles=sty, refs=[(np.full_like(t, d_min), f"d_min = {d_min} m")])
        plots.series(t, [S[k]["e"].clip(1e-6) for k in keys], labs, OUT / f"{name}_S0_bearing_error.png",
                     "‖g − g*‖ (log)", f"{name}, S0: bearing error (price of safety)", colors=cols, styles=sty, logy=True)
        kc = [k for k in keys if k[1]]
        plots.series(t, [S[k]["dPi"] for k in kc], [labs[keys.index(k)] for k in kc], OUT / f"{name}_S0_intervention.png",
                     "max_i ‖Π_i − Π_nom,i‖ (m/s²)", f"{name}, S0: CBF intervention", colors=[cols[keys.index(k)] for k in kc])
        for c in ("M1", "IRL"):
            for cbf in (False, True):
                if (c, cbf) in S:
                    Lr = {kk: S[(c, cbf)][kk] for kk in ("t", "p", "p_star", "psi")} | {"formation": F}
                    plots.trajectories(Lr, [0, 10, 21, 32, 40], OUT / f"{name}_S0_{c}_{'cbf' if cbf else 'none'}_traj.png",
                                       f"{name}, S0, {c}, {'CBF' if cbf else 'no filter'}")


if __name__ == "__main__":
    main()
