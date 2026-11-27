# Các bài liên quan và đóng góp còn đứng được

Lập ngày 27/11/2026. Agent đã đọc toàn văn ba bài trong `Related_paper/`:

- **[Mol21]** T. G. Molnar, R. K. Cosner, A. W. Singletary, W. Ubellacker, A. D. Ames, *Model-free safety-critical control for robotic systems*, IEEE RA-L 2021 (arXiv 2109.09047).
- **[Zha24]** X. Zhang, Q. Yang, J. Lyu, X. Zhao, H. Fang, *Distributed variation parameter design for dynamic formation maneuvers with bearing constraints*, IEEE TASE 2024 (file `2023TASE_scaling.pdf`).
- **[NH26]** A. A. Naeem, M. A. Haque, *A barrier-modulated architecture for safe affine formation control in second-order multi-agent systems*, arXiv 2606.08137 (06/2026).

Ký hiệu của ta: Paper A = bài gốc (bearing, co giãn, H∞ IRL); Paper B = RHTF-CBF cho multi-QUAV.

Mục 3 là bản nháp đóng góp của Đức (gửi 27/11), kèm nhận xét của agent.

---

## 1. Bảng so sánh

| | [Mol21] | [Zha24] | [NH26] | Paper B | **Ta** |
|---|---|---|---|---|---|
| Bài toán | một robot, tránh vật cản | đội hình bearing, đổi kích thước và tịnh tiến | đội hình affine, tránh va chạm giữa các agent | multi-QUAV, tránh va chạm | đội hình bearing của tàu mặt nước, co giãn, đi qua kênh |
| Đội hình | không | bearing, leader–follower qua tham chiếu chung p\* | affine (ma trận stress), leader–follower | khoảng cách tương đối | bearing (Paper A), 2 leader |
| CBF đặt ở đâu | **mô hình rút gọn**: vận tốc an toàn của khâu tích phân đơn (hoặc unicycle), rồi bộ bám vận tốc đuổi theo | **chỉ trên biến tỉ lệ**: HOCBF giữ κ ≥ κ_min và chặn biên độ chính sách tỉ lệ; khoảng cách tới vật cản **không** nằm trong CBF | **trực tiếp trên đầu vào của agent thật** (tích phân kép có bất định tham số), cộng với hệ số điều biến ρ_i làm giảm luật danh định | trên đầu vào của QUAV (có bộ quan sát nhiễu) | **trên tàu ảo** (tích phân kép đúng tuyệt đối, p̈_d = Π), QP tập trung |
| Xử lý sai số bám | **h_V = −V + α_e h** (V là Lyapunov của bộ bám); cần λ > α; có bản ISSf khi bám chỉ ISS | không xét: robot coi như bám hoàn hảo p_d | không có tầng bám (CBF tác động thẳng vào agent); bất định Φθ bị chặn | bộ quan sát nhiễu, hàm thời gian hữu hạn | **biên cố định ε** đo được (bất đẳng thức tam giác); Mốc 9b so với ε(t) và h_V |
| Tầng thấp | bộ bám vận tốc bất kỳ, giả thiết bám mũ (hoặc ISS) | luật đội hình kinh điển cho tích phân kép | sliding mode thích nghi kèm ADP actor–critic **cho phần an toàn** | backstepping, mô hình biết | **H∞ IRL off-policy, không cần mô hình** (hoặc M1), tàu 3 bậc tự do có nhiễu |
| Co giãn thích nghi | không | **có**: κ sinh từ "kích thích môi trường" f_i (kiểu trường thế) đi qua hệ tích phân bậc ba ảo, đồng thuận bằng DAT | không | không (xoay đích để thoát deadlock) | **có, theo kế hoạch**: β là biến quyết định trong QP của leader, ràng buộc thật với bờ và vật cản |
| Phản hồi chéo giữa các tầng | tầng an toàn không nhận gì từ tầng bám (chỉ chọn α đủ nhỏ) | một chiều: môi trường → tham số → luật đội hình | ρ_i làm giảm luật danh định khi gần biên; ρ_i làm đóng băng luật thích nghi | không | ε từ tầng thấp vào biên CBF; QP khó khả thi hoặc deadlock → tầng co giãn (Mốc 9) |
| Vật cản có được chứng minh an toàn không | **có** (Định lý 3, Hệ quả 1) | **không**: chỉ chứng minh κ ≥ κ_min và tính chia sẻ điều khiển giữa hai HOCBF; tránh vật cản chỉ là hệ quả của f_i heuristic | chỉ va chạm giữa các agent (Định lý 2, 4); vật cản không có trong phần lý thuyết | có (giữa các agent) | **có, theo kế hoạch**: HOCBF với bờ và vật cản trên tàu ảo cộng biên ε |
| Phân tán | không áp dụng | **có** (DAT, chỉ cần láng giềng) | có (cảm biến cục bộ R_sense) | có | **không**: QP tập trung cho follower; leader quyết β |

