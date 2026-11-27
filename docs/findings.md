# Những điểm cần biết

Sổ theo dõi các phát hiện quan trọng, cập nhật sau mỗi mốc. Mỗi mục ghi: phát hiện là gì, tại sao quan trọng, và đã xử lý thế nào (kèm số mục trong `assumptions.md`).

Chi tiết số liệu: `replication_report.md`. Bằng chứng từ tài liệu: `reports/Thông lệ IRL và bearing formation.md`.

Trạng thái: ✅ đã xử lý · ⚠️ còn mở hoặc cần theo dõi · 💡 ý cho bài báo của ta

---

## Mốc 0: đọc bài, khảo sát code và tài liệu

- ✅ **Code của nhóm tác giả xác nhận cách cài plant**: d11 dùng u², còn d22, d23, d32 dùng |u|. Nhiễu δ(t) của Paper A có sẵn trong khối Simulink, đang bị comment. Q = 100·blkdiag(I₆, 0).
- ✅ **Algorithm 2 và Remark 9–10 chép gần nguyên văn Modares 2015 [M15].** Dấu của ρ₂ in sai trong (58)–(59) (B-5).
- ✅ **Tầng cao và M1 lấy từ Lu 2021 [L21]:** leader dùng R_pᵀ (B-1); tâm c lấy theo đội hình đích của mọi tàu (B-2); M1 là luật (27) của [L21] (B-14); (14) là luật (6) của [L21].
- ✅ **Paper A là bước "model-free" mà bài [N24] hứa.** Vì vậy RL thuần, không có khâu bù mô hình; X(1..9) = [z; υ_d] (mục 10).
- ⚠️ **Bảng 1 của Paper A tự mâu thuẫn**: IAE = 37.2 trong 40 s không thể đi cùng RMSE = 0.0178. Chỉ so tỉ lệ giữa các phương pháp (B-8).
- ⚠️ **Thang đo của hàm chi phí:** τ ≈ 1100 N khi chạy đều, trong khi R = I. Nghiệm tối ưu thật có thể chấp nhận bám kém. Sẽ kiểm ở Mốc 5 (K4).
- ⚠️ **W_d có thể không xác định được** vì δ gần như hằng số (B-6). Sẽ kiểm hạng ρ₁ ở Mốc 5.
- ✅ Code gốc của Paper A đã mất: tự quyết, tinh chỉnh theo tiêu chí khách quan (assumptions §1).

## Mốc 1: mô hình tàu, hình học bearing

- ✅ B_ff khả nghịch, trị riêng nhỏ nhất 0.145 (Case 1) và 0.039 (Case 2). Từ (8) ra đúng hình vuông cạnh 9 và hình chữ nhật 18×9.
- ⚠️ **Ma trận cản D không tiêu tán năng lượng ở hai vùng:** khi u = 0 và |r| ≥ 1.75 rad/s (vì d23 dùng |u|), và khi |u| ≈ 20 m/s. Cả hai nằm ngoài vùng hoạt động; giữ nguyên mô hình, có test ghi nhận.
- 💡 Ở 5.66 m/s, mô hình chạy ngoài dải vận tốc thực của CyberShip II, nên lực lên tới cỡ 10³ N.

## Mốc 2: tầng cao riêng, bám hoàn hảo

- ✅ **k_v = 0.1 của Paper A gần như chắc chắn in sai.** Ba bằng chứng: hệ gần như không có cản (ζ ≈ 0.01); đội hình dao động suốt 40 s; bài [Z23] cùng dạng luật dùng k_v/k_p = 2.5. **Đã chọn k_v = 20 (Case 1) và 40 (Case 2)**, lệch bài (K2).
- 💡 **Với k_v = 0.1, hai tàu tiến sát nhau tới 0.29 m** (Case 1), ngay cả khi bám hoàn hảo. Cản kém thì khoảng cách nhỏ nhất tụt còn 3.6–6.6 m, trong khi cạnh đội hình là 9 m. Đây là động lực trực tiếp cho phần CBF.
- ⚠️ **Gia tốc tham chiếu ban đầu ‖Π‖ khoảng 300–470 m/s²**, do k_p = 30 nhân với sai lệch ban đầu 10–20 m. Nó gây quá độ lớn ở tầng thấp, giải thích các quá độ cỡ 10⁵ ở Hình 8, 17, 20.
- ⚠️ **Còn sai số dư khoảng 1e-3 trong các pha co giãn**, vì luật (13) không có thành phần bù gia tốc leader. Đây là hệ quả của việc Giả thiết 1 bị vi phạm (mục 12).
- ✅ Kích thước đội hình bám đúng lịch (63); khi bỏ hệ số 1/n thì khớp Hình 12a.
- ✅ Runner giữ Π (thay vì Ξ) không đổi trong mỗi bước, để p̈_d = Π đúng tuyệt đối.

