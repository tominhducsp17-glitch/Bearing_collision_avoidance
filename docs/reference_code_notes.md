# Ghi chú khảo sát code tham khảo (Mốc 0)

Ngày khảo sát: 26/11/2026. Người viết: coding agent. Người duyệt: Đức.

Hai repo đã được tải về `external/` để đối chiếu. Thư mục này chỉ để đọc và **không** thuộc code của dự án.

| Repo | Đường dẫn local | Ghi chú tải |
| --- | --- | --- |
| HoangAnhMasterDev/Reinforcement-Learning-Based-Control-Framework-for-Leader-Following-Cascade-Formation-of-SVs | `external/repoA/` | `git clone --depth 1`, commit `d05ac0a`. Không có file license. |
| Huy-Quang-Dao/OffQLCTS.jl | `external/offqlcts/` | `git clone` lỗi mạng vì repo chứa khoảng 50 MB file `.mat`, nên chỉ tải 8 file nguồn nhỏ qua raw.githubusercontent (`src/OffQLearningVer1.jl`, `Ver2`, `options.jl`, `problems/F16QlearningVer1.jl`, `comparation1.jl`, README, LICENSE). License MIT. |

Code trong file `.slx` được trích bằng cách giải nén rồi đọc thẻ `<P Name="script">` trong `simulink/stateflow/chart_*.xml`. Cấu hình solver lấy từ `simulink/configSet0.xml`.

---

## 1. Đối chiếu từng phần của repo tiền thân với Paper A

Ký hiệu: **=** giống, **≈** giống một phần hoặc khác chi tiết, **≠** khác hẳn, **∅** repo không có.

