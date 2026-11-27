# PLAN giai đoạn 2: tầng an toàn CBF trên tàu ảo (Mốc 7–11)

Lập ngày 27/11/2026, dựa trên đề xuất của Đức (bảng Mốc 7–11) và kết quả Mốc 5–6. Các mục đánh **[CHỐT]** cần Đức duyệt trước khi code mốc tương ứng. Số liệu kịch bản ở §3 là bản nháp do agent đề xuất.

Quy ước tên: "bài 3" = Paper A (bearing + H∞ IRL); "bài 6" = Paper B (RHTF-CBF cho multi-QUAV, thoát deadlock bằng chỉnh trạng thái mong muốn).

---

## 1. Kiến trúc (đã có khung, chỉ cắm thêm)

```
[Tầng sinh tham số, Mốc 9]   β(t) theo bề rộng kênh phía trước; co đội hình khi QP khó khả thi hoặc kẹt
        ▼
[Tầng cao, bài 3]            luật (13) → Π_nom (đã bão hòa ‖Π‖ ≤ a_max)
        ▼
[Bộ lọc CBF-QP, Mốc 7–8]     Π = argmin Σ_i ‖Π_i − Π_nom,i‖²  s.t. HOCBF (tàu–tàu, tàu–bờ, tàu–vật cản), ‖Π_i‖ ≤ a_max
        ▼
[Tầng thấp]                  M1 hoặc IRL (trọng số Mốc 5), tàu thật bám tàu ảo với sai số ≤ ε
```

- Điểm cắm có sẵn: `safety_filter.filter(Pi_nom, xd, env, t)` trong `src/sim/runner.py`, giao diện ở `src/safety/base.py` (`Environment.banks`, `.obstacles`). Hiện dùng `IdentityFilter`.
- Tàu ảo có p̈_d = Π đúng tuyệt đối (runner giữ Π không đổi trong mỗi bước, Mốc 2). Vì vậy khoảng cách là hàm có **bậc tương đối 2 theo Π**, dùng được HOCBF bậc 2 mà không cần bộ quan sát nhiễu.
- **Biên an toàn theo ε.** Giữ tàu ảo cách nhau D_ij = d_min + ε_i + ε_j thì tàu thật cách nhau ít nhất d_min (bất đẳng thức tam giác). Với bờ và vật cản: D = d_safe + ε_i. Leader là điểm động học, bám hoàn hảo, nên ε_leader = 0.
- Giá trị ε lấy từ Mốc 6 (`results/moc6/<case>_eps.npz`, sup theo mọi t và mọi seed): **M1 ≈ 0.15 m, IRL ≈ 0.9 m** (đỉnh quá độ Case 2 khoảng 0.86 m). Phải **đo lại ε ở mọi lượt chạy có CBF**, vì CBF làm Π đổi đột ngột và có thể đẩy sai số bám lên (xem rủi ro R1).

## 2. Các mốc

### Mốc 7: CBF giữa các tàu (kịch bản S0)

Code:
- `src/safety/cbf.py`: HOCBF bậc 2 cho một cặp, h = ‖p_i − p_j‖² − D², ψ₁ = ḣ + α₁h, điều kiện ψ̇₁ + α₂ψ₁ ≥ 0. Điều kiện này tuyến tính theo (Π_i, Π_j). Dạng có thành phần thay đổi theo thời gian theo (31)–(35) của bài 6, dùng lại ở S3.
- `src/safety/qp_filter.py`: QP **tập trung** trên mọi follower (biến 2·n_f, tức 4 hoặc 8 biến), giải bằng OSQP hoặc quadprog. Ràng buộc ‖Π_i‖ ≤ a_max là ràng buộc nón, nên thay bằng **đa giác nội tiếp 16 cạnh** (sai lệch dưới 2 %) để vẫn là QP. Bản phân tán (mỗi tàu nhận nửa trách nhiệm, như bài 6) là mở rộng sau, không làm ở Mốc 7.
- Cặp leader–follower: leader không bị lọc, gia tốc của nó tính được từ (9). Follower nhận toàn bộ trách nhiệm.
- Log mỗi bước: h_ij nhỏ nhất, các ràng buộc đang hoạt động, ‖Π − Π_nom‖, trạng thái QP (khả thi hay không), d thật nhỏ nhất, ε(t).

Kiểm:
- Test đơn vị: hai chất điểm tích phân kép lao vào nhau, h ≥ 0 tại mọi bước; khi không có xung đột thì QP trả đúng Π_nom.
- S0, trên M1 trước: không lọc thì d_min = 0.16 m (đã đo ở Mốc 3); có lọc thì khoảng cách thật phải ≥ d_min, tàu ảo ≥ D. Báo cả RMSE bearing (cái giá của an toàn).
- Sau đó lặp lại S0 với IRL (10 seed).

