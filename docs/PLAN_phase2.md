# PLAN giai đoạn 2: tầng an toàn CBF trên tàu ảo (Mốc 7–11)

Lập ngày 27/11/2026, dựa trên đề xuất của Đức (bảng Mốc 7–11) và kết quả Mốc 5–6. **Cập nhật lần 1 (27/11, sau Mốc 7):** thêm quy trình chỉnh α (Mốc 8), thiết kế lại Mốc 9 (β là biến quyết định), thêm Mốc 9b, bổ sung baseline cho Mốc 10, và thêm §4 (phát biểu định lý dự kiến). Khảo sát liên quan: `docs/related_work.md`. Các mục đánh **[CHỐT]** cần Đức duyệt trước khi code mốc tương ứng. Số liệu kịch bản ở §3 là bản nháp do agent đề xuất.

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

### Mốc 7: CBF giữa các tàu (kịch bản S0) — ✅ xong 27/11 (`docs/moc7_table.md`)

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

**Biên ε: phương án 1 (Đức chốt 27/11).** ε được hiệu chuẩn **riêng cho từng kịch bản**: chạy kịch bản đó không lọc (cùng hệ số tầng cao, cùng a_max), lấy sup_t ε(t) trên mọi seed, cộng 10 % dự phòng. Kiểm (c) (ε thật ≤ ε giả định) vẫn chạy ở mọi lượt có lọc; lượt nào trượt (c) thì báo cáo đúng như vậy. Riêng S0: khoảng 2.0 m (IRL) và 0.2 m (M1); cần chạy lại Mốc 7 với các giá trị này.

**Quy trình chỉnh α₁, α₂ (theo Nhận xét 1 của [Mol21]: tăng α dần từ nhỏ).** Ý nghĩa của điều kiện λ > α trong cascade của ta: α càng lớn thì tàu ảo được phép tiến lại gần biên càng nhanh, nên Π đổi càng gắt, và tầng thấp (tốc độ hội tụ λ) càng khó bám kịp; khi đó ε thật tăng lên và có thể vượt ε giả định.
1. Giữ tỉ lệ α₂ = 2α₁, quét α₁ ∈ {0.125, 0.25, 0.5, 1, 2, 4, 8} (1/s).
2. Với mỗi α₁: chạy S0 trên M1 và trên 10 seed IRL. Ghi lại: (a) d thật ≥ d_min; (c) ε thật ≤ ε giả định; số bước QP vô nghiệm; mức bảo thủ (d nhỏ nhất đạt được trừ D); RMSE bearing.
3. **Ngưỡng mất an toàn α₁\*** là giá trị nhỏ nhất làm (a) hoặc (c) trượt ở ít nhất một seed. Chọn α₁ là giá trị lớn nhất trong lưới còn nhỏ hơn α₁\* (ít bảo thủ nhất mà vẫn an toàn). Báo cả α₁\* của M1 và của IRL: IRL bám chậm hơn (λ nhỏ hơn) nên α₁\* dự kiến nhỏ hơn.
4. Ước lượng λ của từng tầng thấp từ trị riêng của vòng kín tuyến tính hóa (M1: từ hệ số; IRL: từ W_a học được), và đối chiếu với α₁\*. Đây là kiểm tra thực nghiệm của điều kiện λ > α trong cascade bậc hai; ta không có định lý cho nó (§4, chỗ chưa chắc U1).
5. Lặp lại bước 2 trên S1–S3 với α đã chọn; nếu trượt thì quét lại trên kịch bản đó.

Code:
- `Environment`: bờ kênh là chuỗi đoạn thẳng, mỗi bờ một đường gấp khúc; vật cản tròn tĩnh; vật cản tròn động với vận tốc hằng, coi là đo được.
- HOCBF với bờ: h = n_kᵀ(p − a_k) − D, n_k là pháp tuyến trong của đoạn gần nhất. Bậc tương đối 2, tuyến tính theo Π. Chỗ đoạn thẳng nối nhau phải xử lý để không nhảy ràng buộc (dùng mọi đoạn trong một cửa sổ phía trước, hoặc làm trơn góc).
- HOCBF với vật cản tròn: như cặp tàu, nhưng vật cản không phản ứng. Với vật cản động thì có thêm ∂h/∂t.
- Leader: thiết kế kênh để quỹ đạo leader nằm trong kênh với lịch co giãn cố định (Đức duyệt phương án (a), 27/11). Từ Mốc 9 thì β của leader lo phần này.

Kiểm: S1, S2, S3 với lịch co giãn cố định (63), không lọc và có lọc. Kết quả dự kiến: có lọc thì không va chạm, nhưng ở S1 đội hình bị méo nặng hoặc kẹt. Kết quả này là động lực cho Mốc 9.

