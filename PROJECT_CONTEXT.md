# PROJECT_CONTEXT: Đội hình tàu bearing + H∞ IRL off-policy, có thêm CBF tránh va chạm

> **Đọc file này đầu tiên.** File dành cho coding agent và cho Đức (người review code).
> Mục tiêu của file: để agent nắm trọn ý đồ bài báo, đọc paper gốc, rồi **tự lập kế hoạch code chi tiết và đưa Đức duyệt trước khi viết code**.
>
> Tác giả dự án: Tô Minh Đức (HUST). Thầy hướng dẫn: thầy Nam (nhóm PGS. Đào Phương Nam, HUST).
> Cập nhật: 26/11/2026.

---

## 0. Tóm tắt một đoạn

Ta viết một bài báo mở rộng **bài gốc** (gọi là **Paper A**): điều khiển đội hình tàu mặt nước theo **bearing**, có **co giãn đội hình**, cấu trúc **cascade hai tầng**. Tầng cao sinh quỹ đạo tham chiếu (tàu ảo). Tầng thấp là bộ điều khiển **H∞ học off-policy (IRL), không cần mô hình**. Paper A **không có tránh va chạm**, dù động lực của nó là đi qua luồng hẹp. Đóng góp của ta: **thêm tầng an toàn CBF** (lấy công cụ từ **Paper B**) để các tàu không đâm nhau, không đâm bờ hay vật cản, và đội hình tự co lại khi luồng hẹp.

**Giai đoạn hiện tại: chỉ mô phỏng lại Paper A cho đúng.** Phần CBF làm ở giai đoạn sau, nhưng kiến trúc code **phải chừa sẵn chỗ** cho nó (xem mục 6).

---

## 1. Tài liệu nguồn (agent phải đọc)

| Mã | Bài | Vai trò | Đọc thế nào |
| --- | --- | --- | --- |
| **Paper A** | H.A.N. Duc, M.H. Phung, P.N. Dao, *Bearing-based cascade formation scaling control for multiple perturbed surface vehicles via off-policy reinforcement learning*, J. Franklin Institute 363 (2026) 109193. File: `papers/Bearing_based.pdf` | **Bài cần mô phỏng lại** | Toàn văn, nhất là mục 2, 3 và 4 (trang 3–22) |
| **Paper B** | L. Duo, H. Yin, P. Fu, A. Li, *Safety-critical control of multi-QUAVs under external disturbances and input saturation using RHTF-CBF*, J. Franklin Institute 363 (2026) 109129. File: `1656_JFI_26_Safety-critical_control_of_multi-QUAVs...pdf` | Nguồn công cụ CBF cho giai đoạn 2 | Mục 2.3 và 3.2 (trang 4–14). **Giai đoạn 1 chỉ cần đọc lướt** để thiết kế interface |
| Nền | Zhao & Zelazo, *Translational and scaling formation maneuver control via a bearing-based approach*, IEEE TCNS 2017 (arXiv 1506.05636) | Nguồn của (6)–(9) trong Paper A | Chỉ tra khi cần |
| Nền | Jiang & Jiang, Automatica 2012; Modares, Lewis & Jiang, IEEE TNNLS 2015 | Nguồn của IRL off-policy | Chỉ tra khi cần |
| Nền | Skjetne et al. 2004 (mô hình CyberShip II) | Đối chiếu tham số tàu ở trang 18 của Paper A | Chỉ tra khi nghi tham số in sai |

Nếu chưa có file PDF nào, **hỏi Đức**, không đoán nội dung.

### 1.1 Code tham khảo đã có (khảo sát 26/11/2026)

**Paper A không có code công khai.** Khảo sát chỉ tìm thấy code của bài tiền thân cùng nhóm tác giả:

- Repo: [HoangAnhMasterDev/Reinforcement-Learning-Based-Control-Framework-for-Leader-Following-Cascade-Formation-of-SVs](https://github.com/HoangAnhMasterDev/Reinforcement-Learning-Based-Control-Framework-for-Leader-Following-Cascade-Formation-of-SVs). MATLAB R2023a và Simulink; cập nhật lần cuối 17/01/2025; không có file license.
- Bài toán **khác** Paper A: 5 tàu, đội hình leader-following theo **độ dời tương đối** (không phải bearing), tầng cao có prescribed performance, tầng thấp là **actor-critic online** (trọng số cập nhật liên tục theo đạo hàm). **Không** có bearing, co giãn, H∞ hay off-policy. Bộ điều khiển trong repo **có dùng ma trận M**.
- Dùng được:
  1. **Mô hình tàu**: M, C, D giống hệt trang 18 của Paper A. Ví dụ d11 dùng u², d22 dùng |u|. Vậy các biểu thức "trông như in nhầm" ở Paper A **khớp code của nhóm**: cài đúng như in, không sửa theo CyberShip II.
  2. **Baseline M3 (AISMC) và M4 (FXESO)**: file `AISMC/AISMC.m` và `FXESO/FXESO.m`, có đủ tham số. Hai baseline này nhiều khả năng chính là [42] và [43] của Paper A. Cài lại bằng Python, đối chiếu với hai file này.
  3. Cách tổ chức vòng mô phỏng, hàm vẽ (`drawGraph.m`).
- Các script baseline đặt `T_end = 500` s. Nhiều khả năng đây là nguồn của chữ "500" trong chú thích Bảng 1 của Paper A (mục 3, ý 11).
- Code bài 1 của nhóm (Q-learning off-policy cho hệ tuyến tính, Julia): [Huy-Quang-Dao/OffQLCTS.jl](https://github.com/Huy-Quang-Dao/OffQLCTS.jl). Tham khảo cách dựng ma trận bình phương tối thiểu off-policy.

Phần thu dữ liệu và học off-policy H∞ của Paper A **không có code ở đâu cả**. Đây vẫn là chỗ phải xin tác giả hoặc tự thiết kế (mục 3, ý 5).

### 1.2 Việc agent phải làm với hai repo trên (thuộc Mốc 0)

**Repo tiền thân** (`git clone https://github.com/HoangAnhMasterDev/Reinforcement-Learning-Based-Control-Framework-for-Leader-Following-Cascade-Formation-of-SVs`):

| Đường dẫn | Nội dung | Agent cần rút ra |
| --- | --- | --- |
| `README.md` | mô tả phương pháp, hướng dẫn chạy | bối cảnh |
| `AISMC/AISMC.m` + `C.m`, `D.m`, `J.m`, `J_dot.m`, `J_dot_dot.m`, `l.m`, `sig.m` | baseline sliding mode tích phân thích nghi, chạy bằng script (Euler, bước 0.001 s) | công thức và tham số của M3; xác nhận khớp với tài liệu [42] của Paper A |
| `FXESO/FXESO.m` + các hàm phụ | baseline ESO thời gian cố định | công thức và tham số của M4; xác nhận khớp [43] |
| `Actor-Critic/Multiagent_1030_ActorCritic.slx` | mô hình Simulink: plant, bộ điều khiển động học, actor-critic online | xem mục dưới |
| `Actor-Critic/Paramaters.m`, `convertData2txt.m`, `multiple_xy_graph.m`, `drawGraph.m` | chạy mô phỏng, xuất dữ liệu, vẽ hình | cách log và vẽ |

**Đọc code trong file `.slx`** (không cần MATLAB): file `.slx` là file zip. Giải nén, rồi đọc thẻ `<P Name="script">` trong `simulink/stateflow/chart_*.xml`. Mỗi file ứng với một khối MATLAB Function, tên khối nằm trong thẻ `<P Name="name">`. Các khối chính: `Dynamics` (plant M, C, D), `Kinematics`, `Kinematics Controller` (prescribed performance), `RL controller/Controller` (actor-critic, có `gradPhi`), `eta_0/MATLAB Function` (quỹ đạo leader).

Sau khi khảo sát, viết `docs/reference_code_notes.md` gồm:

1. bảng đối chiếu từng phần của repo với từng phần của Paper A: giống, khác, hay không có;
2. tham số M, C, D trích nguyên văn từ code và kết luận về cách cài plant;
3. công thức và tham số của M3, M4, kèm ghi chú chỗ nào khác với Paper A;
4. **những gì trong repo KHÔNG được dùng cho Paper A**, và lý do. Ví dụ: actor-critic online ≠ IRL off-policy, đội hình độ dời ≠ đội hình bearing, bộ điều khiển dùng M ≠ không cần mô hình.

**Repo OffQLCTS.jl** (Julia): chỉ đọc phần dựng ma trận hồi quy và giải bình phương tối thiểu off-policy, để tham khảo cách cài (57)–(61). Không cần chạy.

**Không sao chép nguyên khối code MATLAB sang.** Cài lại bằng Python theo cấu trúc ở mục 5. Repo chỉ dùng để đối chiếu công thức, tham số và kết quả.

---

## 2. Paper A: tóm tắt kỹ thuật để code

Ký hiệu và số công thức theo Paper A.

### 2.1 Mô hình tàu (công thức (1)–(2), tham số trang 18)

Tàu mặt nước 3 bậc tự do, **fully actuated**:

```
η̇ = J(ψ) υ                     η = [x, y, ψ],  υ = [u, v, r] (vận tốc trong hệ thân tàu)
M υ̇ = −C(υ) υ − D(υ) υ + τ + δ(t)
J(ψ) = blkdiag(R(ψ), 1),  R(ψ) = [[cos ψ, −sin ψ], [sin ψ, cos ψ]]
```

- M = [[m11, 0, 0], [0, m22, m23], [0, m32, m33]], C có các phần tử c13, c23, c31, c32, D = [[d11, 0, 0], [0, d22, d23], [0, d32, d33]].
- Số liệu ở trang 18 (m11 = 25.8, m22 = 33.8, m23 = m32 = 1.0948, m33 = 2.76, các biểu thức c và d). Một vài biểu thức d trông như in nhầm biến (d11 có 5.8664·u², d22 dùng |u|), nhưng **khớp với code của nhóm** (mục 1.1). Cài đúng như trong `AISMC/D.m` của repo tham khảo.
- Nhiễu δ(t) (trang 18): hằng số (3, −2.5, 3) cộng các dao động sin/cos nhỏ cộng 0.1·rand. Dùng seed cố định.
- **Bộ điều khiển đề xuất coi M, C, D, δ là chưa biết.** Chỉ mô phỏng (plant) mới dùng chúng.

### 2.2 Đồ thị và bearing (mục 2.1, công thức (6)–(8))

- Đồ thị vô hướng. n_l leader đứng đầu, còn lại là follower.
- Bearing g_ij = (p_j − p_i)/‖p_j − p_i‖. Ma trận chiếu P_g = I − g·gᵀ.
- Bearing Laplacian B: khối (i, j) = −P_{g_ij} nếu là láng giềng, khối (i, i) = Σ_k P_{g_ik}.
- Đồ thị tăng cường Ḡ: thêm cạnh giữa mọi cặp leader. Điều kiện: B_ff khả nghịch. Vị trí follower đích: p_f* = −B_ff⁻¹ B_fl p_l (8).

### 2.3 Tầng cao (mục 3.1, công thức (9)–(14))

- **Leader** (9): ϑ_i = R_p(ψ_i)·(v_c + β(t)·(p_i − c(p))), với c = tâm các leader, s = kích thước đội hình.
- **Lịch co giãn** (63): β = 0.073 khi 0–15 s, β = 0 khi 15–25 s, β = −0.073 khi 25–40 s.
- **Tàu ảo của follower** (10)–(11): ṗ_d = R_p(ψ_d)·ϑ_d, ϑ̇_d = Ξ_p (hệ điều khiển gia tốc, bậc 2).
- **Gia tốc tàu ảo** (12)–(13):
  ```
  Π_i = −Σ_{j∈N_i} P_{g*_ij} · ( k_p (p_i − p_j) + k_v (ṗ_i − ṗ_j) )      ← dùng vị trí TÀU THẬT
  Ξ_pi = R_p⁻¹(ψ_di) · ( Π_i − Ṙ_p(ψ_di) ϑ_di )
  ```
  **Chú ý:** (13) dùng vị trí, vận tốc của **tàu thật** (p_i, p_j), không phải tàu ảo. Đây là chỗ hai tầng dính nhau.
- **Đồng thuận góc hướng** (14): ω_di = −k_ω·[Σ a_ij (ψ_i − ψ_j) + b_i (ψ_i − ψ₀)].

### 2.4 Tầng thấp (mục 3.2, công thức (15)–(61))

1. **Sai số và backstepping** (15)–(19): z_η = η − η_d; vận tốc ảo α = Jᵀ(η)·(−β_η z_η + J(η_d) υ_d); z_υ = υ − α; ghép z = [z_η; z_υ] ∈ ℝ⁶.
2. **Trạng thái mở rộng** (20)–(21): Ω = [η_d; υ_d; υ̇_d] ∈ ℝ⁹, X = [z; Ω] ∈ ℝ¹⁵; Ẋ = F(X) + G(X)u + K(X)d, với u = τ, d = δ.
3. **Chi phí** (22)–(24): r = XᵀQ'X + uᵀRu − γ²dᵀd, có chiết khấu e^(−α(t−T₁)). Q' = blkdiag(Q, 0₉ₓ₉): chỉ phạt phần z.
4. **Lời giải tối ưu** (26)–(30): u* = −½R⁻¹Gᵀ∇V*, d* = (1/2γ²)Kᵀ∇V*, phương trình HJI (30).
5. **Phương trình Bellman IRL off-policy** (43)–(45), viết trên các khoảng [t, t+T].
6. **Xấp xỉ** (51)–(56): V ≈ W_cᵀσ(X), u ≈ W_aᵀφ(X), d ≈ W_dᵀψ(X).
7. **Bình phương tối thiểu** (57)–(61): gom các khoảng thành ρ₁·Ŵ = ρ₂, giải Ŵ = (ρ₁ᵀρ₁)⁻¹ρ₁ᵀρ₂.
8. **Thuật toán 2** (trang 11): pha 1 thu dữ liệu **một lần** bằng cách lái ổn định + nhiễu thăm dò; pha 2 lặp bình phương tối thiểu trên dữ liệu đã thu đến khi Ŵ hội tụ.

### 2.5 Thiết lập mô phỏng (mục 4)

| Tham số | Giá trị (Paper A) |
| --- | --- |
| Thời gian mô phỏng | 40 s |
| k_p, k_v (tầng cao) | 30, 0.1 |
| Khoảng tích phân IRL T | 0.001 s |
| α (chiết khấu), γ | 0.1, 5 |
| R_i, Q_i | I₃, "100·I₃" (**xem mục 3, mâu thuẫn kích thước**) |
| Hàm cơ sở critic σ | 45 tích bậc hai X(k)·X(l), 1 ≤ k ≤ l ≤ 9 |
| Hàm cơ sở actor φ, disturber ψ | X(1), ..., X(9) (tuyến tính) |
| Trọng số ban đầu | W_a, W_c, W_d = 0 |
| v_c | (4, 4) m/s |
| ψ₀ | π/4 |

**Case 1 (4 tàu):** leader 1, 2; follower 3, 4. Bearing đích: g*₃₁ = [1, 0], g*₃₂ = [√2/2, −√2/2], g*₄₂ = [1, 0], g*₄₃ = [0, 1]. Trạng thái đầu: η₁ = [10, 0, π/4], η₂ = [10, −9, π/4], η₃ = [−11, 1, π/2], η₄ = [−9, −10, 0], mọi υ = 0. Đồ thị ở Hình 2.

**Case 2 (6 tàu):** thêm follower 5, 6. Bearing thêm: g*₅₃ = [1, 0], g*₅₆ = [0, −1], g*₆₃ = [√2/2, √2/2], g*₆₄ = [1, 0]. η₅ = [−20, −1, π/2], η₆ = [−20, −10, π/2]. Đồ thị ở Hình 13.

**Baseline (trang 18):**

- **M1** (dựa trên mô hình, công thức (62), ζ = 0.5, 0.7, 0.5): dùng đúng M, C, D.
- M2 (Lu et al., TNNLS 2021, tài liệu [3] của Paper A), M3 (sliding mode tích phân thích nghi, [42]), M4 (ESO thời gian cố định, [43]): **cần đọc bài gốc** của từng phương pháp.

**Chỉ số (Bảng 1):** IAE = ∫‖e‖dt, ITAE = ∫t·‖e‖dt, RMSE, với e là sai số bearing ‖g − g*‖ của cả đội; tổng lực Σ∫|τ|dt (Hình 7).

**Kết quả cần tái tạo (để so, không bắt buộc khớp từng số):**

| | M1 | M2 | M3 | M4 | Đề xuất |
| --- | --- | --- | --- | --- | --- |
| RMSE Case 1 | 0.1136 | 0.1737 | 0.2050 | 0.1464 | **0.0178** |
| RMSE Case 2 | 0.2903 | 0.3903 | 0.5110 | 0.3624 | **0.0678** |

Các hình cần tái tạo: 3 và 14 (quỹ đạo), 4 và 15 (ảnh chụp đội hình), 5 (sai số bearing), 6 và 16 (góc hướng), 7 (tổng lực), 8 và 17 (sai số vận tốc), 10, 11 và 18 (hội tụ trọng số, sai số Bellman), 12 (kích thước đội hình).

---

## 3. Chỗ Paper A mơ hồ hoặc mâu thuẫn: KHÔNG được đoán lặng lẽ

Mỗi mục dưới đây: agent chọn một cách hợp lý, **ghi vào `docs/assumptions.md`** (lý do, ảnh hưởng), và **báo Đức trong bản kế hoạch**.

1. **Q_i = 100·I₃** nhưng theo (23) Q_i phải 6×6. Có thể là 100·I₆.
2. **γ hay γ²**: (22) viết γ_i·dᵀd, còn (25)–(30) viết γ². Dùng γ² cho nhất quán với lý thuyết H∞.
3. **Hệ số β_η** của vận tốc ảo (16) không cho giá trị.
4. **k_ω và b_i** của (14) không cho (tàu nào biết ψ₀?).
5. **Pha thu dữ liệu không được mô tả**: cách lái nào, nhiễu thăm dò gì, thu bao lâu, bao nhiêu khoảng M, T₁ là bao nhiêu, thu trong lúc chạy 40 s hay ở một lần chạy riêng. Đây là chỗ quan trọng nhất cần chốt với Đức.
6. **Ngưỡng dừng ε và số vòng lặp tối đa** không cho (các hình cho thấy 10 đến 20 vòng).
7. **Điều kiện dừng trong Thuật toán 1, 2 bị in ngược** ("while ‖V^k − V^(k−1)‖ < ε"). Đúng ra là dừng khi nhỏ hơn ε.
8. **Trọng số ban đầu bằng 0** tức u = 0. Cần kiểm tra đó có phải chính sách "ổn định và thăm dò" (Định nghĩa 1) với mô hình tàu này không.
9. **Phương trình (45) cần nhiễu thật d** trong dữ liệu. Mô phỏng thì biết d; ghi rõ đây là giả thiết không thực tế.
10. **Thứ tự các thành phần của X** và vì sao mạng chỉ dùng **X(1..9)** trong 15 thành phần: cần suy ra từ (20)–(21) và ghi lại.
11. **Chú thích Bảng 1 ghi tích phân đến 500 s** trong khi mô phỏng 40 s. Dùng 40 s.
12. **Giả thiết 1 (leader vận tốc không đổi) bị vi phạm** khi β ≠ 0 (30 trên 40 s). Vẫn mô phỏng đúng như bài, nhưng ghi lại.
13. **Leader là tàu có động lực học hay chỉ là điểm động học?** Trang 19 nói "chỉ điều khiển hai follower". Cần chốt.
14. **M1 (62)**: ký hiệu υ_e và Ξ_ε không được định nghĩa rõ.
15. **Ký hiệu trùng**: β (tốc độ co giãn) và β_η (hệ số backstepping); α (chiết khấu) và α_i (vận tốc ảo); J_p và R_p là cùng một ma trận quay.

---

## 4. Ý đồ bài báo của ta (đề xuất P1)

### 4.1 Khoảng trống của Paper A ta lấp

- Không có **tránh va chạm** giữa các tàu, dù co giãn làm tàu đến gần nhau.
- Không có **luồng hẹp, bờ, vật cản**, dù đó là động lực của bài.
- Kích thước đội hình theo **lịch cố định** (63), không phản ứng theo môi trường.
- Pha thu dữ liệu nhiều tàu **không có đảm bảo an toàn**.

### 4.2 Kiến trúc dự kiến (3 tầng)

```
[Tầng sinh tham số, MỚI]  tỉ lệ co giãn s(t) / β(t) do leader chọn
        │                  (theo bề rộng luồng, thoát deadlock)
        ▼
[Tầng cao, Paper A]       luật bearing (13) → Ξ_nom cho tàu ảo
        │
        ▼
[Bộ lọc an toàn, MỚI]     CBF-QP trên tàu ảo: Ξ = argmin ‖Ξ − Ξ_nom‖²
        │                  s.t. HOCBF giữa các tàu, với bờ, với vật cản
        ▼
[Tầng thấp, Paper A]      H∞ IRL off-policy, tàu thật bám tàu ảo
```

**Ý chính về toán:** CBF đặt lên **tàu ảo** (mô hình (10)–(11) biết chính xác, bậc tương đối 2, không nhiễu), nên dùng được HOCBF bậc 2 của Paper B mà **không cần bộ quan sát nhiễu**. Sự bất định của tàu thật được tầng thấp gói vào một **bán kính sai số bám ε** (vùng UUB, Định lý 1 của Paper A). Giữ tàu ảo cách nhau ít nhất d_min + 2ε thì tàu thật cách nhau ít nhất d_min (bất đẳng thức tam giác).

### 4.3 Hai mức đóng góp

- **Mức 1 (làm trước):** bộ lọc CBF trên tàu ảo, biên an toàn theo ε, co giãn theo bề rộng luồng, thoát deadlock bằng co đội hình.
- **Mức 2 (nếu kịp):** an toàn trong **pha thu dữ liệu** cho nhiều tàu: lọc tín hiệu thăm dò qua CBF-QP (ý tưởng của Kanso et al., IJRNC 2024), kiểm tra dữ liệu sau lọc vẫn đủ hạng.

### 4.4 Công cụ lấy từ Paper B (giai đoạn 2)

| Thành phần | Công thức Paper B | Dùng trong dự án |
| --- | --- | --- |
| HOCBF bậc 2 cho khoảng cách hai agent, có thành phần thay đổi theo thời gian | (31)–(35) | Ràng buộc giữa các tàu ảo |
| Bộ lọc QP | (41), (54) | Lọc Ξ_nom của tầng cao |
| CBF giữ vùng khả thi bằng quả cầu Chebyshev (LP) | (44)–(49) | Tham khảo; ưu tiên dùng co giãn thay slack |
| Phát hiện deadlock theo sự kiện | (57)–(58) | Kích hoạt co đội hình thay vì xoay đích |

Điểm yếu của Paper B cần tránh lặp lại: slack làm mất đảm bảo khả thi; công thức thể tích viết r thay vì r³; ma trận xoay (59) sai; kiểm tra deadlock bằng Q = 0 tuyệt đối.

### 4.5 Kế hoạch mô phỏng của bài mới (để biết code cần hỗ trợ gì)

- Kịch bản: 4 và 6 tàu đi qua **luồng hẹp dần**, có vật cản tĩnh và động.
- Chỉ số: khoảng cách nhỏ nhất giữa các tàu, với bờ, với vật cản; RMSE bearing; thời gian qua luồng; số lần QP vô nghiệm; số va chạm trong pha thu dữ liệu.
- Baseline: Paper A gốc; Paper A + trường thế nhân tạo (APF); Paper A + CBF đặt trong hàm chi phí.

---

## 5. Yêu cầu về code (để Đức đọc và review được)

### 5.1 Ngôn ngữ và thư viện

- **Python 3** (numpy, scipy; matplotlib cho hình; cvxpy hoặc OSQP cho QP ở giai đoạn 2). Paper A dùng MATLAB, nhưng ta chọn Python để dễ đọc, dễ test, miễn phí. Nếu Đức đổi ý sang MATLAB thì giữ nguyên cấu trúc module.
- Không dùng framework nặng. Không dùng deep learning library: "mạng nơ-ron" ở đây chỉ là tổ hợp tuyến tính của hàm cơ sở cố định.

### 5.2 Nguyên tắc cấu trúc

1. **Mỗi file ứng với một khối của paper**, đặt tên theo khối (xem gợi ý 5.3). Đọc tên file là biết nó ứng với mục nào của bài.
2. **Mỗi hàm có docstring ghi số công thức** của Paper A (ví dụ `"""Eq. (13): bearing-based reference acceleration."""`). Tên biến bám ký hiệu của bài khi có thể (`z_eta`, `z_upsilon`, `Xi_p`, `W_c`), và có bảng đối chiếu ký hiệu trong `docs/notation.md`.
3. **Tách tham số ra file cấu hình** (`config/case1.yaml`, `case2.yaml`), không hard-code trong thuật toán.
4. **Tách plant và controller**: controller không được import tham số M, C, D (trừ baseline M1, phải ghi rõ).
5. **Hàm thuần, ít trạng thái ẩn**: mỗi bước mô phỏng nhận trạng thái và trả trạng thái mới; log đầy đủ để vẽ hình.
6. **Chừa chỗ cho giai đoạn 2** (mục 6) nhưng **không viết trước** logic CBF.
7. Seed cố định; mỗi lần chạy lưu config, log và hình vào một thư mục `results/<tên-lần-chạy>/`.
8. Code ngắn, dễ đọc ưu tiên hơn tối ưu tốc độ. Không viết những trừu tượng hóa chưa dùng đến.

### 5.3 Gợi ý cấu trúc (agent được điều chỉnh, nhưng phải giải thích trong kế hoạch)

```
formation_cbf/
├── README.md                    cách chạy, sơ đồ module
├── docs/
│   ├── notation.md              bảng ký hiệu paper ↔ tên biến
│   ├── assumptions.md           mọi lựa chọn cho các chỗ mơ hồ ở mục 3
│   └── replication_report.md    so kết quả với Paper A
├── config/                      case1.yaml, case2.yaml
├── src/
│   ├── models/vessel.py         (1)–(2), tham số trang 18, nhiễu δ(t)
│   ├── graph/bearing.py         P_g, B, (6)–(8), kiểm tra B_ff khả nghịch
│   ├── high_level/leaders.py    (9), (63)
│   ├── high_level/followers.py  (10)–(14)
│   ├── low_level/backstepping.py      (15)–(19)
│   ├── low_level/augmented_state.py   (20)–(21)
│   ├── low_level/basis.py             σ, φ, ψ
│   ├── low_level/offpolicy_irl.py     (43)–(45), (57)–(61), Thuật toán 2
│   ├── baselines/m1_model_based.py    (62); M2–M4 làm sau
│   ├── safety/                         giai đoạn 2 (hiện chỉ có bộ lọc identity)
│   ├── sim/runner.py                   vòng lặp mô phỏng, tích phân số
│   ├── metrics.py                      IAE, ITAE, RMSE, tổng lực, khoảng cách nhỏ nhất
│   └── plots.py                        vẽ lại các hình của Paper A
├── scripts/                     run_case1.py, run_case2.py, train_irl.py
└── tests/                       kiểm thử từng khối (mục 5.4)
```

### 5.4 Kiểm thử bắt buộc trước khi chạy toàn bộ

1. **Hình học bearing:** P_g·g = 0; với Case 1 và Case 2, B_ff khả nghịch; p_f* từ (8) cho đúng hình vuông và hình chữ nhật.
2. **Tầng cao riêng:** cho tàu thật bám **hoàn hảo** tàu ảo (bỏ qua tầng thấp), đội hình phải hội tụ về bearing đích, kích thước theo đúng lịch (63).
3. **Plant:** tàu không điều khiển, không nhiễu thì vận tốc tắt dần (có lực cản); kiểm tra ma trận M đối xứng xác định dương.
4. **IRL trên bài toán đồ chơi:** cài Thuật toán 2 cho một **hệ tuyến tính nhỏ biết trước lời giải** (ví dụ ẋ = ax + bu, hoặc hệ 2 chiều có nhiễu), so trọng số học được với nghiệm Riccati/HJI tính bằng scipy. **Phải khớp đến vài chữ số trước khi áp lên tàu.**
5. **Bình phương tối thiểu:** in hạng và số điều kiện của ρ₁; dừng với cảnh báo nếu thiếu hạng (thiếu nhiễu thăm dò).

### 5.5 Log ngay từ giai đoạn 1 (phục vụ bài mới)

Ngoài các chỉ số của Paper A, log thêm **khoảng cách nhỏ nhất giữa mọi cặp tàu theo thời gian**. Số liệu này cho biết Paper A gốc có tàu nào đến quá gần nhau không, và là động lực trực tiếp cho phần CBF.

---

## 6. Interface cần chừa sẵn cho giai đoạn 2 (CBF)

1. Tầng cao tách thành hai bước: `compute_nominal_accel(...) -> Xi_nom` và `integrate_virtual_vessel(Xi, ...)`. **Giữa hai bước có một bộ lọc an toàn** với interface kiểu:
   ```python
   class SafetyFilter(Protocol):
       def filter(self, Xi_nom, virtual_states, env, t) -> tuple[Xi, info]: ...
   ```
   Giai đoạn 1 dùng `IdentityFilter` (trả nguyên Xi_nom).
2. `β(t)` của leader lấy từ một **đối tượng lịch co giãn** (giai đoạn 1: lịch cố định (63); giai đoạn 2: tầng sinh tham số chọn theo môi trường).
3. Một cấu trúc `Environment` (bờ luồng, vật cản) có thể rỗng ở giai đoạn 1 nhưng đã được truyền qua runner.
4. Pha thu dữ liệu IRL nhận tín hiệu thăm dò qua một hàm có thể thay thế (để giai đoạn 2 lọc qua CBF).

---

## 7. Cách làm việc với Đức

1. **Bước đầu tiên: không viết code.** Đọc Paper A (và lướt Paper B mục 3.2), khảo sát hai repo theo mục 1.2 và viết `docs/reference_code_notes.md`, rồi nộp **bản kế hoạch** gồm:
   - cấu trúc thư mục, file chính và vai trò của từng file;
   - lựa chọn cho **từng mục** trong mục 3 (mơ hồ/mâu thuẫn), cần Đức chốt mục nào;
   - thứ tự các mốc, mỗi mốc có tiêu chí kiểm tra (mục 5.4);
   - rủi ro (chỗ nào có thể không tái tạo được kết quả).
2. Chờ Đức duyệt. Sau đó làm **từng mốc**, mỗi mốc dừng lại báo kết quả kiểm thử và hình.
3. Khi kết quả lệch Paper A: **báo và giải thích**, không chỉnh tham số tùy tiện cho khớp số. Ghi vào `docs/replication_report.md`.
4. Nhận xét trong code và tài liệu: **ngắn, rõ, ghi số công thức**. Đức sẽ đọc từng file.
5. Không tự mở rộng phạm vi (không thêm CBF, không thêm baseline M2–M4) khi chưa được yêu cầu.
