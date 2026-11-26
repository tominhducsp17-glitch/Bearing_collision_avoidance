# Thông lệ thu thập dữ liệu trong off-policy IRL / model-free H∞ cho tàu mặt nước, AUV, quadrotor, robot Euler–Lagrange (ưu tiên nhóm Phuong Nam Dao, HUST)

Phạm vi đã kiểm chứng: đọc full text 2 bài của nhóm Dao (ACSIS 2022 quadrotor; arXiv 2509.16821 F-16) và mã nguồn GitHub của Quang Huy Dao (OffQLCTS.jl, DataDrivenControl-AI-RL-NZSG-Tracking). Các bài vessel của nhóm (ISA Trans 2022, IJRNC 2024, SCL 2025, Springer 2022) và bài gốc Modares–Lewis–Jiang 2015 đều paywall/không fetch được, nên **chi tiết thu thập dữ liệu của chúng: chưa xác minh**. Đã thực hiện ~17 lượt tool call.

## Câu hỏi 1: Những bài ứng dụng nào dùng off-policy IRL / model-free H∞ trên vessel/AUV/quadrotor/robot? (bảng từng bài)

### Takeaway
Nhóm Dao có ít nhất 1 bài off-policy RL quadrotor (ACSIS 2022) nêu rõ pha thu thập dữ liệu dùng **PID + nhiễu** nhưng **không cho con số nào**. Bài F-16 (arXiv 2509.16821) và repo kèm theo là nguồn duy nhất của nhóm cho thông số cụ thể: T = 0.01 s, 10 bước RK4 con, 100 khoảng (1 s) cho LQR / 250 khoảng (2.5 s) cho tracking, nhiễu là tổng 100 sin với tần số ngẫu nhiên trong [−500, 500] rad/s, least squares bằng `pinv(X'X)X'Y`. Với các bài vessel của nhóm, tôi không xác minh được chi tiết thu thập dữ liệu.

### Bảng từng bài

