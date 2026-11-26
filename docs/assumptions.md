# Giả thiết và lựa chọn cho các chỗ Paper A mơ hồ

Chốt ngày 26/11/2026 (Đức + agent), cập nhật sau khi đọc toàn văn các bài nguồn. Số mục tham chiếu PLAN.md, mục (b). Bằng chứng chi tiết: `reports/Thông lệ IRL và bearing formation.md`, phần "Cập nhật 26/11/2026".

**Nguyên tắc (Đức):** không bắt buộc tái tạo y hệt từng con số của Paper A. Baseline phải **đúng tinh thần phương pháp, chạy được, và ghi rõ mọi giả thiết**. Chỗ nào ảnh hưởng tận gốc đến kết quả thì khảo sát tài liệu trước, rồi mới hỏi thầy.

Ký hiệu nguồn: [L21] Lu et al. TNNLS 2021 (bài [3] của Paper A); [M15] Modares–Lewis–Jiang TNNLS 2015 (bài [39]); [N24] Nguyen–Dang–Pham–Dao IJRNC 2024 (bài [8]); [Z23] Zhang et al. Ocean Eng. 2023 (bài [4]); [K17] Kiumarsi–Lewis–Jiang Automatica 2017.

---

## 1. Tự quyết kèm quy trình tinh chỉnh (Đức, 26/11/2026)

Thầy cho biết code gốc đã mất, nên **không chờ tác giả**. Hai mục dưới đây ta tự tinh chỉnh khi code, theo tiêu chí khách quan, **không chỉnh để khớp số của Paper A**. Mọi lần quét đều được lưu và báo cáo.

| # | Điểm xuất phát | Tiêu chí chọn và điều kiện dừng |
| --- | --- | --- |
| K2: k_p, k_v | k_p = 30. Chạy đối chứng một lần đúng k_v = 0.1. Ứng viên: k_v ∈ {5, 10, 20, 40}, **chọn riêng cho từng case**. Đây là lệch bài: Paper A dùng chung một bộ hệ số cho cả hai case. Dạng luật (13) giống [Z23], bài này dùng k_v/k_p = 2.5 | (i) Khi bám hoàn hảo (Mốc 2): mode chậm nhất có ζ ≥ 0.7, hoặc thời gian xác lập chậm nhất gần mức tốt nhất đạt được. Mức đó khoảng 5 s ở k_v ≈ 2√(k_p/λ_min)·0.7: Case 1 cần k_v ≈ 20, Case 2 cần k_v ≈ 39. (ii) Trong vòng kín (Mốc 3, 5): không phân kỳ, sai số bearing nhỏ nhất, và ghi lại lực điều khiển. Chọn giá trị nhỏ nhất thỏa (i) và (ii). |
| K4: thang đo R | **Đã kích hoạt ở Mốc 5: R = diag(1/τ_nom²), τ_nom = (1100, 300, 30).** R = I của Paper A chạy như biến thể | Lời giải tham chiếu tuyến tính hóa cho thấy: với R = I, nghiệm tối ưu *thật* của chính hàm chi phí Paper A cho tàu trễ sau tàu ảo khoảng 123 m (bù lực cản không đủ dưới chiết khấu α = 0.1). Với R đã chuẩn hóa, độ trễ chỉ khoảng 4.5 mm. Điều kiện R⁻¹ − γ⁻²I > 0 vẫn thỏa. Hệ quả: γ = 5 giờ đo độ suy giảm nhiễu tương đối so với lực đã chuẩn hóa |
| Biến thể actor | φ = X(1..9), tuyến tính như bài | Nếu ở Mốc 5 sai số xác lập đổi theo pha co giãn: thử biến thể có nhãn, thêm hằng số bù cùng các số hạng u_d² và u_d³ vào φ. Lý do: lực cản d11(u)·u có số hạng u³, và φ tuyến tính không có hằng số bù. Critic giữ nguyên 45 số hạng. |
| K1: pha thu dữ liệu | **Chốt ở Mốc 5:** thu **nhiều đợt**, mỗi đợt là một tàu bám tàu ảo có **vận tốc thân tàu hằng** υ_d. Lưới u_d ∈ {5, 5.66, 6.3} m/s × v_d ∈ {−0.3, 0, 0.3} m/s, với ω_d = 0. Mỗi đợt 5 s, sai số ban đầu ngẫu nhiên. Chính sách hành vi là **PI** không dùng mô hình: τ = −K_b·z_υ − K_i∫z_υ + e(t), K_b = (2000, 2000, 200), K_i = (4000, 4000, 400); e(t) là tổng 20 sin dải 0.05–20 rad/s, biên độ (600, 180, 18). Mỗi follower thu riêng, seed khác nhau. Giữ lại 10 % dữ liệu để kiểm định | Thu trong lúc chạy kịch bản đội hình (cách đã thử đầu tiên) **vi phạm giả thiết tự trị** của (20) và [M15]: Ω phụ thuộc thời gian, láng giềng, và cả tàu thật qua (13). Bình phương tối thiểu khi đó vô nghĩa (dấu khuếch đại sai, phân kỳ). Tham chiếu vận tốc hằng thì tự trị. ω_d = 0 giữ z_η (hệ trái đất) nhất quán với lúc triển khai (ψ ≈ ψ₀). Thành phần I loại bỏ độ lệch hằng của z_υ, vốn làm z_υ cộng tuyến với υ_d. Chi tiết: replication_report.md, Mốc 5 |

