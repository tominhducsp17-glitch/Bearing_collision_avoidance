# Các bài liên quan và đóng góp còn đứng được

Lập ngày 27/11/2026. Agent đã đọc toàn văn ba bài trong `Related_paper/`:

- **[Mol21]** T. G. Molnar, R. K. Cosner, A. W. Singletary, W. Ubellacker, A. D. Ames, *Model-free safety-critical control for robotic systems*, IEEE RA-L 2021 (arXiv 2109.09047).
- **[Zha24]** X. Zhang, Q. Yang, J. Lyu, X. Zhao, H. Fang, *Distributed variation parameter design for dynamic formation maneuvers with bearing constraints*, IEEE TASE 2024 (file `2023TASE_scaling.pdf`).
- **[NH26]** A. A. Naeem, M. A. Haque, *A barrier-modulated architecture for safe affine formation control in second-order multi-agent systems*, arXiv 2606.08137 (06/2026).

Ký hiệu của ta: Paper A = bài gốc (bearing, co giãn, H∞ IRL); Paper B = RHTF-CBF cho multi-QUAV.

Lưu ý: bản nháp 4 ý đóng góp mà Đức nhắc **không có trong tin nhắn agent nhận được**. Mục 3 dưới đây là bản agent tự viết lại từ PROJECT_CONTEXT §4 và từ ba bài; Đức gửi bản nháp thì agent sẽ đối chiếu.

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

## 3. Đóng góp còn đứng được (bản agent đề xuất, chờ Đức đối chiếu với bản nháp 4 ý)

**Đ1. Co giãn do an toàn quyết định, có bảo đảm khả thi.** Tốc độ co giãn β là *biến quyết định* trong QP của leader, cùng với các ràng buộc HOCBF thật với bờ kênh và vật cản (đã cộng biên ε), và ràng buộc tỉ lệ tối thiểu s ≥ s_min. Ta chứng minh QP luôn khả thi cho tới khi chạm s_min (mục 4, Định lý 2); deadlock được thoát bằng cách co đội hình.
*Khác [Zha24]:* ở họ, tỉ lệ do một kích thích heuristic quyết định và CBF chỉ chặn chính biến tỉ lệ, nên không có bảo đảm an toàn với vật cản. Ở ta, an toàn với bờ và vật cản là ràng buộc cứng của bài toán chọn β.
*Khác Paper B:* ta không xoay đích để thoát deadlock.
→ **Mạnh nhất.** Đây nên là đóng góp chính.

**Đ2. An toàn cho tàu thật khi tầng thấp là bộ điều khiển học, không cần mô hình.** CBF đặt trên tàu ảo (tích phân kép đúng tuyệt đối), và an toàn của tàu thật được suy ra từ bán kính sai số bám ε của tầng thấp IRL. Đây là bản nhiều tàu, bậc hai, của ý tưởng [Mol21].
*Khác [Mol21]:* nhiều tàu và ràng buộc giữa các tàu; mô hình rút gọn bậc 2 (HOCBF); tầng thấp chỉ UUB, học từ dữ liệu, có nhiễu; biên từ ε được hiệu chuẩn bằng dữ liệu.
*Khác [NH26]:* ta có cascade, tàu ảo biết chính xác, nên không cần học phần an toàn.
→ **Trung bình.** Một mình Đ2 dễ bị coi là "[Mol21] cho nhiều agent". Nó đứng được khi gắn với Đ1 và Đ3.

**Đ3. So sánh có hệ thống ba cách đưa sai số bám vào biên an toàn** (Mốc 9b): ε cố định đã hiệu chuẩn; ε(t) có chặn Lipschitz; và biên động h_V = −V + α_e·h của [Mol21], với V lấy từ **critic V̂ của chính IRL** hoặc từ một hàm Lyapunov của tầng thấp. Dùng critic V̂ của H∞ IRL làm h_V là ý mới (agent chưa thấy bài nào làm), nhưng rủi ro cao: V̂ là hàm giá trị có chiết khấu, không chắc là hàm Lyapunov (xem PLAN_phase2 Mốc 9b).
→ **Có tiềm năng, chưa chắc.** Nếu h_V với V̂ không chạy được thì vẫn giữ được phần so sánh ε cố định với ε(t) như một kết quả thực nghiệm.

**Đ4. Bằng chứng tái tạo về Paper A** (R = I cho nghiệm trễ 123 m; W = 0 không chấp nhận được; thu dữ liệu trong lúc chạy đội hình vi phạm giả thiết tự trị; M1 với ζ in trong bài hỏng góc hướng). Theo quyết định của Đức (27/11), **đây không phải đóng góp** của bài: chỉ ghi trong phần cài đặt và phụ lục để người khác chạy lại được.

## 4. Chỗ còn thiếu trong khảo sát

Agent chỉ đọc ba bài này cộng Paper A, Paper B. Trước khi khóa đóng góp, nên tìm thêm, đặc biệt cho Đ1 và Đ2:
- "safety-critical control via reduced-order models" (các bài tổng quan và nối tiếp [Mol21] của nhóm Ames, 2022–2025);
- "formation scaling" kết hợp "control barrier function" hoặc "narrow passage" (đội hình qua chỗ hẹp, tối ưu tỉ lệ trực tuyến);
- "bearing formation" cộng "collision avoidance" cho USV hoặc ASV.

Agent không khẳng định gì về các bài chưa đọc.
