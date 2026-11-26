# Cách chọn gain trong luật bearing-based bậc hai (double-integrator), đặc biệt formation maneuver/scaling

Bối cảnh: bài JFI 363 (2026) 109193 (Duc, Phung, Dao) dùng p̈_i = −Σ P_{g*_ij}[k_p(p_i−p_j) + k_v(ṗ_i−ṗ_j)] với k_p = 30, k_v = 0.1. Mình đã đối chiếu với bản PDF cục bộ `Main_paper/Bearing based.pdf`. Mục 4.1 viết đúng: "the parameters of the designed input acceleration are given by: k_p = 30, k_υ = 0.1, the integral time interval T = 0.001s". Mục này cũng ghi các gain trên được dùng chung cho mọi phương pháp so sánh, trong đó có Method 2, tức [3] Lu et al.

## Câu hỏi 1. Bảng tổng hợp các bài báo: luật, gain, tỉ lệ k_v/k_p, điều kiện ổn định, thời gian hội tụ

### Takeaway
Mọi bài đã xác minh đều dùng k_v ≥ k_p hoặc cùng bậc với k_p (k_v/k_p từ khoảng 1 đến 4), tức hệ được thiết kế quanh mức cản tới hạn hoặc cản dư. Không bài nào dùng k_v/k_p ≈ 0.003 như bài JFI (30/0.1). Bài gốc Zhao & Zelazo dùng (k_p, k_v) = (0.5, 2) và (1, 3), và bearing error hội tụ trong khoảng 10–15 s.

### Bảng

| # | Bài báo (DOI/arXiv) | Dạng luật | Gain trong mô phỏng | k_v/k_p | Điều kiện ổn định trên gain | Hội tụ quan sát được |
|---|---|---|---|---|---|---|
| 1 | Zhao & Zelazo, "Translational and scaling formation maneuver control via a bearing-based approach", IEEE TCNS 4(3) 2017; arXiv:1506.05636 | (7) u_i = −Σ P_{g*_ij}[k_p(p_i−p_j)+k_v(v_i−v_j)] (leader vận tốc hằng) | k_p = 0.5, k_v = 2 (Fig. 4) | 4 | Mọi k_p, k_v > 0 (đa thức đặc trưng λ² + k_v μ λ + k_p μ, μ ∈ eig(B_ff)) | Bearing error về ≈0 trong khoảng ~10 s, trục thời gian 0–100 s (mình đọc trực tiếp từ Fig. 4b) |
| 1b | như trên | (10) u_i = −K_i⁻¹ Σ P_{g*_ij}[k_p(p_i−p_j)+k_v(v_i−v_j) − v̇_j] (có acceleration feedforward) | k_p = 1, k_v = 3 (Fig. 5, khối lập phương 3D) | 3 | Mọi k_p, k_v > 0 (λ = (−k_v ± √(k_v²−4k_p))/2) | Trục thời gian 0–80 s. Không đọc được thời điểm hội tụ chính xác từ text, nhưng theo cực ước tính thì ~10 s |
| 1c | như trên, luật có tích phân (disturbance) | thêm −k_I∫Σ P(p_i−p_j) | Không thấy giá trị số trong text đã trích | – | **0 < k_I < k_p k_v λ_min(B_ff)** (Routh–Hurwitz) | – |
| 2 | Lu & Sun, "Concise adaptive fault-tolerant formation scaling control for autonomous vehicles with bearing measurements", JMSE 12(8) 1407, 2024 (cùng tác giả đầu với [3]) | Backstepping/DSC: luật ảo **bậc nhất** cho vị trí α_zi = −R_zᵀ K_i⁻¹ Σ P_{g*_ij}[k_zi(z_1i−z_1j) − R_z(ψ_j)α_zj], sau đó bộ lọc bậc nhất và luật lực động lực học | K_z = 10·I, K_ψ = 26·I, k_u = 5, k_v = 10, k_r = 10, T = 0.1 | (không có k_v vị trí; k_z = 10 cho hằng số thời gian ~0.1 s) | "tồn tại tham số thích hợp" (UUB) | Mình không đọc được trục thời gian từ text |
| 3 | Vu et al., "Decentralized sliding-mode control laws for the bearing-based formation tracking problem", arXiv:2110.05153 | u_i = −k_1 v_i − k_2 sign(s_i), s_i = Σ P_{g*_ij}(v_i−v_j + k_1(p_i−p_j)) | k_1 = 0.5, k_2 = 2. Luật (13): k_1 = k_2 = k_3 = 1, k_4 = 0.5, k_5 = 2 | Mặt trượt có trọng số vận tốc 1, vị trí 0.5, tức tương đương k_v/k_p = 2 | k_2 > δ_2 + k_1 δ_1 | Hội tụ tiệm cận (không trích được số giây) |
| 4 | Tang, Cunha, Hamel, Silvestre, "Formation control of a leader–follower structure in 3D using bearing measurements", Automatica 128 (2021) 109567; arXiv:2110.08054 | double-integrator, bearing + relative velocity | k_p = 3, k_d = 10 | 3.3 | **k_d > 1 và k_p < 4 − 4/k_d²** (văn bản trích ra bị vỡ; đọc là "k_pi < 4 − k4²", nên mình suy ra 4/k_d²): có ràng buộc ghép k_p–k_d | "để đảm bảo tốc độ hội tụ nhanh" |
| 5 | arXiv:2609.19106 (2026), "Leader-follower formation control with prescribed convergence rates under bearing persistence of excitation", phần mở rộng double-integrator | luật (25) bậc hai | k_p = 0.8, k_v = 1.5 | 1.9 | (không trích) | (không trích) |
| 6 | Lu, Wen, Shen, Zhang, TNNLS 32(10) 4653–4664, 2021, DOI 10.1109/TNNLS.2020.3025807 (ref [3]) | **chưa xác minh.** Mình không lấy được toàn văn (IEEE paywall). Suy đoán: cấu trúc backstepping giống bài #2 (cùng tác giả đầu, bài #2 tự mô tả là mở rộng hướng này) | **chưa xác minh** | – | Formation errors UUB nếu augmented formation infinitesimally bearing rigid (abstract) | **chưa xác minh** |
| 7 | Zhang et al., "Bearing-based formation control for multiple underactuated ASVs with flexible size scaling", Ocean Eng. 2023, DOI 10.1016/j.oceaneng.2022.113242 | **chưa xác minh** (không có toàn văn) | **chưa xác minh** | – | – | – |
| 8 | Cheng & Huang, "Bearing-based formation with disturbance rejection", arXiv:2308.15260 | double-integrator + internal model | Bản arXiv không có mô phỏng | – | – | – |

