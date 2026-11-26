"""Mốc 5, K4: lời giải tham chiếu dùng mô hình (chỉ để kiểm tra, KHÔNG dùng trong bộ điều khiển).

Tuyến tính hóa hệ sai số (15)-(19) quanh chạy thẳng upsilon_d = upsilon0 = (|v_c|, 0, 0),
psi = psi_d = psi0, rồi giải ARE trò chơi có chiết khấu với hàm chi phí của Paper A trên
trạng thái  x = [z_eta(3); z_ups(3); upsilon_d(3)]  (dạng [e; r] của [M15], r = upsilon_d hằng):

  z_eta_dot = -beta z_eta + J0 z_ups
  z_ups_dot = (beta I - M^-1 A_N) z_ups + (M^-1 A_N beta J0^T - beta^2 J0^T) z_eta
              - M^-1 N(upsilon0) upsilon_d + M^-1 tau + M^-1 delta
  upsilon_d_dot = 0
A_N = d(N(nu) nu)/d nu tại upsilon0 (tiếp tuyến cho phần lệch), N(upsilon0) (cát tuyến cho
tham chiếu, đúng tại upsilon0), N = C + D.

In: nghiệm, khuếch đại, và trạng thái xác lập z_ss, tau_ss khi upsilon_d = upsilon0, delta = 0
và delta = (3, -2.5, 3). Đó là chất lượng bám mà hàm chi phí đã cho ngụ ý.

Chạy:  .venv/bin/python scripts/irl_reference.py [r_scale]
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.analysis.hinf_reference import game_are, gains           # noqa: E402
from src.models.vessel import M, coriolis, damping, J             # noqa: E402


def N_nu(nu):
    return (coriolis(nu) + damping(nu)) @ nu


def linear_model(u0=4 * np.sqrt(2), psi0=np.pi / 4, beta=2.0):
    ups0 = np.array([u0, 0.0, 0.0])
    Mi = np.linalg.inv(M)
    A_N = np.zeros((3, 3))
    for k in range(3):
        e = np.zeros(3); e[k] = 1e-6
        A_N[:, k] = (N_nu(ups0 + e) - N_nu(ups0 - e)) / 2e-6
    N_sec = coriolis(ups0) + damping(ups0)
    J0 = J(psi0)
    I3, Z3 = np.eye(3), np.zeros((3, 3))
    A = np.block([[-beta * I3, J0, Z3],
                  [Mi @ A_N @ (beta * J0.T) - beta ** 2 * J0.T, beta * I3 - Mi @ A_N, -Mi @ N_sec],
                  [Z3, Z3, Z3]])
    B = np.vstack([Z3, Mi, Z3])
    return A, B, B.copy(), ups0


def steady_state(A, B, E, K, L, ups0, delta):
    """Closed loop with u = -K x and the ACTUAL disturbance delta (not the worst case):
    solve 0 = (A - B K)_zz z + (A - B K)_zr ups0 + E_z delta for z."""
    Acl = A - B @ K
    z = -np.linalg.solve(Acl[:6, :6], Acl[:6, 6:] @ ups0 + E[:6] @ delta)
    x = np.r_[z, ups0]
    return z, -K @ x


def main(r_scale=1.0):
    A, B, E, ups0 = linear_model()
    Q = np.diag([100.0] * 6 + [0.0] * 3)
    R = r_scale * np.eye(3)
    gamma, alpha = 5.0, 0.1
    P = game_are(A, B, E, Q, R, gamma, alpha)
    K, L = gains(P, B, E, R, gamma)
    np.set_printoptions(precision=3, suppress=True, linewidth=140)
    print(f"R = {r_scale:g} I : eig(A - BK + EL - alpha/2) =",
          np.round(np.linalg.eigvals(A - B @ K + E @ L - 0.05 * np.eye(9)).real, 3))
    print("K (rows tau_u, tau_v, tau_r; cols z_eta(3) z_ups(3) ups_d(3)):\n", K)
    for name, d in (("delta = 0", np.zeros(3)), ("delta = (3,-2.5,3)", np.array([3, -2.5, 3.0]))):
        z, tau = steady_state(A, B, E, K, L, ups0, d)
        print(f"  {name:20s} z_eta_ss = {z[:3]},  z_ups_ss = {z[3:]},  tau_ss = {tau}")
    tau_needed = N_nu(ups0)
    print("  tau needed to cruise at ups0 (no error):", tau_needed)
    return K


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 1.0)
