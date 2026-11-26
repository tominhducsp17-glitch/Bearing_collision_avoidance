# PLAN: tái tạo Paper A (giai đoạn 1)

Người viết: coding agent. Người duyệt: Đức. Ngày: 26/11/2026.
Tài liệu đi kèm: [docs/reference_code_notes.md](docs/reference_code_notes.md) (khảo sát hai repo tham khảo).

**Cách đọc.** Mục (b) có các nhãn sau:
- **[CẦN CHỐT]**: Đức phải quyết.
- **[XÁC NHẬN]**: agent đã có đề xuất kèm bằng chứng, Đức chỉ cần đồng ý hoặc bác.
- **[ĐÃ RÕ]**: suy ra được bằng toán hoặc từ code, chỉ ghi lại.

Sau khi Đức chốt, nội dung mục (b) sẽ được chép sang `docs/assumptions.md`. Mục 5 cuối file gom toàn bộ câu hỏi theo thứ tự ưu tiên.

Ký hiệu (mục 3, ý 15 của PROJECT_CONTEXT): `beta_s` là tốc độ co giãn β(t); `beta_eta` là hệ số backstepping β_η; `alpha_disc` là chiết khấu α; `alpha_v` là vận tốc ảo α_i; R_p ≡ J_p.

---

## (a) Cấu trúc thư mục

Gốc dự án là `Paper_1/` (không lồng thêm thư mục `formation_cbf/` như gợi ý ở §5.3, cho đường dẫn ngắn hơn). Mọi thứ khác bám §5.3. Các điều chỉnh có lý do ghi ở cuối mục này.

```
Paper_1/
├── PROJECT_CONTEXT.md, PLAN.md, README.md
├── requirements.txt              numpy, scipy, matplotlib, pyyaml, pytest
├── Main_paper/, Side_paper/      PDF (không sửa)
├── external/                     repo tham khảo, chỉ đọc, không thuộc code dự án
├── docs/
│   ├── reference_code_notes.md   (đã viết ở Mốc 0)
│   ├── notation.md               bảng ký hiệu paper ↔ tên biến
│   ├── assumptions.md            các lựa chọn ở mục (b), sau khi Đức chốt
│   └── replication_report.md     Mốc 6
├── config/
│   ├── case1.yaml, case2.yaml    mọi tham số Mục 4 của Paper A + các lựa chọn ở (b)
│   └── toy_irl.yaml              Mốc 4
├── src/
│   ├── models/vessel.py
│   ├── graph/bearing.py
│   ├── high_level/scaling.py
│   ├── high_level/leaders.py
│   ├── high_level/followers.py
│   ├── safety/base.py
│   ├── low_level/backstepping.py
│   ├── low_level/augmented_state.py
│   ├── low_level/basis.py
│   ├── low_level/offpolicy_irl.py
│   ├── low_level/data_collection.py
│   ├── low_level/irl_controller.py
│   ├── baselines/m1_model_based.py
│   ├── sim/integrators.py
│   ├── sim/runner.py
│   ├── metrics.py
│   └── plots.py
├── scripts/  run_highlevel_only.py, run_case.py, toy_irl.py, train_irl.py, make_figures.py
├── tests/    mỗi file src có một file test_*.py tương ứng, cộng thêm test_separation.py
└── results/<tên-lần-chạy>/   config.yaml đã dùng + log .npz + hình + metrics.json
```

### Vai trò từng file và công thức Paper A cài đặt

