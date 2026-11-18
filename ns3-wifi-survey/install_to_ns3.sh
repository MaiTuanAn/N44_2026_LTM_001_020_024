#!/usr/bin/env bash
# ==============================================================================
# Chép các file của dự án vào đúng vị trí trong thư mục ns-3.
# Cách dùng:  ./install_to_ns3.sh <đường-dẫn-thư-mục-ns-3>
# Ví dụ:      ./install_to_ns3.sh ~/ns3-project/ns-3-dev
# ==============================================================================
set -e

if [ -z "$1" ]; then
    echo "Cách dùng: ./install_to_ns3.sh <đường-dẫn-thư-mục-ns-3>"
    exit 1
fi

if [ ! -d "$1" ]; then
    echo "[LỖI] Không tìm thấy thư mục: $1"
    exit 1
fi

NS3_DIR="$(cd "$1" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "$NS3_DIR/ns3" ] || [ ! -d "$NS3_DIR/scratch" ]; then
    echo "[LỖI] '$NS3_DIR' không phải thư mục gốc ns-3 (phải có file 'ns3' và thư mục 'scratch')."
    exit 1
fi

cp "$HERE/wifi-survey.cc" "$NS3_DIR/scratch/wifi-survey.cc"
for f in run_experiments.sh measure_resources.sh plot_results.py make_tables.py; do
    cp "$HERE/$f" "$NS3_DIR/$f"
done
chmod +x "$NS3_DIR/run_experiments.sh" "$NS3_DIR/measure_resources.sh"

echo "[OK] Đã chép vào: $NS3_DIR"
echo "     - scratch/wifi-survey.cc"
echo "     - run_experiments.sh, measure_resources.sh, plot_results.py, make_tables.py"
echo "Bước tiếp theo:  cd $NS3_DIR && ./ns3 build"