### Nhận xét về từng bài (điểm cần biết khi viết phần so sánh)

**[Mol21]** là bài gần ta nhất về *ý tưởng*: tách an toàn ra một mô hình rút gọn biết chính xác, rồi để bộ bám không cần mô hình đuổi theo. Định lý 3 cần ba điều: CBF chỉ phụ thuộc cấu hình (h(q), gradient bị chặn C_h), bộ bám ổn định mũ với tốc độ λ, và λ > α. Nhận xét 1 cho quy trình chỉnh: tăng α dần từ 0. Khác ta ở bốn chỗ: (i) mô hình rút gọn là **bậc 1** (vận tốc an toàn), còn ta là **bậc 2** (gia tốc an toàn cho tàu ảo, HOCBF); (ii) một robot, không có đội hình và không có ràng buộc giữa nhiều agent; (iii) bộ bám giả thiết ổn định mũ (hoặc ISS), còn IRL của ta chỉ UUB và được học từ dữ liệu; (iv) biên dùng V của bộ bám, còn ta dùng ε đo được. Rủi ro: người phản biện sẽ hỏi "đây chỉ là [Mol21] cho nhiều tàu?" — xem mục 3.

**[Zha24]** là bài gần ta nhất về *co giãn*: cũng là đội hình bearing, cũng tự đổi kích thước theo môi trường, cũng dùng HOCBF. Nhưng HOCBF của họ chỉ đặt lên **biến tỉ lệ** (κ ≥ κ_min, và một ràng buộc biên độ để thuật toán DAT hội tụ). Lượng co lại do một "kích thích" f_i quyết định (công thức (35): lực đẩy kiểu trường thế khi cách vật cản dưới 5 m). Không có định lý nào nói robot không đâm vật cản. Robot là tích phân kép, coi như bám hoàn hảo. Điểm mạnh mà ta không có: phân tán hoàn toàn, có thí nghiệm Crazyflie, có chứng minh chia sẻ điều khiển giữa hai HOCBF.

**[NH26]** trùng ta ở cụm từ "HOCBF + học tăng cường + đội hình" nên dễ bị so. Nhưng cách làm khác hẳn: an toàn tác động trực tiếp lên agent (không có cascade, không có tàu ảo); bộ điều khiển an toàn hoặc là lực đẩy theo gradient, hoặc là actor–critic ADP học trực tuyến; luật danh định bị nhân với ρ_i ∈ [0, 1]. Họ chỉ xét va chạm giữa các agent, không có bờ và vật cản trong lý thuyết, không co giãn. Phần chứng minh có chỗ yếu đáng nêu khi so sánh: Định lý 4 lập luận rằng tại biên, ∇V\* → ∞ nên chính sách học được nằm đúng trên biên bão hòa — đó là tính chất của nghiệm tối ưu *thật*, không phải của actor xấp xỉ có sai số. Bài là arXiv 06/2026, chưa qua phản biện.

## 2. Những gì đã có người làm (không được nhận là của ta)

- Tách an toàn sang mô hình rút gọn và bám bằng bộ điều khiển không cần mô hình, kèm điều kiện λ > α: [Mol21] (và các bài trước đó của nhóm Ames).
- Đội hình bearing tự đổi kích thước theo môi trường, có HOCBF trên biến tỉ lệ: [Zha24].
- Kết hợp HOCBF với học tăng cường / ADP cho đội hình tích phân kép có bất định: [NH26], và các bài [33]–[35] mà [NH26] trích (Marvi; Wang — CBF đặt trong hàm chi phí của trò chơi tổng bằng không).
- HOCBF giữa các agent với giới hạn đầu vào, phát hiện deadlock theo sự kiện: Paper B.

## 3. Đóng góp còn đứng được (bản nháp của Đức để trình thầy, kèm nhận xét của agent)

**1. Bộ lọc an toàn ở tầng tàu ảo của đội hình bearing cascade có phản hồi chéo, cùng định lý an toàn cho tàu thật dưới tầng thấp H∞ học được.** Mở rộng khung ISSf của [Mol21] sang nhiều tàu, trong đó tham chiếu có trạng thái riêng và phụ thuộc vị trí tàu thật.