## Mốc 3: chạy kín với plant thật và M1

- ✅ **Đã sửa luật (14).** Nếu dùng ψ của tàu thật với k_ω = 25, ψ_d trôi tới khoảng 12 rad (tàu quay gần 2 vòng). Hiện dùng ψ_d của tàu ảo và k_ω = 3 (mục 4).
- ⚠️ **M1 có sai số xác lập ≈ δ/k**, vì không bù nhiễu: z_u ≈ 0.15 m/s, z_r ≈ 0.6 rad/s. **Góc hướng xác lập là khoảng 1.08 rad thay vì π/4.** Hình 6 của Paper A thì cho M1 về π/4; chưa rõ vì sao.
- ✅ **Với ζ = (0.5, 0.7, 0.5) như Paper A in, M1 hỏng phần góc hướng** (tàu gần như chạy ngược). Cấu hình chính dùng hệ số (20, 12, 5) của [L21]; ζ của Paper A là biến thể.
- 💡 **Sai số bearing gần như không phụ thuộc tầng thấp tốt hay kém:** biến thể ζ có z_υ khoảng 3 m/s mà RMSE bearing vẫn bằng cấu hình chính. Lý do là (13) dùng vị trí tàu thật, nên tàu ảo tự bù phần trễ. **Khi so các phương pháp (Mốc 6) phải báo thêm z_υ, z_η và tổng lực.**
- ⚠️ Quá độ góc hướng trong 2 s đầu là lớn, do ‖Π‖ ban đầu rất lớn và do (62) bỏ qua m23. Dùng M đầy đủ giảm được khoảng 40 %.
- ✅ Lực surge khoảng 1100 N khi chạy đều, khớp Hình 9a.

## Mốc 4: IRL trên bài toán đồ chơi

- ✅ **Thuật toán 2 cài đúng.** Trọng số học được khớp nghiệm ARE H∞ có chiết khấu (sai số tương đối 1e-10 đến 1e-7) và khớp phép lặp chính sách dùng mô hình **ở từng vòng**. Phép kiểm này xác nhận cả việc sửa dấu ρ₂ (B-5).
- ✅ **T = 1 ms của Paper A không phải vấn đề** khi dữ liệu không có nhiễu đo: cả 36 cấu hình quét (T, thời lượng thu, biên độ thăm dò) đều đủ hạng và chính xác.
- ⚠️ **Đã tái hiện được rủi ro B-6 trên bài đồ chơi:** nhiễu nhiều kênh gần như hằng, cộng với W_d⁽⁰⁾ = 0, làm ρ₁ thiếu hạng. Ở Mốc 5 sẽ thử lần lượt: đo hạng với dữ liệu như bài, rồi W_d⁽⁰⁾ ≠ 0, rồi bơm thêm nhiễu thăm dò vào kênh d.
- ⚠️ Rủi ro chính của Mốc 5 chuyển sang việc **xấp xỉ hệ phi tuyến bằng cơ sở hàm bị cắt** (45 số hạng bậc hai, actor tuyến tính), và thang đo của R (K4).
- ✅ Hệ không ổn định cần khởi tạo từ một chính sách chấp nhận được. Code đã có sẵn phương án này (mục 8).

## Mốc 5: IRL trên tàu

