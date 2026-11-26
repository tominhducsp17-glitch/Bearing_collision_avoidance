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
