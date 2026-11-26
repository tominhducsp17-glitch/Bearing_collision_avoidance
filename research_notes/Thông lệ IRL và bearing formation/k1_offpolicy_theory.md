# Thông lệ thu thập dữ liệu (pha 1) trong off-policy IRL và off-policy H∞ / zero-sum cho hệ liên tục

Phạm vi: các bài nền tảng về off-policy IRL (LQR, tracking, H∞), dùng để chọn thiết kế pha 1 khi tái lập Algorithm 2 của Duc, Phung, Dao (J. Franklin Inst. 363 (2026) 109193). Bài này không nêu chi tiết pha 1. Các thiết lập của nó: T = 0.001 s, α = 0.1, γ = 5, Q = 100I, R = I, critic 45 số hạng bậc hai, actor và disturber tuyến tính theo 9 trạng thái, 99 ẩn mỗi agent, trọng số ban đầu bằng 0.

Mức độ truy cập nguồn (đọc trước):
- **Đọc được toàn văn:**
  - Luo, Wu, Huang (arXiv 1311.6107).
  - Chương sách của Modares, Kiumarsi, Vamvoudakis, Lewis (2018). Chương này trình bày lại đúng Algorithm 2 của Modares–Lewis–Jiang 2015, nhưng không có phần mô phỏng.
  - Sách *Robust Adaptive Dynamic Programming* của Y. Jiang & Z.-P. Jiang (Wiley 2017). Chương 2 trình bày lại thuật toán và ví dụ của bài Automatica 2012.
  - Survey của Kiumarsi và cộng sự (TNNLS 2018).
  - Hai preprint arXiv về sau: 2401.12882 và 2001.07355.
- **Không truy cập được toàn văn:**
  - Modares–Lewis–Jiang TNNLS 2015 (paywall IEEE; luận án UTA trả về 403).
  - Modares & Lewis Automatica 2014.
  - Song–Lewis–Wei–Zhang TCYB 2016.
  - Kiumarsi–Lewis–Jiang Automatica 2017 (bản AM trên ScienceDirect trả về 403).
  - Bản gốc Jiang & Jiang Automatica 2012 (chỉ có bản Studocu, bị paywall).
- Mọi số liệu của nhóm "không truy cập được" ghi bên dưới đều đi qua nguồn trung gian và được đánh dấu rõ.

## 1. Bảng tổng hợp theo từng bài (thông tin đã xác minh)

### Takeaway
Thông lệ chung trong các bài:
- Behavior policy là một luật "ổn định + có nhiễu thăm dò". Luật này thường là K0 = 0 khi hệ hở đã ổn định, một gain ổn định đã biết, hoặc tín hiệu ngẫu nhiên thuần.
- Nhiễu thăm dò có hai dạng phổ biến: tổng nhiều sinusoid (tới 100 tần số ngẫu nhiên), hoặc nhiễu ngẫu nhiên đều.
- Số mẫu N lấy khoảng 2–16 lần số ẩn. Dữ liệu thu một lần, rồi lặp LS đến ngưỡng ‖ΔW‖ ≤ 10⁻⁷ (Luo; δ-PI) hoặc |ΔP| ≤ 5·10⁻⁴ (Jiang).
- Kiểm chứng bằng cách so với nghiệm ARE/GARE (lệnh CARE).
- Với H∞: nhiễu d là tín hiệu đo được và phải có mặt trong dữ liệu, kể cả khi nó là nhiễu ngoài không điều khiển được.

### Cited Findings