- ✅ **K4 đã kích hoạt: R = I của Paper A làm nghiệm tối ưu *thật* chấp nhận bám kém.** Theo lời giải tham chiếu H∞ tuyến tính hóa, với R = I tàu trễ sau tàu ảo khoảng **123 m**, vì bù lực cản 1100 N bị phạt quá nặng dưới chiết khấu α = 0.1. Chọn R = diag(1/τ_nom²): trễ chỉ khoảng 4.5 mm, khuếch đại cỡ 10⁴, cùng bậc với mức khoảng 7000 suy ra từ Hình 8–9 của bài. *Hình bám chặt của Paper A không thể có được với R = I nếu thuật toán thực sự hội tụ về nghiệm tối ưu.*
- ✅ **Khởi tạo W = 0 của Paper A không phải chính sách chấp nhận được.** Với τ = 0, hệ sai số không ổn định (trị riêng +1.05, do số hạng +β_η của backstepping). Phép lặp chính sách từ 0, kể cả bản dùng mô hình, hội tụ về một nghiệm ARE **sai**. Đã sửa: khởi tạo từ chính sách hành vi (mục 8). Có test.
- ✅ **Thu dữ liệu trong lúc chạy kịch bản đội hình vi phạm giả thiết tự trị** của (20) và [M15]: Ω phụ thuộc thời gian, láng giềng và chính tàu thật qua (13). Bình phương tối thiểu khi đó vô nghĩa (dấu khuếch đại sai, phân kỳ). Ngay cả trên mô hình tuyến tính, tham chiếu biến thiên theo thời gian cũng phá hỏng việc học. Có test.
- ✅ **Thiết kế pha thu dữ liệu mới** (chi tiết cài đặt để baseline chạy được, *không phải đóng góp*, theo Đức 27/11): nhiều đợt, mỗi đợt một tham chiếu vận tốc thân tàu hằng (nên tự trị), ω_d = 0 (hệ trái đất nhất quán), chính sách hành vi PI (khử cộng tuyến giữa z_υ và υ_d), sai số ban đầu ngẫu nhiên (kích thích z_η). Trên tàu phi tuyến, khuếch đại học được khớp lời giải tham chiếu trong khoảng 1–3 %. Có test.
- ✅ **B-6 không xảy ra:** phần 0.1·rand của δ đủ để khối W_d xác định được.
- ⚠️ **Đặc trưng không được kích thích thì nhận trọng số khổng lồ**: θ_d,v gần hằng trong dữ liệu nhưng nhận trọng số cỡ 10⁶. Lúc triển khai thì bùng nổ. Bài học: dữ liệu phải phủ vùng mà bộ điều khiển sẽ gặp khi triển khai.
- ✅ **Đã thêm giới hạn ‖Π‖ ≤ 5 m/s² cho mọi phương pháp (B-16, Đức chốt).** Gia tốc 300 m/s² của (13) đẩy tầng thấp ra ngoài vùng dữ liệu. 💡 Ràng buộc gia tốc tàu ảo dùng lại được cho CBF.
- ⚠️ **Độ bền theo seed còn yếu.** Dữ liệu tàu thật chỉ khớp với hàm V bậc hai ở mức khoảng 1 % (lực cản và phép quay phi tuyến; nhiễu δ không ảnh hưởng). Sai lệch này đủ làm phép lặp **trôi dần sang một nghiệm Riccati sai dấu**, dù vài vòng đầu vẫn đúng; sai số Bellman *giảm* trong lúc trôi. Giảm chấn không giúp, vì vẫn rơi vào cùng nghiệm. Giảm biên độ kích thích còn làm tệ hơn. Lưới có v_d ≠ 0 tệ hơn lưới chỉ u.
- ✅ **Cách khắc phục được chấp thuận:** kiểm định từng vòng bằng một lần chạy thử không cần mô hình, chọn vòng tốt nhất, chỉ chấp nhận nếu tốt hơn chính sách hành vi, nếu không thì thu thêm lô (tối đa 5). Trên các seed khó: 0, 2, 3 ổn; 4 vẫn hỏng. Điều kiện "xong" là khoảng 80 % trên 10 seed (Đức, 27/11). Xem HANDOFF.md.
- 💡 **Đóng góp của bài nằm ở tầng cao (CBF trên tàu ảo).** Tầng thấp chỉ cần bán kính sai số bám ε bị chặn và đo được. Mốc 6 phải log ε(t). Nếu IRL chưa ổn, làm CBF trên M1 trước (Đức, 27/11).
- ✅ **Mốc 5 xong: Case 1 đạt 10/10 seed** (`results/moc5_irl/case1_seeds_table.md`, log `experiments/moc5/seeds_case1.log`). Tiêu chí đặt trước khi chạy: đủ 40 s không phân kỳ, và ε(t) = max_i ‖p_i − p_d,i‖ ≤ 1 m với t ≥ 5 s. Kết quả ε_max(t ≥ 5) = 0.12–0.60 m (M1: 0.13 m); RMSE bearing 0.114–0.118 (M1: 0.1165). 8/10 seed chấp nhận ở cả hai follower sau 1–3 lô. Seed 4 và 7: SV3 hết 5 lô vẫn không thắng chính sách hành vi (J/J_hv = 2.96 và 1.82), nhưng vòng tốt nhất vẫn ổn định và triển khai được, với ε lớn nhất trong nhóm (0.48 và 0.60 m).
- ✅ **Case 2 cũng đạt 10/10** (`results/moc5_irl/case2_seeds_table.md`): ε_max(t ≥ 5) = 0.11–0.66 m (M1: 0.13 m), RMSE 0.120–0.137 (M1: 0.122). Có 4 seed mà một follower hết 5 lô vẫn chưa được chấp nhận, nhưng vẫn triển khai ổn. Pha học không phụ thuộc case (cùng ψ₀ và cùng lưới), nên trọng số của SV3 và SV4 trùng nhau giữa hai case với cùng seed.
- ⚠️ **Đỉnh lực của IRL lớn hơn M1 nhiều:** max|τ| = 1.3·10⁴ đến 9.7·10⁴, so với khoảng 4·10³ của M1. Đỉnh nằm ở quá độ đầu (khuếch đại cỡ 10⁴, đúng như R = diag(1/τ_nom²) dự đoán). Tổng ∫|τ| chỉ lớn hơn M1 khoảng 7–15 %. Phải báo cáo ở Mốc 6; nếu cần, đây là chỗ để thêm bão hòa lực (chưa làm).
- ⚠️ **Sai số bám xác lập của IRL còn lớn:** |z_υ| t > 30 khoảng 0.1–0.5 m/s, cùng bậc với M1. ε bị chặn nhưng không về 0; đủ cho giai đoạn 2 (chỉ cần ε bị chặn và đo được).
- ✅ **Mốc 3 đã chạy lại với a_max = 5** (`results/moc3_m1/table.md`): Case 1 M1 RMSE 0.1165, xác lập 6.65 s, ε ≈ 0.13 m. 💡 Với k_v = 0.1 của Paper A, khoảng cách nhỏ nhất vẫn tụt còn 0.16 m (Case 1, t = 35.6 s) và 1.41 m (Case 2), dù đã giới hạn gia tốc. Đây là động lực trực tiếp cho CBF.

