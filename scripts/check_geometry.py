"""Mốc 1: in bảng hình học của Case 1, Case 2 (Eqs. (6)-(8)) và phân tích cản của tầng cao.

Chạy:  .venv/bin/python scripts/check_geometry.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import load_case                                     # noqa: E402
from src.graph.bearing import (bearing_laplacian, partition,        # noqa: E402
                               check_ff_invertible, target_follower_positions)


def main():
    for name in ("case1", "case2"):
        cfg = load_case(f"config/{name}.yaml")
        n, nl = cfg["n"], cfg["graph"]["n_leaders"]
        B = bearing_laplacian(n, cfg["graph"]["bearings"])
        _, _, B_fl, B_ff = partition(B, nl)
        lam = np.linalg.eigvalsh(B_ff)
        check_ff_invertible(B_ff)
        p_l = np.concatenate([cfg["initial"]["eta"][i][:2] for i in range(1, nl + 1)])
        p_f = target_follower_positions(p_l, B_fl, B_ff).reshape(-1, 2)
        p_star = np.vstack([p_l.reshape(-1, 2), p_f])
        c = p_star.mean(axis=0)
        print(f"\n=== {name}: n = {n}, leaders 1..{nl}")
        print("  eig(B_ff) =", np.round(lam, 4))
        for i, p in enumerate(p_star, start=1):
            role = "leader  " if i <= nl else "follower"
            print(f"  {role} {i}: p* = ({p[0]:6.2f}, {p[1]:6.2f})")
        s_n = np.sqrt(((p_star - c) ** 2).sum() / n)
        s_raw = np.sqrt(((p_star - c) ** 2).sum())
        print(f"  centroid c(p*) = ({c[0]:.2f}, {c[1]:.2f});  s = {s_n:.2f} (/n, [L21])"
              f"  |  {s_raw:.2f} (không /n, khớp Hình 12)")
        hl = cfg["high_level"]
        for kv in (0.1, 5.0, 10.0, 20.0, 40.0):
            zeta = kv * np.sqrt(lam) / (2 * np.sqrt(hl["k_p"]))
            # slowest real part of s^2 + kv*lam*s + kp*lam = 0
            re = [max(np.roots([1, kv * l, hl["k_p"] * l]).real) for l in lam]
            print(f"  k_p = {hl['k_p']:g}, k_v = {kv:5.1f}: zeta in [{zeta.min():.3f}, {zeta.max():.3f}],"
                  f"  slowest 2% settling ~ {4 / -max(re):6.1f} s")


if __name__ == "__main__":
    main()