| Thành phần Paper A | Trong repo (file / khối) | Đánh giá | Ghi chú |
| --- | --- | --- | --- |
| Mô hình tàu (1)–(2): M, C, D (tr. 18) | `AISMC/C.m`, `D.m`; khối `Subsystem*/Dynamics` | **=** | Trích nguyên văn ở mục 2. Các khối Dynamics của 5 tàu giống hệt nhau (diff chỉ khác dòng trống, tên output). |
| Động học η̇ = J(ψ)υ | `J.m`; khối `Subsystem*/Kinematics` | **=** | |
| Nhiễu δ(t) (tr. 18) | khối `Dynamics`, biến `tau_w` | **≈** | Biểu thức **trùng từng chữ** với Paper A nhưng **đang bị comment**. Nhiễu thực sự được dùng là `noise`: tổng 4 sin tần số cao (20–45 rad/s), chỉ bật khi t < 15 s. Vậy nhiều khả năng Paper A đã bật lại `tau_w`. |
| Tích phân số | AISMC/FXESO: Euler tường minh, `step = 0.001`. Simulink: `SolverName = FixedStepAuto`, `FixedStep = 0.001`, `StopTime = 500` | **≈** | Paper A không nói solver. Bước 0.001 s khớp T = 0.001 s của Paper A. |
| `T_end = 500` | `AISMC.m`, `FXESO.m`, `StopTime` của `.slx` | | Nhiều khả năng đây là nguồn của "∫₀⁵⁰⁰" trong chú thích Bảng 1 (mục 3, ý 11 của PROJECT_CONTEXT). |
| Đồ thị, bearing (6)–(8), B_ff | ∅ | **≠** | Repo dùng leader-following theo **độ dời**: η_r = η_{i−1} + J(ψ_{i−1})·[6cos(2π/3), 6sin(2π/3), 0] (khối `Kinematics Controller/MATLAB Function4`). |
| Leader (9), co giãn (63) | khối `eta_0/MATLAB Function` | **≠** | Leader ảo chạy thẳng 0.5 m/s trong 40 s rồi chạy cung tròn. Không có co giãn, không có β(t). |
| Tầng cao (10)–(14), tàu ảo bậc 2 | ∅ | **≠** | Tầng cao của repo là **prescribed performance** (khối `Kinematics Controller/MATLAB Function1`), sinh vận tốc mong muốn v_d từ sai số đã biến đổi log. Không có tàu ảo bậc 2, không có Π_i. |
| Đồng thuận góc (14) | ∅ | **≠** | |
| Backstepping (15)–(19) | ≈ khối `Kinematics Controller` + `RL controller` | **≈** | Có sai số vận tốc z2 = v − v_d và sai số vị trí đã biến đổi z. Nhưng v_d sinh bởi prescribed performance, không phải α_i = Jᵀ(η)(−β_η z_η + J(η_d)υ_d). |
| Trạng thái mở rộng X (20)–(21) | khối `RL controller/Controller`: `x = [z2; z; eta_r; eta_r_dot]` (12 chiều) | **≈** | Ý tưởng giống: ghép sai số với tín hiệu tham chiếu. Thứ tự khác: **sai số vận tốc đứng trước**. X có 12 chiều thay vì 15. |
| Chi phí (22)–(23), Q | `Q = 100*[eye(6) zeros(6,6); zeros(6,6) zeros(6)]`, R = I; chiết khấu `gamma = 0.01` | **≈** | **Bằng chứng mạnh cho mục 3, ý 1:** nhóm tác giả dùng **100·I₆** trên 6 thành phần sai số. Repo không có số hạng −γ²dᵀd (không phải H∞). |
| Critic / actor | `gradPhi` 15×3, 15 hàm cơ sở chọn tay (6 bậc hai của z2 và 9 tích bậc 4 kiểu x₁²x₇²) | **≠** | Paper A dùng 45 tích bậc hai X(k)X(l), k ≤ l ≤ 9. |
| Học | `Wc_dot`, `Wa_dot`: gradient liên tục, chuẩn hóa | **≠** | Actor-critic **online, on-policy**. Không thu dữ liệu, không bình phương tối thiểu, không lặp chính sách. |
| Nhiễu đối kháng d* (29) | ∅ | **≠** | |
| Lực điều khiển | `tau = tau_d + u`, với `tau_d = M*v_d_dot + C(v_d)*v_d + D(v_d)*v_d` | **≠** | **Có feedforward dùng mô hình đầy đủ M, C, D.** RL chỉ là thành phần bù `u = −½M⁻ᵀ∇Φᵀ W_a`, cũng dùng M. |
| Baseline M1 (62) | ∅ | | Repo không có baseline dựa trên mô hình dạng (62). |
| M3 (AISMC), M4 (FXESO) | `AISMC/AISMC.m`, `FXESO/FXESO.m` | **≈** | Xem mục 3: cả hai đều có chỗ không khớp bài gốc [42], [43]. |
| Chỉ số IAE, ITAE, RMSE | ∅ | | Repo chỉ tính chi phí `costFunction`, và tính sai: `cumsum` trên một số vô hướng thì không cộng dồn. |
| Vẽ hình | `drawGraph.m`, `multiple_xy_graph.m`, `convertData2txt.m` | **≈** | Dữ liệu xuất txt, lấy mẫu mỗi 100 bước (0.1 s). Chỉ tham khảo cách bố trí hình. |

## 2. Tham số plant trích nguyên văn và kết luận

Nguyên văn từ `AISMC/D.m`, `AISMC/C.m`, giống hệt khối `Dynamics` trong `.slx`. Ở đây `v = [u; v; r]`, nên `v(1)` = u (surge), `v(2)` = v (sway), `v(3)` = r (yaw rate).

```matlab
M = [25.8,0,0; 0,33.8,1.0948; 0,1.0948,2.76];

C = [0,0,-33.8*v(2)-1.0948*v(3);
     0,0,25.8*v(1);
     33.8*v(2)+1.0948*v(3),-25.8*v(1),0];

D = [0.7225 + 1.3274*abs(v(1)) + 5.8664*v(1)^2, 0, 0;
     0, 0.8612+36.2823*abs(v(1)) + 0.805*abs(v(3)), -0.1079 + 0.845*abs(v(1)) + 3.45*abs(v(3));
     0, -0.1052 - 5.0437*abs(v(1)) - 0.13*abs(v(3)), 1.9-0.08*abs(v(2))+0.75*abs(v(3))];

v_dot = -M\C*v - M\D*v + M\(tau + noise);       % khối Dynamics
% tau_w = [3-0.2*sin(0.1*t)+0.1*cos(0.02*t)+0.1*rand(1);
%          -2.5 + 0.1*cos(0.1*t) + 0.1*sin(0.02*t) + 0.1*rand(1);
%          3 - 0.2*sin(0.1*t) - 0.1*cos(0.02*t) + 0.1*rand(1)];   % đang comment
```