## Mốc 6: Case 1 và Case 2, M1 so với IRL (làm gọn)

- ✅ Bảng: `docs/moc6_table.md`. Hình: `docs/figures/moc6/`. ε(t) của M1 và 10 seed IRL lưu ở `results/moc6/<case>_eps.npz` (đầu vào cho giai đoạn 2).
- 💡 **IRL không thắng M1 về bearing** (RMSE 0.117 so với 0.116 ở Case 1; 0.122 so với 0.122 ở Case 2), trái với Bảng 1 của Paper A. Nó bám vị trí còn kém hơn: ε_max khoảng 0.2–0.5 m so với 0.13 m. Ưu điểm duy nhất thấy được là z_υ,r xác lập nhỏ hơn. Báo cáo trung thực; điều này không ảnh hưởng đóng góp chính, vốn nằm ở tầng cao.
- ✅ **Đỉnh lực 10⁴–10⁵ N của IRL chỉ nằm ở bước t = 0**: ω_d nhảy bậc nên z_r ≈ 7 rad/s, nhân với khuếch đại lớn. Với t ≥ 0.1 s, max|τ| bằng 1.5–6 lần M1.
- ⚠️ **Thời gian xác lập theo ngưỡng 0.01 không bền** (Case 2 IRL: trung vị 26 s, dù đường cong gần như trùng M1). Báo kèm, nhưng không dùng để kết luận.
- ⚠️ Chưa chạy lại bảng biến thể của IRL (basis_literal, R_identity, init_zero) với quy trình mới. Không bắt buộc cho giai đoạn 2.
- 💡 **Cho CBF:** với các tham số chính, d_min ≈ 9 m (bằng cạnh đội hình), nên kịch bản gốc không có xung đột. Giai đoạn 2 cần kịch bản có vật cản hoặc k_v = 0.1 (d_min = 0.16 m) để CBF có việc làm. Biên an toàn phải cộng thêm ε, khoảng 0.7 m cho IRL hoặc 0.15 m cho M1.