| File | Vai trò | Công thức |
| --- | --- | --- |
| `models/vessel.py` | Plant: M, C(υ), D(υ) theo `AISMC/C.m`, `D.m`; J(ψ); vế phải của ODE; nhiễu δ(t) có seed. **Chỉ có hai file được import file này:** runner và baseline M1. | (1), (2), tham số tr. 18 |
| `graph/bearing.py` | g_ij, P_g, bearing Laplacian B, tách B_ll…B_ff, kiểm tra B_ff khả nghịch, vị trí đích p_f* | (6), (7), (8) |
| `high_level/scaling.py` | Đối tượng lịch co giãn `ScalingSchedule.beta_s(t)`. Giai đoạn 1 là lịch cố định (63); giai đoạn 2 thay bằng tầng sinh tham số (§6.2). | (63) |
| `high_level/leaders.py` | Vận tốc leader; tâm c(p), kích thước s(p) | (9) |
| `high_level/followers.py` | `compute_nominal_accel` → Π_nom; đổi Π ↔ Ξ_p; `integrate_virtual_vessel`; đồng thuận góc ω_d và đạo hàm ω̇_d | (10)–(14) |
| `safety/base.py` | `SafetyFilter` (Protocol), `IdentityFilter`, `Environment` (rỗng ở giai đoạn 1) | §6.1, §6.3 |
| `low_level/backstepping.py` | z_η, vận tốc ảo alpha_v, z_υ, z | (15)–(17), (19) |
| `low_level/augmented_state.py` | Dựng Ω_i (9 chiều) và X_i (15 chiều) theo thứ tự cấu hình được (xem B-10) | (20), (21) |
| `low_level/basis.py` | σ: 45 tích bậc hai X(k)X(l), k ≤ l ≤ 9; φ, ψ: tuyến tính X(1..9). Viết dạng tổng quát theo n để dùng lại cho bài đồ chơi. | (51)–(56), tr. 18–19 |
| `low_level/offpolicy_irl.py` | **Không biết gì về tàu.** Nhận dữ liệu theo khoảng (X, u, d tại các mẫu) rồi dựng hàng hồi quy, giải bình phương tối thiểu, lặp chính sách; trả lịch sử W, ‖δ_B‖, hạng, số điều kiện. | (45), (57)–(61), Thuật toán 2 pha 2 |
| `low_level/data_collection.py` | Pha 1 của Thuật toán 2: chạy hệ với chính sách hành vi cộng tín hiệu thăm dò (`ProbingSignal`, hàm thay thế được, §6.4); ghi dữ liệu với bước con mịn | Thuật toán 2 pha 1 |
| `low_level/irl_controller.py` | Triển khai u = Ŵ_aᵀφ(X) | (55) |
| `baselines/m1_model_based.py` | Baseline M1. **Có dùng M, C, D**, ghi rõ ở đầu file. | (62) |
| `sim/integrators.py` | RK4 bước cố định | |
| `sim/runner.py` | Vòng mô phỏng. Ba chế độ tầng thấp: `perfect_tracking` (Mốc 2), `m1`, `irl`. Truyền `Environment` và `SafetyFilter` qua mọi bước. Log đầy đủ. | sơ đồ Hình 1 |
| `metrics.py` | Sai số bearing, IAE, ITAE, RMSE, tổng lực, kích thước đội hình (cả hai định nghĩa, B-2), **khoảng cách nhỏ nhất giữa mọi cặp tàu** (§5.5) | Bảng 1, Hình 7, Hình 12 |
| `plots.py` | Vẽ lại các Hình 3–20 | |

### Thứ tự tính trong một bước dt của runner

1. Leader: tính vận tốc theo (9), với β(t) lấy từ `ScalingSchedule`.
2. Follower, tầng cao: Π_nom theo (13), dùng p, ṗ của **tàu thật**. Lọc an toàn: `Π = filter(Π_nom, …)` (giai đoạn 1 là identity). Đổi sang Ξ_p = R_pᵀ(ψ_d)(Π − Ṙ_p(ψ_d)ϑ_d) theo (12). Tính ω_d theo (14).
3. Follower, tầng thấp: z theo (15)–(16), X theo (20). Tính τ bằng IRL, M1, hoặc bỏ qua ở chế độ `perfect_tracking`.
4. Tích phân RK4 toàn bộ trạng thái (tàu thật, tàu ảo, leader). Các tín hiệu phía bộ điều khiển (Π, ω_d, τ) và mẫu `rand` của δ được giữ nguyên trong suốt bước (ZOH).

### Điều chỉnh so với gợi ý §5.3, kèm lý do

- Tách `scaling.py` khỏi `leaders.py`: đúng yêu cầu §6.2, là đối tượng thay thế được ở giai đoạn 2.
- Tách `data_collection.py` khỏi `offpolicy_irl.py`. Phần giải bình phương tối thiểu phải dùng lại nguyên vẹn cho bài đồ chơi (Mốc 4) và cho tàu (Mốc 5). Tín hiệu thăm dò cần là một điểm cắm riêng để giai đoạn 2 lọc qua CBF (§6.4).
- Thêm `irl_controller.py`, để lúc triển khai không phải import cả bộ học.
- Thêm `tests/test_separation.py`: kiểm tra tự động rằng ngoài `models/`, `sim/runner.py` và `baselines/` thì không file nào import tham số tàu (§5.2.4).
- Bộ lọc an toàn tác động lên **Π** (gia tốc tàu ảo trong hệ trái đất, p̈_d = Π) thay vì Ξ. Hai đại lượng tương đương một-một qua (12). Với Π, tàu ảo là khâu tích phân kép, nên HOCBF khoảng cách ở giai đoạn 2 viết gọn hơn (xem B-11).

---

## (b) Các chỗ mơ hồ, mâu thuẫn: đề xuất xử lý

### b.1 Mười lăm mục trong §3 của PROJECT_CONTEXT

