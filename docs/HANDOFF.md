# Bàn giao cho phiên làm việc tiếp theo (27/11/2026)

Đọc theo thứ tự: `PROJECT_CONTEXT.md` → `PLAN.md` → file này → `docs/findings.md` → `docs/assumptions.md`.

## Trạng thái

| Mốc | Trạng thái |
| --- | --- |
| 0–4 | ✅ |
| 5. IRL trên tàu | ✅ 10/10 seed ở cả Case 1 và Case 2 (27/11) |
| 6. Case 1, Case 2 và báo cáo | ✅ làm gọn (`docs/moc6_table.md`, `docs/figures/moc6/`) |
| Giai đoạn 2: CBF trên tàu ảo | ⏳ **làm tiếp từ đây**, đóng góp chính của bài |

## Quyết định của Đức (27/11/2026)

1. **Đóng góp của bài nằm ở tầng cao (CBF trên tàu ảo), không nằm ở tầng thấp.** Tầng thấp chỉ cần có bán kính sai số bám ε bị chặn và đo được. Không mở nhánh cải tiến cơ sở hàm, và không coi các sửa đổi ở tầng thấp là đóng góp.
2. **Quy trình Mốc 5 được chấp thuận:** học bằng Algorithm 2 từ chính sách hành vi; **sau mỗi vòng, kiểm định bằng một lần chạy thử không cần mô hình** (5 s, tham chiếu chạy đều, sai số ban đầu cố định, không nhiễu thăm dò, chi phí có chiết khấu (22) bỏ số hạng d); chọn vòng có chi phí kiểm định thấp nhất; **chỉ chấp nhận nếu chi phí đó thấp hơn chi phí của phần P trong chính sách hành vi** (J ≈ 282); nếu không đạt thì thu thêm một lô dữ liệu (seed mới, nối vào dữ liệu cũ), tối đa 5 lô.
3. **Điều kiện "xong" của Mốc 5:** chạy 10 seed; đạt nếu khoảng 80 % seed triển khai đủ 40 s, hệ bị chặn, và ε bị chặn. Seed hỏng thì báo cáo đúng như vậy, không chỉnh tiếp cho đến khi đạt 100 %.
4. **Giới hạn thời gian:** tối đa 1 phiên nữa cho Mốc 5. Hết thời gian thì dùng quy trình tốt nhất đang có và chuyển tiếp.
5. **Mốc 6 làm gọn:** Case 1 và Case 2 với M1 và IRL; hình, bảng chỉ số, các điểm lệch; **log thêm ε(t) = max_i ‖p_i − p_d,i‖** cho giai đoạn 2. Không tái tạo từng hình của bài.
6. **Nếu IRL vẫn chưa ổn, phát triển CBF trên M1 trước**, vì bộ lọc đặt trên Π độc lập với tầng thấp; cắm IRL vào sau.

## Đã làm ở phiên 27/11 (chiều)

- Kiểm định và chấp nhận đã vào code chính thức: `src/sim/episodes.validation_cost` và `scripts/run_irl.train` (vòng lặp lô). Config: lưới chỉ u, `repeat: 3`, `max_batches: 5`, `select: true`, ε = 1e-5, tối đa 40 vòng. Có test `test_validation_cost_ranks_policies`.
- `scripts/run_irl.py <case> --seeds 10 --workers 10` chạy quét seed. Kết quả ở `results/moc5_irl/<case>_seeds_table.md` và `_seeds.json`; trọng số ở `<case>_seed<s>_W.npz`. Tiêu chí đạt (đặt trước khi chạy): đủ 40 s, và ε(t) ≤ 1 m với t ≥ 5 s. **Case 1: 10/10, Case 2: 10/10.** Mỗi lần quét mất khoảng 10–25 phút với 10 tiến trình.
- `evaluate()` đã log ε(t) = max_i ‖p_i − p_d,i‖ (`tracking_radius`).
- Mốc 3 (M1) đã chạy lại với a_max = 5.
- Mốc 6: `scripts/run_moc6.py` chạy M1 và 10 seed IRL trên cả hai case (khoảng 5 phút). IRL ngang M1 về bearing, kém hơn về ε (0.2–0.5 m so với 0.13 m). Đỉnh lực 10⁴–10⁵ N chỉ có ở bước t = 0. Chuỗi ε(t) lưu ở `results/moc6/<case>_eps.npz`. Xem findings.md, mục Mốc 6.

## Việc cần làm ngay ở phiên mới: giai đoạn 2 (CBF trên Π)

1. Đọc lại PLAN.md (phần giai đoạn 2) và Paper B. Khung sẵn có: `src/safety/` và `safety_filter.filter(Pi_nom, xd, env, t)` trong runner (đang là IdentityFilter).
2. **Kịch bản gốc không có xung đột** (d_min ≈ 9 m bằng cạnh đội hình), nên cần kịch bản để CBF có việc làm: vật cản trên đường, hoặc k_v = 0.1 của Paper A (d_min = 0.16 m), hoặc đội hình co nhỏ. Hỏi Đức nếu chưa có trong PLAN.
3. Biên an toàn trên tàu ảo phải cộng thêm ε: khoảng 0.7 m với IRL (max qua 10 seed) hoặc 0.15 m với M1. Ràng buộc ‖Π‖ ≤ a_max đưa vào QP.
4. Làm CBF trên M1 trước, sau đó cắm IRL vào (trọng số ở `results/moc5_irl/<case>_seed<s>_W.npz`).
5. Không bắt buộc: chạy lại bảng biến thể IRL (`run_irl.py` không kèm `--seeds`).

## Lưu ý kỹ thuật

- Code nặng nên chạy nền và theo dõi (Đức muốn được cập nhật chủ động). Mỗi seed mất khoảng 40–250 s.
- Đừng dùng `pkill -f <tên script>` trong cùng lệnh với tên đó: nó tự giết chính shell (exit 144).
- `results/` nằm trong `.gitignore`. Hình chọn lọc để xem trên GitHub đặt ở `docs/figures/`.
