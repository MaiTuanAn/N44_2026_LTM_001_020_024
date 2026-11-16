#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kịch bản vẽ đồ thị tự động từ tệp results.csv xuất ra bởi ns-3.
Chạy lệnh: python3 plot_results.py
Đầu ra: 4 tệp ảnh đồ thị độ phân giải cao (.png) để chèn vào báo cáo Word.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Cấu hình phông chữ và giao diện đồ thị chuẩn báo cáo khoa học
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "bold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 200,
})

CSV_FILE = "results.csv"
OUTPUT_DIR = "figures"


def main():
    if not os.path.exists(CSV_FILE):
        print(f"[LỖI] Không tìm thấy tệp '{CSV_FILE}'. Hãy chạy ./run_experiments.sh trước!")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(CSV_FILE)

    # Lọc dữ liệu không bật RTS/CTS cho Kịch bản 1 & 2
    df_no_rts = df[(df["protocol"] == "UDP") & (df["rtsCts"] == 0)]

    # -------------------------------------------------------------------------
    # Hình 1: Tổng thông lượng (Throughput) theo Số lượng thiết bị (nSta)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    for dist, marker, color in [(10, "o", "#1B4F72"), (30, "s", "#2E86C1"), (50, "^", "#E67E22")]:
        sub = df_no_rts[df_no_rts["distance"] == dist].sort_values("nSta")
        if not sub.empty:
            ax.plot(
                sub["nSta"],
                sub["totalThroughputMbps"],
                marker=marker,
                linewidth=2,
                color=color,
                label=f"Khoảng cách d = {dist} m",
            )

    ax.set_title("Ảnh hưởng của số lượng thiết bị (STA) đến tổng thông lượng mạng")
    ax.set_xlabel("Số lượng thiết bị trạm (nSta)")
    ax.set_ylabel("Tổng thông lượng (Mbps)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0.08, y=0.15)
    ax.legend(bbox_to_anchor=(0.5, 1.12), loc="lower center", ncol=3, frameon=False)
    fig.savefig(os.path.join(OUTPUT_DIR, "fig1_throughput_vs_nsta.png"), bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Hình 2: Độ trễ trung bình & Tỉ lệ mất gói theo Số lượng thiết bị (nSta)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    for dist, marker, color in [(10, "o", "#1B4F72"), (30, "s", "#2E86C1"), (50, "^", "#C0392B")]:
        sub = df_no_rts[df_no_rts["distance"] == dist].sort_values("nSta")
        if not sub.empty:
            ax.plot(
                sub["nSta"],
                sub["avgDelayMs"],
                marker=marker,
                linewidth=2,
                color=color,
                label=f"Khoảng cách d = {dist} m",
            )

    ax.set_title("Ảnh hưởng của số lượng thiết bị (STA) đến độ trễ truyền gói trung bình")
    ax.set_xlabel("Số lượng thiết bị trạm (nSta)")
    ax.set_ylabel("Độ trễ trung bình End-to-End (ms)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0.08, y=0.15)
    ax.legend(bbox_to_anchor=(0.5, 1.12), loc="lower center", ncol=3, frameon=False)
    fig.savefig(os.path.join(OUTPUT_DIR, "fig2_delay_vs_nsta.png"), bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Hình 3: Thông lượng theo Khoảng cách (distance)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    for nsta, marker, color in [(1, "o", "#117864"), (10, "s", "#2874A6"), (25, "D", "#B03A2E")]:
        sub = df_no_rts[df_no_rts["nSta"] == nsta].sort_values("distance")
        if not sub.empty:
            ax.plot(
                sub["distance"],
                sub["totalThroughputMbps"],
                marker=marker,
                linewidth=2,
                color=color,
                label=f"Số trạm N = {nsta} STA",
            )

    ax.set_title("Sự suy giảm thông lượng theo khoảng cách truyền dẫn")
    ax.set_xlabel("Khoảng cách từ STA đến AP (m)")
    ax.set_ylabel("Tổng thông lượng (Mbps)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0.08, y=0.15)
    ax.legend(bbox_to_anchor=(0.5, 1.12), loc="lower center", ncol=3, frameon=False)
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_throughput_vs_distance.png"), bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Hình 4: Tỉ lệ mất gói (Packet Loss %) theo Khoảng cách
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    for nsta, marker, color in [(1, "o", "#117864"), (10, "s", "#2874A6"), (25, "D", "#B03A2E")]:
        sub = df_no_rts[df_no_rts["nSta"] == nsta].sort_values("distance")
        if not sub.empty:
            ax.plot(
                sub["distance"],
                sub["packetLossPct"],
                marker=marker,
                linewidth=2,
                color=color,
                label=f"Số trạm N = {nsta} STA",
            )

    ax.set_title("Tỉ lệ mất gói tin (Packet Loss Ratio) theo khoảng cách")
    ax.set_xlabel("Khoảng cách từ STA đến AP (m)")
    ax.set_ylabel("Tỉ lệ mất gói (%)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0.08, y=0.15)
    ax.legend(bbox_to_anchor=(0.5, 1.12), loc="lower center", ncol=3, frameon=False)
    fig.savefig(os.path.join(OUTPUT_DIR, "fig4_loss_vs_distance.png"), bbox_inches="tight")
    plt.close(fig)

    print(f"[HOÀN TẤT] Đã xuất 4 đồ thị PNG vào thư mục '{OUTPUT_DIR}/'.")


if __name__ == "__main__":
    main()