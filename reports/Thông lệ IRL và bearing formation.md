# Thông lệ tài liệu lấp ba lỗ hổng tái lập

Bài Duc–Phung–Dao (J. Franklin Inst. 363 (2026) 109193, [DOI 10.1016/j.jfranklin.2026.109193](https://doi.org/10.1016/j.jfranklin.2026.109193)) để trống ba chỗ. Tài liệu liên quan lấp được phần lớn, nhưng không lấp được tất cả.

**K1 (pha thu dữ liệu off-policy).** Thông lệ khá thống nhất:
- behavior policy là một luật ổn định đã biết cộng nhiễu thăm dò, thường là tổng nhiều sinusoid tần số ngẫu nhiên hoặc nhiễu ngẫu nhiên đều;
- dữ liệu thu **một lần**, số khoảng N bằng khoảng **2–17 lần số ẩn**;
- nhiễu d phải **đo được** và có mặt trong dữ liệu;
- lặp least squares trên cùng tập dữ liệu đến ngưỡng ‖ΔW‖ ≤ 10⁻⁷ hoặc |ΔP| ≤ 5·10⁻⁴.

Chính bài gốc Modares–Lewis–Jiang 2015 (ref [39]) cũng không định lượng pha 1. Vì vậy việc bài JFI thiếu chi tiết này là "thông lệ" của cả dòng bài, không phải sơ suất riêng.

**K2 (gain luật bearing bậc hai).** Kết luận mạnh nhất: mọi bài đã xác minh dùng **k_v/k_p ≈ 1–4**. Cặp **k_p = 30, k_v = 0.1** cho hệ số cản ζ ≈ 0.004–0.014 và thời gian xác lập **33–550 s**. Con số này không khớp với hội tụ dưới 1 s trên hình của bài. Hoán đổi hai gain cũng không cứu được.

**K3 (trạng thái trong basis và feedforward).**
- Trường phái Modares/Lewis đưa toàn bộ trạng thái tăng cường [e; x_d] vào basis. Nhưng x_d trong các ví dụ của họ luôn **bị chặn**, không bao giờ là vị trí tuyệt đối.
- Các ứng dụng tàu (Martinsen 2020) và, theo mô tả chưa xác minh, bài IJRNC 2024 của chính nhóm Dao dùng **feedforward mô hình cộng RL trên sai số**.

**Khuyến nghị cho dự án.** Làm baseline "đúng tinh thần, chạy được" với các giả định mặc định nêu ở từng mục, ghi lại từng giả định. Chỉ gửi thầy năm câu hỏi còn lại ở cuối báo cáo.

Quy ước độ tin cậy: **[đã đọc]** là đã đọc toàn văn hoặc đoạn liên quan; **[chưa xác minh]** là chỉ có abstract, nguồn trung gian hoặc trí nhớ; **[suy luận]** là nhóm tự tính hoặc tự suy ra.

## K1: pha 1 được định tính kỹ nhưng gần như không được định lượng

### Nguồn của cụm "stable and exploring" và vai trò của nhiễu d

Cụm "stable and exploring behavior policy" trong bài JFI gần như chắc chắn lấy từ Modares–Lewis–Jiang, IEEE TNNLS 26(10) 2015, [DOI 10.1109/TNNLS.2015.2441749](https://doi.org/10.1109/TNNLS.2015.2441749). Phần mô phỏng của bài này không đọc được (paywall). Algorithm 2 đọc được qua chương sách cùng nhóm (Elsevier 2018) **[đã đọc phần lý thuyết]**, và chương này chỉ nói ba điều:
- "The fixed control policy u should be a stable and exploring control policy";
- pha 1 thu "state, control input and disturbance at N different sampling intervals T";
- N ≥ l1 + m·l2 + q·l3, tức số ẩn ([Modares et al. 2018, Ch.14](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)).

Trong khung này, d là **nhiễu thực, đo được, không cần điều chỉnh được**. Luo–Wu–Huang (TCYB 45(1) 2015, [arXiv 1311.6107](https://arxiv.org/pdf/1311.6107)) cũng viết như vậy: thu "(x_m, u_m, w_m)" và dùng lại dữ liệu cho mọi vòng. Survey Kiumarsi et al. 2018 coi việc "require the disturbance to be measured during learning" là hạn chế còn mở ([survey, DOI 10.1109/TNNLS.2017.2773458](https://par.nsf.gov/servlets/purl/10078417)). Hướng không đo d của Song et al. 2016 ([DOI 10.1109/TCYB.2015.2421338](https://www.aminer.cn/pub/55465ea40cf2939c2feebde0/off-policy-actor-critic-structure-for-optimal-control-of-unknown-systems-with)) phải thêm bộ bù nhiễu và chỉ đạt UUB **[chỉ có abstract]**.

### Con số cụ thể có ở các bài nền tảng đọc được toàn văn

| Bài | Cách làm (behavior, nhiễu, d) | Con số |
|---|---|---|
| Jiang & Jiang, Automatica 48(10) 2012, DOI 10.1016/j.automatica.2012.06.096 (đọc qua sách RADP 2017, Ch.2) | u₀ = −K₀x + e, với K₀ = 0 vì hệ hở ổn định. e = Σ₁¹⁰⁰ sin(ω_k t). Không có d (bài toán LQR) | ω_k ~ U[−50, 50]; thu dữ liệu trong [0, 1] s, mỗi khoảng 0.1 s. Quy tắc N ≥ 2 lần số ẩn. Dừng khi \|ΔP\| ≤ 5·10⁻⁴, sau 16 vòng. Kiểm chứng bằng nghiệm ARE ([RADP](http://library.sadjad.ac.ir/opac/temp/19352.pdf)) |
| Luo, Wu, Huang, TCYB 2015, arXiv 1311.6107, ví dụ F-16 | Nhiễu ngẫu nhiên thuần, không có phản hồi trạng thái. Đo w | Nhiễu U[0, 0.1], Δt = 0.1 s (thử thêm 0.1–0.5 s, không nhạy), M = 100 mẫu (≈17 lần số ẩn), θ⁰ = 0, ξ = 10⁻⁷, hội tụ sau 5 vòng, so với CARE ([arXiv](https://arxiv.org/pdf/1311.6107)) |
| Luo et al., ví dụ RTAC phi tuyến | Như trên | Nhiễu U[0, 0.5], Δt = 0.033 s, M = 300 (15 lần số ẩn), γ = 6, 3 vòng, tỷ số L₂ bằng 3.70 < γ ([arXiv](https://arxiv.org/pdf/1311.6107)) |
| δ-PI tracking, arXiv 2401.12882 (ví dụ kiểu Modares) | Cả u lẫn d là tín hiệu ngẫu nhiên chủ động bơm vào | T = 0.1 s, N = 1000 (≈11 lần 93 ẩn), tổng 100 s. γ = 5, α = 0.1. Ngưỡng 10⁻⁷, 96 vòng ([arXiv](https://arxiv.org/pdf/2401.12882)) |
| arXiv 2001.07355 (tự nhận dựng "in line with" Modares 2015) | d = 0.1e^{−0.1t}sin(0.1t) | T = 0.001 s, discount 0.25. **[chưa xác minh]** các số này thuộc Modares 2015 hay do preprint tự chọn ([arXiv](https://arxiv.org/pdf/2001.07355v1)) |
| Kiumarsi, Lewis, Jiang, Automatica 78 2017 (hệ rời rạc), DOI 10.1016/j.automatica.2016.12.009 | u = −K₁x + e, gain admissible. d là nhiễu thực từ môi trường | Không có số. Kết quả "insensitive to probing noise" **[chỉ có abstract và survey]** ([survey](https://par.nsf.gov/servlets/purl/10078417)) |

Có một mâu thuẫn nội tại trong sách RADP: 1 s dữ liệu chia khoảng 0.1 s chỉ cho khoảng 10 khoảng, ít hơn 33 ẩn của ví dụ. Như vậy chính ví dụ đó vi phạm quy tắc "≥ 2 lần số ẩn" của sách. Có thể bản Automatica gốc dùng khoảng khác **[chưa xác minh]**.

### Thói quen của nhóm Phuong Nam Dao chỉ lộ ra qua quadrotor và F-16

Chưa đọc được bài vessel nào của nhóm (Springer 2022, ISA 2022, IJRNC 2024, SCL 2025). Hai nguồn đọc được và một repo cho thấy các thói quen sau.

| Nguồn | Cách làm | Con số |
|---|---|---|
| Pham, Cao, Nguyen, Dao, ACSIS 33 (2022), [DOI 10.15439/2022R52](https://annals-csis.org/Volume_33/drp/pdf/52.pdf), quadrotor cascade | Pha 1 dùng "2 PID-controllers for both outer and inner loops", cộng thêm "noises … to guarantee the PE condition" | Không có con số nào |
| Nguyen, Dao, Dao, [arXiv 2509.16821](https://arxiv.org/pdf/2509.16821), F-16, cùng mã [OffQLCTS.jl](https://github.com/Huy-Quang-Dao/OffQLCTS.jl) | Behavior chỉ là nhiễu, K₀ = 0, không có feedback. Tích phân tính bằng cách tăng chiều ODE. LS giải bằng `pinv(X'X)X'Y` | u = C̄·Σ₁¹⁰⁰ sin(ω_i t), ω_i ~ U[−500, 500]. C̄ = 50/15 (LQR) hoặc 50/2 (tracking); trong mã còn chia thêm cho 100. T = 0.01 s với 10 bước RK4 con. 100 khoảng (1 s) cho LQR, 250 khoảng (2.5 s) cho tracking. Theo tính của nhóm, đó là khoảng 10× và 9× số ẩn **[suy luận]**. 39 episode, hội tụ sau khoảng 4 vòng |
| Repo NZSG rời rạc của Q. H. Dao ([GitHub](https://github.com/Huy-Quang-Dao/DataDrivenControl-AI-RL-NZSG-Tracking)) | Gain khởi tạo khác 0, cộng nhiễu, có ghi w | Số mẫu bằng số ẩn + 20, 20 vòng |

Từ đó suy ra thói quen của nhóm Dao **[suy luận]**:
- tách hẳn ba pha: thu dữ liệu, học, áp dụng;
- dùng một bộ điều khiển cổ điển ổn định (PID) cho hệ phi tuyến/robot;
- nhiễu là tổng nhiều sin tần số ngẫu nhiên;
- T nhỏ, tích phân con bằng RK4;
- số khoảng chỉ gấp khoảng 10 lần số ẩn;
- không xử lý điều kiện số một cách tường minh. `pinv(X'X)` bình phương số điều kiện.

Câu "collecting data for T = 1 s in each episode" với 39 episode trong bài F-16 có thể hiểu là thu lại dữ liệu sau mỗi episode. Ghi chú hiện có chưa đủ để khẳng định điều này **[chưa xác minh]**.

### Ba hệ quả cấu trúc mà tài liệu không nói nhưng bài JFI buộc phải đối mặt

**Thứ nhất, d phải được kích thích trong pha 1.** Trọng số ban đầu bằng 0 nên d₀ = 0. Khối hồi quy của disturber là ∫e^{−α(τ−t)}2γ²(d − d_j)⊗φ dτ. Nếu d ≡ 0 khi thu dữ liệu thì khối này bằng 0 và ma trận hồi quy mất hạng ngay từ vòng đầu **[suy luận từ phương trình trong Ch.14]**. Nhiễu δ = (3, −2.5, 3) + sin + 0.1·rand của bài gần hằng, nên các cột liên quan đến d có thể gần cộng tuyến với các cột khác **[suy luận]**.

**Thứ hai, T = 0.001 s quá ngắn để áp dụng quy tắc "khoảng mẫu dài hơn chu kỳ nhiễu" của Jiang.** Muốn thỏa quy tắc đó thì cần tần số trên 6000 rad/s. Khi T nhỏ như vậy, độ giàu thông tin phải đến từ sự thay đổi của quỹ đạo giữa các khoảng. Luo gợi ý thêm cách "starting from different initial states".

**Thứ ba, với 99 ẩn mỗi agent** (45 critic + 27 actor + 27 disturber), N cần ≥ 198 theo quy tắc của Jiang, và khoảng 1000–1700 theo thực hành của Luo và δ-PI. Với T = 0.001 s, đó chỉ là 1–2 s dữ liệu **[suy luận]**.

### Mặc định đề xuất cho K1

Đề xuất sau là **[suy luận]**, ghi lại thành giả định A1–A6.

**Behavior policy (A1):** luật ổn định đã biết, gồm feedforward mô hình + PD trên sai số, hoặc chính luật formation + PD tầng động lực học. Cộng nhiễu Σ của 20–100 sinusoid, tần số ngẫu nhiên trong khoảng 0.5–50 rad/s, biên độ cỡ 10–30% lực danh định trên mỗi kênh.

**Kênh d (A2):** δ của mục 4, được đo và ghi lại, cộng thêm một thành phần đa tần độc lập với nhiễu trên u, để khối disturber đủ hạng.

**Lượng dữ liệu (A3):** thu một lần, N ≈ 2000 khoảng T = 0.001 s. Có thể ghép 3–5 đoạn quỹ đạo xuất phát từ các trạng thái đầu khác nhau.

**Kiểm tra trước khi lặp (A4):** rank(ρ₁) = 99 và số điều kiện. Giải bằng `lstsq`/QR, có scale cột, không dùng `pinv(X'X)`.

**Điều kiện dừng (A5):** ‖ΔŴ‖ ≤ 10⁻⁶, tối đa 50 vòng.

**Kiểm chứng (A6):** so với nghiệm GARE có chiết khấu của mô hình tuyến tính hóa, và kiểm tra tỷ số L₂ < γ = 5.

**Câu hỏi còn lại cho thầy:** behavior policy, dạng và biên độ nhiễu, tổng thời gian thu dữ liệu, cách tạo d trong pha 1, ngưỡng dừng.

## K2: k_v = 0.1 lệch khỏi mọi bài đã xác minh hai bậc độ lớn

Luật bearing bậc hai tuyến tính của Zhao & Zelazo **ổn định với mọi k_p, k_v > 0**. Đa thức đặc trưng là λ² + k_vμλ + k_pμ với μ ∈ eig(B_ff), nên luật này không cần điều kiện ghép gain. Điều kiện ghép chỉ xuất hiện khi thêm khâu khác:
- khâu tích phân: 0 < k_I < k_pk_vλ_min(B_ff) ([arXiv 1506.05636](https://arxiv.org/abs/1506.05636));
- đo bearing-only: k_d > 1 và k_p < 4 − 4/k_d². Văn bản trích bị vỡ ký tự, đây là cách đọc của nhóm **[suy luận]** ([arXiv 2110.08054](https://arxiv.org/abs/2110.08054)).

| Bài | Cách làm | Con số (k_p, k_v; k_v/k_p; hội tụ) |
|---|---|---|
| Zhao & Zelazo, IEEE TCNS 4(3) 2017, [arXiv 1506.05636](https://arxiv.org/abs/1506.05636) | Luật (7): leader có vận tốc hằng | (0.5, 2); tỷ lệ 4; bearing error ≈ 0 sau khoảng 10 s (đọc từ Fig. 4b) **[đã đọc]** |
| Như trên, luật (10) | Có feedforward gia tốc | (1, 3); tỷ lệ 3; theo cực thì khoảng 10 s **[suy luận]** |
| Tang, Cunha, Hamel, Silvestre, Automatica 128 (2021) 109567, [arXiv 2110.08054](https://arxiv.org/abs/2110.08054) | Double-integrator, bearing + vận tốc tương đối | (3, 10); tỷ lệ 3.3; chọn "to ensure a fast convergence rate" |
| [arXiv 2609.19106](https://arxiv.org/abs/2609.19106) (2026) | Luật (25), bậc hai | (0.8, 1.5); tỷ lệ 1.9 |
| Vu et al., [arXiv 2110.05153](https://arxiv.org/abs/2110.05153) | Sliding mode | k₁ = 0.5, k₂ = 2; mặt trượt tương đương tỷ lệ 2; điều kiện k₂ > δ₂ + k₁δ₁ |
| Lu & Sun, JMSE 12(8) 1407, 2024 ([MDPI](https://www.mdpi.com/2077-1312/12/8/1407)), cùng tác giả đầu với ref [3] | Luật ảo bearing **bậc nhất** + DSC/backstepping | K_z = 10I, K_ψ = 26I, k_u = 5, k_v = k_r = 10. Tham số tàu "same as [1]", với [1] là Lu et al. TNNLS 2021 |
| Lu, Wen, Shen, Zhang, TNNLS 32(10) 2021, [DOI 10.1109/TNNLS.2020.3025807](https://doi.org/10.1109/TNNLS.2020.3025807) (ref [3]) | Abstract: UUB nếu formation infinitesimally bearing rigid | Gain **[chưa xác minh]**. Đoán là cấu trúc bậc nhất giống Lu & Sun 2024 **[suy luận]** |
| JFI 2026, mục 4.1 (đối chiếu PDF cục bộ) | "k_p = 30, k_υ = 0.1, … T = 0.001 s", dùng chung cho mọi phương pháp so sánh, kể cả Method 2 = [3] | (30, 0.1); tỷ lệ ≈ 0.003 |

Nhóm tự tính các cực của s² + k_vλs + k_pλ với λ ∈ {0.145, 1, 1.40, 2.45} **[suy luận]**:
- (30, 0.1): ζ = 0.0035–0.0143, T_s ≈ 33–552 s, tức dao động gần như không cản;
- (0.1, 30), tức hoán đổi: cực chậm ≈ −0.0033, T_s ≈ 1200 s, nên giả thuyết hoán đổi bị loại;
- (30, 10), một cặp nhóm tự giả định: T_s ≈ 0.8–1.1 s cho λ ≥ 1, khoảng 5.5 s cho λ_min. Cặp này gần nhất với hình "hội tụ dưới 1 s".

Theorem 1 của bài còn có vế (k_v − βk_v²/(4k_p))λ_min. Với k_v = 0.1 vế này chỉ khoảng 0.0145, tức Theorem 1 đòi tốc độ scaling |β| ≲ 0.0145 s⁻¹ **[suy luận]**. Nếu mô phỏng dùng β lớn hơn thì chính định lý của bài bị vi phạm.

Có hai cách giải thích:
- k_v bị ghi sai, ví dụ 10 thành 0.1, hoặc nhầm với α = 0.1 hay T. Đây là khả năng cao nhất;
- hình được sinh từ luật khác, ví dụ luật vận tốc bậc nhất kiểu Lu với k_z ≈ 10.

Cả hai đều **[suy luận]** và không có code gốc để kiểm.

**Mặc định đề xuất:**
- giữ k_p = 30;
- chạy một lần với k_v = 0.1 đúng như bài để ghi lại hành vi;
- dùng k_v = 10 làm baseline chính (ζ ≈ 0.35–1.43 trên dải λ), quét thêm k_v ∈ {5, 2√k_p ≈ 11};
- tính và báo cáo β(t) so với cận của Theorem 1.

Ghi lại thành giả định B1–B2.

**Câu hỏi còn lại cho thầy:** k_v = 0.1 có đúng không, và β(t) cụ thể trong mô phỏng là bao nhiêu.

## K3: basis tăng cường chỉ chứa trạng thái tham chiếu bị chặn, còn tàu thì thường cộng feedforward

Trong dòng Modares/Lewis/Kiumarsi, trạng thái tăng cường là X = [e_d; r] và chính sách được định nghĩa là "u = β(e_d, r)". Basis σ, φ, ϕ lấy trên toàn bộ X, vì "both feedback and feedforward parts of the control input are obtained simultaneously". Chiết khấu "is essential" vì phần feedforward không về 0 ([Ch.14](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)). Survey 2018 đặt cạnh nhau hai cách ([survey](https://par.nsf.gov/servlets/purl/10078417)):
- tách u = u_d + u_e, với critic chỉ theo e. Cách này cần mô hình để tính u_d;
- tăng cường [e; x_d] với Q_T = diag(Q, 0), tức không phạt x_d.

| Bài | Cách làm | Con số / ghi chú |
|---|---|---|
| Modares & Lewis, Automatica 50(7) 2014, [DOI 10.1016/j.automatica.2014.05.011](https://scholarsmine.mst.edu/ele_comeng_facwork/2850) | [e; x_d], x_d từ command generator, RL thuần | Basis gồm cả x_d **[trí nhớ, chưa xác minh]** |
| Modares, Lewis, Jiang, TNNLS 2015 / Ch.14 | [e_d; r] ∈ R²ⁿ; critic, actor, disturber đều trên X | α > 0 bắt buộc; ví dụ số **[chưa xác minh]** |
| Kiumarsi et al., Automatica 50(4) 2014, DOI 10.1016/j.automatica.2014.02.015 | LQT rời rạc, Q-function toàn phương theo [x; r; u] | u = −K₁x − K₂r, trong đó −K₂r là feedforward tuyến tính |
| Mishra & Ghosh, [arXiv 1911.04153](https://arxiv.org/pdf/1911.04153) | z = [e_p, e_q, e_r, p_des, q_des, r_des], critic-only | 27 hàm (6 tuyến tính + 21 bậc hai); Q = diag(10, 10, 50, 0, 0, 0); R = I₃; T = 0.001 s. Reference là **tốc độ góc**, bị chặn **[đã đọc]** |
| Martinsen et al., Front. Robot. AI 7:32 (2020), [DOI 10.3389/frobt.2020.00032](https://pmc.ncbi.nlm.nih.gov/articles/PMC7806118), tàu ReVolt | **Feedforward từ mô hình học online + RL feedback** có bão hòa tanh | Basis chỉ gồm tích bậc hai của sai số; không chiết khấu; τ̄ = [50, 20, 32]. Lý do dùng RL: chỉ feedforward thì "the vessel will experience drift" **[đã đọc]** |
| Nguyen, Dang, Pham, Dao, IJRNC 34(3) 2024, DOI 10.1002/rnc.7083 ([AMiner](https://www.aminer.cn/pub/6573437f939a5f4082f9d21d/formation-control-scheme-with-reinforcement-learning-strategy-for-a-group-of-multiple)) | Formation displacement-based ở tầng trên, RL tối ưu ở tầng dưới | Công thức τ = Mυ̇_d + C(υ_d)υ_d + D(υ_d)υ_d + u_RL lấy từ mô tả trong dự án; nhóm nghiên cứu **chưa tự đọc được bài** |
| Wen et al., TCYB 49(9) 2019, DOI 10.1109/TCYB.2018.2844177 ([tóm tắt](https://www.bohrium.com/paper-details/adaptive-tracking-control-of-surface-vessel-using-optimized-backstepping-technique/813021884298821633-2427)) | Optimized backstepping cho tàu, mỗi bước có một cặp critic/actor | Actor học luôn phần động học **[chỉ có abstract]** |
| Vu, Dao, Loc, Huy, JCAES 2021 ([DOI 10.1007/s40313-020-00674-w](https://link.springer.com/article/10.1007/s40313-020-00674-w)); Dao et al., MATCOM 229 (2025) ([RePEc](https://ideas.repec.org/a/eee/matcom/v229y2025icp151-175.html)) | Manipulator/teleoperator: biến trượt s = ė + Λe, RL cộng RISE | Critic theo s hoặc e **[chỉ có abstract]** |

Trong các ví dụ đã kiểm, không bài nào đưa **vị trí tham chiếu tuyệt đối tăng không giới hạn** (p_d, ψ_d) vào basis. Nếu đọc X(1..9) theo nghĩa đen là [z; p_d; ψ_d], với p_d lên tới khoảng 160 m, thì có ba vấn đề **[suy luận]**:
- feedforward phụ thuộc vào vị trí. Điều này phi vật lý vì lực cản Fossen chỉ phụ thuộc υ_d và υ̇_d;
- mất bất biến tịnh tiến;
- basis bậc hai bị ill-conditioned.

Cost của bài phạt toàn bộ τ với Q = 100I, R = I. Lực xác lập khoảng 1100 N cho uᵀRu ≈ 1.2·10⁶, tương đương ‖e‖ ≈ 110 về mặt chi phí. Do đó lời giải tối ưu có chiết khấu sẽ chủ động hy sinh tracking **[suy luận định lượng, chưa mô phỏng]**. Martinsen tránh được vấn đề này vì chỉ phạt phần RL.

**Mặc định đề xuất:**
- τ = Mυ̇_d + C(υ_d)υ_d + D(υ_d)υ_d + u_RL;
- R chỉ phạt u_RL;
- basis lấy trên X = [z_η; z_υ; υ_d] ∈ R⁹, trong đó υ_d bị chặn. Cách này giữ đúng 45 số hạng critic và 99 ẩn của bài, nên Algorithm 2 không đổi;
- chạy thêm một ablation theo nghĩa đen ([z; p_d; ψ_d], RL thuần) và báo cáo sai số xác lập cùng lực thực tế.

Ghi lại thành giả định C1–C3.

**Câu hỏi còn lại cho thầy:** X(1..9) gồm chính xác những gì; có dùng feedforward mô hình như IJRNC 2024 không; R phạt toàn bộ τ hay chỉ phần RL.

## Kết luận

Ba câu hỏi khác nhau về bản chất:
- **K1 là khoảng trống do thông lệ.** Cả dòng bài không định lượng pha 1, nên tự chọn mặc định có lý do và ghi giả định là đủ trung thực với tinh thần phương pháp. Rủi ro thực sự là kỹ thuật: d phải được kích thích, T = 0.001 s làm ma trận hồi quy ill-conditioned, và `pinv(X'X)` bình phương số điều kiện. Tài liệu không cảnh báo những điều này.
- **K2 nhiều khả năng là lỗi ghi tham số.** Lý do không phải "trái thông lệ" mà là phép tính cực cho thấy (30, 0.1) không thể sinh ra hình của bài, và còn làm Theorem 1 gần như vô dụng.
- **K3 là chỗ diễn giải ảnh hưởng mạnh nhất đến kết quả.** Chọn RL thuần hay feedforward + RL quyết định sai số xác lập. Vì vậy K3 cần ablation hai nhánh dù thầy trả lời thế nào.

Ưu tiên khi hỏi là K2 và K3 trước, vì chúng thay đổi kết quả định tính. K1 xếp sau, vì chỉ ảnh hưởng tốc độ hội tụ và điều kiện số.

## Tin nhắn gửi thầy (sẵn sàng gửi)

> Em chào thầy ạ. Em đang tái lập bài "Bearing-based cascade formation scaling control for multiple perturbed surface vehicles via off-policy RL" (JFI 2026) và còn mấy điểm chưa rõ, mong thầy chỉ giúp em ạ:
>
> 1. Pha thu dữ liệu của Algorithm 2: behavior policy cụ thể là bộ điều khiển nào (PD, backstepping hay luật khác)? Nhiễu thăm dò có dạng gì và biên độ bao nhiêu? Tổng thời gian (hoặc số khoảng T = 0.001 s) thu dữ liệu là bao nhiêu? Dữ liệu thu một lần hay nhiều đợt? Ngưỡng dừng và số vòng lặp là bao nhiêu ạ?
> 2. Trong pha thu dữ liệu, nhiễu d có phải chính là δ = (3, −2.5, 3) + sin + 0.1·rand và được đo trực tiếp không, hay có bơm thêm kích thích vào kênh d ạ?
> 3. Ở mục 4.1, k_v = 0.1 có đúng không ạ? Theo em tính, với k_p = 30 thì hệ gần như không cản, không hội tụ dưới 1 s như trên hình. Ngoài ra, β(t) trong mô phỏng cụ thể là bao nhiêu ạ?
> 4. Vector X(1..9) dùng trong critic/actor gồm chính xác những thành phần nào ạ? Có gồm vị trí tham chiếu p_d, ψ_d hay là υ_d?
> 5. Bộ điều khiển có cộng feedforward mô hình τ_d = Mυ̇_d + Cυ_d + Dυ_d như bài IJRNC 2024 không ạ? Và R phạt toàn bộ τ hay chỉ phần RL ạ?
>
> Em cảm ơn thầy ạ.

---

## Cập nhật 26/11/2026: sau khi đọc toàn văn 6 bài Đức tải về

Phần này **thay thế** các kết luận "chưa xác minh" ở trên khi hai bên mâu thuẫn. Các bài đã đọc toàn văn: Modares–Lewis–Jiang TNNLS 2015; Lu et al. TNNLS 2021 (bài [3]); Nguyen–Dang–Pham–Dao IJRNC 2024 (bài [8]); Modares–Lewis Automatica 50 (2014) 1780–1792; Kiumarsi–Lewis–Jiang Automatica 78 (2017) 144–152; Zhang et al. Ocean Eng. 267 (2023) 113242 (bài [4]).

### K1: pha thu dữ liệu

| Bài | Chính sách hành vi | Nhiễu thăm dò | T, số mẫu | Nhiễu d | Kết quả |
| --- | --- | --- | --- | --- | --- |
| Modares 2015, Algorithm 2 và Remark 9–10 | "a fixed stable and exploring control policy u", không định lượng | Không nêu | F-16: T = 0.05 s; điều kiện N ≥ l₁ + m·l₂ + q·l₃; manipulator: học trong 25 s đầu rồi mới cập nhật | "d is the actual external disturbance … not under our control", không cần điều chỉnh, nhưng phải đo | Khởi tạo gain = 0; khoảng 5–7 vòng; giải bằng phương trình chuẩn Ŵ = (HHᵀ)⁻¹HY (80) |
| Modares 2014 Automatica | Không nêu | "A small probing noise is added to the control input" | T = 0.1 s | (không có d) | Khớp nghiệm ARE |
| Kiumarsi 2017 | **Luật ổn định đã biết u = −K₁x + e**, K₁ ≠ 0 | e_k = a·sin(1.009k) + cos²(0.538k) + sin(0.9k) + cos(100k), với a ∈ {0.2, 1, 4} | 25 mẫu mỗi vòng; nhiễu bật trong 400 bước | d đo được | Chứng minh nhiễu thăm dò **không làm lệch** nghiệm off-policy; 4–5 vòng |
| IJRNC 2024 (cùng nhóm) | Luật của chính bài: feedforward + RL | "a small exploratory signal containing sinusoids of varying frequencies … for the first 15 seconds" | (actor-critic online) | | Khớp đúng khối `noise` (t < 15 s) trong Simulink của repo |

Nhận xét:
- Algorithm 2 và Remark 9–10 của Paper A gần như **chép nguyên** từ Modares 2015. Dấu của y(t) trong (77) của Modares là y = ∫e^{−α(τ−t)}(−XᵀQX − uᵢᵀRuᵢ + γ²dᵢᵀdᵢ), tức **âm** của tích phân chi phí. Điều này xác nhận (58)–(59) của Paper A in sai dấu (PLAN B-5).
- Không bài nào bơm nhiễu vào kênh d. Họ đều dùng nhiễu thật, đo được.

### K2: hệ số bearing

| Bài | Dạng luật | Hệ số | Hội tụ |
| --- | --- | --- | --- |
| Lu 2021 (bài [3]), (7) | **Bậc nhất**, ở mức vận tốc ảo: α_zi = −R_zᵀ(ψ_i)·{K_i⁻¹·Σ P_g*[k_z(z_1i − z_1j) − R_z(ψ_j)α_zj]}, với K_i = Σ P_g* | k_z = 15; k_ψ = 25 (đồng thuận góc, luật (6)) | Sai số bearing ≈ 0 sau khoảng 10–15 s (Hình 7) |
| Zhang 2023 (bài [4]), (32) | **Bậc hai**, cùng dạng (13) của Paper A: M_i·Σ P_g*(k_p(p_i − p_j) + k_υf(h_iϑ_i − h_jϑ_j)) | k_p = 0.8, k_υf = 2 (follower), k_υl = 10 (leader); k_v/k_p = 2.5 | Ổn định khi k_p, k_v > 0 (38) |
| Paper A | Bậc hai | k_p = 30, k_v = 0.1; k_v/k_p = 0.003 | Theo tính toán: không hội tụ trong 40 s |

**Kết luận:** (30, 0.1) không có tiền lệ nào. Bài gần nhất cùng dạng luật (Zhang 2023) dùng k_v/k_p = 2.5. Bài gốc của tầng cao (Lu 2021) dùng luật bậc nhất, không có k_v.

### K3: đặc trưng và khâu bù mô hình

| Bài | Trạng thái mở rộng, cơ sở hàm | Khâu bù mô hình |
| --- | --- | --- |
| Modares 2015, F-16 | X = [e; r], r hằng số; ma trận P đủ 6×6, nên **u* chứa cả r** (feedforward học được); Q_T chỉ phạt e | Không, RL thuần |
| Modares 2015, manipulator | X = [e₁…e₄, r₁…r₄], r là các sin bị chặn; critic gồm lũy thừa chẵn đến bậc 4, actor gồm đa thức đến bậc 3; Q = 10I, R = 1, γ = 20 | Không |
| Modares 2014 | X = [e_d1, e_d2, x_d1, x_d2], x_d là dao động bị chặn; critic 10 số hạng bậc hai | Không |
| IJRNC 2024 (cùng nhóm, tiền thân) | Critic 12 số hạng chọn tay; Q = I₃, R = 1; **β_η = 2** | **Có**: τ = u + τ_d, τ_d = M·v̇_d + C(v_d)v_d + D(v_d)v_d (14)–(15). Phần kết luận ghi: "In the future … extend the low-level tracking controller with **model-free RL** algorithms" |

**Kết luận:**
- Paper A chính là bước "model-free" mà bài IJRNC 2024 hứa hẹn. Vì vậy, đúng tinh thần bài là **RL thuần, không có khâu bù mô hình**.
- Thông lệ của Modares là đưa trạng thái tham chiếu vào cơ sở hàm, nhưng chỉ khi tham chiếu **bị chặn**.
- Do đó chọn X(1..9) = [z_η; z_υ; υ_d]: υ_d bị chặn, đóng vai trò của r. Cách đọc đúng chữ [z; p_d; ψ_d] chạy như một biến thể so sánh.

### Các phát hiện phụ (giải quyết luôn vài mục của PLAN)

1. **B-1 (R_pᵀ trong (9)):** Lu (3) viết đúng z_2i = **R_zᵀ**(ψ₀){v_c + α_s[z_1i − c(z₁*)]}. Đã xác nhận.
2. **B-2 (tâm c):** Lu định nghĩa c(z₁*) = (1/n)·Σ_{i∈V} z₁ᵢ*, tức **tâm của đội hình đích, tính trên mọi tàu**, và s = (Σ_{i∈V}‖z₁ᵢ* − c‖²/n)^{1/2}. Leader tính được c vì z₁f* = −B_ff⁻¹B_fl·z₁l chỉ phụ thuộc vị trí leader. Điều này giải thích các mức lực ở Hình 9 và giữ được tính phân tán.
3. **B-14 (M1):** (62) của Paper A chính là luật dựa trên mô hình (27) của Lu: τ_ξi = −k_ξi·ξ_ei − m_ξi·f̄_ξi + m_ξi·α̇_ξi, với ξ_ei = ξ_i − α_ξi (sai số so với **vận tốc ảo**). Đây là cách hiểu (B). Lu dùng k = (20, 12, 5); Paper A ghi ζ = (0.5, 0.7, 0.5).
4. **Đồng thuận góc (14):** chép từ (6) của Lu. Trong đó tổng chỉ lấy trên **follower láng giềng**, d_i = 1 nếu tàu i nối trực tiếp với leader, và k_ψ = 25.
5. **β_η:** IJRNC 2024 dùng β_η = 2, đúng với mặc định đã chọn.

### Câu hỏi còn lại cho thầy (rút gọn từ 5 xuống 2)

Ba câu đã có câu trả lời từ tài liệu: X(1..9) và khâu bù mô hình (K3), d trong pha thu dữ liệu (K1). Còn lại:

> Em chào thầy ạ. Em đang mô phỏng lại bài "Bearing-based cascade formation scaling control…" (JFI 2026), còn hai điểm mong thầy xác nhận giúp em:
> 1. Ở mục 4.1, k_p = 30, k_v = 0.1 có đúng là giá trị trong code không ạ? Em tính thì với luật (13) và hai giá trị này, đội hình gần như không có cản (ζ ≈ 0.01), nên không thể hội tụ dưới 1 s như Hình 5. Bài [4] cùng dạng luật dùng k_v/k_p ≈ 2.5.
> 2. Pha thu dữ liệu của Algorithm 2 dùng chính sách hành vi nào (PD, hay luật có khâu bù mô hình như bài IJRNC 2024), nhiễu thăm dò dạng gì, và thu trong bao lâu ạ? (Em đang mặc định là tổng sin trong 15 s đầu, theo bài IJRNC.)
>
> Em cảm ơn thầy ạ.