Nếu QP vô nghiệm (HOCBF cộng giới hạn a_max): trước hết chỉnh α₁, α₂; nếu vẫn vô nghiệm thì đổi sang **CBF tính theo quãng đường hãm** h = ‖Δp‖ − D − v_lại_gần²/(2·a_hãm). Không dùng slack để che vô nghiệm, vì đó là điểm yếu của bài 6. Số lần QP vô nghiệm là một chỉ số của bài.

### Mốc 8: bờ kênh và vật cản (S1, S2, S3)

Code:
- `Environment`: bờ kênh là chuỗi đoạn thẳng, mỗi bờ một đường gấp khúc; vật cản tròn tĩnh; vật cản tròn động với vận tốc hằng, coi là đo được.
- HOCBF với bờ: h = n_kᵀ(p − a_k) − D, n_k là pháp tuyến trong của đoạn gần nhất. Bậc tương đối 2, tuyến tính theo Π. Chỗ đoạn thẳng nối nhau phải xử lý để không nhảy ràng buộc (dùng mọi đoạn trong một cửa sổ phía trước, hoặc làm trơn góc).
- HOCBF với vật cản tròn: như cặp tàu, nhưng vật cản không phản ứng. Với vật cản động thì có thêm ∂h/∂t.
- **Leader cũng là tàu**, nhưng hiện là điểm động học theo (9), không qua bộ lọc **[CHỐT]**. Đề xuất: ở Mốc 8, thiết kế kênh để quỹ đạo của leader luôn nằm trong kênh, chỉ follower bị ép; ở Mốc 9, tầng co giãn lo cho leader. Phương án khác: lọc vận tốc leader bằng CBF bậc 1 (leader là khâu tích phân đơn).

Kiểm: S1, S2, S3 với lịch co giãn cố định (63), không lọc và có lọc. Kết quả dự kiến: có lọc thì không va chạm, nhưng ở S1 đội hình bị méo nặng hoặc kẹt. Kết quả này là động lực cho Mốc 9.

### Mốc 9: co giãn thích nghi và thoát deadlock (S1, S2)

Code (`src/high_level/scaling.py`: thay `ScalingSchedule` bằng một đối tượng cùng giao diện `beta_s(t, state)`):
- **Kích thước tham chiếu theo bề rộng kênh phía trước:** s_ref(t) = min(s_nom, (W(x + L_look) − 2(d_wall + ε_max)) / w_shape), với w_shape là bề rộng ngang của hình đội hình đích ở kích thước 1. Chặn dưới s ≥ s_min, với s_min đủ để mọi cạnh của đội hình ≥ D. β(t) bám s_ref qua bộ lọc bậc 1, có giới hạn |β| để a_max vẫn đủ.
- **Phát hiện deadlock theo sự kiện** (ý của (57)–(58) bài 6, nhưng không kiểm Q = 0 tuyệt đối): vận tốc theo hướng tiến nhỏ hơn v_th trong T_dl giây khi vẫn còn xa đích, **hoặc** QP vô nghiệm hay gần vô nghiệm. Khi sự kiện kích hoạt thì giảm s_ref; không xoay đích π/5 như bài 6. Giữ tính không Zeno (thời gian tối thiểu giữa hai sự kiện).
- Nếu co hết cỡ (s_min) mà vẫn kẹt, ví dụ vật cản nằm đúng giữa trục đối xứng ở S2: dùng phương án dự phòng là lệch đích theo một phía đã định, ghi rõ là trường hợp hiếm.

Kiểm: S1 qua được chỗ thắt mà không va chạm, đội hình co rồi giãn lại, sai số bearing trở về; S2 không kẹt. Báo thời gian qua kênh và kích thước nhỏ nhất.

### Mốc 10: so sánh và Monte Carlo (S0–S3)

Bốn phương pháp, cùng tầng thấp (lần lượt M1 rồi IRL):
1. Bài 3 gốc, không lọc.
2. Bài 3 cộng APF: lực đẩy cộng vào Π_nom, có bão hòa a_max. Chỉnh hệ số APF một lần trên S0 theo tiêu chí khách quan, rồi giữ nguyên.
3. Bài 3 cộng CBF đặt trong hàm chi phí: phạt mềm, không phải ràng buộc cứng.
4. Đề xuất của ta: CBF-QP, biên theo ε, cộng co giãn thích nghi.

Monte Carlo: 10 seed IRL (đã có trọng số) × seed nhiễu δ × nhiễu nhỏ ở vị trí ban đầu và vị trí vật cản. Chỉ số: số va chạm (d thật < d_min), d nhỏ nhất với tàu/bờ/vật cản, RMSE bearing, thời gian qua kênh, số lần QP vô nghiệm, Σ∫|τ|, ε lớn nhất.

