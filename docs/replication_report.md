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

## Mốc 3: chạy kín với plant thật và baseline M1 (26/11/2026)

Lệnh chạy: `.venv/bin/python scripts/run_m1.py` (khoảng 2.5 phút). Kết quả nằm ở `results/moc3_m1/`; một số hình chọn lọc được chép vào `docs/figures/moc3/`.

Thiết lập:
- Follower là tàu thật theo (1), có nhiễu δ(t). Leader là điểm động học.
- Tầng cao (13) dùng vị trí và vận tốc của tàu thật.
- Tầng thấp gồm backstepping (15)–(17) với β_η = 2, cộng M1 = luật (27) của [L21] với k = (20, 12, 5). Đây chính là (62) của Paper A (B-14).
- τ, Π, ω_d và δ được giữ không đổi trong mỗi bước 1 ms.

### Kết quả

| run | RMSE | IAE | ITAE | xác lập (e < 0.01), s | Σ∫\|τ\| | max\|τ\| | d_min, m | \|z_υ\| khi t > 30 (u, v, r) | max\|z_ψ\| |
|---|---|---|---|---|---|---|---|---|---|
| **case1 / main** | 0.0440 | 0.368 | 0.67 | 3.02 | 1.19e5 | 1.31e4 | 8.99 | 0.16, 0.21, 0.60 | 2.26 |
| case1 / ζ của Paper A | 0.0441 | 0.372 | 0.70 | 3.04 | 1.37e5 | 1.88e4 | 8.99 | **3.01, 1.80, 5.74** | 3.30 |
| case1 / M đầy đủ | 0.0440 | 0.368 | 0.67 | 3.00 | 1.20e5 | 1.03e4 | 8.99 | 0.16, 0.21, 0.61 | 1.41 |
| case1 / k_v = 0.1 | 0.696 | 16.22 | 346.2 | không đạt | 3.92e6 | 2.76e5 | **0.15** | 0.94, 0.21, 2.98 | 2.97 |
| **case2 / main** | 0.0662 | 0.767 | 2.35 | 5.60 | 2.30e5 | 1.42e4 | 8.97 | 0.16, 0.21, 0.60 | 2.74 |
| case2 / ζ của Paper A | 0.0662 | 0.769 | 2.37 | 5.66 | 2.53e5 | 1.42e4 | 8.97 | 3.01, 1.79, 5.73 | 4.02 |
| case2 / M đầy đủ | 0.0662 | 0.767 | 2.35 | 5.61 | 2.35e5 | 1.41e4 | 8.97 | 0.16, 0.21, 0.61 | 2.19 |
| case2 / k_v = 0.1 | 0.374 | 11.72 | 214.6 | không đạt | 1.59e6 | 1.60e5 | 2.28 | 0.18, 0.21, 2.01 | 3.50 |

Paper A báo cáo RMSE của M1 là 0.1136 (Case 1) và 0.2903 (Case 2), và tổng lực khoảng 7.2·10⁵ (Case 1). Như đã ghi ở B-8, các số này không so trực tiếp được.

### Nhận xét và độ lệch so với Paper A