**(a) Jiang & Jiang, Automatica 48(10):2699–2704, 2012. DOI 10.1016/j.automatica.2012.06.096**
Nguồn đọc được là sách RADP (Jiang & Jiang 2017), Ch. 2, §2.3–2.4, trình bày lại thuật toán và ví dụ động cơ diesel. Chưa đối chiếu trực tiếp với bản Automatica.
- **Off-policy ADP (Algorithm 2.3.10):**
  - Bước khởi tạo là "Find K0 such that A − BK0 is Hurwitz".
  - Thu dữ liệu bằng u0 = −K0x + e, "where K0 is stabilizing and e is the exploration noise", cho tới khi điều kiện rank thỏa.
  - Sau đó lặp off-policy trên cùng dữ liệu cho tới khi |Pk − Pk−1| ≤ ε.
  - Nguồn: [Jiang & Jiang, RADP book, Ch.2](http://library.sadjad.ac.ir/opac/temp/19352.pdf)
- **Behavior policy không bắt buộc là tuyến tính (Remark 2.3.11):**
  - u0 có thể là luật phản hồi phi tuyến, "or even an open-loop control policy".
  - Yêu cầu là quỹ đạo bị chặn, không có finite escape, và điều kiện rank thỏa.
  - Nguồn: [RADP book](http://library.sadjad.ac.ir/opac/temp/19352.pdf)
- **Điều kiện rank và quy tắc kinh nghiệm:**
  - rank(Θ) = n(n+1)/2 + mn.
  - Quy tắc: "use data from at least twice as many sampling intervals as the unknowns", tức lk ≥ n(n+1) + 2mn.
  - Nếu nhiễu là tuần hoàn thì "the length of any sampling interval should be sufficiently larger than the period of the noise".
  - Rank "can be checked computationally, but not analytically" (Assumption 2.3.1).
  - Nguồn: [RADP book](http://library.sadjad.ac.ir/opac/temp/19352.pdf)
- **Chọn nhiễu (Remark 2.2.1):**
  - "Choosing the exploration noise is not a trivial task". Các dạng đã dùng: random noise, exponentially decreasing probing noise.
  - Mô phỏng của sách dùng "sum of sinusoidal signals with different frequencies".
  - Nguồn: [RADP book](http://library.sadjad.ac.ir/opac/temp/19352.pdf)
- **Ví dụ off-policy (động cơ diesel turbocharged có EGR, bậc 6, m = 2):**
  - K0 = 0₂ₓ₆ vì hệ hở ổn định tiệm cận. Q = diag(100,0,0,0,0,100), R = I₂.
  - Trạng thái đầu chọn ngẫu nhiên quanh gốc.
  - Trong t ∈ [0, 1] s bơm e = Σ₁¹⁰⁰ sin(ωₖt), với ωₖ ngẫu nhiên đều trên [−50, 50].
  - "State and input information is collected over each interval of 0.1s".
  - PI bắt đầu tại t = 1 s và hội tụ sau 16 vòng với |Pk − Pk−1| ≤ 0.0005.
  - P10 và K10 khớp nghiệm ARE đến khoảng 3–4 chữ số.
  - Nguồn: [RADP book §2.4.2](http://library.sadjad.ac.ir/opac/temp/19352.pdf)
- **Ví dụ on-policy (hệ bậc 3), dùng làm đối chiếu:**
  - K = [0 0 0], δt = 0.1, ε = 0.5×10⁻⁴, ode45 với bước tối đa 0.001.
  - e = 2 sin(100t), tức chu kỳ khoảng 0.063 s < δt.
  - Mỗi vòng dùng 10 khoảng mẫu. Hội tụ sau 6 vòng, vào khoảng t ≈ 6.5 s.
  - Kiểm chứng bằng cách so với P*, K* của ARE.
  - Nguồn: [RADP book §2.4.1](http://library.sadjad.ac.ir/opac/temp/19352.pdf)
- **Chương nonlinear (RTAC-like, 4 trạng thái):** nhiễu là "sum of sinusoidal signals with six different frequencies", hội tụ sau 19 vòng. Nguồn: [RADP book §3](http://library.sadjad.ac.ir/opac/temp/19352.pdf)
- **Chương 4 (global ADP):** e = 0.01(sin 10t + sin 3t + sin 100t), tắt sau vòng thứ 4. Ngưỡng |pᵢ − pᵢ₋₁| ≤ 10⁻³. Nguồn: [RADP book §4](http://library.sadjad.ac.ir/opac/temp/19352.pdf)

**(b) Modares, Lewis, Jiang, IEEE TNNLS 26(10):2550–2562, 2015. DOI 10.1109/TNNLS.2015.2441749. Đây là ref [39] của bài cần tái lập.**
Không đọc được phần mô phỏng của bài báo. Algorithm 2 đọc được qua chương sách của Modares, Kiumarsi, Vamvoudakis, Lewis (2018), DOI 10.1016/B978-0-12-812976-0.00018-X. Chương này trình bày lại cùng phương pháp, cùng chữ dùng.
- **Nguồn gốc cụm "stable and exploring":**
  - Câu gốc trong chương: "The fixed control policy u should be a stable and exploring control policy".
  - "the disturbance input w is the actual external disturbance that comes from an external source and is not under our control".
  - Ưu điểm được nêu: "the disturbance input that is applied to the system does not require to be adjustable".
  - Nguồn: [Modares et al. 2018 chapter, §14.2.2](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)
- **Phase 1:** "Apply a fixed control policy u to the system and collect required system information about the state, control input and disturbance at N different sampling intervals T". Như vậy d được đo và ghi lại. Nguồn: [chapter, Algorithm 2](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)
- **Phương trình Bellman off-policy có chiết khấu:**
  - e^{−αT}V(X(t+T)) − V(X(t)) = ∫ e^{−α(τ−t)}(−XᵀQX − uⱼᵀRuⱼ + γ²dⱼᵀdⱼ)dτ + ∫ e^{−α(τ−t)}(−2uⱼ₊₁ᵀR(u − uⱼ) + 2γ²dⱼ₊₁ᵀ(d − dⱼ))dτ.
  - V, uⱼ₊₁, dⱼ₊₁ được giải đồng thời bằng LS.
  - Số mẫu: N ≥ l1 + m×l2 + q×l3, tức số phần tử độc lập của Ŵ. Nghiệm Ŵ = (HHᵀ)⁻¹HY.
  - Nguồn: [chapter §14.2.3](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)
- **Về α:** "The use of the discount factor is essential", vì phần feedforward không tiến về 0. Bài TNNLS tìm một cận trên cho α để bảo đảm ổn định cục bộ của sai số bám. Nguồn: [chapter](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf); [Scholars' Mine abstract](https://scholarsmine.mst.edu/ele_comeng_facwork/2835)
- **Bằng chứng gián tiếp (chưa xác minh) về setup mô phỏng, lấy từ một preprint IET (arXiv 2001.07355):**
  - Preprint nói nó dựng "in line with that in [30]", với [30] có vẻ là bài Modares 2015 vì có cận trên discount factor và cập nhật LS.
  - Các số của preprint: "T = .001s", R = 1, Q = diag(9.9,0,…), discount 0.25, d = 0.1e^{−0.1t}sin(0.1t), αd = 1.5 rồi 2.2.
  - Không rõ các số này là của Modares 2015 hay do preprint tự chọn.
  - Nguồn: [arXiv 2001.07355](https://arxiv.org/pdf/2001.07355v1)
- **Bằng chứng gián tiếp (chưa xác minh) từ δ-PI tracking (arXiv 2401.12882):**
  - Bài này dùng ví dụ phi tuyến 2 trạng thái + tham chiếu (r̈ = −2.25r), Q = 10I, R = 1, γ = 5, α = 0.1, critic 45 số hạng, actor và disturber 24 số hạng.
  - Ví dụ này rất giống ví dụ phi tuyến thường gán cho Modares 2015. Trùng ngẫu nhiên với γ = 5, α = 0.1 của bài cần tái lập.
  - Pha 1: X0 = [−1, 1, 1, 0]ᵀ, "random signals are leveraged as behavior policies" cho cả u và d (Fig. 2: "Behavior policies u and d for data sampling"), T = 0.1 s, N = 1000, tức khoảng 100 s.
  - Pha 2: W⁰ = 0, ngưỡng ‖Wⁱ⁺¹ − Wⁱ‖ < 10⁻⁷, 96 vòng (Newton bước 0.3).
  - Nguồn: [arXiv 2401.12882](https://arxiv.org/pdf/2401.12882)

**(c) Luo, Wu, Huang, IEEE TCYB 45(1):65–76, 2015. DOI 10.1109/TCYB.2014.2319577, arXiv 1311.6107. Đọc được toàn văn.**
- **Về d:**
  - Trong off-policy, "the control u and disturbance w can be arbitrarily on U and W … thus disturbance w does not required to be adjustable".
  - Step 1 của Algorithm 2: "Collect real system data (x_m, u_m, w_m)". Như vậy w được đo.
  - Dữ liệu dùng lại cho mọi vòng: "no extra data is required".
  - Nguồn: [arXiv 1311.6107](https://arxiv.org/pdf/1311.6107)
- **Điều kiện rank (Remark 4):**
  - Z^{(i)} phải full column rank. Điều này "depends on the richness of the sampling data set S_M and its size M".
  - Gợi ý: tăng M, "starting from different initial states", và dùng "random noises, sinusoidal function noises with enough frequencies".
  - PE "would be nice … but is not a necessity". Việc chọn tín hiệu và M "are generally experience-based".
  - Nguồn: [arXiv 1311.6107](https://arxiv.org/pdf/1311.6107)
- **Ví dụ F-16 tuyến tính (3 trạng thái, d là gió giật):**
  - R = 1, γ = 5. Nghiệm ARE tính bằng MATLAB CARE.
  - Critic có L = 6 số hạng, θ⁰ = 0, ξ = 10⁻⁷, Δt = 0.1 s.
  - M = 100 mẫu (khoảng 16.7 lần số ẩn), "random noise in interval [0,0.1] as input signals".
  - Hội tụ về θ* của ARE sau 5 vòng. Với Δt = 0.2, 0.3, 0.4, 0.5 s vẫn hội tụ sau 5 vòng, nên tác giả kết luận "insensitive to the parameter Δt".
  - Nguồn: [arXiv 1311.6107 §VI-A](https://arxiv.org/pdf/1311.6107)
- **Ví dụ RTAC phi tuyến (4 trạng thái):**
  - R = 1, γ = 6, L = 20, θ⁰ = 0, ξ = 10⁻⁷, Δt = 0.033 s.
  - M = 300 (15 lần số ẩn), nhiễu ngẫu nhiên trong [0, 0.5]. Hội tụ sau 3 vòng.
  - Kiểm chứng bằng mô phỏng vòng kín với w = 0.2r₁(t)e^{−0.2t}cos t và tỷ số suy giảm r_d → 3.7024 < γ.
  - Nguồn: [arXiv 1311.6107 §VI-B](https://arxiv.org/pdf/1311.6107)
- **Chỗ mơ hồ:** bài viết "random noise … as input signals" nhưng không nói rõ là cho cả u lẫn w hay chỉ cho u. Behavior policy là nhiễu ngẫu nhiên thuần, không có phản hồi trạng thái. Nguồn: [arXiv 1311.6107](https://arxiv.org/pdf/1311.6107)

**(d) Modares & Lewis, Automatica 50(7):1780–1792, 2014. DOI 10.1016/j.automatica.2014.05.011**
- Không truy cập được toàn văn (Semantic Scholar: CLOSED). Đây là bài IRL tracking on-policy/partially-unknown có input bị chặn, không phải H∞ off-policy. Không có số liệu pha 1. Nguồn: [Semantic Scholar record](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.automatica.2014.05.011)

**(e) Song, Lewis, Wei, Zhang, IEEE TCYB 46(5):1041–1050, 2016. DOI 10.1109/TCYB.2015.2421338**
- Chỉ đọc được tóm tắt. Bài cho rằng khi có nhiễu chưa biết, off-policy IRL "may not converge or may be biased", nên thêm "disturbance compensation controller" và chứng minh UUB. Nghĩa là bài này xét trường hợp d không được mô hình hóa trong phương trình Bellman, khác với Modares và Luo. Nguồn: [AMiner](https://www.aminer.cn/pub/55465ea40cf2939c2feebde0/off-policy-actor-critic-structure-for-optimal-control-of-unknown-systems-with)

**(f) Kiumarsi, Lewis, Jiang, Automatica 78:144–152, 2017 (hệ rời rạc). DOI 10.1016/j.automatica.2016.12.009**
- Không đọc được toàn văn. Tóm tắt (qua ResearchGate/kết quả tìm kiếm) nói: không có bias do thêm probing noise vào điều khiển để duy trì PE, và hội tụ "insensitive to probing noise". Nguồn: [ResearchGate record](https://www.researchgate.net/publication/312870994_H_control_of_linear_discrete-time_systems_Off-policy_reinforcement_learning)
- **Theo survey 2018, Algorithm 5 (off-policy GARE, DT):**
  - Bắt đầu với "admissible control policy u(k) = −K1x(k) + e(k) where e(k) is probing noise".
  - Fig. 2: "The behavior disturbance policy is the actual disturbance from the environment that cannot be specified".
  - Nguồn: [Kiumarsi et al. survey 2018](https://par.nsf.gov/servlets/purl/10078417)

**(g) Survey Kiumarsi, Vamvoudakis, Modares, Lewis, IEEE TNNLS 29(6):2042–2062, 2018. DOI 10.1109/TNNLS.2017.2773458**
- Off-policy "take into account the effect of probing noise needed for exploration". Dữ liệu từ behavior policy "can be obtained offline". Nguồn: [survey](https://par.nsf.gov/servlets/purl/10078417)
- Algorithm 12 (off-policy IRL cho HJI) bắt đầu từ "admissible policy u0". Phương trình được giải "for a fixed control policy u(t) and the actual disturbance". Nguồn: [survey §III-E](https://par.nsf.gov/servlets/purl/10078417)
- Hướng mở được nêu: "existing RL-based H∞ controllers require the disturbance to be measured during learning". Nguồn: [survey, Conclusion](https://par.nsf.gov/servlets/purl/10078417)
- Survey không đưa ra quy tắc định lượng nào cho thiết kế nhiễu, số mẫu hay biên độ (đã kiểm tra bằng tìm từ khóa trong toàn văn). Nguồn: [survey](https://par.nsf.gov/servlets/purl/10078417)

**Bảng tóm tắt**

| Bài | Behavior u (pha 1) | Nhiễu thăm dò | d khi thu dữ liệu | T | N (N/ẩn) | Tổng thời gian | Dừng / số vòng | Kiểm chứng |
|---|---|---|---|---|---|---|---|---|
| Jiang & Jiang 2012 (qua sách RADP) | −K0x + e, K0 = 0 (hệ hở ổn định) | Σ100 sin(ωₖt), ωₖ ~ U[−50, 50] | không có d (LQR) | 0.1 s (theo sách) | ~10 khoảng trong 1 s? (xem Gaps) / 33 ẩn | 1 s, thu một lần, không reset | \|ΔP\| ≤ 5e−4, 16 vòng | so với P*, K* của ARE |
| Luo–Wu–Huang 2015, F-16 | nhiễu ngẫu nhiên U[0, 0.1] | random | đo w_m; tín hiệu w cụ thể không nêu rõ | 0.1 s (thử 0.1–0.5) | M = 100 / 6 ẩn (~17×) | ~10 s (suy ra) | ξ = 1e−7, 5 vòng | so với θ* từ CARE |
| Luo–Wu–Huang 2015, RTAC | nhiễu ngẫu nhiên U[0, 0.5] | random | như trên | 0.033 s | M = 300 / 20 ẩn (15×) | ~10 s (suy ra) | ξ = 1e−7, 3 vòng | tỷ số L2 r_d = 3.70 < γ = 6 |
| Modares–Lewis–Jiang 2015 | "stable and exploring" cố định | không xác minh được | nhiễu ngoài thực, đo được | không xác minh (T = 0.001? xem 2001.07355) | N ≥ số ẩn | không xác minh | không xác minh | không xác minh |
| δ-PI (arXiv 2401.12882), ví dụ kiểu Modares | tín hiệu ngẫu nhiên | random | d cũng là tín hiệu ngẫu nhiên chủ động | 0.1 s | 1000 / 93 ẩn (~11×) | 100 s | ‖ΔW‖ < 1e−7, 96 vòng (Newton bước 0.3) | mô phỏng L2-gain |
| Kiumarsi 2017 (DT) | −K1x + e, admissible | probing e | nhiễu thực, không chỉ định | — | không xác minh | — | ‖ΔK‖ ≥ ε | GARE (theo tóm tắt và survey) |
| Song 2016 | không xác minh | không xác minh | nhiễu chưa biết, bù bằng bộ bù nhiễu | không xác minh | — | — | UUB | không xác minh |

### Inferences
- Cụm "stable and exploring behavior policy plus probing noise" trong bài cần tái lập gần như chắc chắn chép từ Modares–Lewis–Jiang 2015 hoặc chương sách 2018. Các bài gốc này cũng không định lượng pha 1. Vì vậy, việc thiếu chi tiết là "thông lệ" của dòng bài này chứ không riêng bài cần tái lập.
- Với 99 ẩn mỗi agent (45 critic + 9m actor + 9q disturber, khớp với m = q = 3):
  - Quy tắc của Jiang (≥ 2 lần số ẩn) cho N ≥ 198.
  - Thực hành của Luo và δ-PI là khoảng 10–17 lần, tức N ≈ 1000–1700.
  - Với T = 0.001 s, N = 1000–2000 khoảng chỉ ứng với 1–2 s dữ liệu.
  - (suy luận)
- Với T = 0.001 s, điều kiện của Jiang ("khoảng mẫu lớn hơn nhiều so với chu kỳ nhiễu tuần hoàn") đòi tần số trên khoảng 6000 rad/s, không thực tế. Khi đó tính đa dạng giữa các hàng của ma trận hồi quy chủ yếu đến từ việc quỹ đạo trạng thái và tín hiệu thay đổi giữa các khoảng. Cách làm hợp lý hơn:
  - dùng sinusoid tần số vừa phải hoặc nhiễu ngẫu nhiên giữ mức theo từng khoảng;
  - và/hoặc nối nhiều đoạn quỹ đạo từ các trạng thái đầu khác nhau, đúng như gợi ý "different initial states" của Luo.
  - Vì T rất nhỏ, mỗi hàng có biên độ nhỏ (∝ T), nên điều kiện số của ρ1ᵀρ1 cần được kiểm tra.
  - (suy luận)
- **Trọng số ban đầu bằng 0 kéo theo uⱼ = dⱼ = 0 ở vòng 0:**
  - Khối hồi quy của actor là ∫ e^{−α(τ−t)} 2R(u − 0)⊗φ dτ, nên u phải khác 0 và kích thích đủ.
  - Khối của disturber là ∫ e^{−α(τ−t)} 2γ²(d − 0)⊗φ dτ. Nếu d ≡ 0 khi thu dữ liệu, khối này bằng 0 và ρ1 mất hạng ngay từ vòng đầu.
  - Do đó khi tái lập, d phải có mặt, được đo và kích thích đủ trong pha 1. Có thể dùng một tín hiệu nhiễu biết trước bơm vào kênh d, như δ-PI làm.
  - Ở các vòng sau, d − dⱼ = d − Ŵ_dφ(x) cũng cần độc lập tuyến tính với φ(x). Nếu d chỉ là hàm của x hoặc là hằng thì không đạt.
  - (suy luận từ cấu trúc phương trình trong chương Modares 2018 và bài Luo)
- K0 = 0 hay θ⁰ = 0 là lựa chọn phổ biến (Jiang, Luo, δ-PI) và hợp lệ khi hệ hở ổn định. Theo Remark 2.3.11 của Jiang, behavior policy chỉ cần giữ quỹ đạo bị chặn. Nếu hệ của bài cần tái lập không ổn định hở (ví dụ động lực vị trí/tư thế quadrotor), behavior policy nên là một bộ điều khiển ổn định đã biết (PD hoặc LQR thô) cộng nhiễu. (suy luận / suy đoán)
- Luo chỉ ra off-policy H∞ tương đương phương pháp Newton nên chỉ hội tụ cục bộ: θ⁰ cần nằm trong lân cận nghiệm và việc chọn θ⁰ "experience-based". Trọng số 0 không được bảo đảm lý thuyết cho mọi hệ. Nguồn: [arXiv 1311.6107, Remark 5](https://arxiv.org/pdf/1311.6107)

### Gaps
- Không đọc được phần mô phỏng của Modares–Lewis–Jiang TNNLS 2015, là ref [39] và ưu tiên cao nhất. Dạng nhiễu, biên độ, T, N, số vòng và cách tạo d trong bài này đều chưa xác minh. Số T = 0.001 s chỉ là suy đoán từ một preprint nói rằng nó dựng "in line with [30]". Nên lấy bản IEEE hoặc luận án Modares (UTA 2015, mavmatrix, bị chặn 403 với bot).
- Sách RADP ghi "each interval of 0.1s" trong 1 s, tức khoảng 10 khoảng, ít hơn 33 ẩn (21 + 12) của bài diesel. Điều này mâu thuẫn với chính quy tắc lk ≥ 2 lần số ẩn của sách. Có thể bản Automatica 2012 dùng 0.01 s (chưa xác minh / suy đoán), cần đối chiếu bản gốc.
- Song 2016, Modares & Lewis 2014 và Kiumarsi 2017: không có toàn văn, nên không có số liệu pha 1.
- Không tìm được review hay tutorial 2018–2025 nào đưa ra hướng dẫn định lượng về biên độ nhiễu so với tín hiệu điều khiển. Survey 2018 chỉ nói định tính.

## 2. Nhiễu d trong phương trình Bellman off-policy H∞

### Takeaway
Trong cả Modares (2015/2018), Luo (2015) và Kiumarsi (2017), d là nhiễu thực từ môi trường. Nó không cần điều chỉnh được nhưng phải đo được và được ghi cùng x, u. Survey 2018 coi việc phải đo d là hạn chế còn mở. Hướng không đo d (Song 2016) phải thêm bộ bù nhiễu và chỉ đạt UUB. Trong mô phỏng, cách thực tế là bơm một d biết trước, ngẫu nhiên hoặc nhiều tần số, để khối disturber đủ hạng.

### Cited Findings
- Modares: "the disturbance input w is the actual external disturbance … not under our control"; pha 1 thu "state, control input and disturbance". Nguồn: [chapter](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)
- Luo: thu (x_m, u_m, w_m). w có thể là "arbitrarily on W". Một nhược điểm của on-policy là cần d "adjustable", điều "usually impractical". Nguồn: [arXiv 1311.6107](https://arxiv.org/pdf/1311.6107)
- Survey: "existing RL-based H∞ controllers require the disturbance to be measured during learning". Nguồn: [survey](https://par.nsf.gov/servlets/purl/10078417)
- δ-PI: cả u và d trong pha 1 là "random signals … as behavior policies". Nguồn: [arXiv 2401.12882](https://arxiv.org/pdf/2401.12882)
- Song 2016: với nhiễu chưa biết, off-policy IRL có thể "biased", nên thêm bộ bù nhiễu. Nguồn: [AMiner](https://www.aminer.cn/pub/55465ea40cf2939c2feebde0/off-policy-actor-critic-structure-for-optimal-control-of-unknown-systems-with)

### Inferences
- Không bài nào đọc được phát biểu riêng một điều kiện rank cho khối disturber. Rank chỉ được nêu chung cho toàn ma trận Z hay H, với yêu cầu N ≥ l1 + m·l2 + q·l3. Từ cấu trúc phương trình, khối disturber chỉ đủ hạng khi d ≠ 0 và d giàu tần số (xem mục 1). (suy luận)

### Gaps
- Chưa xác minh được bài Modares 2015 dùng tín hiệu d cụ thể nào trong pha 1.

## 3. Rank/PE, số vòng, ngưỡng dừng, discount, kiểm chứng

### Takeaway
- Rank được kiểm tra bằng tính toán, không có điều kiện giải tích.
- Ngưỡng dừng thường là 10⁻⁷ trên ‖ΔW‖ (Luo, δ-PI) hoặc 5·10⁻⁴ trên |ΔP| (Jiang).
- Số vòng: 3–5 (Luo), 16 (Jiang), 96 (δ-PI với bước Newton tắt dần).
- Kiểm chứng chuẩn là so với nghiệm ARE/GARE (CARE) cho hệ tuyến tính. Với hệ phi tuyến, kiểm chứng bằng tỷ số L2 r_d(t) < γ.
- Discount α = 0.1 xuất hiện trong δ-PI với γ = 5, giống bài cần tái lập.

### Cited Findings
- Jiang: rank "can be checked computationally, but not analytically"; ε cân bằng giữa thăm dò và khai thác (Remark 2.3.5). Nguồn: [RADP book](http://library.sadjad.ac.ir/opac/temp/19352.pdf)
- Luo: ξ = 10⁻⁷; F-16 hội tụ sau 5 vòng, RTAC sau 3 vòng; so với CARE; r_d = 3.7024 < 6. Nguồn: [arXiv 1311.6107](https://arxiv.org/pdf/1311.6107)
- δ-PI: α = 0.1, γ = 5, Q = 10I; ngưỡng 10⁻⁷; 96 vòng. Nguồn: [arXiv 2401.12882](https://arxiv.org/pdf/2401.12882)
- Modares: dừng khi |vⱼ₊₁ − vⱼ| ≤ ε và |wⱼ₊₁ − wⱼ| ≤ ε (Algorithm 3/4 trong chương); α > 0 "essential". Nguồn: [chapter](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)

### Inferences
- **Đề xuất pha 1 cho bài tái lập, ở mức "theo thông lệ" (suy luận):**
  - Behavior policy: một bộ điều khiển ổn định đã biết, cộng nhiễu tổng nhiều sinusoid, khoảng 10–100 tần số ngẫu nhiên trong vài đến vài chục rad/s, biên độ cỡ 10–50% tín hiệu điều khiển danh định. Có thể thay bằng nhiễu ngẫu nhiên.
  - Kênh d: một tín hiệu đo được và giàu tần số, độc lập với nhiễu trên u.
  - Số mẫu: N ≥ 2×99, khuyến nghị khoảng 1000 khoảng hoặc hơn. Với T = 0.001 s, đó là ≥ 1 s dữ liệu, có thể gồm nhiều đoạn từ các trạng thái đầu khác nhau.
  - Kiểm tra rank(ρ1) = 99 và số điều kiện của ρ1ᵀρ1 trước khi lặp.
  - Dừng khi ‖ΔŴ‖ ≤ 10⁻⁶ đến 10⁻⁷.
  - Nếu có thể tuyến tính hóa, đối chiếu với nghiệm GARE có chiết khấu: AᵀP + PA − αP + Q − PBR⁻¹BᵀP + γ⁻²PDDᵀP = 0.

### Gaps
- Không có nguồn nào nêu biên độ nhiễu so với tín hiệu điều khiển theo dạng tỷ lệ. Các biên độ đã biết là tuyệt đối: 0.1 và 0.5 (Luo), 2 (Jiang on-policy), tổng 100 sin biên độ 1 (Jiang off-policy), 0.01 (Jiang global ADP).