Đối chiếu với trang 18 của Paper A và CyberShip II (Skjetne 2004):

| Hệ số | Paper A in | Code | CyberShip II | Kết luận |
| --- | --- | --- | --- | --- |
| c13, c31 | ∓(33.8·ϑ + 1.0948·r) | dùng `v(2)` = sway | sway | ϑ trong bản in là **sway v** |
| c23, c32 | ±25.8u | `v(1)` | u | khớp |
| d11 | 5.8664·**v**² | 5.8664·**u**² | u² | theo code: **u²** |
| d22 | 36.2823·\|**u**\| | \|u\| | \|v\| | theo code (= bản in): **\|u\|** |
| d23 | 0.845·\|**u**\| | \|u\| | \|v\| | theo code: **\|u\|** |
| d32 | −5.0437·\|**u**\| | \|u\| | \|v\| | theo code: **\|u\|** |
| d33 | −0.08·\|v\| | \|v\| | \|v\| | khớp |

**Kết luận về plant:** cài đúng như code (`AISMC/D.m`, `C.m`). Chỗ duy nhất code khác bản in là d11 dùng u², và Hình 9 của Paper A xác nhận u². Ở u ≈ 5.66 m/s, công thức u² cho lực cản ≈ 0.72 + 7.5 + 188 ≈ 196 N·s/m, tức ≈ 1110 N, khớp τ_3x ≈ 1100 N ở Hình 9a. Công thức v² chỉ cho khoảng 47 N.

Ghi thêm:
- Plant dùng M đầy đủ, có m23 = m32. M đối xứng, xác định dương: định thức khối 2×2 là 33.8·2.76 − 1.0948² > 0.
- Ở 5.66 m/s, mô hình chạy ngoài dải vận tốc thực của CyberShip II (tàu mô hình dài 1.255 m). Ta không sửa, chỉ ghi lại để hiểu vì sao lực lên tới cỡ 10³ N.
- Trong Simulink, `rand(1)` được gọi ở mỗi lần đánh giá khối, tức mỗi bước 0.001 s. Ta tái tạo bằng một mẫu đều U[0,1) **mỗi bước**, giữ nguyên trong suốt bước tích phân, seed cố định.
- Phương trình plant đúng là `M υ̇ = −Cυ − Dυ + τ + δ`, khớp (1). Biểu thức Θ_i dưới (18) của Paper A viết `C υ − D υ + g_i(η_i)`, lệch dấu và thừa g_i. Chỗ đó chỉ ảnh hưởng phần lý thuyết, không ảnh hưởng plant (xem PLAN, mục 3, ý B4).

## 3. Baseline M3 (AISMC) và M4 (FXESO)

Hai baseline này **chưa làm ở giai đoạn này** (PROJECT_CONTEXT §7.5). Dưới đây ghi lại để dùng sau.

### 3.1 M3: `AISMC/AISMC.m` (bài [42]: M. Van, ISA Trans. 2019)

Tham số trong code: `k1 = 20, k2 = 20, rho = 100, w_hat = 1, gamma = 1, deadzoneSize = 0.01, K = 20, epsi1 = 12, epsi2 = 10, slidingGain = 20, delta_s = 5·I₃` (các tham số `K`, `epsi*`, `slidingGain`, `delta_s` chỉ dùng trong phần DOB đang bị comment), `c = 0.1` không dùng.

Công thức trong code, viết theo hệ trái đất, với Δ = J(η)M⁻¹ và Γ = Δ(C υ + D υ + J̇ ψ̇ υ):
```
z1 = η − η_d,   α1 = −k1 z1 + η̇_d,   z2 = η̇ − α1
u0 = Δ⁻¹ ( −Γ + η̈_d − k1 ż1 − z1 − k2 z2 )            ← dùng M, C, D thật
ud = −Δ⁻¹ δ̂,  δ̂ = tín hiệu sin biết trước (0.1·Σ sin tần số 20–45 rad/s)
σ̇ = −(ρ + ŵ) sign(σ) + δ̂ ,  k̂̇ = |σ|/γ (có vùng chết)
us = −Δ⁻¹ (k̂ + ŵ) ⊙ sign(σ)
τ = u0 + ud + us
plant: υ̇ = M⁻¹(τ − Cυ − Dυ)                          ← KHÔNG có nhiễu
```