*Nhận xét của agent:*
- Điểm khác [Mol21] đáng nhấn mạnh nhất là **tham chiếu có trạng thái riêng** (tàu ảo bậc hai) và **phụ thuộc tàu thật qua (13)**. Bản thân việc "phụ thuộc vị trí thật" không phải là điểm khác: vận tốc an toàn q̇_s(q) của [Mol21] cũng phụ thuộc cấu hình thật. Cái khác là ở ta, phụ thuộc này là một vòng kín động: sai số bám làm méo tham chiếu (số hạng Q₂ trong Định lý 1 của Paper A), và tham chiếu lại quyết định sai số bám. Chính điều này sinh ra chỗ chưa chắc U1 (PLAN_phase2 §4), nên cũng là chỗ phần chứng minh phải giải quyết.
- Với biên ε cố định, Định lý 1 hiện tại là **lập luận ống** (bất biến HOCBF cộng bất đẳng thức tam giác), chưa phải ISSf. Chỉ gọi là "mở rộng khung ISSf" khi mục 3 (h_V) chạy được. Đề xuất cách viết: "định lý an toàn theo bán kính bám ε; bản ISSf khi tầng thấp có hàm Lyapunov (mục 3)".

**2. Co giãn vì an toàn.** Tốc độ co giãn β là biến quyết định trong QP: giữ QP khả thi khi kênh hẹp dần, thoát deadlock, chỉ leader quyết định, có chứng minh. Bản của [Zha24] là heuristic và không bảo đảm an toàn với vật cản.

*Nhận xét của agent:* đồng ý, đây là đóng góp mạnh nhất. Hai chỗ nên viết chặt hơn: (i) "có chứng minh" nên ghi rõ là chứng minh **khả thi dưới giả thiết về hình học kênh** (B1–B3 của Định lý 2); (ii) **thoát deadlock chưa có chứng minh**: khả thi không có nghĩa là hết deadlock (U6), nên phần này hiện chỉ có bằng chứng số. "Chỉ leader quyết định" vừa là điểm gọn vừa là điểm yếu so với [Zha24] (phân tán); nên nêu thẳng.

**3. (Ứng viên) Biên an toàn động.** Lấy từ hàm Lyapunov của tầng thấp theo kiểu h_V của [Mol21], thay cho ε cố định. Ở Paper A, V\* đóng vai hàm Lyapunov (Định lý 1), nên có thể dùng critic V̂ học được. Ý này mới, nhưng V̂ chỉ là xấp xỉ và Paper A dùng chiết khấu, nên phải kiểm bằng số trước khi nhận là đóng góp.

*Nhận xét của agent (đã đọc lại chứng minh Định lý 1 của Paper A):* khẳng định "V\* đóng vai hàm Lyapunov" **chỉ đúng một phần**. Cụ thể:
- Paper A chỉ chứng minh V̇\* ≤ −(1 − θ₁)λ_min(Q)‖z‖² + c₁, với c₁ ≥ ‖αV\*([0, Ω]) + γ²dᵀd‖, và **chỉ trong một lân cận** ‖z‖ ≤ L⁻¹(…). Hằng số c₁ ≠ 0 ngay cả khi không có nhiễu, vì có chiết khấu α và vì V\* phụ thuộc Ω (tức υ_d). Kết quả chỉ là UUB.
- Chứng minh có một chỗ hở: ở (41) Paper A viết V\*(z) và coi nó xác định dương theo z, trong khi V\* là hàm của X = [z; Ω], và V\*([0, Ω]) ≠ 0.
- Hệ quả cho mục 3: dạng V̇ ≤ −λV + c đúng là dạng ISS mà Hệ quả 1 của [Mol21] cần, nên hướng đi vẫn hợp lý. Nhưng (a) chỉ được ISSf, với tập an toàn nới rộng theo c₁/α, mà c₁ có thể lớn; (b) phải dùng V̂(z, Ω) − V̂(0, Ω) thay vì V̂; (c) chỉ đúng cục bộ, nên phải kiểm quỹ đạo nằm trong vùng đó; (d) V̂ là xấp xỉ với sai số khớp khoảng 1 %. Tất cả đã đưa vào Mốc 9b. Giữ trạng thái **ứng viên** là đúng.

**4. (Nếu kịp) An toàn trong pha thu dữ liệu nhiều tàu** (Mốc 11). Không có nhận xét thêm.

Ngoài bốn mục trên: các bằng chứng tái tạo về Paper A (R = I cho nghiệm trễ 123 m; W = 0 không chấp nhận được; thu dữ liệu vi phạm giả thiết tự trị; M1 với ζ in trong bài hỏng) **không phải đóng góp** (quyết định của Đức, 27/11), chỉ ghi trong phần cài đặt.

## 4. Chỗ còn thiếu trong khảo sát

Agent chỉ đọc ba bài này cộng Paper A, Paper B. Trước khi khóa đóng góp, nên tìm thêm, đặc biệt cho Đ1 và Đ2:
- "safety-critical control via reduced-order models" (các bài tổng quan và nối tiếp [Mol21] của nhóm Ames, 2022–2025);
- "formation scaling" kết hợp "control barrier function" hoặc "narrow passage" (đội hình qua chỗ hẹp, tối ưu tỉ lệ trực tuyến);
- "bearing formation" cộng "collision avoidance" cho USV hoặc ASV.

Agent không khẳng định gì về các bài chưa đọc.