## 2. Đã quyết (có nguồn hoặc lý do)

| Mục PLAN | Quyết định | Nguồn / lý do |
| --- | --- | --- |
| 1 | Q_i = 100·I₆, Q' = blkdiag(Q_i, 0₉) | Code của nhóm; [M15] chỉ phạt e |
| 2 | γ² trong r | (25)–(30); [M15] |
| 3 | β_η = 2·I₃ | [N24] dùng β_η = 2 với cùng luật backstepping (16) |
| 4 | Đồng thuận góc theo dạng (6) của [L21]: tổng chỉ lấy trên follower láng giềng; b_i = 1 nếu i nối trực tiếp với leader. **Dùng góc của tàu ảo ψ_d**, không dùng góc tàu thật. **k_ω = 3** | (14) chép từ [L21] (6). Sửa ở Mốc 3: nếu dùng ψ thật với k_ω = 25, ψ_d tích phân một ω_d rất lớn trong khi tàu thật bị trễ, nên ψ_d trôi đi khoảng 12 rad. k_ω = 3 cho ψ hội tụ trong khoảng 1 s như Hình 6. Khi bám hoàn hảo, hai cách cho kết quả như nhau |
| 6 | ε = 1e-6 (tương đối), tối đa 50 vòng | Các hình của bài: 10–20 vòng; [M15], [K17]: 4–7 vòng |
| 7 | Lặp đến khi ‖ΔW‖ < ε | Lỗi in |
| 8 | **W_a⁽⁰⁾ = −K_b ở các hàng z_υ (chính sách hành vi), W_d⁽⁰⁾ = 0.** W = 0 của Paper A chạy như biến thể | Đã chứng minh ở Mốc 5 (`tests/test_irl_vessel.py`): với τ = 0, hệ sai số **không ổn định** (trị riêng +1.05 trong nghĩa có chiết khấu, do số hạng +β_η của backstepping). Phép lặp chính sách xuất phát từ 0, kể cả bản dùng mô hình, hội tụ về một nghiệm ARE **sai**. Đây là phương án dự phòng đã ghi sẵn |
| 9, B-6 | d trong dữ liệu là δ thật do plant ghi lại, không bơm thêm | [M15] Remark 9. **Ở Mốc 5, B-6 không xảy ra:** phần 0.1·rand của δ đủ để ρ₁ đủ hạng (99/99, hoặc 84/99 khi ω_d ≡ 0, vì khi đó các cột ω_d bằng 0 đúng như dự kiến) |
| 10 / K3 | **X(1..9) = [z_η; z_υ; υ_d]**, RL thuần, **không** có khâu bù mô hình. Biến thể so sánh: (a) đúng chữ [z; p_d; ψ_d]; (b) khâu bù mô hình [N24] + RL, với R chỉ phạt phần RL | [N24] hứa "extend … with model-free RL", và Paper A là bước đó. [M15] đưa tham chiếu r vào cơ sở hàm nhưng r luôn bị chặn; υ_d đóng vai trò r |
| 11 | Mô phỏng 40 s | |
| 12 | Mô phỏng đúng bài dù Giả thiết 1 bị vi phạm | |
| 13 | Leader là điểm động học | Trang 19; [L21] Remark 4 (leader ảo) |
| 15 | Tên biến `beta_s`, `beta_eta`, `alpha_disc`, `alpha_v` | |
| B-1 | ϑ_i = R_pᵀ(ψ_i)(v_c + β(p_i − c)) | [L21] (3) |
| B-2 | **c = tâm của đội hình đích trên mọi n tàu**, c = (1/n)Σ_{i∈V} p_i*, với p_f* = −B_ff⁻¹B_fl·p_l (leader tính được). Vẽ s theo cả hai định nghĩa: có /n như [L21], và không /n để khớp số đọc trên Hình 12 | [L21] (2)–(3); khớp mức lực ở Hình 9 |
| B-5 | ρ₂ = −∫e^{−α(τ−t)}(XᵀQ'X + ûᵀRû − γ²d̂ᵀd̂)dτ | [M15] (77) |
| B-7 | η_d(0) = η(0), υ_d(0) = 0 | |
| B-8 | e = sqrt(Σ_cạnh‖g − g*‖²); IAE, ITAE trên [0, 40]; RMSE = sqrt((1/40)∫‖e‖²dt); tổng lực = Σ_follower ∫\|τ\|dt. So tỉ lệ giữa các phương pháp | Bảng 1 tự mâu thuẫn |
| B-11 | Bộ lọc an toàn đặt trên Π | Tương đương Ξ qua (12) |
| B-14 | M1 = luật dựa trên mô hình (27) của [L21]: τ = −k·(υ − alpha_v) − m·f̄ + m·α̇_v (cách hiểu B). **Cấu hình chính dùng k = (20, 12, 5) của [L21].** Biến thể: ζ = (0.5, 0.7, 0.5) như Paper A ghi | Với ζ của Paper A, sai số xác lập ≈ δ/ζ ≈ 6 m/s, biến M1 thành baseline yếu một cách giả tạo. Dùng hệ số của bài gốc phương pháp là công bằng hơn |
| B-16 (mới) | **Giới hạn gia tốc tàu ảo ‖Π‖ ≤ a_max = 5 m/s²**, áp dụng cho mọi phương pháp, kể cả M1 (Đức chốt ngày 26/11/2026) | Với k_p = 30 và sai lệch ban đầu 10–20 m, (13) cho ‖Π‖ khoảng 300–470 m/s² (cỡ 30–50 g), không có ý nghĩa vật lý. Gia tốc đó đẩy tầng thấp đã học ra xa vùng dữ liệu, gây phân kỳ. a_max = 3 cho hội tụ chậm (Case 2 mất 26.6 s); a_max = 5 cho 6.7 s và 7.9 s. 💡 Ràng buộc này dùng lại được cho CBF ở giai đoạn 2 |
| B-15 | RK4, dt = 1e-3; pha thu dữ liệu dt = 1e-4; mẫu rand của δ đổi mỗi 1e-3 s | Code của nhóm dùng bước 0.001 s |
| B-13 | `.venv` bằng uv; PDF và `external/` không đẩy lên repo công khai | |

Mỗi khi kết quả lệch Paper A vì một lựa chọn trong file này, ghi vào `docs/replication_report.md` kèm số mục.