### Mốc 9: co giãn do an toàn quyết định và thoát deadlock (S1, S2) — **thiết kế lại**

Ý chính (đóng góp Đ1 trong `related_work.md`): **tốc độ co giãn β(t) là biến quyết định trong một QP của leader**, chịu các ràng buộc an toàn thật, thay vì do một lịch cố định (63) hoặc một heuristic quyết định.

Mô hình: leader là điểm động học theo (9), ṗ_l = v_c + β(p_l − c), và ċ = v_c. Vị trí đích của mọi tàu (kể cả follower, vì p\*_f = −B_ff⁻¹B_fl p_l là tuyến tính) cũng thỏa ṗ\*_k = v_c + β(p\*_k − c). Kích thước s của đội hình đích thỏa ṡ = β s. Mọi ràng buộc dưới đây đều tuyến tính theo β và có bậc tương đối 1, vì β đi thẳng vào vận tốc.

QP của leader, mỗi bước:

    β* = argmin (β − β_nom)²   (β_nom kéo s về s_nom khi kênh đủ rộng)
    s.t. bờ kênh:     n_wᵀ(v_c + β(p*_k − c)) ≥ −α_w (n_wᵀ(p*_k − a_w) − D_w,k)   cho mọi tàu k và mọi đoạn bờ w gần
         vật cản:     tương tự, với khoảng cách tới tâm vật cản (vật cản động thì có thêm số hạng vận tốc của nó)
         tỉ lệ:       β s ≥ −α_s (s − s_min)                                  (s ≥ s_min, với s_min đủ để mọi cạnh ≥ D)
         tốc độ:      |β| ≤ β_max                                              (để follower vẫn bám được với ‖Π‖ ≤ a_max)

D_w,k = d_safe + ε_k cho follower và d_safe cho leader. Lớp CBF-QP của follower ở Mốc 7–8 giữ nguyên, chạy sau QP của leader.

- **Phát biểu khả thi (Định lý 2 ở §4):** nếu tâm c đi trong kênh với khoảng hở đủ lớn, và kênh ở chỗ hẹp nhất vẫn chứa được đội hình ở kích thước s_min cộng biên, thì luôn tồn tại β đủ âm thỏa mọi ràng buộc bờ và vật cản cho tới khi chạm s_min.
- **Thoát deadlock bằng co đội hình:** phát hiện theo sự kiện (ý của (57)–(58) Paper B, nhưng không kiểm Q = 0 tuyệt đối): vận tốc theo hướng tiến nhỏ hơn v_th trong T_dl giây khi còn xa đích, **hoặc** QP của follower vô nghiệm hay gần vô nghiệm. Khi đó hạ β_nom (co chủ động); không xoay đích π/5 như Paper B. Có thời gian tối thiểu giữa hai sự kiện (không Zeno). Nếu co tới s_min mà vẫn kẹt (vật cản nằm đúng trục đối xứng ở S2) thì dùng phương án dự phòng: cho phép QP của leader giảm thêm tốc độ tiến |v_c|, hoặc lệch đích về một phía đã định; ghi rõ là trường hợp hiếm.
- **Khác [Zha24] ở đâu (ghi vào bài):**
  1. Ở [Zha24], tỉ lệ do kích thích môi trường f_i (lực đẩy kiểu trường thế, công thức (35) của họ) quyết định, còn HOCBF chỉ ràng buộc *chính biến tỉ lệ* (κ ≥ κ_min, chặn biên độ). Ở ta, β được chọn *trực tiếp* sao cho khoảng cách thật tới bờ và vật cản thỏa HOCBF.
  2. [Zha24] không có định lý an toàn với vật cản; ta có (Định lý 1 cộng Định lý 2).
  3. [Zha24] coi robot bám hoàn hảo p_d; ta có biên ε của tầng thấp không cần mô hình.
  4. [Zha24] phân tán (DAT); ta tập trung ở leader. Đây là điểm yếu của ta, phải nêu thẳng; mở rộng phân tán là hướng sau.
  5. [Zha24] dùng tịnh tiến để né; ta chỉ dùng co giãn (cộng giảm tốc dự phòng).

Kiểm: S1 qua được chỗ thắt mà không va chạm, đội hình co rồi giãn lại, sai số bearing trở về; S2 không kẹt. Báo thời gian qua kênh, kích thước nhỏ nhất, số lần QP vô nghiệm (cả của leader lẫn follower).

### Mốc 9b: so sánh ba cách đưa sai số bám vào biên an toàn

