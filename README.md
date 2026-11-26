# Bearing_collision_avoidance

Tái tạo bài *Bearing-based cascade formation scaling control for multiple perturbed surface vehicles via off-policy reinforcement learning* (Duc, Phung, Dao, J. Franklin Inst. 2026), làm nền để thêm tầng an toàn CBF tránh va chạm.

- Bối cảnh và yêu cầu: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)
- Kế hoạch, các mốc: [PLAN.md](PLAN.md)
- Mọi giả thiết cho chỗ bài gốc mơ hồ: [docs/assumptions.md](docs/assumptions.md)
- Bảng ký hiệu: [docs/notation.md](docs/notation.md)

## Cài đặt

```bash
uv venv .venv && uv pip install -p .venv -r requirements.txt
```

## Chạy

```bash
.venv/bin/python -m pytest -q                 # toàn bộ test
.venv/bin/python scripts/check_geometry.py    # bảng hình học + phân tích cản tầng cao
```

PDF các bài báo và repo tham khảo của bên thứ ba **không** nằm trong repo này (xem `.gitignore`, `docs/reference_code_notes.md`).