| # | Vấn đề | Đề xuất | Lý do, bằng chứng | Nhãn |
| --- | --- | --- | --- | --- |
| 1 | Q_i = 100·I₃ nhưng (23) cần 6×6 | **Q_i = 100·I₆**, Q' = blkdiag(Q_i, 0₉ₓ₉) | Bài tiền thân dùng đúng `Q = 100*blkdiag(I6, 0)` (reference_code_notes §1) | XÁC NHẬN |
| 2 | γ hay γ² trong (22) | Dùng **γ²** trong r | (25)–(30) đều dùng γ²; định nghĩa L₂-gain chuẩn | ĐÃ RÕ |
| 3 | β_η không cho | Mặc định **β_η = 2·I₃**, đặt trong config, quét {1, 2, 5, 10} | Hình 6 cho thấy ψ hội tụ trong khoảng 1 s, nên tốc độ cỡ vài 1/s. Hai bằng chứng xung đột: quá độ z_υ ở Hình 8/17 rất lớn (tới 100–400 m/s) gợi ý β_η lớn hoặc η_d(0) ≠ η(0) (xem B-7) | **CẦN CHỐT** |
| 4 | k_ω, b_i của (14); ψ trong (14) là của tàu thật hay tàu ảo | b_i = 1 cho mọi follower (đều biết ψ₀); a_ij theo đồ thị, kể cả cạnh tới leader; ψ của leader giữ cố định bằng ψ₀; **k_ω = 2**; ψ_i, ψ_j trong (14) là **của tàu thật**, viết đúng như in, giống cách (13) dùng p thật. ω̇_d tính giải tích bằng cách thay ψ̇ = r đo được. | Bài không cho số. Hình 6 cho thấy hội tụ trong khoảng 1 s | **CẦN CHỐT** |
| 5 | Pha thu dữ liệu | Mặc định đề xuất xem bảng b.3 | Bài không mô tả. Đây là chỗ quyết định kết quả | **CẦN CHỐT** |
| 6 | ε và số vòng lặp tối đa | Dừng khi ‖Ŵ^{k+1} − Ŵ^k‖ ≤ 1e-6·max(1, ‖Ŵ^k‖); tối đa 50 vòng. Lưu ‖Ŵ^k‖ và ‖δ_B‖ mỗi vòng để vẽ Hình 10, 11, 18, 19 | Các hình cho thấy 10–20 vòng | XÁC NHẬN |
| 7 | Điều kiện dừng in ngược | Lặp **đến khi** sai khác < ε | Lỗi in hiển nhiên | ĐÃ RÕ |
| 8 | W = 0 tức u⁽⁰⁾ = 0 có "ổn định" không | Giữ W⁽⁰⁾ = 0 như bài. Ở Mốc 5 chạy thử u = 0 để xem z có bị chặn không (theo nghĩa có chiết khấu, α = 0.1). Nếu phép lặp phân kỳ, báo Đức và đề xuất khởi tạo W_a⁽⁰⁾ từ chính sách hành vi, ghi rõ là lệch bài. | Pha 2 chỉ dùng u⁽⁰⁾ trong công thức lặp, không dùng để chạy hệ. Lý thuyết lặp chính sách vẫn cần u⁽⁰⁾ chấp nhận được | XÁC NHẬN |
| 9 | (45) cần nhiễu thật d | Dùng δ(t) thật mà plant ghi lại (chỉ làm được trong mô phỏng). Ghi rõ đây là giả thiết không thực tế. | Bắt buộc theo (45) | ĐÃ RÕ |
| 10 | Thứ tự X và vì sao chỉ dùng X(1..9) | Xem B-10 | | **CẦN CHỐT** |
| 11 | "∫₀⁵⁰⁰" ở Bảng 1 | Tích phân trên [0, 40] s. Chữ 500 nhiều khả năng là `T_end = 500` trong code của nhóm. Định nghĩa chỉ số: xem B-8 | reference_code_notes §1 | XÁC NHẬN |
| 12 | Giả thiết 1 bị vi phạm khi β ≠ 0 | Mô phỏng đúng như bài, ghi vào báo cáo | | ĐÃ RÕ |
| 13 | Leader là tàu có động lực học hay điểm động học | **Điểm động học**: η_l tích phân đúng (9) với ψ_l = ψ₀ cố định, không có plant, không có nhiễu, τ = 0 khi tính tổng lực | Trang 19: "we only control two followers"; các Hình 6, 16 chỉ có follower | **CẦN CHỐT** |
| 14 | M1 (62): υ_e, Ξ_ε là gì | Xem B-14 | | **CẦN CHỐT** |
| 15 | Ký hiệu trùng | Đổi tên như dòng "Ký hiệu" ở đầu file; lập bảng trong `docs/notation.md` | | ĐÃ RÕ |

### b.2 Các chỗ mơ hồ mới phát hiện khi đọc bài và code

