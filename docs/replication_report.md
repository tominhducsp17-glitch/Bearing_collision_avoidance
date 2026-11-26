# Báo cáo tái tạo Paper A

Ghi theo từng mốc. Mỗi độ lệch so với Paper A đều kèm số mục trong `docs/assumptions.md`.

## Mốc 2: tầng cao riêng, tàu thật bám hoàn hảo tàu ảo (26/11/2026)

Lệnh chạy: `.venv/bin/python scripts/run_highlevel_only.py`. Kết quả nằm ở `results/moc2_highlevel/` (gồm `sweep.md`, `metrics.json` và các file PNG). Thư mục này không đưa lên git; chạy lại lệnh trên là sinh lại được.

Thiết lập: k_p = 30; leader chạy theo (9), dùng R_pᵀ (B-1) và lấy tâm c theo đội hình đích (B-2); lịch co giãn (63); đồng thuận góc theo [L21] với k_ω = 25; η_d(0) = η(0) (B-7); RK4, dt = 1 ms, Π giữ không đổi trong mỗi bước.

### Kết quả quét k_v

Sai số bearing e = sqrt(Σ‖g − g*‖²), tính trên 40 s:

| run | xác lập (e < 0.01), s | RMSE | IAE | e(40) | max‖Π‖, m/s² | max‖Π‖ khi t > 1 s | d_min, m (tại t) |
|---|---|---|---|---|---|---|---|
| case1, k_v = 0.1 (Paper A) | không đạt | 0.386 | 9.57 | 4.8e-2 | 225 | 206 | **0.29 (4.4 s)** |
| case1, k_v = 5 | 8.24 | 0.077 | 0.95 | 4.0e-4 | 245 | 30.3 | 3.57 (1.6 s) |
| case1, k_v = 10 | 5.18 | 0.046 | 0.48 | 3.5e-4 | 265 | 19.9 | 6.59 (1.6 s) |
| **case1, k_v = 20** | **3.02** | **0.044** | **0.37** | 3.6e-4 | 305 | **16.6** | 8.99 (40 s) |
| case1, k_v = 40 | 4.92 | 0.058 | 0.63 | 3.8e-4 | 468 | 27.4 | 8.99 (40 s) |
| case2, k_v = 0.1 (Paper A) | không đạt | 0.327 | 10.27 | 2.3e-1 | 255 | 168 | 3.24 (2.4 s) |
| case2, k_v = 5 | 24.0 | 0.101 | 1.96 | 9.8e-4 | 276 | 18.7 | 5.03 (2.8 s) |
| case2, k_v = 10 | 29.7 | 0.073 | 1.25 | 2.0e-3 | 297 | 11.5 | 6.62 (3.0 s) |
| case2, k_v = 20 | 26.6 | 0.059 | 0.78 | 1.2e-3 | 338 | 17.4 | 8.90 (3.0 s) |
| **case2, k_v = 40** | **5.63** | 0.066 | 0.77 | 1.4e-3 | 422 | 20.4 | 8.97 (40 s) |

### Chọn k_v (assumptions.md §1, K2)

- **Case 1: k_v = 20.** Đây là giá trị nhỏ nhất làm mode chậm nhất đạt ζ ≥ 0.7. Nó cũng cho RMSE, IAE, thời gian xác lập và ‖Π‖ (khi t > 1 s) đều nhỏ nhất.
- **Case 2: k_v = 40.** Chỉ giá trị này cho thời gian xác lập ngắn (5.6 s). Với k_v từ 5 đến 20, mode có λ_min = 0.039 dao động kéo dài 24–30 s. RMSE của k_v = 40 cao hơn k_v = 20 một chút (0.066 so với 0.059), nhưng chênh lệch đó đến từ quá độ ban đầu chậm hơn, không phải từ dao động kéo dài.
- Dùng k_v khác nhau cho hai case là lệch so với Paper A, vốn dùng chung một bộ hệ số. Lựa chọn này sẽ được kiểm lại trong vòng kín ở Mốc 3 và Mốc 5.

### So với Paper A

1. **k_v = 0.1 không tái tạo được Hình 3 và Hình 5.** Đội hình dao động suốt 40 s; đường đi của follower ngoằn ngoèo (`case1_kv0.1_trajectories.png`). Ở Case 1, **hai tàu tiến sát nhau tới 0.29 m lúc t = 4.4 s**, tức gần như va chạm. Đây là bằng chứng thứ tư cho thấy giá trị in trong bài sai. Các bằng chứng trước: phân tích cực, so sánh với [Z23], và điều kiện của Định lý 1.
2. **Gia tốc tham chiếu ban đầu rất lớn**, ‖Π‖ khoảng 225–470 m/s² trong khoảng 1 s đầu, do k_p = 30 nhân với sai lệch vị trí ban đầu cỡ 10–20 m. Điều này phù hợp với các quá độ rất lớn ở Hình 8, 17, 20 của Paper A (z_υ tới hàng trăm, τ tới cỡ 10⁵).
3. **Kích thước đội hình** bám đúng lịch (63): đỉnh = 2.99 × giá trị ban đầu. Khi bỏ hệ số 1/n, các giá trị 12.73 và 38.05 khớp Hình 12a.
4. **Sai số dư khoảng 1e-3 trong các pha co giãn**, kể cả khi k_v lớn. Khi β ≠ 0, leader có gia tốc, nhưng luật (13) không có thành phần bù gia tốc như luật (10) của Zhao & Zelazo. Đây là hệ quả trực tiếp của việc Giả thiết 1 bị vi phạm (mục 12), không phải lỗi cài đặt.
5. **Động lực cho phần CBF:** ngay cả khi bám hoàn hảo, nếu cản kém (k_v ≤ 10) thì khoảng cách nhỏ nhất giữa các tàu vẫn tụt xuống còn 3.6–6.6 m trong quá độ, trong khi đội hình đích có cạnh 9 m.

### Test

26 test qua (`.venv/bin/python -m pytest -q`). Riêng Mốc 2 kiểm:
- lịch (63);
- tâm đội hình đích chạy đúng v_c;
- s(p*) = s₀·exp(∫β);
- p̈_d = Π, cả theo giải tích lẫn trên số liệu log;
- đồng thuận góc hội tụ;
- khi leader đứng yên, k_v = 20 cho hội tụ còn k_v = 0.1 thì không;
- hook của bộ lọc an toàn được gọi thật.