Chỗ khác với Paper A hoặc với bài gốc [42]:
1. Plant trong script **không có nhiễu**. "Ước lượng nhiễu" δ̂ là một tín hiệu biết trước, được bù vào τ, trong khi plant không hề có nhiễu đó.
2. Bộ quan sát nhiễu (DOB) bị comment ("Add disturbance observer later"). Mặt trượt σ được tích phân như một ODE riêng, **không nối với trạng thái tàu**. Vậy đây không phải AISMC đầy đủ của [42].
3. Bộ điều khiển dùng mô hình đầy đủ M, C, D.
4. Quỹ đạo là leader-following theo độ dời, không có bearing.

→ **Không thể "cài lại bằng Python, đối chiếu với file này" mà vẫn gọi là [42].** Khi làm M3, phải cài theo bài [42], còn script này chỉ dùng để tham khảo bộ tham số.

### 3.2 M4: `FXESO/FXESO.m` (bài [43]: Zhang, Yu, Yan, Ocean Eng. 2019)

Tham số: `miu1 = 10, epsi1 = 10, miu2 = 20, epsi2 = 20, miu3 = 50, epsi3 = 50, alpha1..3 = 0.8, 0.6, 0.4, beta1..3 = 2.2, 3.4, 2.6, k1 = k2 = 80, gamma1 = 0.3, gamma2 = 2γ1/(1+γ1), Gamma = 5`. Hàm `sig(β, x) = sign(x)|x|^β`.

```
ESO:  η̂̇ = ŵ + μ1 sig^{α1}(η−η̂) + ε1 sig^{β1}(η−η̂)
      ŵ̇ = J M⁻¹ τ + X̂ + μ2 sig^{α2}(η − η_d) + ε2 sig^{β2}(η − η̂)     ← chú ý (η − η_d)
      X̂̇ = μ3 sig^{α3}(η−η̂) + ε3 sig^{β3}(η−η̂) + Γ sign(η−η̂)
Luật:  τ = M J⁻¹ ( −k1 sig^{γ1}(η−η_d) − k2 sig^{γ2}(ŵ − η̇_d) − X̂ + η̈_d )      ← dùng M
plant: υ̇ = M⁻¹(τ + noise − Cυ − Dυ),  noise chỉ bật khi t < 15 s
```

Chỗ khác:
1. Số hạng thứ hai của ŵ̇ dùng `eta − eta_d` thay vì `eta − eta_hat`. Nhiều khả năng đây là lỗi gõ: một ESO chuẩn chỉ dùng sai số quan sát η − η̂. Cần đối chiếu với [43].
2. Nhiễu là `noise` tần số cao chỉ bật trong 15 s đầu, không phải δ(t) của Paper A.
3. Dùng M (chỉ M; C, D được ESO gộp vào X̂).
4. Quỹ đạo là leader-following theo độ dời.

### 3.3 Hai baseline có thật sự là [42] và [43] của Paper A không?

Tiêu đề trong README của repo trùng tên bài [42] và [43] của Paper A. Vậy *định danh* bài là khớp. Còn *cách cài* trong repo thì không trung thành với hai bài đó (mục 3.1, 3.2), và cũng không khớp bối cảnh bearing của Paper A. Ta không biết Paper A đã chỉnh hai script này thế nào để chạy trong Case 1 và Case 2.

## 4. Repo OffQLCTS.jl: phần dựng ma trận hồi quy

Bài toán: LQR tuyến tính ẋ = Ax + Bu, Q-learning off-policy dùng hàm advantage. Đây không phải H∞, không có nhiễu, không có chiết khấu. Những ý dùng được cho (57)–(61):

