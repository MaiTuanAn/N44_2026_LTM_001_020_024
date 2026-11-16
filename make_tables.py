#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doc results.csv va in ra so lieu de dien vao Bang 6.1, 6.2, 6.3 trong bao cao.
Chay: python3 make_tables.py
Dong thoi luu cac bang vao thu muc tables/ (.csv) de mo bang Excel neu can.
"""

import os
import sys

import pandas as pd

CSV_FILE = "results.csv"
OUT_DIR = "tables"

NSTA_LIST = [1, 5, 10, 15, 20, 30, 40]
DIST_LIST = [5, 15, 30, 45, 60, 80, 100]


def pick(df, **cond):
    """Lay dung 1 dong theo dieu kien, tra ve None neu khong co."""
    sub = df
    for k, v in cond.items():
        sub = sub[sub[k] == v]
    return None if sub.empty else sub.iloc[0]


def val(row, col, fmt="{:.2f}"):
    return "N/A" if row is None else fmt.format(row[col])


def main():
    if not os.path.exists(CSV_FILE):
        print(f"[LOI] Khong thay '{CSV_FILE}'. Hay chay ./run_experiments.sh truoc.")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(CSV_FILE)
    # Kich ban 1 va 2 co vai cau hinh trung nhau -> bo dong lap
    df = df.drop_duplicates(subset=["nSta", "distance", "protocol", "rtsCts", "seed"])
    udp = df[df["protocol"] == "UDP"]
    base = udp[udp["rtsCts"] == 0]

    # ------------------------------------------------------------------ Bang 6.1
    rows = []
    for n in NSTA_LIST:
        a = pick(base, nSta=n, distance=10)
        b = pick(base, nSta=n, distance=30)
        rows.append({
            "nSta": n,
            "Throughput_Mbps [10m / 30m]": f"{val(a, 'totalThroughputMbps')} / {val(b, 'totalThroughputMbps')}",
            "Delay_ms [10m / 30m]": f"{val(a, 'avgDelayMs')} / {val(b, 'avgDelayMs')}",
            "Loss_pct [10m / 30m]": f"{val(a, 'packetLossPct')} / {val(b, 'packetLossPct')}",
            "Jain [10m / 30m]": f"{val(a, 'jainsFairness', '{:.3f}')} / {val(b, 'jainsFairness', '{:.3f}')}",
        })
    t1 = pd.DataFrame(rows)
    t1.to_csv(os.path.join(OUT_DIR, "bang_6_1.csv"), index=False)
    print("\n=== BANG 6.1 (Kich ban 1: theo so tram) ===")
    print(t1.to_string(index=False))

    # ------------------------------------------------------------------ Bang 6.2
    rows = []
    for d in DIST_LIST:
        a = pick(base, nSta=1, distance=d)
        b = pick(base, nSta=10, distance=d)
        rows.append({
            "distance_m": d,
            "Throughput_Mbps [N=1 / N=10]": f"{val(a, 'totalThroughputMbps')} / {val(b, 'totalThroughputMbps')}",
            "PerSTA_Mbps [N=10]": val(b, "perStaThroughputMbps"),
            "Delay_ms [N=1 / N=10]": f"{val(a, 'avgDelayMs')} / {val(b, 'avgDelayMs')}",
            "Loss_pct [N=1 / N=10]": f"{val(a, 'packetLossPct')} / {val(b, 'packetLossPct')}",
        })
    t2 = pd.DataFrame(rows)
    t2.to_csv(os.path.join(OUT_DIR, "bang_6_2.csv"), index=False)
    print("\n=== BANG 6.2 (Kich ban 2: theo khoang cach) ===")
    print(t2.to_string(index=False))

    # ------------------------------------------------------------------ Bang 6.3
    rows = []
    for n in NSTA_LIST:
        a = pick(base, nSta=n, distance=25)
        b = pick(udp[udp["rtsCts"] == 1], nSta=n, distance=25)
        rows.append({
            "nSta": n,
            "Thr_Baseline": val(a, "totalThroughputMbps"),
            "Thr_RTSCTS": val(b, "totalThroughputMbps"),
            "Loss_Baseline_pct": val(a, "packetLossPct"),
            "Loss_RTSCTS_pct": val(b, "packetLossPct"),
        })
    t3 = pd.DataFrame(rows)
    t3.to_csv(os.path.join(OUT_DIR, "bang_6_3.csv"), index=False)
    print("\n=== BANG 6.3 (Kich ban 3: Baseline DCF vs RTS/CTS, d = 25 m) ===")
    print(t3.to_string(index=False))
    if (t3["Thr_Baseline"] == "N/A").any():
        print("\n[CANH BAO] Thieu du lieu Baseline tai d=25 m. Hay chay them cac lenh "
              "baseline (xem huong dan) roi chay lai file nay.")

    # ------------------------------------------------------------------ Goi y dien phan phan tich
    print("\n=== GOI Y SO LIEU DIEN VAO PHAN PHAN TICH ===")
    for d in (10, 30):
        s = base[base["distance"] == d].sort_values("nSta")
        if s.empty:
            continue
        peak = s.loc[s["totalThroughputMbps"].idxmax()]
        last = s.iloc[-1]
        first = s.iloc[0]
        print(f"[d={d} m] Thong luong dat cuc dai {peak['totalThroughputMbps']:.2f} Mbps "
              f"tai nSta={int(peak['nSta'])}; tai nSta={int(first['nSta'])}: "
              f"{first['totalThroughputMbps']:.2f} Mbps; tai nSta={int(last['nSta'])}: "
              f"{last['totalThroughputMbps']:.2f} Mbps, tre {last['avgDelayMs']:.1f} ms, "
              f"mat goi {last['packetLossPct']:.1f} %, Jain {last['jainsFairness']:.3f}")

    s = base[base["nSta"] == 1].sort_values("distance")
    if not s.empty:
        peak = s["totalThroughputMbps"].max()
        dead = s[s["totalThroughputMbps"] < 0.05 * peak]
        if not dead.empty:
            print(f"[N=1] Thong luong rot duoi 5% cuc dai tu d = {int(dead.iloc[0]['distance'])} m "
                  f"(cuc dai {peak:.2f} Mbps)")
        else:
            print(f"[N=1] Thong luong khong rot duoi 5% cuc dai trong dai khao sat (cuc dai {peak:.2f} Mbps)")

    ok = t3[(t3["Thr_Baseline"] != "N/A") & (t3["Thr_RTSCTS"] != "N/A")].copy()
    if not ok.empty:
        ok["gain"] = ok["Thr_RTSCTS"].astype(float) - ok["Thr_Baseline"].astype(float)
        win = ok[ok["gain"] > 0]
        if win.empty:
            print("[RTS/CTS] Trong dai khao sat, RTS/CTS khong cai thien thong luong so voi Baseline.")
        else:
            print(f"[RTS/CTS] RTS/CTS bat dau cho thong luong cao hon Baseline tu nSta = "
                  f"{int(win.iloc[0]['nSta'])}")
        print("[RTS/CTS] Chenh lech thong luong (RTS - Baseline) theo nSta:")
        for _, r in ok.iterrows():
            base_v = float(r["Thr_Baseline"])
            pct = (r["gain"] / base_v * 100) if base_v > 0 else float("nan")
            print(f"    nSta={int(r['nSta']):>2}: {r['gain']:+.2f} Mbps ({pct:+.1f} %)")


if __name__ == "__main__":
    main()
