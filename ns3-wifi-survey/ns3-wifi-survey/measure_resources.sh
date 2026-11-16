#!/usr/bin/env bash
# ==============================================================================
# Đo thời gian chạy (giây) và RAM đỉnh (KB) của chương trình mô phỏng
# cho 3 trường hợp: 1, 20, 40 trạm (d = 10 m). Dùng để điền Bảng 6.4 báo cáo.
#
# Cách dùng: đặt file này ở thư mục gốc ns-3 (cùng cấp với ./ns3), sau khi đã
#            build xong, rồi chạy:  ./measure_resources.sh
# Cần cài: sudo apt install -y time
# Kết quả in ra màn hình và lưu vào resources.txt
# ==============================================================================

cd "$(dirname "$0")"

if [ ! -x /usr/bin/time ]; then
    echo "[LỖI] Chưa có /usr/bin/time. Hãy chạy: sudo apt install -y time"
    exit 1
fi

EXE=$(find build/scratch -type f -executable -name "*wifi-survey*" 2>/dev/null | head -1)
if [ -z "$EXE" ]; then
    echo "[LỖI] Không thấy file thực thi wifi-survey trong build/scratch."
    echo "      Hãy chạy ./ns3 build trước (và chắc chắn scratch/wifi-survey.cc đã tồn tại)."
    exit 1
fi
echo "Dùng file thực thi: $EXE"

export LD_LIBRARY_PATH="$PWD/build/lib:$LD_LIBRARY_PATH"
rm -f resources.txt

for n in 1 20 40; do
    /usr/bin/time -a -o resources.txt \
        -f "nSta=$n: %e giây, RAM đỉnh %M KB" \
        "$EXE" --nSta=$n --distance=10 --csvFile=/tmp/measure_test.csv > /dev/null
done

echo ""
cat resources.txt
echo ""
echo "RAM (MB) = số KB lớn nhất ở trên chia cho 1024."