Phụ (nếu Đức muốn, khoảng nửa phiên): **M1 với mô hình sai lệch** (M, D lệch ±20–30 % so với plant). Mục đích là đặt so sánh M1 với IRL cho công bằng: Paper A có thể đã làm M1 kém đi (Mốc 3: với ζ in trong bài, M1 hỏng góc hướng). Đây không phải đóng góp của bài, chỉ để báo cáo trung thực.

### Mốc 11 (nếu kịp): an toàn trong pha thu dữ liệu (mức 2)

Lọc tín hiệu thăm dò qua CBF-QP khi nhiều tàu thu dữ liệu cùng lúc trong kênh. Kiểm dữ liệu sau lọc vẫn đủ hạng (ρ₁), và IRL học từ dữ liệu đó vẫn qua bước kiểm định của Mốc 5. Chỉ số: số va chạm trong pha thu dữ liệu.

## 3. Thông số đề xuất **[CHỐT]**

| Thông số | Đề xuất | Lý do |
|---|---|---|
| d_min (tàu–tàu, thật) | **2 m** | Khoảng 1.5 lần chiều dài CyberShip II (1.255 m), cộng khoảng đệm |
| d_safe (tàu–bờ, tàu–vật cản) | **1.5 m** | Nửa thân tàu cộng khoảng đệm |
| ε | M1: 0.15 m; IRL: 0.9 m (đo lại ở mỗi lượt) | sup trên Mốc 6 |
| D tàu–tàu (tàu ảo) | M1: 2.3 m; IRL: 3.8 m | d_min + 2ε |
| α₁, α₂ của HOCBF | 1 và 2 (1/s), chỉnh ở Mốc 7 | Đủ khả thi với a_max = 5 trên S0 |
| Bộ giải QP | OSQP (thêm vào requirements) hoặc quadprog | Nhỏ, nhanh, chạy được với dt = 1 ms |

Kịch bản (bản nháp, viết cho Case 1; Case 2 điều chỉnh theo hình chữ nhật 18×9). Trục kênh dọc theo hướng ψ₀ = π/4. Hình vuông 9 m đặt theo trục tọa độ, nên **bề rộng ngang hướng đi là 9√2 ≈ 12.7 m**.

| | Mô tả | Hình học đề xuất | Kết quả mong đợi |
|---|---|---|---|
| S0 | k_v = 0.1 của bài 3, không có môi trường | như Case 1 | không lọc: 0.16 m; có lọc: ≥ 2 m |
| S1 | kênh hẹp dần | rộng 40 m, thu hẹp trong 20 m còn **12 m**, giữ 30 m, rồi mở lại | đội hình 9 m cần 12.7 + 2(1.5 + 0.9) ≈ 17.5 m nên không lọt; co về s ≲ 0.5 thì lọt, cạnh 4.5 m vẫn ≥ D = 3.8 m |
| S2 | vật cản tĩnh giữa kênh | tròn, bán kính 2 m, nằm trên trục kênh ở đoạn rộng | không co: tàu tách hai bên; tâm đặt đúng trục đối xứng để thử deadlock |
| S3 | tàu lạ cắt ngang | tròn, bán kính 1 m, 3 m/s vuông góc trục kênh, canh thời điểm để cắt qua giữa đội hình | follower nhường đường, rồi đội hình tự phục hồi |

## 4. Rủi ro

- **R1: CBF làm IRL ra ngoài vùng dữ liệu.** IRL học với tham chiếu vận tốc hằng; khi CBF can thiệp, Π đổi gắt và có thành phần ngang lớn, nên sai số bám có thể vượt ε. Cách xử lý: đo ε thật ở mọi lượt chạy; nếu vượt thì tăng ε hoặc giới hạn tốc độ thay đổi của Π (thêm vào QP). Nếu IRL vẫn hỏng thì giữ kết quả trên M1 làm chính (quyết định 6 của Đức).
- **R2: QP vô nghiệm** khi nhiều ràng buộc cùng hoạt động cộng a_max (S1 ở chỗ thắt). Cách xử lý: CBF theo quãng đường hãm, và tầng co giãn của Mốc 9 chủ động làm nhỏ đội hình trước khi tới chỗ thắt.
- **R3: Mốc 8 trước Mốc 9 có leader đi xuyên bờ** (leader không bị lọc). Cách xử lý: hình học kênh ở §3 giữ leader trong kênh, hoặc dùng phương án CBF bậc 1 cho leader (mục [CHỐT] ở Mốc 8).
- **R4: chi phí tính toán.** Mỗi bước 1 ms giải một QP: 40 000 QP cho mỗi lượt chạy, vẫn chấp nhận được với OSQP (warm start). Monte Carlo chạy song song như Mốc 5.

## 5. Thứ tự và mốc kiểm

Làm từng mốc, dừng lại báo cáo sau mỗi mốc. Mỗi mốc có test, cập nhật `findings.md` và `HANDOFF.md`, rồi commit. Thứ tự: 7 (M1 → IRL) → 8 → 9 → 10 → 11.