### Cited Findings
- Zhao & Zelazo luật (7): "k_p and k_v are positive constant control gains". Đa thức đặc trưng det(λ²I + λk_v B_ff + k_p B_ff) = 0 cho λ = (−k_v μ ± √(k_v²μ² − 4k_p μ))/2, nên Re(λ) < 0 với mọi k_p, k_v, μ > 0 — [arXiv:1506.05636](https://arxiv.org/abs/1506.05636)
- Nhãn hình Fig. 4: "kp=0.5, kv=2". Nhãn hình Fig. 5: "kp=1, kv=3". Trục thời gian 0–100 s và 0–80 s. Trên Fig. 4b, tổng bearing error giảm từ ~7 về ~0 trong khoảng 10 s — [arXiv:1506.05636](https://arxiv.org/abs/1506.05636)
- Luật có tích phân: "0 < k_I < k_p k_v λ_min(B_ff)". Tác giả nhận xét: "the integral control gain must be bounded by λ_min(B_ff)" — [arXiv:1506.05636](https://arxiv.org/abs/1506.05636)
- Lu & Sun 2024: luật ảo vị trí bậc nhất α_zi với gain k_zi > 0. Mô phỏng chọn "Kψ = 26·I2, Kz = 10·I4, k_ui = 5, k_vi = 10, k_ri = 10, Tu = Tv = Tr = 0.1". Tham số mô hình tàu "selected as the same as those in [1]", với [1] là Lu et al. TNNLS 2021 — [JMSE 12(8):1407](https://www.mdpi.com/2077-1312/12/8/1407)
- Vu et al.: "control law (4) with parameters k1 = 0.5, k2 = 2", điều kiện "k2 > δ2 + k1δ1" — [arXiv:2110.05153](https://arxiv.org/abs/2110.05153)
- Tang et al.: "kpi = 3 and kdi = 10 … to ensure a fast convergence rate according to Theorem 3 while ensuring that inequalities kdi > 1 and kpi < 4 − k4² [vỡ ký tự] are satisfied" — [arXiv:2110.08054](https://arxiv.org/abs/2110.08054)
- arXiv:2609.19106: "kpi = 0.8 and kvi = 1.5 for controller (25)" — [arXiv:2609.19106](https://arxiv.org/abs/2609.19106)
- Lu et al. TNNLS 2021: abstract nói formation errors UUB nếu augmented formation infinitesimally bearing rigid, NN weights rút gọn thành một tham số trên mỗi kênh, và có auxiliary systems cho input saturation — [PubMed 33017292](https://pubmed.ncbi.nlm.nih.gov/33017292/); [DOI](https://doi.org/10.1109/TNNLS.2020.3025807)

### Inferences
- Thông lệ là k_v/k_p ∈ [~1, 4] với k_p, k_v cỡ 0.5–10. Mục đích là ζ ≈ 0.5–2 trên dải eig(B_ff), cho hội tụ trong vài đến vài chục giây.
- Các bài ASV theo hướng Lu (backstepping) dùng luật bearing **bậc nhất** ở mức kinematic với gain ~10. Kiểu luật này cho hội tụ dưới 1 s mà không cần k_v. Nếu bài JFI vẽ hình bằng code kế thừa kiểu này, hội tụ dưới 1 s không mâu thuẫn với hình, nhưng mâu thuẫn với luật (k_p = 30, k_v = 0.1) mà bài ghi. Đây là suy đoán.

### Gaps
- Mình không lấy được toàn văn Lu et al. TNNLS 2021 (ref [3]), Zhang et al. Ocean Eng. 2023, Li et al. TCAS-II 2023 (prescribed-time) và Su et al. CSL 2023. Gain của các bài này **chưa xác minh**.
- Zhao & Zelazo TAC 2016 (bearing rigidity, almost global) và CSM 2019 (survey): không kiểm tra được trong phiên này. Theo hiểu biết của mình, cả hai chủ yếu bàn luật single-integrator/gradient nên ít liên quan đến k_p/k_v (suy đoán). DOI theo trí nhớ, chưa kiểm tra: TAC 61(5) 2016 10.1109/TAC.2015.2459651; CSM 39(2) 2019 10.1109/MCS.2018.2888681; TCNS 4(3) 2017 10.1109/TCNS.2016.2570118.

## Câu hỏi 2. Có điều kiện nào ghép các gain (kiểu k_v² so với k_p λ_max), tương tự Theorem 1 của bài JFI?

### Takeaway
Luật bearing bậc hai tuyến tính thuần (Zhao & Zelazo) ổn định với mọi k_p, k_v > 0, nên không cần điều kiện ghép. Điều kiện ghép chỉ xuất hiện khi thêm thành phần: tích phân (0 < k_I < k_p k_v λ_min(B_ff)), sliding mode (k_2 > δ_2 + k_1δ_1), hoặc bearing-only/PE (Tang et al.: k_d > 1, k_p < 4 − 4/k_d²). Mình không tìm thấy bài nào có điều kiện giống hệt β ≤ min{√(k_p λ_max), (k_v − βk_v²/(4k_p))λ_min}.

### Cited Findings
- Zhao & Zelazo: Re(λ) < 0 "for any k_p, k_v, μ > 0". Riêng có tích phân: 0 < k_I < k_v k_p λ_min(B_ff) — [arXiv:1506.05636](https://arxiv.org/abs/1506.05636)
- Tang et al.: k_d > 1 và giới hạn trên của k_p phụ thuộc k_d — [arXiv:2110.08054](https://arxiv.org/abs/2110.08054)

### Inferences
- Điều kiện Theorem 1 của JFI có cấu trúc giống điều kiện kiểu k_I < k_p k_v λ_min. Trong đó β (tốc độ scaling của leader) đóng vai trò nhiễu/tham số, và vế (k_v − βk_v²/(4k_p))λ_min tỉ lệ với k_v. Với k_v = 0.1 và λ_min = 0.145, vế này chỉ khoảng 0.0145. Như vậy Theorem 1 đòi |β| ≤ ~0.0145 s⁻¹, rất chặt. Vế √(k_p λ_max) = √(30·2.45) ≈ 8.57 thì gần như không ràng buộc (mình tự tính từ công thức). Nếu bài dùng β lớn hơn 0.0145 trong mô phỏng thì chính Theorem 1 của bài bị vi phạm. Cần kiểm tra β trong mô phỏng.

### Gaps
- Mình chưa kiểm tra β(t) thực tế mà bài JFI dùng trong mô phỏng.

## Câu hỏi 3. Có bài nào dùng k_p = 30, k_v = 0.1 hoặc k_v thấp tương tự? k_p = 30, k_v = 0.1 có hợp lý, hay là lỗi đánh máy/hoán đổi?

### Takeaway
Mình không tìm thấy bài nào dùng k_v ≪ k_p như vậy. Về mặt phân tích, (30, 0.1) cho ζ ≈ 0.0035–0.014 và thời gian xác lập 2% khoảng 33–550 s. Hoán đổi thành (0.1, 30) cũng không cứu được: cực chậm ≈ −k_p/k_v = −0.0033, nên xác lập khoảng 1200 s. Hội tụ dưới 1 s trong hình chỉ khớp với gain kiểu k_p = 30, k_v ≈ 10 (một cặp mình tự giả định), hoặc với luật bậc nhất. Vì vậy "k_v = 0.1" nhiều khả năng là lỗi ghi tham số (sai giá trị, ví dụ 10 thành 0.1), hoặc hình không được sinh từ luật như đã ghi. Đây là suy đoán, chưa xác minh.

### Cited Findings
- Bài JFI ghi "k_p = 30, k_υ = 0.1" và dùng chung cho mọi phương pháp so sánh — PDF cục bộ `/home/d/projects/Paper_1/Main_paper/Bearing based.pdf`, mục 4.1; [DOI 10.1016/j.jfranklin.2026.109193](https://doi.org/10.1016/j.jfranklin.2026.109193)
- Gain tham chiếu trong tài liệu: (0.5, 2), (1, 3) [Zhao & Zelazo](https://arxiv.org/abs/1506.05636); (3, 10) [Tang et al.](https://arxiv.org/abs/2110.08054); (0.8, 1.5) [arXiv:2609.19106](https://arxiv.org/abs/2609.19106); k_1 = 0.5 với trọng số vận tốc 1 [Vu et al.](https://arxiv.org/abs/2110.05153)

### Inferences (mình tự tính với s² + k_v λ s + k_p λ = 0, λ ∈ {0.145, 1, 1.40, 2.45}; T_s ≈ 4/|Re cực chậm|)
- (k_p, k_v) = (30, 0.1): ζ = 0.0035 / 0.0091 / 0.0108 / 0.0143. T_s = 552 / 80 / 57 / 33 s. Hệ dao động gần như không cản. Không thể hội tụ dưới 1 s.
- (0.1, 30), tức hoán đổi: cực chậm Re ≈ −0.0033 với mọi λ, T_s ≈ 1200 s. Giả thuyết hoán đổi bị loại.
- (0.5, 2) và (1, 3) của Zhao & Zelazo: T_s ≈ 14–28 s và 10–18 s. Khớp với Fig. 4 (~10 s).
- (30, 10), cặp mình tự giả định: T_s ≈ 0.8–1.1 s cho λ ≥ 1, và ~5.5 s cho λ = 0.145. Đây là cặp gần nhất với "hội tụ dưới 1 s" trên các mode chính.
- Kết luận suy đoán: k_p = 30, k_v = 0.1 không hợp lý so với thông lệ và với chính hình của bài. Khả năng cao nhất là lỗi ghi k_v (một giá trị cỡ 10 bị ghi thành 0.1, hoặc 0.1 là tham số khác như T hay α = 0.1). Khả năng thứ hai là hình được sinh từ cấu trúc khác, ví dụ luật vận tốc bậc nhất kiểu Lu (k_z ~ 10), hoặc có thêm thành phần cản/feedforward không ghi trong bài. Khi replicate nên thử k_v ∈ {5, 10, 2√(k_p λ)} và ghi rõ đây là sai khác so với bài.

### Gaps
- Mình không truy cập được code hay dữ liệu gốc của bài JFI. Chưa kiểm tra việc lớp dynamic/RL bên trong (inner loop) có thêm cản hiệu dụng, khiến tracking không còn "perfect", hay không.
- Mình chưa xác minh gain của Lu et al. 2021 [3]. Bài JFI nói các gain được "set equally for every method", nên nếu [3] dùng luật bậc nhất thì việc gán k_p, k_v cho Method 2 càng khó hiểu.
