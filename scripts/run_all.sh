#!/usr/bin/env bash
# Chạy lại toàn bộ phần tái tạo Paper A theo thứ tự các mốc (docs/report_paperA.md, mục 5).
# Dùng:  bash scripts/run_all.sh [quick|full]
#   quick (mặc định): test + tầng cao + M1 + bài đồ chơi + hình báo cáo, dùng lại trọng số
#                     IRL đã học (results/moc5_irl/*_W.npz). Khoảng 10 phút.
#   full:             như quick, nhưng học lại IRL cho 10 seed ở cả hai case, rồi chạy Mốc 6.
#                     Khoảng 45–60 phút trên 10–18 lõi.
# Mọi kết quả nằm trong results/ (không đưa lên git).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
MODE=${1:-quick}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

step() { echo; echo "=== $1 ==="; }

step "Test (khoảng 35 s)"
$PY -m pytest -q

step "Mốc 1: hình học bearing"
$PY scripts/check_geometry.py

step "Mốc 2: tầng cao, bám hoàn hảo, quét k_v (khoảng 1 phút)"
$PY scripts/run_highlevel_only.py

step "Mốc 3: M1 với plant thật (khoảng 2.5 phút)"
$PY scripts/run_m1.py

step "Mốc 4: IRL trên bài toán đồ chơi (khoảng 15 s)"
$PY scripts/toy_irl.py

if [ "$MODE" = "full" ]; then
  step "Mốc 5: học IRL, 10 seed mỗi case (khoảng 10–25 phút mỗi case)"
  $PY scripts/run_irl.py case1 --seeds 10 --workers 10
  $PY scripts/run_irl.py case2 --seeds 10 --workers 10
  step "Mốc 5: bảng biến thể đúng như bài (R = I, W = 0, cơ sở đúng chữ), Case 1"
  $PY scripts/run_irl.py case1
  step "Mốc 6: M1 so với IRL trên 10 seed (khoảng 5 phút)"
  $PY scripts/run_moc6.py
fi

step "Hình cho báo cáo (khoảng 5 phút)"
$PY scripts/make_report_figures.py

echo; echo "Xong. Hình báo cáo: results/report/. Bảng: results/moc*/."