| # | Bài (DOI/arXiv) | Đối tượng | Behavior policy | Probing noise | T / số mẫu / thời lượng | Nhiễu d trong phương trình off-policy | Số vòng lặp / rank | Trạng thái |
|---|---|---|---|---|---|---|---|---|
| 1 | Pham, Cao, Nguyen, **Dao**, "Optimal tracking controllers with Off-policy RL Algorithm in Quadrotor", ACSIS Vol. 33 (RICE 2022), pp. 29–32, DOI 10.15439/2022R52 | Quadrotor, cascade: vòng ngoài vị trí + vòng trong attitude, mỗi vòng có off-policy RL riêng | **2 bộ PID** (vòng ngoài và vòng trong) ở pha 1 "to collect data for the next stage of training" | "noises is added to the system to guarantee the PE condition"; không nêu dạng hay biên độ | Không nêu T, số mẫu, thời lượng. Có hình "position tracking error at initial stage" | Không có nhiễu ngoài/H∞ (chỉ là optimal tracking, cost có chiết khấu e^{−λ(τ−t)}) | Có "threshold" dừng; hội tụ trọng số chỉ thể hiện bằng hình | Đã đọc full text |
| 2 | D. C. Nguyen, Q. H. Dao, **P. N. Dao**, "A model free approach for continuous-time optimal tracking control with unknown user-define cost and constrained control input via advantage function", arXiv:2509.16821 (2025) | F-16 tuyến tính, 3 trạng thái (LQR) và hệ tăng cường 6 trạng thái (LQT, có A_r) | Behavior là **chỉ nhiễu thăm dò** u(t) = C̄ Σ_{i=1}^{100} sin(ω_i t), không có feedback (mã: `K0 = zeros`, `u_i0 = zeros`). Không cần admissible initial policy | ω_i ngẫu nhiên trong [−500, 500]; C̄ = 50/15 (feedback), 50/2 (tracking). Trong mã: `u = 50/2 * (1/100) Σ sin(i·t)`, tức biên độ được chia thêm cho 100 | Mã: `T = 0.01` s mỗi khoảng tích phân, `d = 10` bước RK4 con (δt = 1 ms). `max_collect = 100` khoảng (1 s) mặc định; tracking dùng `max_collect = 250` (2.5 s, khớp "T = 2.5 s" trong bài). Bài: N_train = 39 episode | Không có d (LQR/LQT, không H∞) | `max_iters = 39`; LS bằng `pinv(X1'*X1)*X1'*Y`; Lemma 1 nêu điều kiện rank rank[I_xx, I_xu, I_uu] = n(n+1)/2 + mn + m(m+1)/2; hội tụ sau khoảng 4 vòng (LQR) | Đã đọc full text và mã |
| 3 | Repo Q. H. Dao, DataDrivenControl-AI-RL-NZSG-Tracking (tái lập bài off-policy NZSG tracking rời rạc, DOI 10.1002/oca.2597) | Hệ DT tuyến tính 3+1 trạng thái | Gain ban đầu khác 0 (K10, K20) cộng nhiễu | Có nhiễu thăm dò (README: "probing noise will not affect the system and the Nash equilibrium") | Số mẫu `f = n² + m1² + m2² + m1·m2 + n(m1+m2) + 20`, tức số ẩn cộng thêm **20** mẫu dư | Có w (đầu vào thứ hai) được ghi lại | `n_learn = 20` vòng; dùng `pinv` | Đã đọc mã (không phải bài ứng dụng robot/vessel) |
| 4 | V. T. Vu, **P. N. Dao**, X. M. Phan (2022), "Robust Optimal Control Based on the Off-Policy IRL Algorithm for Surface Vessel Systems with Unknown Dynamics", Springer LNNS/ICERA, DOI 10.1007/978-3-030-99666-6_124 (suy ra từ link Springer) | Surface vessel | chưa xác minh | chưa xác minh | chưa xác minh | chưa xác minh | chưa xác minh | Paywall (303 tới Springer IdP) |
| 5 | V. T. Vu, Q. H. Pham, **P. N. Dao**, "Disturbance observer-based adaptive reinforcement learning for perturbed uncertain surface vessels", ISA Trans. 2022 (PII S0019057822001495) | Surface vessel | Adaptive/online actor-critic + DOB, không phải off-policy batch | — | — | Nhiễu được bù bằng DOB (theo tiêu đề) | — | Chỉ có abstract/tiêu đề |
| 6 | K. Nguyen, V. T. Dang, D. D. Pham, **P. N. Dao**, "Formation control scheme with RL strategy for a group of multiple surface vehicles", IJRNC 34(3):2252–2279, 2024, DOI 10.1002/rnc.7083 | Đội SV: displacement-based formation ở mức cao + RL tối ưu ở mức thấp cho từng agent | chưa xác minh | chưa xác minh | chưa xác minh | chưa xác minh | chưa xác minh | Chỉ có metadata |
| 7 | **P. N. Dao**, H. A. Nguyen Duc, Y.-C. Liu, "RL-based control framework for leader-following cascade formation of multiple perturbed surface vehicles", Syst. Control Lett. 200 (2025) 106077 (PII S0167691125000593) | Đội SV, cascade leader/follower, Actor/Critic | chưa xác minh (khung actor/critic, có thể là online, chưa rõ có off-policy không) | chưa xác minh | chưa xác minh | chưa xác minh | chưa xác minh | Chỉ có metadata |
| 8 | Bài đang tái lập: Duc, Phung, Dao, J. Franklin Inst. 363 (2026) 109193 | CyberShip II 3-DOF, z 6 chiều + Ω 9 chiều | "stable exploring policy" (theo mô tả của người dùng) | không nêu | không nêu | δ = (3, −2.5, 3) + sin + 0.1·rand | Alg. 2 dùng LS | Theo mô tả của người dùng |
| 9 | Modares, Lewis, Jiang, "H∞ tracking control of completely unknown continuous-time systems via off-policy RL", IEEE TNNLS 26(10), 2015 (PubMed 26111401), DOI 10.1109/TNNLS.2015.2441749 (DOI chưa xác minh trực tiếp) | Bài lý thuyết gốc của khung H∞ tracking off-policy (hệ tăng cường e–r, cost có chiết khấu) | chưa xác minh từ text | Search snippet: phương pháp "not affected by probing noise" và không cần nhiễu d điều chỉnh được | chưa xác minh | Snippet: "does not require adjustable disturbance inputs" (d chỉ cần đo được, không cần chủ động chọn) | chưa xác minh | Không fetch được full text |

