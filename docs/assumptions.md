# Giả thiết và lựa chọn cho các chỗ Paper A mơ hồ

Chốt ngày 26/11/2026 (Đức + agent). Số mục tham chiếu PLAN.md, mục (b).

**Nguyên tắc (Đức, 26/11/2026):** không bắt buộc tái tạo y hệt từng con số của Paper A. Mục tiêu là tái tạo đúng *cơ chế và xu hướng*: hội tụ, so sánh tương đối giữa các phương pháp, hình dạng các hình. Chỗ nào ảnh hưởng tận gốc đến kết quả thì hỏi tác giả; còn lại ta tự quyết, có lý do, và ghi ở đây.

---

## 1. Đang chờ tác giả trả lời

Trong lúc chờ, dùng giá trị **tạm** ghi ở cột cuối. Mốc 1 và Mốc 4 không phụ thuộc các câu hỏi này.

| # | Câu hỏi | Vì sao là chỗ then chốt | Giá trị tạm |
| --- | --- | --- | --- |
| K1 | Pha thu dữ liệu: chính sách hành vi, nhiễu thăm dò, thời lượng hoặc số khoảng M, thu trong lần chạy 40 s hay chạy riêng (PLAN mục 5, b.3) | Bài không mô tả. Quyết định ρ₁ có đủ hạng không và W học ra thế nào | Đề xuất ở PLAN b.3: chạy riêng trên trọn 40 s; u_b = −K_b·z + tổng 10 sin; T = 1e-3 |
| K2 | k_p = 30, k_v = 0.1 có đúng là giá trị đã dùng không (PLAN B-3) | Với hai giá trị này, tầng cao gần như không có cản (ζ ≈ 0.01), trái với Hình 5 | Giữ đúng bài; báo kết quả ở Mốc 2 |
| K3 | X(1..9) gồm những thành phần nào; τ có cộng thêm khâu bù dùng mô hình (feedforward theo M, C, D như bài tiền thân) không (PLAN B-10, R3) | Quyết định bộ điều khiển có thật sự không cần mô hình, và có bám được ở mức lực khoảng 1100 N không | Chạy cả (A) [z; p_d; ψ_d] lẫn (B) [z; υ_d]; **không** dùng feedforward |

## 2. Ta tự quyết

| Mục PLAN | Quyết định | Lý do ngắn |
| --- | --- | --- |
| 1 | Q_i = 100·I₆, Q' = blkdiag(Q_i, 0₉) | Code của nhóm dùng đúng cấu trúc này |
| 2 | γ² trong hàm chi phí r | Nhất quán với (25)–(30) |
| 3 | β_η = 2·I₃ | Hình 6 hội tụ trong khoảng 1 s |
| 4 | k_ω = 2; b_i = 1 cho mọi follower; ψ trong (14) là của tàu thật; ψ của leader cố định bằng ψ₀ | Bài không cho số |
| 6 | ε = 1e-6 (tương đối), tối đa 50 vòng | Các hình cho thấy 10–20 vòng |
| 7 | Lặp đến khi ‖ΔW‖ < ε | Lỗi in |
| 8 | W⁽⁰⁾ = 0. Nếu phân kỳ thì khởi tạo từ K_b, ghi lại | Đúng bài, có phương án dự phòng |
| 9 | d trong dữ liệu là δ thật do plant ghi lại | Chỉ làm được trong mô phỏng; ghi là giả thiết |
| 11 | Mô phỏng 40 s | |
| 12 | Mô phỏng đúng như bài dù Giả thiết 1 bị vi phạm | |
| 13 | Leader là điểm động học | Trang 19: chỉ điều khiển các follower |
| 15 | Tên biến `beta_s`, `beta_eta`, `alpha_disc`, `alpha_v` | Tránh trùng ký hiệu |
| B-1 | ϑ_i = R_pᵀ(ψ_i)(v_c + β(p_i − c)) | Khớp hướng đi ở Hình 3 |
| B-2 | c là tâm các **leader** (đúng chữ); vẽ s theo cả hai định nghĩa | Giữ đúng tinh thần phân tán: chỉ leader biết thông tin toàn cục. Đây cũng là nền cho tầng co giãn ở giai đoạn 2 |
| B-6 | Nếu khối W_d thiếu hạng: bơm thêm nhiễu thăm dò đã biết vào pha 1 | Chỉ làm được trong mô phỏng, ghi rõ |
| B-7 | η_d(0) = η(0), υ_d(0) = 0 | Lựa chọn tự nhiên |
| B-8 | e = sqrt(Σ_cạnh‖g − g*‖²); IAE, ITAE trên [0, 40]; RMSE = sqrt((1/40)∫‖e‖²dt); tổng lực = Σ_follower ∫\|τ\|dt. **So tỉ lệ giữa các phương pháp** | Bảng 1 của Paper A tự mâu thuẫn |
| B-11 | Bộ lọc an toàn đặt trên Π | Tương đương Ξ qua (12); CBF viết gọn hơn |
| B-14 | M1 hiểu theo (C): τ = m_ε(−ζ_ε z_υε − f_ε + α̇_ε), với z_υ = υ − alpha_v | Cách hiểu (A) và (B) cho sai số xác lập khoảng 6 m/s, vô lý so với kết quả M1 trong bài |
| B-15 | RK4, dt = 1e-3; pha thu dữ liệu dt = 1e-4; mẫu rand của δ đổi mỗi 1e-3 s | Khớp bước 0.001 s trong code của nhóm |
| B-13 | Tạo `.venv` bằng uv; repo git đã khởi tạo; PDF và `external/` không đẩy lên repo công khai | |

Mỗi khi kết quả lệch Paper A vì một lựa chọn trong file này, ghi vào `docs/replication_report.md` kèm số mục.