1. **Đã sửa luật đồng thuận góc (assumptions.md, mục 4).** Ban đầu (14) dùng ψ của tàu thật với k_ω = 25. Khi đó ψ_d tích phân một ω_d rất lớn (tới 59 rad/s) trong lúc tàu thật chưa kịp quay, nên z_ψ vọt tới khoảng 12 rad: tàu quay gần 2 vòng. Bản hiện tại dùng ψ_d của tàu ảo và k_ω = 3.
2. **M1 có sai số xác lập đúng bằng δ/k, vì luật (27) không bù nhiễu.** Cụ thể: z_u ≈ 3.05/20 = 0.15 m/s, z_v ≈ 0.21 m/s, z_r ≈ 3/5 = 0.6 rad/s. Từ đó z_ψ ≈ z_r/β_η ≈ 0.3 rad, nên **góc hướng xác lập là khoảng 1.08 rad thay vì π/4**. Hình 6 của Paper A lại cho thấy M1 hội tụ về π/4. Có thể Paper A dùng δ khác cho M1, hoặc M1 của họ có bù nhiễu; điều này chưa rõ.
3. **Với ζ = (0.5, 0.7, 0.5) như Paper A in, M1 hỏng phần góc hướng.** z_υ khoảng 3–6, góc hướng xác lập khoảng 3.65 rad (tàu gần như chạy ngược hướng), tàu thật trễ sau tàu ảo khoảng 1.7 m. Cấu hình chính vì vậy dùng hệ số của [L21].
4. **Quá độ góc hướng ở 2 s đầu** (ψ₃ vọt lên 2.85 rad) đến từ gia tốc tham chiếu rất lớn (‖Π‖ khoảng 300 m/s²). Thêm vào đó, (62) bỏ qua m23, nên lực ngang cỡ 10⁴ N tràn sang kênh yaw. Dùng M đầy đủ giảm max|z_ψ| từ 2.26 xuống 1.41 rad, nhưng không loại hết. Hình 6 của Paper A không có quá độ này.
5. **Sai số bearing gần như không phụ thuộc chất lượng bám của tầng thấp.** RMSE của biến thể ζ (z_υ khoảng 3 m/s) bằng cấu hình chính tới 3 chữ số. Lý do là (13) dùng vị trí tàu thật, nên tàu ảo tự chạy lệch để bù phần trễ của tàu thật. **Hệ quả cho việc so sánh:** chỉ số bearing ở Bảng 1 không phân biệt được tầng thấp tốt hay kém. Khi so các bộ điều khiển (Mốc 6), phải báo thêm z_υ, z_η và tổng lực.
6. **Với k_v = 0.1, hai tàu tiến sát nhau tới 0.15 m** (Case 1, t = 38.3 s), và tổng lực tăng khoảng 30 lần.
7. **Mức lực:** τ_u xác lập khoảng 1100 N (SV3) và 700–1700 N (SV4, thay đổi theo pha co giãn), khớp Hình 9a của Paper A.

### Test

31 test qua. Riêng Mốc 3 kiểm:
- ν = α_v thì ż_η = −β_η z_η;
- α̇_v giải tích khớp sai phân hữu hạn;
- M1 không nhiễu bám về 0;
- z_u xác lập ≈ δ_u/k_u;
- ngoài plant, runner và baselines, không file nào import tham số tàu.

## Mốc 4: IRL trên bài toán đồ chơi biết trước lời giải (26/11/2026)

Lệnh chạy: `.venv/bin/python scripts/toy_irl.py` (khoảng 15 s). Kết quả nằm ở `results/moc4_toy/`. Các test tương ứng ở `tests/test_irl_toy.py` (9 test).

### Cài đặt