### Cited Findings
- Bài quadrotor: "At the first stage, we use 2 PID-controllers for both outer and inner loops to collect data for the next stage of training to obtain the optimal controllers. Note that noises is added to the system to guarantee the PE condition." Thuật toán: "Start with an acceptable control input u0p and noise upe which is added to guarantee PE condition. Collect data and determine a threshold". Bài không cho số nào về T, số mẫu hay biên độ — [ACSIS 2022, DOI 10.15439/2022R52](https://annals-csis.org/Volume_33/drp/pdf/52.pdf)
- Bài quadrotor có cấu trúc cascade: vòng trong dùng hệ tăng cường [e_Θ; x_Θd] 12 chiều với ẋ_Θd = F_Θd x_Θd, cost có chiết khấu e^{−λ(τ−t)}. Đây là cùng kiểu "error + reference augmented" như bài JFI 2026 — [ACSIS 2022](https://annals-csis.org/Volume_33/drp/pdf/52.pdf)
- F-16: "trained over episodes N_train = 39, collecting data for T = 1(s) in each episode… Algorithms 4 and 5 were used to track problems … collecting data for T = 2.5(s)… the behaviour policy used for exploration … is defined as the sum of sinusoidal signals with random frequencies u(t) = C̄ Σ_{i=1}^{100} sin(ω_i t), ω_i randomly selected from [−500, 500], C̄ is set to 50/15 for the feedback case and 50/2 for the tracking case" — [arXiv:2509.16821](https://arxiv.org/pdf/2509.16821)
- F-16: điều kiện rank (26) rank[I_xx, I_xu, I_uu] = ½n(n+1) + mn + ½m(m+1) bảo đảm Δ_i full rank ở mọi vòng lặp, và có thể kiểm tra chỉ từ dữ liệu thu được. Bài phê phán việc reset trạng thái ngẫu nhiên ([24]) và việc probing noise gây bias trong on-policy — [arXiv:2509.16821](https://arxiv.org/pdf/2509.16821)
- F-16: On-policy Q-learning mất ổn định khi có nhiễu thăm dò, Online Q-learning bị bias. Off-policy Alg. 2/3 hội tụ sau khoảng 4 vòng lặp — [arXiv:2509.16821](https://arxiv.org/pdf/2509.16821)
- Mã OffQLCTS.jl: `Options(max_iters = 39, max_collect = 100, T = 0.01)`. Tracking: `setOpt(max_collect = 250)`, x0 = [1, 1, 0, 0, 0, 0.5], K0 = 0. Nhiễu `i1 = (rand(100) .- 0.5) .* 1000` và `u = 50/2 * Σ sin(i t)/length(i1)`. RK4 với `d = 10` bước con mỗi khoảng T. Các tích phân ∫x⊗x, ∫x⊗u, ∫u⊗u được tính bằng cách **tăng chiều ODE** (tích phân cùng lúc với trạng thái), không dùng tổng hình thang sau khi mô phỏng. LS: `pinv(X1'*X1)*X1'*Y` — [GitHub Huy-Quang-Dao/OffQLCTS.jl](https://github.com/Huy-Quang-Dao/OffQLCTS.jl)
- Mã NZSG (rời rạc): số mẫu = số ẩn + 20, `n_learn = 20`, gain khởi tạo khác 0 — [GitHub DataDrivenControl-AI-RL-NZSG-Tracking](https://github.com/Huy-Quang-Dao/DataDrivenControl-AI-RL-NZSG-Tracking)
- Danh sách repo GitHub của Huy-Quang-Dao không có repo nào cho vessel, formation hay H∞ zero-sum liên tục (gồm OffQLCTS.jl, DataDrivenControl-RL-lamda-PI, NonZeroSumGame-RL-OffPolicy-for-DT-System, Inverse-RL-Intelligent-Control-DT, I2Robotics, …) — [GitHub API user repos](https://github.com/Huy-Quang-Dao)
- IJRNC 2024: "a high-level displacement-based formation controller and a low-level RL-based optimal control strategy for individual SV agents", DOI 10.1002/rnc.7083 — [Scilit](https://www.scilit.com/publications/ea8254db3893fa13b9462153cb55c5e2)
- SCL 2025: "leader/follower cascade formation control structure employing the Actor/Critic framework for a group of multiple perturbed surface vehicle agents" — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0167691125000593)
- Vu–Dao–Phan 2022, bài off-policy IRL cho surface vessel, xuất hiện trong danh mục tham khảo của Springer — [Springer](https://link.springer.com/10.1007/978-3-030-99666-6_124)
- Có một bài JMST (Việt Nam) về điều khiển USV model-free bằng PI + IRL, dùng order-reduction và off-policy actor-critic trên mô hình USV 3-DOF có nhiễu biến thiên. Tác giả và chi tiết chưa xác minh (trang trả 404) — [VJOL JMST 126526](https://vjol.vista.gov.vn/jmst/en/article/view/126526)
- Modares–Lewis–Jiang 2015: off-policy học nghiệm HJI tracking mà không cần động lực học. Theo search snippet, phương pháp không bị ảnh hưởng bởi probing noise và không cần đầu vào nhiễu điều chỉnh được — [PubMed 26111401](https://pubmed.ncbi.nlm.nih.gov/26111401/), [ResearchGate](https://www.researchgate.net/publication/276921112_H_Tracking_Control_of_Completely_Unknown_Continuous-Time_Systems_via_Off-Policy_Reinforcement_Learning)

### Inferences
- "Thói quen" của nhóm Dao (suy đoán, dựa trên 2 bài và mã đã đọc): (a) với hệ phi tuyến/robot thì behavior policy là một bộ điều khiển cổ điển ổn định (PID) cộng nhiễu, chạy ở **pha riêng trước** pha học (pha 1 thu thập, pha 2 học, pha 3 áp dụng). Mã F-16 cũng tách rõ "phase1: learning and phase2: application". (b) Nhiễu là tổng nhiều sin tần số ngẫu nhiên, biên độ khá lớn. (c) T nhỏ (0.01 s) với tích phân con bằng RK4 qua tăng chiều ODE. (d) Số khoảng chỉ gấp vài lần số ẩn (100–250 khoảng cho 6–21×n ẩn) và dùng pinv. Với JFI 2026, khả năng cao họ dùng một bộ điều khiển ổn định (PD/backstepping) cộng tổng sin, nhưng điều này **chưa xác minh**.
- Lưu ý khi áp dụng cho bài vessel: trong mã F-16, nhiễu Σ sin chia cho 100 nên biên độ hiệu dụng nhỏ (cỡ 25/√(2·100) ≈ 1.8, suy đoán theo thống kê tổng sin ngẫu nhiên). Nếu bê nguyên sang vessel có lực drag cỡ hàng trăm N thì kích thích sẽ yếu, cần scale lại (suy đoán).
- Tần số đến 500 rad/s với T = 0.01 s nghĩa là nhiều thành phần sin dao động gần hoặc vượt Nyquist của khoảng tích phân. Điều này giúp làm giàu rank nhưng chỉ ổn khi tích phân con đủ mịn (δt = 1 ms) (suy đoán).

### Gaps
- Không đọc được full text của bất kỳ bài vessel nào của nhóm Dao (Springer 2022, ISA 2022, IJRNC 2024, SCL 2025, JFI 2026), nên không biết họ chọn behavior policy, biên độ nhiễu, T, số mẫu như thế nào cho vessel.
- Không tìm được bài quadrotor zero-sum/H∞ off-policy của nhóm có full text.
- Không xác minh được các bài nhóm ngoài (Wang Ning, Peng Zhouhua, Zhang Huaguang, Wei Qinglai) cho vessel/AUV/manipulator với off-policy IRL H∞. Search không trả về bài cụ thể có chi tiết pha thu thập dữ liệu.

## Câu hỏi 2: Xử lý nhiễu d trong phương trình off-policy (H∞)

### Takeaway
Trong khung H∞ off-policy chuẩn (Modares 2015), d phải **đo được** trong pha thu thập nhưng không cần chủ động chọn. Các bài đã đọc của nhóm Dao (quadrotor, F-16) không có thành phần d. Không xác minh được cách nhóm xử lý d trong các bài vessel.

### Cited Findings
- Off-policy H∞ tracking (Modares 2015) "does not require adjustable disturbance inputs" (theo snippet) — [ResearchGate](https://www.researchgate.net/publication/276921112_H_Tracking_Control_of_Completely_Unknown_Continuous-Time_Systems_via_Off-Policy_Reinforcement_Learning)
- Bài DT H∞ off-policy (Kiumarsi et al., Automatica 2017) kết luận thuật toán không nhạy với biên độ và tần số probing noise, ví dụ trên F-16 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0005109816305179)
- Với output-feedback, phương pháp off-policy dùng input–output không còn miễn nhiễm với probing noise; tác giả dùng discount factor để giảm ảnh hưởng — [CDC 2021](https://dl.acm.org/doi/10.1109/CDC45484.2021.9683057)
- Bài vessel ISA 2022 của nhóm dùng disturbance observer (DOB) thay vì đưa d vào phương trình off-policy — [ScienceDirect ISA Trans.](https://www.sciencedirect.com/science/article/abs/pii/S0019057822001495)

### Inferences
- Với δ = (3, −2.5, 3) gần hằng, các cột ∫(ν-term ⊗ d) trong ma trận hồi quy gần tỉ lệ với ∫ν-term. Điều này có thể gây rank-deficient hoặc ill-conditioned, nhất là khi Ω cũng có thành phần hằng. Một cách làm là kích thích thêm nhiễu vào kênh d, hoặc coi phần hằng như một trạng thái tăng cường (suy đoán, không có nguồn).
- DOB trong ISA 2022 cho thấy nhóm từng xử lý nhiễu bằng ước lượng–bù. JFI 2026 có thể dùng d đo được (vì mô phỏng) (suy đoán).

### Gaps
- Không có nguồn nào đã đọc báo cáo rank-deficiency do nhiễu gần hằng.

## Câu hỏi 3: Học theo từng subsystem trong body frame, scaling/normalization, khó khăn số (ill-conditioning)

### Takeaway
Nhóm Dao tách bài toán theo cascade (vị trí/attitude với quadrotor; formation mức cao + RL mức thấp với vessel). Không tìm được nguồn nào của nhóm nói về scaling trạng thái, Q, R hay ill-conditioning. Lựa chọn của họ (pinv của X'X, tăng chiều ODE) cho thấy họ không xử lý điều kiện số một cách tường minh.

### Cited Findings
- Quadrotor: hai bộ off-policy RL riêng cho vòng ngoài (vị trí, đầu ra u_p ∈ R³ chuyển sang u_z, φ_d, θ_d) và vòng trong (attitude) — [ACSIS 2022](https://annals-csis.org/Volume_33/drp/pdf/52.pdf)
- IJRNC 2024: RL mức thấp cho từng agent SV, tách khỏi formation mức cao — [Scilit](https://www.scilit.com/publications/ea8254db3893fa13b9462153cb55c5e2)
- F-16: Q = M = diag(1, 1, 1), R = I. Tracking dùng Q = diag(1, 1, 1, 0, 0, 0) trên hệ tăng cường. Không có chuẩn hóa — [OffQLCTS.jl F16Tracking1.jl](https://github.com/Huy-Quang-Dao/OffQLCTS.jl)
- F-16: LS giải bằng `pinv(X1'*X1)*X1'*Y`. Dạng normal-equation này bình phương số điều kiện — [OffQLCTS.jl src](https://github.com/Huy-Quang-Dao/OffQLCTS.jl)

### Inferences
- Với vessel có M, D cỡ hàng chục đến hàng nghìn (đơn vị SI) và lực điều khiển hàng trăm N, giải normal equation qua X'X sẽ bình phương số điều kiện. Nên dùng QR/`lstsq` trực tiếp và scale các cột (suy đoán, thực hành chung).
- T nhỏ (0.01 s) làm các hiệu x(t+T)⊗x(t+T) − x(t)⊗x(t) rất nhỏ so với các tích phân. Kết hợp với dải biên độ khác nhau giữa z (cỡ m, rad) và Ω làm cột lệch thang. Đây là nguồn ill-conditioning khả dĩ (suy đoán).

### Gaps
- Không có nguồn đã xác minh nào (của nhóm Dao hay nhóm khác) nói về scaling hay ill-conditioning trong ứng dụng vessel.