Cùng kịch bản S1 (và S0), cùng α, cùng tầng thấp (M1, IRL):

| Cách | Biên | Điều kiện cần | Rủi ro |
|---|---|---|---|
| (i) ε cố định đã hiệu chuẩn | D = d_min + ε_i + ε_j (hằng) | ε thật ≤ ε giả định trên cả lớp tham chiếu mà CBF sinh ra; chỉ cần tầng thấp **UUB** | bảo thủ khi bám tốt; ε phụ thuộc kịch bản (đã thấy ở Mốc 7) |
| (ii) ε(t) có chặn Lipschitz | D(t) = d_min + ε̂_i(t) + ε̂_j(t), với ε̂ là bao trên trơn của sai số đo được, và ‖ė‖ ≤ L | đo được p_i thật (có sẵn); chặn L của tốc độ tăng sai số; D(t) khả vi hai lần để dùng HOCBF thay đổi theo thời gian ((31)–(35) của Paper B) | ε̂ phải "dẫn trước" sai số thật: nếu sai số tăng nhanh hơn L thì mất bảo đảm; chọn L theo dữ liệu |
| (iii) h_V của [Mol21] | h_V = h(p_d) − (C_h / k₁)·V(e), với e là sai số bám, V ≥ k₁‖p − p_d‖ | V là hàm Lyapunov thật của tầng thấp: V̇ ≤ −λV + ι(‖d‖); **λ > α**; bộ bám **ISS** (không chỉ UUB). Khi đó chỉ có **ISSf** (Hệ quả 1 [Mol21]): an toàn của một tập nới rộng theo ι/α | xem dưới |

Chọn V cho (iii):
- **M1:** hàm Lyapunov backstepping có sẵn dạng giải tích (½z_ηᵀz_η + ½z_υᵀMz_υ). Có λ và ι tính được từ hệ số và chặn nhiễu. Đây là bản chạy chắc.
- **IRL, dùng critic V̂ = W_cᵀσ(X):** đây là ý mới nhưng **rủi ro cao**. (1) V̂ là hàm giá trị của trò chơi H∞ *có chiết khấu* α = 0.1: nghiệm có chiết khấu không chắc là hàm Lyapunov của vòng kín, và V̂ có thể không giảm dọc quỹ đạo. (2) X có chứa υ_d, nên V̂ không bằng 0 khi sai số bằng 0; phải tách phần phụ thuộc vào z và kiểm tính xác định dương theo z bằng số. (3) Cơ sở hàm bị cắt, sai số khớp khoảng 1 % (Mốc 5), nên k₁, λ chỉ ước lượng được. (4) Tầng thấp IRL chỉ UUB dưới nhiễu δ không tắt dần, nên tốt nhất chỉ được ISSf. Phải kiểm bằng số V̂̇ ≤ −λV̂ + ι dọc các quỹ đạo của Mốc 6 trước khi dùng. Nếu không đạt, ghi lại như một phát hiện âm tính và dùng V của bản tuyến tính hóa.

Chỉ số so sánh: d thật nhỏ nhất, mức bảo thủ, số lần trượt kiểm (c) hoặc kiểm tương ứng, thời gian qua chỗ thắt, kích thước nhỏ nhất phải co tới.

### Mốc 10: so sánh và Monte Carlo (S0–S3)

Bốn phương pháp, cùng tầng thấp (lần lượt M1 rồi IRL):
1. Bài 3 gốc, không lọc.
2. Bài 3 cộng APF: lực đẩy cộng vào Π_nom, có bão hòa a_max. Chỉnh hệ số APF một lần trên S0 theo tiêu chí khách quan, rồi giữ nguyên.
3. Bài 3 cộng CBF đặt trong hàm chi phí: phạt mềm, không phải ràng buộc cứng.
4. Đề xuất của ta: CBF-QP, biên theo ε, cộng co giãn do an toàn quyết định (Mốc 9).
5. **Co giãn kiểu [Zha24]:** kích thích môi trường f_i theo (35) của họ (lực đẩy khi cách bờ hoặc vật cản dưới một ngưỡng), đi qua động học tỉ lệ bậc ba ảo và HOCBF **chỉ trên tỉ lệ** (κ ≥ κ_min, chặn biên độ), với hệ số của họ. Bản tập trung (bỏ DAT, vì leader quyết tỉ lệ) và ghi rõ là đơn giản hóa. Chạy hai biến thể: không có CBF bờ và vật cản (đúng như bài của họ), và có thêm CBF-QP giữa các tàu của ta.

