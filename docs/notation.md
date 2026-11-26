# Bảng ký hiệu: Paper A ↔ tên biến trong code

Cập nhật dần theo từng mốc. Số công thức theo Paper A.

| Paper A | Code | Ý nghĩa | File |
| --- | --- | --- | --- |
| η = [p; ψ] = [x, y, ψ] | `eta` | Vị trí và góc hướng, hệ trái đất | `models/vessel.py` |
| υ = [ϑ; ω] = [u, v, r] | `nu` | Vận tốc trong hệ thân tàu (surge, sway, yaw rate) | `models/vessel.py` |
| J(ψ), (2) | `J(psi)` | blkdiag(R_p(ψ), 1) | `models/vessel.py` |
| R_p(ψ) ≡ J_p(ψ) | `rot2(psi)` | Ma trận quay 2×2, thân → trái đất | `models/vessel.py` |
| M, C(υ), D(υ) | `M`, `coriolis(nu)`, `damping(nu)` | Quán tính, Coriolis, cản (tr. 18) | `models/vessel.py` |
| δ(t) | `Disturbance(...)(t)` | Nhiễu ngoài (tr. 18), rand giữ theo ZOH 1 ms | `models/vessel.py` |
| τ | `tau` | Lực và mô-men điều khiển | |
| g_ij | `bearing(p_i, p_j)` | Bearing (p_j − p_i)/‖p_j − p_i‖ | `graph/bearing.py` |
| g*_ij | `cfg["graph"]["bearings"][(i, j)]` | Bearing đích | `config/case*.yaml` |
| P_g | `projection(g)` | I − ggᵀ | `graph/bearing.py` |
| B, B_ll, B_lf, B_fl, B_ff, (6)–(7) | `bearing_laplacian`, `partition` | Bearing Laplacian và các khối | `graph/bearing.py` |
| p_f*, (8) | `target_follower_positions` | Vị trí đích của follower | `graph/bearing.py` |
| v_c, β(t) (tốc độ co giãn), ψ₀ | `v_c`, `beta_s`, `psi0` | Tham số tầng cao (9), (63) | `config/case*.yaml` |
| k_p, k_v | `k_p`, `k_v` | Hệ số của (13) | `config/case*.yaml` |
| k_ω | `k_omega` | Hệ số đồng thuận góc (14) | `config/case*.yaml` |
| β_η (hệ số backstepping, (16)) | `beta_eta` | Đổi tên để khỏi trùng β | (Mốc 3) |
| α_i (vận tốc ảo, (16)) | `alpha_v` | Đổi tên để khỏi trùng α chiết khấu | (Mốc 3) |
| α (chiết khấu, (22)) | `alpha_disc` | | (Mốc 4) |