| # | Vấn đề | Đề xuất | Lý do, bằng chứng | Nhãn |
| --- | --- | --- | --- | --- |
| B-1 | (9) viết ϑ_i = R_p(ψ_i)(…), trong khi ϑ là vận tốc trong hệ thân tàu | Dùng **ϑ_i = R_pᵀ(ψ_i)(v_c + β(p_i − c))**, tức ṗ_i = v_c + β(p_i − c), đúng luật Zhao–Zelazo [33] | Nếu dùng đúng chữ in, với ψ = π/4 leader sẽ đi theo hướng (−4, 4). Hình 3 cho thấy leader đi theo (4, 4), đến khoảng (170, 160) lúc 40 s | XÁC NHẬN |
| B-2 | Định nghĩa c(p), s(p): bản in lấy tổng trên V_l nhưng chia cho n | Hai phương án: **(A)** đúng chữ: c là tâm các leader dùng trong (9); **(B)** c là tâm của **mọi tàu**. Dù chọn gì, luôn vẽ s theo cả hai định nghĩa | Giá trị ở Hình 12 khớp s = sqrt(Σ_{mọi i}‖p_i − c_all‖²): Case 1 tính ra 22.4 lúc đầu và 12.7 ở đích, hình là ≈22 và ≈13. Mức lực ở Hình 9 cũng khớp (B) hơn: SV3 có τ_x ≈ 1100 N gần như không đổi suốt 40 s; SV4 ≈ 860 → 2100 → 1400 N, trong khi (A) dự đoán SV4 lên khoảng 2800 N lúc 25 s. Nhưng (B) nghĩa là leader phải biết vị trí follower, trái với tinh thần "chỉ leader biết thông tin toàn cục" | **CẦN CHỐT** |
| B-3 | k_p = 30, k_v = 0.1 cho tầng cao **gần như không có cản** | Mốc 2 kiểm tra đúng tham số bài. **Không tự chỉnh.** Nếu Đức muốn, chạy thêm một biến thể có nhãn rõ ràng | Khi tàu thật bám hoàn hảo, mỗi mode thỏa s² + k_vλs + k_pλ = 0, với λ ∈ eig(B_ff). Case 1: λ ∈ {0.145, 1, 1.40, 2.45}, ζ ≈ 0.0035–0.014, mode chậm nhất cần khoảng 138 s mới tắt. Case 2: mode chậm nhất cần khoảng 508 s. Hình 5 lại cho thấy hội tụ dưới 1 s. Có thể vòng tầng thấp làm thay đổi điều này (kiểm ở Mốc 3), hoặc tham số bị in nhầm | **CẦN CHỐT** (hỏi tác giả) |
| B-4 | Θ_i dưới (18) viết M⁻¹(Cυ − Dυ + g_i(η)), lệch dấu so với (1) và thừa g_i | Plant theo (1). Θ_i chỉ dùng trong lý thuyết | | ĐÃ RÕ |
| B-5 | Dấu của ρ₂ trong (58)–(59) sai; công thức η_i2…η_i5 chứa luôn vec(Ŵ) bên trong | Dựng trực tiếp từ (45). Hàng j: **[ (e^{−αT}σ(X(t_j)) − σ(X(t_{j−1})))ᵀ, 2∫e^{−α(τ−t_{j−1})}((u − û⁽ᵏ⁾)ᵀR ⊗ φᵀ)dτ, −2γ²∫e^{−α(τ−t_{j−1})}((d − d̂⁽ᵏ⁾)ᵀ ⊗ ψᵀ)dτ ]·Ŵ = −∫e^{−α(τ−t_{j−1})}(XᵀQ'X + û⁽ᵏ⁾ᵀRû⁽ᵏ⁾ − γ²d̂⁽ᵏ⁾ᵀd̂⁽ᵏ⁾)dτ**, với vec theo cột | Theo (45), V giảm dọc quỹ đạo nên vế trái âm và bằng −∫r. Thứ tự Kronecker sẽ được bài đồ chơi ở Mốc 4 kiểm tra | ĐÃ RÕ |
| B-6 | **W_d có thể không xác định được** | Ở Mốc 5 đo hạng của ρ₁ với dữ liệu đúng như bài. Nếu thiếu hạng thì báo Đức, và đề xuất bơm thêm một nhiễu thăm dò *đã biết* vào pha 1 (chỉ làm được trong mô phỏng) | δ ≈ (3, −2.5, 3) gần như hằng số, cộng các sin chậm và 0.1·rand. Khi d − d̂ ≈ hằng số, 27 cột của khối W_d chỉ có hạng khoảng 9, nên hạng ρ₁ ≤ 45 + 27 + 9 = 81 < 99 ẩn | **CẦN CHỐT** (nếu xảy ra) |
| B-7 | Trạng thái đầu của tàu ảo η_d(0), υ_d(0) không cho | **η_d(0) = η(0), υ_d(0) = 0** (khi đó z(0) = 0) | Lựa chọn tự nhiên nhất. Quá độ lớn ở Hình 8/17 có thể đến từ k_p = 30 chứ không nhất thiết từ z(0) ≠ 0 | **CẦN CHỐT** |
| B-8 | Định nghĩa chỉ số; Bảng 1 tự mâu thuẫn | e(t) = sqrt(Σ_{(i,j)∈E}‖g_ij − g*_ij‖²) trên danh sách cạnh của Hình 2/13 (4 và 8 cạnh), tính từ vị trí tàu thật. IAE = ∫₀⁴⁰‖e‖dt; ITAE = ∫₀⁴⁰t‖e‖dt; RMSE = sqrt((1/40)∫‖e‖²dt). Báo thêm biến thể RMSE "theo chữ" là sqrt(∫‖e‖²dt/N). Tổng lực = Σ_follower Σ_{u,v,r}∫\|τ\|dt. **Chỉ so tỉ lệ giữa các phương pháp**, không so số tuyệt đối | IAE = 37.2 trong 40 s nghĩa là ‖e‖ trung bình ≈ 0.93. Theo Cauchy–Schwarz, khi đó RMSE ≥ 0.93 (định nghĩa chuẩn), hoặc ≥ 0.029 (định nghĩa theo chữ với N = 40000). Cả hai đều mâu thuẫn với 0.0178. Chú thích bảng còn ghi nhầm "Fig. 12" (đúng ra là Hình 5) | **CẦN CHỐT** |
| B-9 | Các số liệu hình ảnh không nhất quán | Chỉ ghi vào báo cáo: (i) Case 2, s ban đầu trên Hình 12 ≈ 24, trong khi tính từ trạng thái đầu đã cho ra 32.8; (ii) Bellman error ở Hình 11 cỡ 25, ở Hình 19 cỡ 5·10⁻⁴; (iii) số vòng lặp là 20 (Case 1) và 10 (Case 2) | | ĐÃ RÕ |
| B-10 | X(1..9) là gì | **(A) đúng chữ (20)–(21):** X = [z_η(3); z_υ(3); p_d(2); ψ_d; ϑ_d(2); ω_d; ϑ̇_d(2); ω̇_d], nên X(1..9) = [z; p_d; ψ_d]. **(B):** X(1..9) = [z; υ_d]. Config `basis_state_indices`. Mặc định chạy (A); (B) là biến thể có nhãn | Vì G = K = [Λ; 0], u* và d* chỉ phụ thuộc ∂V/∂z_υ, nên việc chỉ dùng 9 thành phần là một lựa chọn xấp xỉ. Với (A), cơ sở chứa **vị trí tuyệt đối** p_d (chạy từ 0 đến 160 m): chính sách không bất biến tịnh tiến, ngoại suy xa vùng thu dữ liệu, ρ₁ có các cột p_d² cỡ 2.5·10⁴. ψ_d ≈ π/4 lại đóng vai trò một hằng số bù. Với (B), có feedforward theo vận tốc, hợp lý về vật lý nhưng lệch chữ | **CẦN CHỐT** |
| B-11 | Vị trí đặt bộ lọc an toàn | Lọc trên Π (mục a) | (12) là song ánh giữa Ξ_p và Π | XÁC NHẬN |
| B-12 | Đường dẫn PDF trong PROJECT_CONTEXT (`papers/…`) sai | Sửa §1 của PROJECT_CONTEXT thành `Main_paper/…`, `Side_paper/…`. Agent sửa nếu Đức cho phép | | XÁC NHẬN |
| B-13 | Môi trường | Tạo `.venv` bằng `uv` với numpy, scipy, matplotlib, pyyaml, pytest (máy hiện chưa có scipy, matplotlib). Có nên `git init` thư mục dự án không (hiện chưa là repo git; `external/` sẽ được gitignore)? | | **CẦN CHỐT** |
| B-14 | M1 (62) | Ba cách hiểu. **(A)** υ_e = υ − υ_d, Ξ = υ̇_d: chỉ bám vận tốc, không phản hồi vị trí. **(B)** υ_e = z_υ = υ − alpha_v, Ξ = d(alpha_v)/dt: có phản hồi vị trí qua (16). **(C)** như (B) nhưng hệ số ζ nhân với khối lượng. Mặc định (B) với ζ đúng như in. Ghi chú thêm: (62) dùng khối lượng đường chéo, bỏ qua m23 | Với (A) hoặc (B), sai số vận tốc xác lập ≈ δ/ζ = 3/0.5 = **6 m/s**, quá lớn so với RMSE 0.11 của M1. Với (C), sai số ≈ δ/(m·ζ) ≈ 0.23 m/s, hợp lý hơn | **CẦN CHỐT** |
| B-15 | Tích phân số và lấy mẫu | RK4, dt = 1e-3 cho các lần chạy 40 s. Pha 1 dùng dt = 1e-4 (10 bước con mỗi khoảng T = 1e-3, như OffQLCTS dùng d = 10), tích phân hình thang. Mẫu rand của δ đổi mỗi 1e-3 s | Code của nhóm dùng bước cố định 0.001 s | XÁC NHẬN |

### b.3 Đề xuất mặc định cho pha thu dữ liệu (mục 5) **[CẦN CHỐT từng dòng]**

| Câu hỏi | Mặc định đề xuất | Phương án khác |
| --- | --- | --- |
| Chạy riêng hay trong lúc chạy 40 s? | **Một lần chạy riêng trước khi triển khai**, đúng như Hình 1 ("Data collection once"), cùng kịch bản và trạng thái đầu của Case 1 hoặc Case 2. Mỗi follower học W riêng | Thu trong vài giây đầu của chính lần chạy 40 s |
| Chính sách hành vi | **u_b = −K_b·z + e(t)**: K_b là khuếch đại PD chọn tay, không dùng mô hình, ghi trong config | (ii) M1 + e(t): ổn định tốt hơn nhưng dùng mô hình ở pha 1, nên tính "không cần mô hình" yếu đi. (iii) u = 0 + e(t): tàu không đuổi kịp tàu ảo |
| Tín hiệu thăm dò e(t) | Tổng 10 sin, tần số cố định ngẫu nhiên trong [0.5, 50] rad/s, pha ngẫu nhiên, có seed; biên độ khoảng 10–20 % lực điển hình (vài trăm N). Là hàm thay thế được (§6.4) | Nhiễu trắng giống OffQLCTS |
| Thời lượng và số khoảng M | **Toàn bộ 40 s kịch bản**, T = 1e-3, nên M = 40 000 ≫ 99 ẩn. Phủ cả ba pha: phóng to, giữ, thu nhỏ | 2 s đầu (M = 2000) |
| T₁ | Bằng thời điểm bắt đầu pha 1. Thực tế không ảnh hưởng: mỗi khoảng dùng e^{−α(τ−t_{j−1})} | |
| Nhiễu d trong dữ liệu | δ(t) thật (mục 9). Nếu thiếu hạng thì xem B-6 | |

---

## (c) Các mốc

Mỗi mốc kết thúc bằng: toàn bộ test qua; hình lưu trong `results/`; một ghi chú ngắn gửi Đức gồm kết quả, độ lệch so với Paper A và giải thích. **Không chuyển mốc khi Đức chưa xem.**

### Mốc 1: Mô hình tàu và hình học bearing

Các file: `requirements.txt`, `config/case1.yaml`, `case2.yaml`, `models/vessel.py`, `graph/bearing.py`, `sim/integrators.py`, `docs/notation.md`.

Tiêu chí hoàn thành: mọi test dưới đây qua; in bảng vị trí đích của Case 1 và Case 2.

Test (§5.4.1, §5.4.3):
- **Plant:** M đối xứng, xác định dương. C(υ) phản đối xứng, nên υᵀC(υ)υ = 0. Tàu không điều khiển, không nhiễu, xuất phát với υ(0) ≠ 0 thì năng lượng ½υᵀMυ giảm đơn điệu về 0. Đồng thời kiểm D + Dᵀ có xác định dương ở các vận tốc điển hình không (d23 và d32 bất đối xứng, có thể âm), và báo nếu không.
- **Động học:** đi thẳng theo surge với ψ = π/4 thì di chuyển theo hướng (1, 1)/√2.
- **Nhiễu:** δ(t) tái lập được theo seed; trung bình ≈ (3.05, −2.45, 3.05).
- **RK4:** sai số bậc 4 trên ẋ = −x.
- **Bearing:** P_g·g = 0, P_g² = P_g. B đối xứng, nửa xác định dương. B·(1⊗I₂) = 0 và B·p* = 0 (bất biến tịnh tiến và co giãn). B_ff khả nghịch: trị riêng nhỏ nhất là 0.145 (Case 1) và 0.039 (Case 2). Từ (8) phải ra p₃* = (1, 0), p₄* = (1, −9) (hình vuông cạnh 9), p₅* = (−8, 0), p₆* = (−8, −9) (hình chữ nhật 18×9). Bearing tính từ p* phải trùng g* trong config.

### Mốc 2: Tầng cao riêng, tàu thật bám tàu ảo hoàn hảo

Các file: `high_level/scaling.py`, `leaders.py`, `followers.py`, `safety/base.py`, `sim/runner.py` (chế độ `perfect_tracking`: η ≡ η_d, υ ≡ υ_d), `metrics.py` (sai số bearing, s theo cả hai định nghĩa, khoảng cách nhỏ nhất), `plots.py` (dạng Hình 3, 5, 6, 12), `scripts/run_highlevel_only.py`.

Tiêu chí hoàn thành: test qua. Ghi chú cho Đức so với Hình 3, 5, 12, và kết luận về B-3. **Đức chốt k_p, k_v trước khi sang Mốc 3.**

Test (§5.4.2):
- **Chỉ có leader:** tâm dịch đúng 40·v_c = (160, 160) (sai số < 1e-6). s(t) = s(0)·exp(∫β) (sai số < 1e-6); đỉnh ứng với tỉ lệ e^{0.073·15} = 2.99, khớp Hình 12 (38/13 và 60/20).
- **Follower với leader đứng yên** (v_c = 0, β = 0): sai số bearing → 0 khi chạy đủ lâu. Tốc độ tắt đo được phải khớp phân tích tuyến tính k_vλ/2 (sai lệch < 5 %).
- **Đúng tham số bài, 40 s:** đo và báo. Tiêu chí là "khớp phân tích", **không phải** "khớp Hình 5".
- **Nhất quán Π ↔ Ξ:** tích phân (10)–(12) phải cho p̈_d = Π.
- **(14):** ψ_d → ψ₀, theo hàm mũ với tốc độ k_ω khi b_i = 1.
- `IdentityFilter` trả nguyên đầu vào; runner chạy được với `Environment` rỗng.

### Mốc 3: Chạy kín với baseline M1

Các file: `low_level/backstepping.py`, `baselines/m1_model_based.py`, runner chế độ `m1` với plant thật, `metrics.py` (IAE, ITAE, RMSE, tổng lực), `scripts/run_case.py --config … --controller m1`, `tests/test_separation.py`.

Tiêu chí hoàn thành: Case 1 chạy đủ 40 s không phân kỳ. Có các hình dạng Hình 3–9 cho M1. Báo RMSE và so với 0.1136, không chỉnh tham số cho khớp. Báo B-3 có còn đúng khi chạy kín không.

Test:
- **Backstepping:** nếu υ ≡ alpha_v thì ż_η = −β_η z_η (kiểm bằng số).
- **M1, δ = 0, mô hình đúng:** z → 0 theo hàm mũ.
- **M1 có δ:** sai số bị chặn; so giá trị xác lập với dự đoán (B-14).
- **Tách biệt:** chỉ `models/`, `sim/runner.py` và `baselines/` được import tham số tàu.
- **Chỉ số:** kiểm trên tín hiệu tổng hợp e(t) = e^{−t}, có lời giải giải tích cho IAE, ITAE, RMSE.
- Log khoảng cách nhỏ nhất giữa mọi cặp tàu (§5.5).

### Mốc 4: IRL trên bài toán đồ chơi biết trước lời giải

Các file: `low_level/offpolicy_irl.py`, `basis.py`, `data_collection.py` (dạng tổng quát cho mọi f(x, u, d)), `scripts/toy_irl.py`, `config/toy_irl.yaml`.

Bài toán:
- **T1:** hệ vô hướng ẋ = ax + bu + ed, với a = −1 và a = +1 (trường hợp không ổn định thì chính sách hành vi phải ổn định hóa).
- **T2:** hệ 2 chiều (khâu tích phân kép có cản) có kênh nhiễu.
- Cả hai dùng α = 0.1 và γ = 5.

Lời giải chuẩn: phương trình Riccati H∞ có chiết khấu
(A − ½αI)ᵀP + P(A − ½αI) + Q − P(BR⁻¹Bᵀ − γ⁻²EEᵀ)P = 0.
Giải bằng `scipy.linalg.solve_continuous_are` với B̄ = [B E], R̄ = blkdiag(R, −γ²I), và kiểm chéo bằng không gian con ổn định của ma trận Hamilton. Đối chiếu thêm với phép lặp Kleinman dùng mô hình (tương đương Thuật toán 1). Từ đó: W_c lấy từ P, u* = −R⁻¹BᵀPx, d* = γ⁻²EᵀPx.

Tiêu chí hoàn thành: **P, K, L học được khớp lời giải chuẩn với sai số tương đối < 1e-4.**

Test (§5.4.4, §5.4.5):
- Khớp ARE như trên.
- **Từng vòng lặp** off-policy phải khớp từng vòng của Kleinman dùng mô hình. Đây là phép kiểm mạnh nhất cho cách dựng ρ₁, ρ₂ (B-5).
- In hạng và số điều kiện của ρ₁. Tắt nhiễu thăm dò thì phải phát hiện thiếu hạng và dừng kèm cảnh báo.
- d hằng số trong dữ liệu thì phải phát hiện khối W_d thiếu hạng (minh họa B-6).
- Độ nhạy theo T ∈ {1e-3, 1e-2} và số bước con.

### Mốc 5: IRL trên tàu

Các file: `low_level/augmented_state.py`, `irl_controller.py`, phần ghép data collection với tàu, `scripts/train_irl.py` (pha 1 và pha 2 cho từng follower, lưu W vào `results/`), runner chế độ `irl`.

Tiêu chí hoàn thành: ρ₁ đủ hạng (99). Phép lặp hội tụ, có các hình dạng Hình 10, 11. Triển khai Case 1 đủ 40 s mà hệ bị chặn. **Dừng, báo Đức trước Mốc 6.**

Test và kiểm tra:
- X dựng từ một trạng thái đã biết phải khớp tính tay, đúng thứ tự cấu hình (B-10).
- Chạy u = 0 để kiểm mục 8.
- Báo hạng, số điều kiện của ρ₁; dừng nếu thiếu hạng (B-6).
- ‖Ŵ^{k+1} − Ŵ^k‖ và ‖δ_B‖ theo từng vòng.
- Sai số Bellman trên các khoảng **giữ lại để kiểm định**, không dùng lúc học. Bài không có phép kiểm này; nó phát hiện học quá khớp.
- **Lời giải tham chiếu dùng mô hình (chỉ trong test, không đưa vào bộ điều khiển):** tuyến tính hóa hệ sai số quanh chế độ chạy thẳng (u ≈ 5.66 m/s, ψ = π/4), giải ARE H∞ với Q = 100·I₆, R = I, γ = 5, α = 0.1. So bậc độ lớn của khối W_a theo z. Phép này đồng thời cho biết **hàm chi phí đã cho ngụ ý chất lượng bám tốt đến đâu** (rủi ro R3).

### Mốc 6: Tái tạo Case 1, Case 2 và viết báo cáo so sánh

Các file: `scripts/make_figures.py`, `docs/replication_report.md`.

Nội dung:
- Chạy M1 và IRL cho cả hai case, cùng seed.
- Case 1: các Hình 3–12. Case 2: các Hình 14–20. Bảng 1, trong đó M2–M4 ghi "chưa cài (ngoài phạm vi)".
- Hình mới: khoảng cách nhỏ nhất giữa các cặp tàu theo thời gian (§5.5).
- Báo cáo: so từng hình về định tính; bảng số liệu; mỗi độ lệch kèm giải thích; danh sách giả thiết đã dùng.

Tiêu chí hoàn thành: báo cáo đầy đủ, Đức đã review.

Test: chạy lại cùng seed thì chỉ số y hệt; có test hồi quy lưu chỉ số của một lần chạy ngắn.

---

## (d) Rủi ro không tái tạo được và phương án dự phòng

Phương án dự phòng chung, có hiệu quả nhất: **PGS. Đào Phương Nam là tác giả liên hệ của Paper A, cũng là người trong nhóm của Đức.** Xin code hoặc chi tiết pha thu dữ liệu từ nhóm tác giả (Hoang Anh Nguyen Duc, Minh Hiep Phung) sẽ giải quyết phần lớn các rủi ro dưới đây.

| # | Rủi ro | Khả năng / ảnh hưởng | Dự phòng |
| --- | --- | --- | --- |
| **R1** | **Tầng cao gần như không có cản** (B-3): với k_p = 30, k_v = 0.1, ζ ≈ 0.002–0.018; đội hình dao động hàng chục đến hàng trăm giây, trái với Hình 5 | Cao / rất lớn: ảnh hưởng mọi hình và Bảng 1 | Xác nhận ở Mốc 2 và 3. Hỏi tác giả tham số thật. Chạy thêm biến thể có nhãn với k_v chọn để mode chậm nhất có ζ ≈ 0.7. Không trình bày biến thể đó như là tái tạo |
| **R2** | **Pha thu dữ liệu không được mô tả, và có vấn đề xác định được:** T = 1e-3 làm Δσ rất nhỏ nên ρ₁ có số điều kiện rất lớn; δ gần hằng nên khối W_d thiếu hạng (hạng ρ₁ ≤ 81 < 99); không biết chính sách hành vi | Cao / lớn | Chuẩn hóa cột; lstsq thay cho phương trình chuẩn. Biến thể có nhãn: T = 1e-2; nhiễu thăm dò đã biết bơm thêm vào d; ridge với λ được báo cáo. Hỏi tác giả |
| **R3** | **Thang đo của hàm chi phí không hợp với vật lý:** để chạy ở 5.66 m/s cần τ ≈ 1100 N, nên phạt R = I tốn khoảng 1.2·10⁶ mỗi giây. Ước lượng thô với α = 0.1: bám hoàn hảo tốn khoảng 1.2·10⁷, đứng yên tốn khoảng 6.4·10⁶. Vậy **nghiệm tối ưu thật có thể không bám tốt**. Trong khi đó Hình 8, 9 cho z_u ≈ −0.15 m/s ứng với τ ≈ 1100 N, tức khuếch đại hiệu dụng khoảng 7000 N/(m/s). Bài tiền thân có feedforward dùng mô hình; nếu Paper A cũng vậy thì kết quả phụ thuộc mô hình | Trung bình–cao / rất lớn | Lời giải tham chiếu ở Mốc 5 giúp tách hai khả năng: "IRL cài sai" và "hàm chi phí vốn cho bám kém". Báo trung thực. Biến thể có nhãn: thu nhỏ R; dùng đặc trưng υ_d (B-10 B). Hỏi tác giả về feedforward |
| R4 | Thứ tự X mơ hồ (B-10): cách (A) đưa vị trí tuyệt đối vào cơ sở, gây ngoại suy và số điều kiện xấu | Trung bình / lớn | Chạy cả (A) và (B), báo cả hai |
| R5 | Cách hiểu M1 (B-14) có thể cho sai số 6 m/s | Trung bình / trung bình | Chạy cả ba cách, báo, để Đức chọn |
| R6 | Chỉ số Bảng 1 tự mâu thuẫn (B-8) | Chắc chắn / trung bình | Chỉ so tỉ lệ và thứ hạng giữa các phương pháp |
| R7 | Định nghĩa c, s và trạng thái đầu tàu ảo (B-2, B-7) làm Hình 9, 12 lệch | Trung bình / nhỏ–trung bình | Chạy biến thể, đối chiếu mức lực ở Hình 9 |
| R8 | Thiếu M2–M4; code M3, M4 trong repo không trung thành với [42], [43] | Chắc chắn / nhỏ ở giai đoạn này | Ngoài phạm vi, chờ Đức yêu cầu |

---

## 5. Câu hỏi cần Đức chốt (theo thứ tự ưu tiên)

1. **Pha thu dữ liệu** (b.3): duyệt từng dòng, nhất là chính sách hành vi và thời lượng thu.
2. **k_p, k_v** (B-3, R1): giữ đúng bài? Có hỏi tác giả không?
3. **Thứ tự X(1..9)** (B-10): (A) đúng chữ hay (B) dùng υ_d?
4. **Tâm co giãn c trong (9)** (B-2): tâm các leader (đúng chữ) hay tâm mọi tàu (khớp Hình 9, 12)?
5. **M1** (B-14): cách hiểu (A), (B) hay (C)?
6. **Leader** (mục 13): điểm động học?
7. **β_η, k_ω, b_i** (mục 3, 4): dùng mặc định β_η = 2·I₃, k_ω = 2, b_i = 1?
8. **Trạng thái đầu tàu ảo** (B-7): η_d(0) = η(0), υ_d(0) = 0?
9. **Định nghĩa chỉ số** (B-8).
10. **Nếu W_d thiếu hạng** (B-6): có cho bơm nhiễu thăm dò đã biết không?
11. **Môi trường** (B-13): cho tạo `.venv` bằng uv không? Có `git init` không? Có cho sửa đường dẫn PDF trong PROJECT_CONTEXT (B-12) không?
12. **Các mục XÁC NHẬN** (1, 6, 8, 11, B-1, B-11, B-15): đồng ý cả chứ?
13. **Có xin code hoặc chi tiết từ nhóm tác giả không?** Nếu có, câu trả lời cho câu 1–5 có thể đến thẳng từ họ.