Hai bản bỏ từng phần của đề xuất (ablation):
- **Không biên ε:** D = d_min (coi tầng thấp bám hoàn hảo). Mục đích: cho thấy biên ε là cần thiết, nhất là với IRL.
- **Tỉ lệ cố định:** lịch (63) như Mốc 8, có CBF. Mục đích: cho thấy co giãn do an toàn quyết định là cần thiết ở S1.

Mỗi phương pháp chạy với cả M1 và IRL ở tầng thấp. Monte Carlo: 10 seed IRL (đã có trọng số) × seed nhiễu δ × nhiễu nhỏ ở vị trí ban đầu và vị trí vật cản. Chỉ số: số va chạm (d thật < d_min), d nhỏ nhất với tàu/bờ/vật cản, RMSE bearing, thời gian qua kênh, số lần QP vô nghiệm, Σ∫|τ|, ε lớn nhất.

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

## 4. Phát biểu dự kiến của các định lý

Đây là phát biểu dự kiến kèm các bước chứng minh chính; các chỗ chưa chắc đánh dấu **U1–U6**. Sẽ sửa khi code xong Mốc 8–9.

**Định lý 1 (an toàn của tàu thật).** Xét cascade: tàu ảo p̈_d,i = Π_i (đúng tuyệt đối), Π lấy từ CBF-QP của Mốc 7–8 với biên D_ij = d_min + ε_i + ε_j (tàu–tàu) và D_w,i = d_safe + ε_i (tàu–bờ, tàu–vật cản). Giả sử:
(A1) QP khả thi tại mọi t;
(A2) lúc đầu, tàu ảo nằm trong tập an toàn bậc hai: h(0) ≥ 0 và ψ₁(0) ≥ 0 cho mọi ràng buộc;
(A3) tầng thấp bảo đảm ‖p_i(t) − p_d,i(t)‖ ≤ ε_i với mọi t ≥ 0.
Khi đó ‖p_i(t) − p_j(t)‖ ≥ d_min và khoảng cách từ tàu thật tới bờ, vật cản ≥ d_safe với mọi t ≥ 0.

Các bước chứng minh: (1) Π thỏa (\*) của HOCBF nên tập C₁ ∩ C₂ bất biến tiến cho tàu ảo (định lý bất biến của HOCBF, Xiao–Belta), suy ra ‖p_d,i − p_d,j‖ ≥ D_ij. (2) Bất đẳng thức tam giác: ‖p_i − p_j‖ ≥ ‖p_d,i − p_d,j‖ − ε_i − ε_j ≥ d_min. Bờ và vật cản: tương tự, với khoảng cách có dấu là hàm 1-Lipschitz theo vị trí.

Chỗ chưa chắc:
- **U1 (vòng luẩn quẩn của A3).** ε phụ thuộc chính tham chiếu mà CBF sinh ra. Định lý 1 của Paper A cho UUB với chặn phụ thuộc vào ‖υ̇_d‖ (tức ‖Π‖ ≤ a_max và ω̇_d) và có thể cả vào tốc độ đổi của Π. Cần chứng minh ε chỉ phụ thuộc a_max và một chặn độ giật (jerk) mà QP bảo đảm; chưa rõ nghiệm QP có Lipschitz theo thời gian với hằng số đủ nhỏ hay không. Hiện A3 được **hiệu chuẩn bằng thực nghiệm** (phương án 1), không chứng minh. Với IRL, UUB chỉ có ở mức thực nghiệm (actor xấp xỉ).
- **U2 (lấy mẫu).** Π giữ hằng trong mỗi bước 1 ms (ZOH), nên bảo đảm liên tục của HOCBF không còn đúng tuyệt đối. Cách xử lý: thêm một biên nhỏ cho sai số lấy mẫu (theo kiểu sampled-data CBF), hoặc chỉ nêu bằng chứng số.
- **U3 (khả thi).** A1 không tự nhiên đúng khi có cùng lúc ràng buộc tàu–tàu, bờ và a_max. Định lý 2 chỉ lo phần của leader; tính "chia sẻ điều khiển" giữa các HOCBF của follower (như Định lý 2 của [Zha24] cho trường hợp của họ) chưa được chứng minh.

**Định lý 2 (khả thi của QP có β).** Xét QP của leader ở Mốc 9, đội hình đích ở kích thước s. Giả sử:
(B1) tâm c(t) = c₀ + v_c t luôn cách mọi bờ ít nhất D_w,max + r_max·s_min, với r_max là bán kính của hình đội hình ở kích thước 1;
(B2) ở mọi điểm của kênh, bề rộng đủ chứa hình đội hình ở kích thước s_min cộng biên D_w hai bên;
(B3) tốc độ bờ áp vào theo phương pháp tuyến, |n_wᵀv_c|, bị chặn bởi β_max·(khoảng cách theo pháp tuyến từ tàu tới c)·(một hằng số hình học), và bởi α_w·(phần dư của biên ở kích thước s_min).
Khi đó với mọi s ∈ [s_min, s_nom] tồn tại β ∈ [−β_max, β_max] thỏa mọi ràng buộc bờ và tỉ lệ; khi s = s_min thì β = 0 là nghiệm khả thi.