- `src/low_level/offpolicy_irl.py` cài phương trình Bellman off-policy (45) và phép lặp (57)–(61) ở dạng tổng quát. Module này không biết gì về tàu.
- Các tích phân trong mỗi khoảng chỉ tính một lần, ở dạng ma trận: ∫w·u·φᵀ, ∫w·φ·φᵀ, ∫w·d·ψᵀ, ∫w·ψ·ψᵀ, với w = e^{−α(τ−t_{j−1})}. Nhờ vậy mỗi vòng lặp chỉ còn các phép nhân ma trận nhỏ. Cách làm theo ý tưởng tích phân Kronecker của OffQLCTS.jl.
- u và d được giữ không đổi trong mỗi bước con (ZOH, giống bộ điều khiển 1 ms của mô phỏng tàu). Tích phân dùng quy tắc hình thang có tính tới ZOH.
- Giải bằng `lstsq` có chuẩn hóa cột, không dùng phương trình chuẩn (61). Mỗi vòng ghi lại hạng và số điều kiện của ρ₁. Nếu ρ₁ thiếu hạng, code dừng và báo `RankDeficientError` (§5.4.5).
- ρ₂ = −∫w·(XᵀQ'X + ûᵀRû − γ²d̂ᵀd̂): dấu theo [M15] (77), không theo (58)–(59) của Paper A (B-5).
- Lời giải chuẩn để đối chiếu (`src/analysis/hinf_reference.py`): nghiệm ARE trò chơi có chiết khấu, tính hai cách (không gian con ổn định của ma trận Hamilton, và scipy với R̄ bất định), cộng phép lặp Kleinman dùng mô hình.

### Kết quả

- **Khớp nghiệm ARE**, sai số tương đối từ 1e-10 đến 1e-7 ở cấu hình mặc định. W_a khớp −K*ᵀ, W_d khớp L*ᵀ.
- **Khớp phép lặp chính sách dùng mô hình ở từng vòng.** Đây là phép kiểm mạnh nhất cho cách dựng ρ₁, ρ₂, kể cả thứ tự Kronecker và dấu.
- Đúng cho: hệ vô hướng ổn định; hệ vô hướng không ổn định (khởi tạo từ chính sách chấp nhận được, đúng phương án dự phòng của mục 8); hệ 2 chiều; hệ 3 chiều có 2 đầu vào và 2 kênh nhiễu.
- **Quét độ nhạy** với T ∈ {1, 10, 50} ms, thời lượng thu {1, 5, 10} s, biên độ thăm dò {0.01 … 10}: cả 36 cấu hình đều đủ hạng, hội tụ sau 6 vòng, sai số P từ 5e-10 đến 3e-4. Sai số tăng theo T², vì ứng với sai số của quy tắc tích phân.
- **Phát hiện thiếu hạng đúng như dự kiến:**
  - Không có nhiễu thăm dò thì code dừng và báo thiếu hạng.
  - **Nhiễu nhiều kênh gần như hằng, với W_d⁽⁰⁾ = 0, cũng làm ρ₁ thiếu hạng.** Đây là minh họa trực tiếp cho rủi ro B-6 khi chuyển sang tàu, vì δ ≈ (3, −2.5, 3).

### Hệ quả cho Mốc 5

1. T = 1 ms như Paper A **không** gây vấn đề điều kiện số khi dữ liệu mô phỏng không có nhiễu đo. Rủi ro chính chuyển sang hai chỗ: (i) hệ phi tuyến bị xấp xỉ bằng cơ sở hàm bị cắt (45 số hạng bậc hai, actor tuyến tính); (ii) khối W_d thiếu hạng vì δ gần như hằng.
2. Hướng xử lý (ii) sẽ thử theo thứ tự:
   (a) đo hạng với dữ liệu đúng như bài;
   (b) khởi tạo W_d⁽⁰⁾ ≠ 0, vì khi đó các cột (d − d̂⁽ᵏ⁾)⊗ψ không còn tỉ lệ với nhau;
   (c) bơm thêm nhiễu thăm dò đã biết vào kênh d (lệch bài, phải ghi rõ).

## Mốc 5: H∞ IRL off-policy trên tàu (27/11/2026)

Quy trình chính thức (`scripts/run_irl.py`, assumptions §1 K1, K4, mục 8):

1. Pha 1: mỗi follower thu dữ liệu riêng, theo từng đợt 5 s, tham chiếu vận tốc thân tàu hằng u_d ∈ {5, 5.66, 6.3} m/s (v_d = ω_d = 0), lặp 3 lần thành 9 đợt mỗi lô. Chính sách hành vi PI cộng nhiễu thăm dò; sai số ban đầu ngẫu nhiên; nhiễu δ(t) của Paper A.
2. Pha 2: Algorithm 2, cơ sở [z; υ_d], R = diag(1/τ_nom²), khởi tạo từ phần P của chính sách hành vi.
3. Kiểm định không cần mô hình sau mỗi vòng (`src/sim/episodes.validation_cost`): chạy thử 5 s, tính chi phí (22) có chiết khấu và bỏ số hạng d. Giữ vòng có chi phí thấp nhất. Chấp nhận nếu chi phí đó thấp hơn chi phí phần P của chính sách hành vi; nếu không thì thu thêm một lô, tối đa 5 lô.

Kiểm độ bền (`--seeds 10`). Tiêu chí đặt trước khi chạy: đủ 40 s, và ε(t) ≤ 1 m với t ≥ 5 s.

| | Case 1 | Case 2 |
|---|---|---|
| Đạt | **10/10** | **10/10** |
| ε_max (t ≥ 5) | 0.12–0.60 m | 0.11–0.66 m |
| Số follower hết 5 lô mà chưa được chấp nhận | 2/20 | 4/40 (vẫn ổn định) |

Bảng chi tiết: `results/moc5_irl/<case>_seeds_table.md`.

## Mốc 6: Case 1 và Case 2, M1 so với IRL (27/11/2026, làm gọn)

`scripts/run_moc6.py` dùng trọng số đã học ở Mốc 5, chạy M1 và 10 seed IRL trên mỗi case. Bảng: `docs/moc6_table.md`. Hình: `docs/figures/README.md` (mục Mốc 6). Chuỗi ε(t) của mọi lượt chạy: `results/moc6/<case>_eps.npz`, đầu vào cho giai đoạn 2.

| Case 1 | M1 | IRL, trung vị [min, max] trên 10 seed |
|---|---|---|
| RMSE bearing | 0.116 | 0.117 [0.114, 0.118] |
| ε_max, t ≥ 5 (m) | 0.131 | 0.208 [0.124, 0.597] |
| Σ∫\|τ\| | 1.16e5 | 1.26e5 [1.24e5, 1.67e5] |
| max\|τ\|, t ≥ 0.1 s | 3.7e3 | 7.5e3 [5.9e3, 1.4e4] |
| d_min (m) | 8.99 | 8.99 |

| Case 2 | M1 | IRL, trung vị [min, max] trên 10 seed |
|---|---|---|
| RMSE bearing | 0.122 | 0.122 [0.120, 0.137] |
| ε_max, t ≥ 5 (m) | 0.131 | 0.479 [0.110, 0.664] |
| Σ∫\|τ\| | 2.40e5 | 2.57e5 [2.53e5, 3.53e5] |
| max\|τ\|, t ≥ 0.1 s | 4.0e3 | 6.3e3 [5.8e3, 2.4e4] |
| d_min (m) | 8.97 | 8.97 |

Các điểm lệch so với Paper A:

- **Paper A cho IRL tốt hơn M1 rõ rệt (Bảng 1). Ở đây hai phương pháp gần như ngang nhau về bearing**, còn IRL bám vị trí kém hơn M1 (ε lớn hơn khoảng 1.5–3.5 lần). Đúng như Mốc 3 đã thấy, chỉ số bearing gần như không nhạy với tầng thấp, vì (13) dùng vị trí tàu thật.
- Ưu điểm của IRL: |z_υ,r| xác lập nhỏ hơn M1 (0.11 so với 0.60 rad/s ở seed đại diện của Case 1), vì có thành phần trên υ_d bù được một phần nhiễu. M1 thì không bù nhiễu.
- Đỉnh lực tại t = 0 (10⁴–10⁵ N) của IRL đến từ việc ω_d nhảy bậc khi khởi động (z_r ≈ 7 rad/s) nhân với khuếch đại cỡ 10⁴. Bỏ bước đầu thì max|τ| chỉ gấp 1.5–6 lần M1.
- Thời gian xác lập theo ngưỡng 0.01 không bền: sai số của cả hai phương pháp dao động quanh ngưỡng này ở các lần co giãn, nên một bướu nhỏ cũng đẩy thời gian xác lập từ khoảng 7 s lên khoảng 26 s (Case 2). Không nên dùng chỉ số này để so sánh.
- Bảng 1 của Paper A tự mâu thuẫn (B-8), nên chỉ so tỉ lệ giữa các phương pháp.
