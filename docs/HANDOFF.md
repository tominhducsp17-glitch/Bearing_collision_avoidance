# Bàn giao cho phiên làm việc tiếp theo (27/11/2026)

Đọc theo thứ tự: `PROJECT_CONTEXT.md` → `PLAN.md` → file này → `docs/findings.md` → `docs/assumptions.md`.

## Trạng thái

| Mốc | Trạng thái |
| --- | --- |
| 0. Kế hoạch, khảo sát code và tài liệu | ✅ |
| 1. Mô hình tàu, hình học bearing | ✅ |
| 2. Tầng cao riêng (bám hoàn hảo) | ✅ |
| 3. Chạy kín với M1 | ✅ (chưa chạy lại sau khi thêm a_max = 5) |
| 4. IRL trên bài toán đồ chơi | ✅ |
| 5. IRL trên tàu | 🔶 đang làm, **giới hạn tối đa 1 phiên nữa** |
| 6. Case 1, Case 2 và báo cáo | ⏳ làm gọn |
| Giai đoạn 2: CBF trên tàu ảo | ⏳ đóng góp chính của bài |

## Quyết định của Đức (27/11/2026)

1. **Đóng góp của bài nằm ở tầng cao (CBF trên tàu ảo), không nằm ở tầng thấp.** Tầng thấp chỉ cần có bán kính sai số bám ε bị chặn và đo được. Không mở nhánh cải tiến cơ sở hàm, và không coi các sửa đổi ở tầng thấp là đóng góp.
2. **Quy trình Mốc 5 được chấp thuận:** học bằng Algorithm 2 từ chính sách hành vi; **sau mỗi vòng, kiểm định bằng một lần chạy thử không cần mô hình** (5 s, tham chiếu chạy đều, sai số ban đầu cố định, không nhiễu thăm dò, chi phí có chiết khấu (22) bỏ số hạng d); chọn vòng có chi phí kiểm định thấp nhất; **chỉ chấp nhận nếu chi phí đó thấp hơn chi phí của phần P trong chính sách hành vi** (J ≈ 282); nếu không đạt thì thu thêm một lô dữ liệu (seed mới, nối vào dữ liệu cũ), tối đa 5 lô.
3. **Điều kiện "xong" của Mốc 5:** chạy 10 seed; đạt nếu khoảng 80 % seed triển khai đủ 40 s, hệ bị chặn, và ε bị chặn. Seed hỏng thì báo cáo đúng như vậy, không chỉnh tiếp cho đến khi đạt 100 %.
4. **Giới hạn thời gian:** tối đa 1 phiên nữa cho Mốc 5. Hết thời gian thì dùng quy trình tốt nhất đang có và chuyển tiếp.
5. **Mốc 6 làm gọn:** Case 1 và Case 2 với M1 và IRL; hình, bảng chỉ số, các điểm lệch; **log thêm ε(t) = max_i ‖p_i − p_d,i‖** cho giai đoạn 2. Không tái tạo từng hình của bài.
6. **Nếu IRL vẫn chưa ổn, phát triển CBF trên M1 trước**, vì bộ lọc đặt trên Π độc lập với tầng thấp; cắm IRL vào sau.

## Việc cần làm ngay ở phiên mới

1. Đưa quy trình kiểm định và chấp nhận vào code chính thức. Hiện nó nằm ở `experiments/moc5/irl_select.py` và `irl_select2.py` (hàm `val_cost`). Vị trí đề xuất: `src/sim/episodes.py` (chạy thử kiểm định) và `scripts/run_irl.py` (vòng lặp lô dữ liệu). Thay lưới pha 1 trong config bằng **lưới chỉ u**: u_d ∈ {5, 5.66, 6.3}, v_d = 0, ω_d = 0, lặp 3 lần. Lưới có v_d ≠ 0 cho kết quả tệ hơn.
2. Chạy 10 seed trên Case 1 và báo tỉ lệ đạt.
3. Chạy lại Mốc 3 (M1) với a_max = 5 (`scripts/run_m1.py`) để có baseline nhất quán.
4. Mốc 6 làm gọn như trên, rồi chuyển sang giai đoạn 2.

## Kết quả thử nghiệm quan trọng của Mốc 5 (chi tiết trong findings.md)

- Thử nghiệm kiểm định và chọn vòng: các seed từng phân kỳ (0, 2, 3, 4) đều chạy đủ 40 s. Seed 2 và 3 tốt (z_υ ≈ 0.1). Khi thêm tiêu chí chấp nhận và tối đa 3 lô, seed 0 ổn; seed 4 vẫn hỏng ở SV4.
- Log của các thử nghiệm: `experiments/moc5/*.log`. Script: `experiments/moc5/*.py` (chạy từ gốc repo).
- `scripts/run_irl.py` hiện **chưa có** bước kiểm định. Lần chạy chính thức trước đó, với lưới u × v và không kiểm định, phân kỳ ở mọi biến thể (`experiments/moc5/run_irl.log`).

## Lưu ý kỹ thuật

- Code nặng nên chạy nền và theo dõi (Đức muốn được cập nhật chủ động). Mỗi seed mất khoảng 40–250 s.
- Đừng dùng `pkill -f <tên script>` trong cùng lệnh với tên đó: nó tự giết chính shell (exit 144).
- `results/` nằm trong `.gitignore`. Hình chọn lọc để xem trên GitHub đặt ở `docs/figures/`.
