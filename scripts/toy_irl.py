"""Mốc 4: Algorithm 2 trên bài toán đồ chơi tuyến tính, so với ARE H∞ có chiết khấu.

Chạy:  .venv/bin/python scripts/toy_irl.py
Kết quả: results/moc4_toy/{sweep.md, convergence.png}
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import plots                                                       # noqa: E402
from src.analysis.hinf_reference import game_are, gains, kleinman_game      # noqa: E402
from src.low_level.basis import QuadraticBasis, LinearBasis                 # noqa: E402
from src.low_level.data_collection import collect, SumOfSines               # noqa: E402
from src.low_level.offpolicy_irl import OffPolicyHinf, RankDeficientError   # noqa: E402

OUT = ROOT / "results" / "moc4_toy"


def learn(c, T, duration, amp):
    A, B, E, Q, R = (np.array(c[k], float) for k in "ABEQR")
    n, m, q = A.shape[0], B.shape[1], E.shape[1]
    eu, ed = SumOfSines(m, amp, seed=1), SumOfSines(q, amp, seed=2)
    f = lambda t, x, u, d: A @ x + B @ u + E @ d
    data = collect(f, np.array(c["x0"], float), lambda t, x: eu(t), lambda t, x: ed(t),
                   T, int(round(duration / T)), c["irl"]["n_sub"])
    idx = list(range(n))
    sig = QuadraticBasis(idx)
    irl = OffPolicyHinf(sig, LinearBasis(idx), LinearBasis(idx),
                        lambda X: np.einsum("...i,ij,...j->...", X, Q, X), R, c["gamma"], c["alpha"])
    irl.precompute(data)
    res = irl.run(np.zeros((n, m)), np.zeros((n, q)), eps=c["irl"]["eps"],
                  max_iter=c["irl"]["max_iter"])
    P = game_are(A, B, E, Q, R, c["gamma"], c["alpha"])
    K, L = gains(P, B, E, R, c["gamma"])
    err = np.abs(sig.P_from_weights(res.W_c) - P).max() / np.abs(P).max()
    errK = np.abs(res.W_a + K.T).max() / np.abs(K).max()
    return res, err, errK, sig, P


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c = yaml.safe_load((ROOT / "config" / "toy_irl.yaml").read_text())
    sw = c["sweep"]
    rows = ["| T (s) | thời lượng (s) | M | biên độ thăm dò | hạng | cond (sau chuẩn hóa) | vòng | lỗi P (tương đối) | lỗi K (tương đối) |",
            "|---|---|---|---|---|---|---|---|---|"]
    for T, dur, amp in itertools.product(sw["T"], sw["duration"], sw["probe_amp"]):
        try:
            res, err, errK, _, _ = learn(c, T, dur, amp)
            rows.append(f"| {T:g} | {dur:g} | {int(round(dur / T))} | {amp:g} | {res.rank}/{res.n_unknowns} | "
                        f"{res.cond:.2e} | {len(res.history)} | {err:.1e} | {errK:.1e} |")
        except RankDeficientError as ex:
            rows.append(f"| {T:g} | {dur:g} | {int(round(dur / T))} | {amp:g} | thiếu hạng | – | – | – | {ex} |")
    (OUT / "sweep.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))

    # convergence figure (cf. Fig. 10, 11): default setting
    res, err, errK, sig, P = learn(c, 0.01, 10.0, 1.0)
    A, B, E, Q, R = (np.array(c[k], float) for k in "ABEQR")
    Pk = kleinman_game(A, B, E, Q, R, c["gamma"], c["alpha"], np.zeros((1, 2)), np.zeros((1, 2)),
                       len(res.history))
    it = np.arange(1, len(res.history) + 1)
    errs = [np.abs(sig.P_from_weights(h["W_c"]) - P).max() / np.abs(P).max() for h in res.history]
    errs_k = [np.abs(Pk[k] - P).max() / np.abs(P).max() for k in range(len(it))]
    plots.series(it, [np.maximum(errs, 1e-16), np.maximum(errs_k, 1e-16)],
                 ["off-policy IRL (no model)", "Kleinman PI (model-based)"],
                 OUT / "convergence.png", "‖P_k − P*‖ / ‖P*‖ (log)",
                 "Toy 2-D H∞: Algorithm 2 vs model-based policy iteration", logy=True,
                 styles=["-", "--"])
    print(f"default: rel. error P = {err:.2e}, K = {errK:.2e}, iterations = {len(res.history)}")


if __name__ == "__main__":
    main()