1. **Tích phân trên mỗi khoảng bằng trạng thái mở rộng.** Hàm `systemCal` trả về `[ẋ; x⊗x; x⊗u; u⊗u]`, rồi RK4 tích phân cả khối. Tích phân trên khoảng [t, t+T] chính là hiệu của trạng thái mở rộng ở hai đầu khoảng (`collectData`). Mỗi khoảng T có `d = 10` bước con RK4.
2. **Chính sách hành vi:** `u = −K x + N(t)`, với K₀ = 0 vì A của F-16 đã ổn định, và N(t) là tổng 100 sin, tần số ngẫu nhiên trong [−500, 500] rad/s, biên độ 50/15·trung bình. Lưu ý: `rand` bị gọi lại **mỗi lần đánh giá**, nên thực chất N là nhiễu gần như trắng chứ không phải tổng sin cố định.
3. **Số liệu thu:** `T = 0.01 s`, `max_collect = 100` khoảng, `max_iters = 10`.
4. **Giải:** `sol = pinv(X1'X1) X1' Y`, tức phương trình chuẩn. Tham số Q, R chỉ dùng khi tính vế phải (`rewardFunction`), không cần mô hình.
5. **Lặp chính sách trên cùng một bộ dữ liệu** (`modelTrain`): mỗi vòng dựng lại ma trận hồi quy theo K hiện tại. Cấu trúc này giống pha 2 của Thuật toán 2.

Ta lấy ý (1) và (5). Riêng ý (4), ta dùng `numpy.linalg.lstsq` (phân tích QR/SVD) thay cho phương trình chuẩn, vì phương trình chuẩn bình phương số điều kiện; nghiệm vẫn như nhau khi ρ₁ đủ hạng. Đồng thời in hạng và số điều kiện của ρ₁ (PROJECT_CONTEXT §5.4.5).

## 5. Những gì trong repo KHÔNG dùng cho Paper A, và lý do

| Không dùng | Lý do |
| --- | --- |
| Actor-critic online (`Wc_dot`, `Wa_dot`, `gradPhi`) | Paper A là IRL **off-policy**: thu dữ liệu một lần rồi lặp bình phương tối thiểu. Luật gradient online là thuật toán khác. |
| Hàm cơ sở 15 số hạng của critic | Paper A quy định 45 tích bậc hai của X(1..9) và cơ sở tuyến tính cho actor, disturber. |
| Feedforward `tau_d = M v̇_d + C(v_d)v_d + D(v_d)v_d` | Bộ điều khiển Paper A phải **không cần mô hình**. Dùng nó là vi phạm §5.2.4 của PROJECT_CONTEXT. |
| `u = −½ M⁻ᵀ ∇Φᵀ W_a` | Dùng M. Paper A học trực tiếp u ≈ W_aᵀφ(X). |
| Tầng cao prescribed performance, leader-following độ dời, quỹ đạo leader 0.5 m/s rồi cung tròn | Paper A dùng bearing (13), co giãn (9) và (63). |
| Nhiễu `noise` tần số cao (t < 15 s) | Paper A dùng δ(t) ở trang 18. Trong repo biểu thức này có sẵn nhưng đang comment. |
| AISMC/FXESO như đang viết | Không trung thành với [42], [43] (mục 3). Chỉ lấy tham số để tham khảo khi làm M3, M4. |
| Cách tính `costFunction` | Có lỗi `cumsum` trên số vô hướng. |

## 6. Điều rút ra có ích cho việc tái tạo Paper A

1. Plant: cài đúng `AISMC/C.m`, `D.m`; nhiễu δ đúng biểu thức `tau_w` đang comment.
2. Q_i = 100·I₆: nhóm tác giả từng dùng đúng cấu trúc này.
3. Bước 0.001 s và `T_end = 500` có trong code của nhóm, giải thích được chữ "500" ở Bảng 1.
4. **Cảnh báo:** trong bài tiền thân, RL chỉ là phần bù chồng lên một feedforward dùng mô hình. Nếu code Paper A kế thừa cấu trúc này, kết quả của Paper A có thể phụ thuộc vào feedforward đó. Đây chỉ là giả thuyết, cần hỏi tác giả, nhưng nó ảnh hưởng trực tiếp đến khả năng tái tạo (PLAN, mục rủi ro R3).