Các bước chứng minh: (1) mỗi ràng buộc bờ có dạng a_k β ≥ b_k với a_k = n_wᵀ(p\*_k − c). Tàu nằm giữa c và bờ có a_k < 0, nên β đủ âm làm vế trái đủ lớn. Tàu ở phía bên kia c có a_k ≥ 0, và nhờ B1 chúng cách bờ đủ xa nên b_k ≤ 0 với mọi β ≤ 0. (2) Tập nghiệm của các ràng buộc bờ là một nửa đường thẳng (−∞, β̄], nên giao với β ≥ −α_s(s − s_min)/s khác rỗng khi β̄ ≥ −α_s(s − s_min)/s. B2 và B3 bảo đảm điều này. (3) Tại s = s_min, B2 cho h_k ≥ 0, và B3 cho ḣ_k ≥ −α_w h_k khi β = 0.

Chỗ chưa chắc:
- **U4:** B3 là một giả thiết về hình học kênh so với tốc độ và a_max; phải kiểm nó thật sự đúng với kịch bản S1.
- **U5:** phát biểu trên là cho đội hình *đích* p\*. Tàu ảo của follower lệch khỏi đích trong quá độ bearing, nên ràng buộc bờ của follower (trong QP của follower) vẫn có thể vô nghiệm; cần thêm một biên cho sai số bearing, hoặc chấp nhận chỉ có bằng chứng số.
- **U6:** vật cản đặt đúng trục đối xứng (S2) có thể làm mọi β thỏa ràng buộc nhưng đội hình vẫn không đi qua được: khả thi không có nghĩa là hết deadlock. Phần thoát deadlock (giảm tốc, lệch đích) không nằm trong Định lý 2.

**Định lý 3 (chỉ khi Mốc 9b đạt, bản ISSf theo [Mol21]).** Nếu tầng thấp có hàm Lyapunov V với k₁‖p − p_d‖ ≤ V và V̇ ≤ −λV + ι(‖δ‖∞), và α < λ, thì với biên động h_V của Mốc 9b, tập an toàn nới rộng S_d = {h + ι/α ≥ 0} là bất biến tiến (ISSf). Chứng minh theo Định lý 3 và Hệ quả 1 của [Mol21], thay khâu tích phân đơn bằng HOCBF bậc hai. Phần này mới hoàn toàn, chưa có bản nháp chứng minh: việc nối HOCBF bậc hai với điều kiện λ > α là chỗ khó nhất.

## 5. Rủi ro

- **R1: CBF làm IRL ra ngoài vùng dữ liệu.** IRL học với tham chiếu vận tốc hằng; khi CBF can thiệp, Π đổi gắt và có thành phần ngang lớn, nên sai số bám có thể vượt ε. Cách xử lý: đo ε thật ở mọi lượt chạy; nếu vượt thì tăng ε hoặc giới hạn tốc độ thay đổi của Π (thêm vào QP). Nếu IRL vẫn hỏng thì giữ kết quả trên M1 làm chính (quyết định 6 của Đức).
- **R2: QP vô nghiệm** khi nhiều ràng buộc cùng hoạt động cộng a_max (S1 ở chỗ thắt). Cách xử lý: CBF theo quãng đường hãm, và tầng co giãn của Mốc 9 chủ động làm nhỏ đội hình trước khi tới chỗ thắt.
- **R3: Mốc 8 trước Mốc 9 có leader đi xuyên bờ** (leader không bị lọc). Cách xử lý: hình học kênh ở §3 giữ leader trong kênh, hoặc dùng phương án CBF bậc 1 cho leader (mục [CHỐT] ở Mốc 8).
- **R4: chi phí tính toán.** Mỗi bước 1 ms giải một QP: 40 000 QP cho mỗi lượt chạy, vẫn chấp nhận được với OSQP (warm start). Monte Carlo chạy song song như Mốc 5.

## 6. Thứ tự và mốc kiểm

Làm từng mốc, dừng lại báo cáo sau mỗi mốc. Mỗi mốc có test, cập nhật `findings.md` và `HANDOFF.md`, rồi commit. Thứ tự: 7 (M1 → IRL, ✅) → 8 (kèm chỉnh α) → 9 → 9b → 10 → 11.
