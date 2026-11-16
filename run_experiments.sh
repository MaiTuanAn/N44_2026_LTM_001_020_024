#!/usr/bin/env bash
# ==============================================================================
# Kịch bản tự động chạy khảo sát hiệu năng mạng Wi-Fi trên WSL ns-3
# Cách dùng: Đặt file này tại thư mục gốc của ns-3 (cùng cấp với ./ns3)
#            (hoặc dùng ./install_to_ns3.sh để tự chép vào)
#            Chạy lệnh: chmod +x run_experiments.sh && ./run_experiments.sh
# ==============================================================================

set -e

CSV_OUTPUT="results.csv"
SIM_TIME=15.0
DATA_RATE="20Mbps"

# Xóa file kết quả cũ nếu tồn tại để bắt đầu phiên đo mới
if [ -f "$CSV_OUTPUT" ]; then
    rm -f "$CSV_OUTPUT"
fi

echo "================================================================"
echo " BƯỚC 1: Biên dịch mã nguồn scratch/wifi-survey.cc trong ns-3"
echo "================================================================"
./ns3 build

echo ""
echo "================================================================"
echo " BƯỚC 2: Kịch bản 1 - Khảo sát theo SỐ LƯỢNG THIẾT BỊ (nSta)"
echo "         (Cố định khoảng cách: 10m, 30m, 50m | Giao thức: UDP)"
echo "================================================================"
NSTA_LIST=(1 5 10 15 20 30 40)
DIST_FIXED_LIST=(10 30 50)

for dist in "${DIST_FIXED_LIST[@]}"; do
    for n in "${NSTA_LIST[@]}"; do
        ./ns3 run "scratch/wifi-survey --nSta=${n} --distance=${dist} --simTime=${SIM_TIME} --dataRate=${DATA_RATE} --protocol=UDP --enableRtsCts=false --csvFile=${CSV_OUTPUT}"
    done
done

echo ""
echo "================================================================"
echo " BƯỚC 3: Kịch bản 2 - Khảo sát theo KHOẢNG CÁCH (distance)"
echo "         (Cố định số trạm: 1, 10, 25 STA | Khoảng cách: 5m -> 100m)"
echo "================================================================"
DIST_SWEEP_LIST=(5 15 30 45 60 80 100)
NSTA_FIXED_LIST=(1 10 25)

for n in "${NSTA_FIXED_LIST[@]}"; do
    for dist in "${DIST_SWEEP_LIST[@]}"; do
        ./ns3 run "scratch/wifi-survey --nSta=${n} --distance=${dist} --simTime=${SIM_TIME} --dataRate=${DATA_RATE} --protocol=UDP --enableRtsCts=false --csvFile=${CSV_OUTPUT}"
    done
done

echo ""
echo "================================================================"
echo " BƯỚC 4: Kịch bản 3 - Đánh giá hiệu quả RTS/CTS khi mật độ cao"
echo "         (Khoảng cách cố định 25m | Bật RTS/CTS = true)"
echo "================================================================"
for n in "${NSTA_LIST[@]}"; do
    ./ns3 run "scratch/wifi-survey --nSta=${n} --distance=25 --simTime=${SIM_TIME} --dataRate=${DATA_RATE} --protocol=UDP --enableRtsCts=true --csvFile=${CSV_OUTPUT}"
done

echo ""
echo "================================================================"
echo " BƯỚC 5: Kịch bản 3 (đối chứng) - Baseline DCF tại d=25m"
echo "         (RTS/CTS tắt, để so sánh với Bước 4)"
echo "================================================================"
for n in "${NSTA_LIST[@]}"; do
    ./ns3 run "scratch/wifi-survey --nSta=${n} --distance=25 --simTime=${SIM_TIME} --dataRate=${DATA_RATE} --protocol=UDP --enableRtsCts=false --csvFile=${CSV_OUTPUT}"
done

echo ""
echo "================================================================"
echo " HOÀN TẤT! Dữ liệu đã được lưu tại: ${CSV_OUTPUT}"
echo " Chạy tiếp: python3 plot_results.py để xuất đồ thị báo cáo."
echo "================================================================"