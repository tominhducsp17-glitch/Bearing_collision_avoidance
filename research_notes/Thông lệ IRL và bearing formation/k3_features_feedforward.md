# K3: Chọn vector đặc trưng critic/actor và feedforward trong RL tracking (trạng thái tăng cường)

Phạm vi: optimal / H∞ tracking bằng (I)RL với trạng thái tăng cường X = [e; x_d]. Ứng dụng: Euler–Lagrange, tàu mặt nước, robot. Mục tiêu là quyết định cách hiểu X(1..9) trong Duc–Phung–Dao, J. Franklin Inst. 363 (2026) 109193.

Quy ước độ tin cậy:
- **[ĐÃ ĐỌC]**: đã đọc toàn văn hoặc đoạn liên quan trong phiên này.
- **[TÓM TẮT]**: chỉ dựa trên abstract hoặc trang mục lục.
- **[TRÍ NHỚ – chưa xác minh]**: lấy từ hiểu biết sẵn có, chưa mở được toàn văn để kiểm.

Giới hạn: phiên này dùng khoảng 15 lệnh tìm kiếm/tải. Nhiều bài IEEE, Springer, Wiley bị paywall nên không đọc được phần mô phỏng.

## Bảng tổng hợp

| # | Bài (DOI/arXiv) | (i) Trạng thái tăng cường | (ii) Thành phần vào basis critic/actor | (iii) Cấu trúc điều khiển | (iv) Q, R, γ, biên độ u | Độ tin cậy |
|---|---|---|---|---|---|---|
| 1 | Modares & Lewis, Automatica 50(7) 2014, 1780–1792, doi:10.1016/j.automatica.2014.05.011 | X = [e; x_d], x_d sinh bởi command generator ẋ_d = h_d(x_d) | Basis đa thức của toàn bộ X, tức có cả x_d (tôi nhớ vậy) | RL thuần. Feedforward và feedback được học chung trong một chính sách u(e, x_d). Có ràng buộc đầu vào qua hàm phạt tanh⁻¹ | Chi phí có chiết khấu e^{-γt}. Giá trị Q, R cụ thể chưa xác minh | Abstract [TÓM TẮT]; basis [TRÍ NHỚ – chưa xác minh] |
| 2 | Modares, Lewis, Jiang, IEEE TNNLS 26(10) 2015, 2550–2562, doi:10.1109/TNNLS.2015.2441749 (bản chương sách cùng nhóm: Modares, Kiumarsi, Vamvoudakis, Lewis, Ch.14 "Adaptive H∞ tracking control of nonlinear systems using RL", Elsevier 2018) | X = [e_d; r] ∈ R^{2n} | Chương sách: basis σ, φ, ϕ là hàm của X (gồm cả r). Định nghĩa 2 viết chính sách là "u = β(e_d, r)" | RL thuần (off-policy IRL), có actor, disturber và critic. Phần feedforward nằm sẵn trong chính sách | Chiết khấu α > 0. Ví dụ là UAV nonaffine | Chương sách [ĐÃ ĐỌC phần lý thuyết]; giá trị số trong TNNLS chưa xác minh |
| 3 | Kiumarsi, Lewis, Modares, Karimpour, Naghibi-Sistani, Automatica 50(4) 2014, 1167–1175, doi:10.1016/j.automatica.2014.02.015 | Hệ tuyến tính DT. X = [x; r], r(k+1) = F r(k) | Q-function bậc hai theo [x; r; u]. Kernel H chứa đủ các khối x–r, r–r, u–r. Chính sách có dạng u = −K₁x − K₂r | RL thuần. Số hạng −K₂r chính là feedforward tuyến tính theo trạng thái reference | Chiết khấu 0 < γ ≤ 1 | Cấu trúc LQT: khảo sát [ĐÃ ĐỌC] mô tả; chi tiết ví dụ [TRÍ NHỚ – chưa xác minh] |
| 4 | Kiumarsi & Lewis, IEEE TNNLS 26(1) 2015, 140–151, doi:10.1109/TNNLS.2014.2358227 | DT phi tuyến. X = [e; x_d] | Critic và actor là NN của X (có x_d) | RL thuần. Mô hình reference được học hoặc dùng làm "identifier" (chưa xác minh) | Có chiết khấu | [TRÍ NHỚ – chưa xác minh] |
| 5 | Kiumarsi, Vamvoudakis, Modares, Lewis, survey IEEE TNNLS 29(6) 2018, 2042–2062 (doi:10.1109/TNNLS.2017.2773458, DOI chưa xác minh) | Trình bày hai cách: (a) u = u_d + u_e và (b) X = [e; x_d] | (a) critic chỉ theo e; (b) theo X đầy đủ | So sánh trực tiếp cách tách feedforward + feedback với cách RL thuần trên trạng thái tăng cường | Q_T = diag(Q, 0): chỉ phạt e, không phạt x_d | [ĐÃ ĐỌC] |
| 6 | Mishra & Ghosh, arXiv:1911.04153 (critic-only IRL, tracking tốc độ góc máy bay) | z = [e_p, e_q, e_r, p_des, q_des, r_des] ∈ R⁶ | ϑ = [z₁..z₆, z₁², …, z₆², mọi z_i z_j] gồm 6 số hạng tuyến tính và 21 số hạng bậc hai, có cả reference | RL thuần, critic-only | Q₁ = diag(10, 10, 50, 0, 0, 0), R = I₃, γ = 0.1, T = 0.001 s | [ĐÃ ĐỌC] |
| 7 | Martinsen, Lekkas, Gros, Glomsrud, Pedersen, Frontiers Robot. AI 7:32 (2020), doi:10.3389/frobt.2020.00032 (tàu ReVolt, 257 kg) | ζ = [e; x_d] | σ(ζ) gồm các tích bậc hai của sai số vị trí và vận tốc trong body frame. Chỉ dùng sai số | **Feedforward (dùng mô hình học online bằng concurrent learning) + RL feedback có bão hòa tanh** | Không chiết khấu. Q 6×6 gần chéo. τ̄ = [50, 20, 32] | [ĐÃ ĐỌC qua PMC] |
| 8 | Nguyen, Dang, Pham, Dao, IJRNC 34(3) 2024, "Formation control scheme with RL strategy for a group of multiple surface vehicles" (DOI chưa lấy được, ngày đăng 20/3/2024 theo MaRDI) | Theo mô tả của người dùng: sai số + RL | Chưa xác minh | **τ = Mυ̇_d + C(υ_d)υ_d + D(υ_d)υ_d + u_RL**: feedforward mô hình + RL hiệu chỉnh (theo người dùng, tôi chưa mở được bài) | Chưa xác minh | [TÓM TẮT] |
| 9 | Vu, Pham, Dao, IJCAS (doi:10.1007/s12555-020-0809-7) và Vu, Pham, Dao, ISA Trans. 2022 "Disturbance observer-based adaptive RL for perturbed uncertain surface vessels" | Chưa xác minh | Chưa xác minh | Online actor-critic, ISA có thêm disturbance observer. Có feedforward mô hình hay không: chưa xác minh | Chưa xác minh | [TÓM TẮT]; Springer bị chặn |
| 10 | Wen, Ge, Chen, Tu, Wang, IEEE TCYB 49(9) 2019, doi:10.1109/TCYB.2018.2844177 ("Optimized backstepping", tàu mặt nước) | Không có trạng thái tăng cường. Mỗi bước backstepping có cost riêng theo z_i | Critic và actor dùng NN theo sai số z_i (và có thể cả trạng thái) | Actor NN học luôn phần động học chưa biết, tức feedforward học được | Chưa xác minh | Abstract [TÓM TẮT]; chi tiết basis [TRÍ NHỚ – chưa xác minh] |
| 11 | Vamvoudakis/Lewis, hướng robot Euler–Lagrange; Dao và cộng sự, robot manipulator (Vu, Dao, Loc, Huy, JCAES 2021, doi:10.1007/s40313-020-00674-w) | Biến trượt s = ė + Λe, giảm bậc | Critic và actor theo biến trượt hoặc sai số | Thông lệ là có thành phần bù mô hình hoặc RISE cộng với RL, nhưng chưa xác minh từ toàn văn | Chưa xác minh | [TÓM TẮT] |

## Câu hỏi 1: Modares–Lewis 2014 và Modares–Lewis–Jiang 2015 dùng trạng thái tăng cường và basis nào? Có đưa trạng thái reference vào basis không?

### Takeaway
Có. Trong dòng nghiên cứu Modares/Lewis/Kiumarsi, trạng thái tăng cường là [e; x_d] (hoặc [e_d; r]). Chính sách được định nghĩa tường minh là hàm của cả sai số lẫn reference. Basis là đa thức hoặc NN trên toàn bộ X, nên x_d nằm trong basis. Vai trò của x_d trong basis là để chính sách tự tái tạo phần feedforward. Đó là lý do duy nhất khiến chiết khấu trở thành bắt buộc.

### Cited Findings
- Bài Automatica 2014 xây "augmented system" gồm động học sai số và động học command generator. Hàm chi phí là discounted, không bậc hai (ràng buộc đầu vào). IRL học nghiệm HJB tracking mà không cần drift dynamics — [Scholars' Mine, Modares & Lewis 2014](https://scholarsmine.mst.edu/ele_comeng_facwork/2850)
- Chương sách H∞ tracking của cùng nhóm định nghĩa X(t) = [e_d(t)ᵀ r(t)ᵀ]ᵀ ∈ R^{2n}. Định nghĩa 2 tìm "control policy u = β(e_d, r) … depending on the tracking error e and the reference trajectory r" — [Modares, Kiumarsi, Vamvoudakis, Lewis, Ch.14 (PDF)](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)
- Cùng chương: "Previous work on the H∞ optimal tracking divides the control input into feedback and feedforward parts … In contrast, in the new formulation, both feedback and feedforward parts of the control input are obtained simultaneously and optimally" — [Ch.14 PDF](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)
- Cùng chương: "The use of the discount factor is essential. This is because the feedforward part of the control input does not converge to zero in general and thus penalizing the control input … without a discount factor makes the performance function unbounded" — [Ch.14 PDF](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)
- Basis σ, φ, ϕ (critic, actor, disturber) là "suitable basis" trên X. Bài TNNLS 2015 có thông tin thư mục xác nhận (vol. 26, no. 10, pp. 2550–2562) — [Ch.14 PDF](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf); [DBLP](https://dblp.dagstuhl.de/rec/journals/tnn/ModaresLJ15.html); [Scholars' Mine TNNLS 2015](https://scholarsmine.mst.edu/ele_comeng_facwork/2835)
- Một ví dụ cùng dòng, đã đọc được toàn văn: Mishra & Ghosh dùng z = [e_p, e_q, e_r, p_des, q_des, r_des]. Critic gồm 27 hàm: mọi z_i tuyến tính và mọi tích z_i z_j, kể cả các tích chỉ có reference. Q₁ = diag(10, 10, 50, 0, 0, 0), tức không phạt reference. R = I₃, γ = 0.1. Reference ở đây là **tốc độ góc mong muốn**, không phải vị trí tuyệt đối — [arXiv:1911.04153](https://arxiv.org/pdf/1911.04153)

### Inferences
- Thông lệ "basis gồm toàn bộ tích X(k)X(l)" (giống 45 tích trong Duc 2026) đúng là thông lệ của trường phái Modares/Lewis. Tuy nhiên trong các ví dụ đã kiểm, x_d là trạng thái bị chặn, thường là sinusoid hoặc tốc độ mong muốn. Không ví dụ nào cho x_d là vị trí tuyệt đối tăng không giới hạn.
- Basis bậc hai hoặc chính sách tuyến tính theo x_d chỉ tái tạo đúng feedforward khi feedforward tuyến tính theo x_d, như trong LQT tuyến tính. Với tàu, feedforward gần đúng là D(υ_d)υ_d + Mυ̇_d. Nó phụ thuộc vào υ_d và υ̇_d, không phụ thuộc p_d. Suy luận này là của tôi, dựa trên cấu trúc mô hình Fossen.

### Gaps
- Chưa mở được toàn văn Automatica 2014 và TNNLS 2015 nên chưa trích được vector basis cụ thể trong ví dụ mô phỏng. Tôi nhớ (chưa xác minh) rằng ví dụ phi tuyến 2 chiều dùng basis đa thức trên X 4 chiều, có cả x_d.

## Câu hỏi 2: Kiumarsi và cộng sự (Automatica 2014, TNNLS 2015) chọn đặc trưng thế nào?

### Takeaway
Trong LQT rời rạc (Automatica 2014), Q-function là dạng toàn phương đầy đủ theo [x; r; u]. Chính sách tối ưu u = −K₁x − K₂r chứa số hạng tuyến tính theo trạng thái reference, và số hạng này đóng vai trò feedforward. Khảo sát 2018 của cùng nhóm đặt hai cách cạnh nhau: tách feedforward u_d + feedback u_e (critic chỉ theo e), và tăng cường [e; x_d] có chiết khấu.

### Cited Findings
- Khảo sát mục "Optimal Tracking Problem": "the control input consists of two terms: a feedforward term that guarantees tracking and a feedback term that stabilizes the system". Theo khảo sát, feedforward u_d(k) = g(x_d)⁻¹(x_d(k+1) − f(x_d)), cost chỉ theo (e, u_e) và u* = u_d + u_e* — [Kiumarsi et al., TNNLS 2018 survey (PDF)](https://par.nsf.gov/servlets/purl/10078417)
- Khảo sát chỉ ra nhược điểm của cách tách: tính feedforward "needs" mô hình đầy đủ. Vì vậy cách tăng cường được phát triển để "gives both feedback and feedforward parts". Q_T = [[Q, 0], [0, 0]], tức không phạt x_d — [survey PDF](https://par.nsf.gov/servlets/purl/10078417)
- Remark 2 của khảo sát: "it is essential to use a discounted performance function … if the reference trajectory does not go to zero … the value is infinite, without the discount factor as the control input contains a feedforward part that depends on the reference trajectory" — [survey PDF](https://par.nsf.gov/servlets/purl/10078417)
- Thông tin thư mục Kiumarsi Automatica 2014 (Q-learning LQT) — [bib-bvb record](https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_pascalfrancis_primary_28387870)

### Inferences
- Khi dùng tăng cường, thông lệ là cho **toàn bộ trạng thái reference generator** vào kernel. Đây là trạng thái đủ để sinh ra reference (trạng thái Markov), và thường bị chặn.

### Gaps
- Chưa đọc được phần ví dụ của Kiumarsi & Lewis TNNLS 2015 (actor-critic DT phi tuyến). Cấu trúc NN critic/actor ghi trong bảng là [TRÍ NHỚ – chưa xác minh].

## Câu hỏi 3: Tàu mặt nước / USV / AUV có kết hợp feedforward với RL không? Trạng thái nào vào critic?

### Takeaway
Trong ứng dụng tàu, cách phổ biến (và thực tế hơn) là **feedforward (theo mô hình, hoặc học bằng NN/identifier) + RL feedback trên sai số**. Critic và actor chỉ nhận sai số, có khi kèm trạng thái bị chặn. Bài trước của chính nhóm Dao (IJRNC 2024) cũng theo cấu trúc này, theo mô tả của người dùng.

### Cited Findings
- Martinsen và cộng sự (ReVolt USV) dùng feedforward tính từ mô hình học online cộng với feedback actor-critic. Lý do họ nêu: "Due to inaccuracies in model approximation and disturbances, using only the feedforward control law, the vessel will experience drift". Basis σ(ζ) là tích bậc hai của sai số vị trí/vận tốc trong body frame. Bão hòa chỉ đặt lên phần RL. Cost không chiết khấu, τ̄ = [50, 20, 32] — [Martinsen et al. 2020, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7806118)
- Wen và cộng sự (TCYB 2019) làm optimized backstepping cho tàu. Virtual control và actual control đều là nghiệm tối ưu của từng hệ con, với cặp critic và actor riêng — [OpenAlex/aggregators; IEEE doi:10.1109/TCYB.2018.2844177](https://www.bohrium.com/paper-details/adaptive-tracking-control-of-surface-vessel-using-optimized-backstepping-technique/813021884298821633-2427)
- Bài IJRNC 2024 của nhóm Dao có cấu trúc hai tầng: tầng trên là formation theo displacement, tầng dưới là "RL-based optimal control strategy". Từ khóa có actor-critic. Ngày đăng 20/3/2024 — [AMiner](https://www.aminer.cn/pub/6573437f939a5f4082f9d21d/formation-control-scheme-with-reinforcement-learning-strategy-for-a-group-of-multiple); [MaRDI](https://portal.mardi4nfdi.de/wiki/Item:Q6117667)
- Vu, Pham, Dao (ISA Trans. 2022) dùng disturbance observer kết hợp adaptive RL cho tàu bất định. Bài IJCAS (doi:10.1007/s12555-020-0809-7) dùng online actor-critic cho tàu bất định. Chi tiết có feedforward hay không: chưa xác minh — [leopt4 publications](https://leopt4.github.io/publications); [Springer IJCAS](https://link.springer.com/article/10.1007/s12555-020-0809-7)
- Dao, Nguyen Duc, Liu có bài RL leader-following formation cho tàu bị nhiễu trên Systems & Control Letters 2025 — [DBLP](https://dblp.dagstuhl.de/rec/journals/scl/DaoDL25.html)

### Inferences
- Câu τ = Mυ̇_d + C(υ_d)υ_d + D(υ_d)υ_d + u_RL trong IJRNC 2024 do người dùng cung cấp. Tôi chưa tự đọc được bài, nhưng cấu trúc này khớp với thông lệ "feedforward mô hình + RL" (Martinsen 2020; cách tách trong khảo sát Kiumarsi 2018).
- Không bài tàu nào tôi kiểm được đưa vị trí reference tuyệt đối p_d (tăng không giới hạn) vào basis.

### Gaps
- Không truy cập được toàn văn IJCAS/ISA/IJRNC của nhóm Dao, cũng như các bài Wang Ning, Zhang Guoqing, Peng Zhouhua. Vì vậy chưa xác minh được basis critic cụ thể của các bài này. Tìm kiếm cũng không ra bài nào của các nhóm đó dùng "augmented critic" với p_d.

## Câu hỏi 4: Robot Euler–Lagrange (Vamvoudakis, Lewis, Dao)

### Takeaway
Thông lệ cho manipulator là dùng biến trượt hoặc sai số lọc s = ė + Λe để giảm bậc. Critic và actor nhận s hoặc e. Phần động học mô hình (hoặc RISE, hoặc NN bù) được cộng thêm. Chưa tìm được bài manipulator nào đưa q_d tuyệt đối vào basis critic.

### Cited Findings
- Vu, Dao, Loc, Huy (JCAES 2021): biến trượt kết hợp RISE và actor-critic cho manipulator 2 bậc tự do. Biến trượt dùng để xử lý nhiễu và "reduced the order of closed systems" — [Springer s40313-020-00674-w](https://link.springer.com/article/10.1007/s40313-020-00674-w)
- Dao, Phat, Hung (MATCOM 229, 2025): actor-critic + RISE cho bilateral teleoperator có trễ. Biến trượt dùng để giảm bậc mô hình — [RePEc](https://ideas.repec.org/a/eee/matcom/v229y2025icp151-175.html)

### Inferences
- Trong các bài Dao về robot, RL thường đi kèm thành phần không phải RL (RISE hoặc bù mô hình) thay vì RL thuần trên [e; q_d]. Đây là suy đoán từ abstract.

### Gaps
- Chưa đọc được toàn văn để xác định critic basis và có feedforward M(q)q̈_d + … hay không. Các bài Vamvoudakis/Lewis cho Euler–Lagrange cũng chưa kiểm.

## Câu hỏi 5: Các bài có bàn việc chiết khấu cộng với điều khiển xác lập khác 0 làm sai số không về 0 không?

### Takeaway
Có, nhưng chủ yếu ở mức điều kiện ổn định ("γ phải nhỏ hơn một cận trên"). Trường phái Modares/Lewis thừa nhận chiết khấu là bắt buộc vì u không về 0. Chính lời giải thích này cho thấy cost phạt **toàn bộ u**, kể cả phần feedforward, nên lời giải tối ưu sẽ đánh đổi giữa tracking và năng lượng.

### Cited Findings
- Chương H∞ tracking: nghiệm "guarantees the stability of the tracking error dynamics … if the discount factor is less than an upper bound" — [Ch.14 PDF](https://innovationcenter.msu.edu/wp-content/uploads/2021/07/Adaptive-tracking-control-of-nonlinear-systems-using-reinforcement-learning.pdf)
- Khảo sát 2018, Remark 2: chiết khấu là "essential", vì nếu không thì uᵀRu không về 0 và giá trị vô hạn — [survey PDF](https://par.nsf.gov/servlets/purl/10078417)
- Martinsen 2020 né vấn đề: feedforward nằm ngoài cost, chỉ phạt phần RL, nên dùng được cost không chiết khấu — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7806118)

### Inferences
Mục này là suy đoán định lượng, chưa xác minh bằng mô phỏng.
- Với Q = 100I trên sai số, R = I và u xác lập khoảng 1100 N, số hạng uᵀRu ≈ 1.2·10⁶. Cùng chi phí đó ở phía sai số tương ứng ‖e‖ ≈ 110 (m hoặc m/s).
- Do đó, nếu cost phạt toàn bộ τ, chính sách tối ưu có chiết khấu sẽ chủ động hy sinh tracking để giảm lực đẩy. Hệ quả là sai số xác lập khác 0, có thể lớn.
- Điều này đúng ngay cả khi basis biểu diễn được hoàn hảo, và độc lập với vấn đề p_d.
- Muốn sai số nhỏ thì cần một trong hai cách: (a) đưa feedforward ra ngoài và chỉ phạt u_RL, hoặc (b) chọn γ rất nhỏ và tỉ lệ Q/R rất lớn.

### Gaps
- Postoyan, Buşoniu, Nešić, Daafouz, "Stability analysis of discrete-time infinite-horizon optimal control with discounted cost", IEEE TAC 62(6) 2017, 2736–2749 (doi:10.1109/TAC.2016.2616644, [TRÍ NHỚ – DOI chưa xác minh]). Bài này cho điều kiện γ đủ gần 1 để ổn định, nhưng phiên này chưa mở được bài.
- Modares & Lewis, "Linear quadratic tracking control of partially-unknown CT systems using RL", IEEE TAC 59(11) 2014 (doi:10.1109/TAC.2014.2317301, [TRÍ NHỚ]) có cận trên cho chiết khấu. Chưa kiểm được trích dẫn cụ thể về sai số xác lập.

## Tổng hợp và khuyến nghị cho việc tái lập Duc–Phung–Dao 2026

1. **Đọc theo nghĩa đen [z; p_d; ψ_d] lệch khỏi thông lệ.**
   - Thông lệ đưa vào basis là trạng thái **bị chặn** của reference generator, hoặc chỉ sai số.
   - Đưa p_d tuyệt đối (đến 160 m) vào chính sách tuyến tính thì feedforward thay đổi theo vị trí. Điều này phi vật lý vì lực cản không phụ thuộc p_d, và cũng làm basis bậc hai mất điều kiện số (ill-conditioned).
   - Nhiều khả năng đây là lỗi chỉ số hoặc cách viết tắt trong bài, không phải ý đồ thiết kế. Đây là suy đoán.
2. **Nếu giữ RL thuần**, chọn X_actor = [z_η; z_υ; υ_d] (hoặc thêm υ̇_d) để tái tạo xấp xỉ D(υ_d)υ_d + Mυ̇_d. Khi đó cũng nên chuẩn hóa thang đo (τ cỡ 10³ N so với z cỡ 1).
3. **Khuyến nghị chính:** làm theo cấu trúc của bài trước cùng nhóm (IJRNC 2024) và của Martinsen 2020:
   - τ = Mυ̇_d + C(υ_d)υ_d + D(υ_d)υ_d + u_RL;
   - critic và actor chỉ theo sai số (z_η, z_υ), có thể kèm υ_d;
   - R chỉ phạt u_RL.
   Lợi ích:
   - tránh việc lời giải tối ưu chủ động bỏ 1100 N lực đẩy;
   - giữ bất biến tịnh tiến;
   - giảm số đặc trưng.
   Khi viết báo cáo, ghi rõ đây là lựa chọn diễn giải và chạy so sánh ablation với cách đọc nghĩa đen.
4. **Nếu bắt buộc theo đúng bài**, dùng 45 tích bậc hai trên 9 thành phần. Cần báo cáo sai số xác lập và lực thực tế, đồng thời so với baseline có feedforward.
