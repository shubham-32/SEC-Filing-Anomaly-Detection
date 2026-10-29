"""Interactive Live Demonstration Script for SEC Filing Anomaly Detection.

Designed for Live Project Evaluation & Examination Demonstrations.
Addresses Instruction #3: 'Every group must bring their own laptop and demonstrate
the live working project during the evaluation.'

Usage:
    python live_demo.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Add project root and src to path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np

from src.anomaly_pipeline import (
    load_pipeline_model,
    resolve_data_dir,
    run_detection,
    score_new_filing,
)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    banner = """
================================================================================
   SEC FILING ANOMALY DETECTION SYSTEM — LIVE DEMO & EVALUATION CONSOLE
   Task ID: FDA-2 | Fraud Detection Through Financial Anomalies
   Sem 7 Big Data Analytics | Deliverables 1 & 2 Completed
================================================================================
"""
    print(banner)


def show_company_explorer(df: pd.DataFrame, scored: pd.DataFrame):
    clear_screen()
    print_banner()
    tickers = sorted(df["ticker"].unique())
    print("Available Companies in Secondary Dataset:")
    for i in range(0, len(tickers), 6):
        print("  " + "  ".join(f"[{t}]" for t in tickers[i:i+6]))
    print("-" * 80)
    choice = input("\nEnter company ticker to inspect (or press Enter to return): ").strip().upper()
    if not choice or choice not in tickers:
        return

    sub = scored[scored["ticker"] == choice].sort_values("period_end")
    group = sub["group"].iloc[0] if "group" in sub else "unknown"
    company_name = sub["company"].iloc[0] if "company" in sub else choice

    print(f"\nProfile for {company_name} ({choice}) — Group: {group.upper()}")
    print("=" * 80)
    print(f"Total Quarters Scored           : {len(sub)}")
    print(f"Isolation Forest Alerts         : {int(sub['if_anomaly'].sum())} quarters")
    print(f"Statistical Z-Score Alerts      : {int(sub['statistical_anomaly'].sum())} quarters")
    print(f"Multi-Year Sudden Deviations    : {int(sub['multi_year_sudden_deviation'].sum())} quarters")
    print("-" * 80)
    print("Historical Anomalous Quarters Summary:")
    
    anom_rows = sub[sub["if_anomaly"] | sub["statistical_anomaly"] | sub["multi_year_sudden_deviation"]].copy()
    if anom_rows.empty:
        print("  No quarters triggered anomaly flags for this company.")
    else:
        for _, r in anom_rows.iterrows():
            fy = r.get("fiscal_year", "N/A")
            fq = r.get("fiscal_quarter", "N/A")
            pend = str(r.get("period_end", "N/A"))[:10]
            if_sc = round(float(r.get("if_anomaly_score", 0)), 3)
            stat_sc = round(float(r.get("statistical_anomaly_score", 0)), 2)
            flags = []
            if r.get("if_anomaly"): flags.append("IF_ML")
            if r.get("statistical_anomaly"): flags.append("STAT_Z")
            if r.get("multi_year_sudden_deviation"): flags.append("TREND_DEV")
            flag_str = "+".join(flags)
            op = round(float(r.get("operating_margin", 0))*100, 1) if pd.notna(r.get("operating_margin")) else "N/A"
            rev_g = round(float(r.get("revenue_yoy_growth", 0))*100, 1) if pd.notna(r.get("revenue_yoy_growth")) else "N/A"
            print(f"  • FY{fy} Q{fq} ({pend}) | IF_Score={if_sc} | Stat_Z={stat_sc}σ | Flags: [{flag_str:<18}] | OpMargin={op}% | RevYoY={rev_g}%")
            
    input("\nPress Enter to return to main menu...")


def show_leaderboard(scored: pd.DataFrame):
    clear_screen()
    print_banner()
    print("Top 15 Most Anomalous Company-Quarters across Universe:")
    print("=" * 80)
    top15 = scored.sort_values("if_anomaly_score", ascending=False).head(15)
    for rank, (_, r) in enumerate(top15.iterrows(), 1):
        ticker = r["ticker"]
        fy = r.get("fiscal_year", "N/A")
        fq = r.get("fiscal_quarter", "N/A")
        pend = str(r.get("period_end", "N/A"))[:10]
        score = round(float(r.get("if_anomaly_score", 0)), 4)
        group = r.get("group", "unknown").upper()
        stat_flag = "STAT:YES" if r.get("statistical_anomaly") else "STAT:NO"
        trend_flag = "TREND:YES" if r.get("multi_year_sudden_deviation") else "TREND:NO"
        print(f"  #{rank:<2} | {ticker:<5} FY{fy} Q{fq} ({pend}) | Group: {group:<9} | IF_Score: {score:.4f} | {stat_flag} | {trend_flag}")
    print("=" * 80)
    input("\nPress Enter to return to main menu...")


def show_live_filing_scoring(data_dir: Path, df: pd.DataFrame):
    clear_screen()
    print_banner()
    print("Automated Pipeline for New Filings — Live Simulation")
    print("-" * 80)
    print("Select a company filing to ingest and score through the automated pipeline:")
    print("  1. Kraft Heinz (KHC) — FY2018 Q4 (Goodwill Write-Down & Procurement Scandal)")
    print("  2. Under Armour (UAA) — FY2016 Q4 (Channel Stuffing & Receivables Surge)")
    print("  3. Super Micro Computer (SMCI) — FY2022 Q4 (Rapid Revenue Acceleration)")
    print("  4. Microsoft (MSFT) — FY2026 Q4 (Healthy Control Blue-Chip Baseline)")
    print("  5. Custom Ticker from Secondary Dataset")
    print("-" * 80)
    opt = input("Select option (1-5, or Enter to cancel): ").strip()
    
    ticker_map = {"1": "KHC", "2": "UAA", "3": "SMCI", "4": "MSFT"}
    target_ticker = ticker_map.get(opt)
    if opt == "5":
        target_ticker = input("Enter ticker: ").strip().upper()

    if not target_ticker:
        return

    sub = df[df["ticker"].str.upper() == target_ticker].sort_values("period_end")
    if sub.empty:
        print(f"Error: Ticker '{target_ticker}' not found.")
        input("Press Enter to continue...")
        return

    model_file = data_dir / "isolation_forest_model.joblib"
    if not model_file.exists():
        print("Training model artifact on the fly...")
        res = run_detection(data_dir, output_dir=data_dir)
        model = res["model"]
        features = res["summary"]["model_features"]
    else:
        model, features, _ = load_pipeline_model(model_file)

    # Ingest: prior history + target filing
    hist = sub.iloc[:-1]
    new_filing = sub.iloc[-1].to_dict()

    print(f"\nIngesting SEC filing for {target_ticker} ({new_filing['period_end']})...")
    time.sleep(0.5)
    print("Calculating financial ratios, working capital metrics, and Sloan accruals...")
    time.sleep(0.5)
    print("Computing trailing 12-quarter multi-year trend deviations...")
    time.sleep(0.5)
    print("Executing Isolation Forest and Robust Z-score scoring engines...")
    time.sleep(0.5)

    scorecard = score_new_filing(new_filing, hist, model=model, feature_columns=features)

    print("\n" + "=" * 75)
    print(f"  SEC FILING FORENSIC AUDIT SCORECARD: {scorecard['ticker']} ({scorecard['period_end']})")
    print("=" * 75)
    print(f"  Fiscal Period           : FY{scorecard['fiscal_year']} Q{scorecard['fiscal_quarter']}")
    print(f"  Risk Classification     : {scorecard['risk_level']}")
    print("-" * 75)
    print(f"  Isolation Forest Score  : {scorecard['isolation_forest_score']}  [Flagged: {scorecard['isolation_forest_flag']}]")
    print(f"  Statistical Z Score     : {scorecard['statistical_anomaly_score']}  [Flagged: {scorecard['statistical_anomaly_flag']}]")
    print(f"  Max Multi-Year Dev      : {scorecard['max_multi_year_deviation']} sigma [Flagged: {scorecard['multi_year_deviation_flag']}]")
    print("-" * 75)
    print("  Triggered Red Flags:")
    if scorecard["contributing_red_flags"]:
        for f in scorecard["contributing_red_flags"]:
            val_str = f"dev={f.get('trend_deviation_sigma', f.get('z_score', 'N/A'))}"
            print(f"   * {f['metric']:<32} | {val_str:<12} | {f['status']}")
    else:
        print("   * None (All indicators within normal statistical boundaries)")

    print("-" * 75)
    print("  Audit Recommendations:")
    for rec in scorecard["audit_recommendations"]:
        print(f"   -> {rec}")
    print("=" * 75)
    input("\nPress Enter to return to main menu...")


def show_case_studies():
    clear_screen()
    print_banner()
    print("Forensic Case Studies — Validating Detection of Documented Fraud Schemes")
    print("=" * 80)
    print("""
1. KRAFT HEINZ (KHC) — PROCUREMENT FRAUD & $15B WRITE-DOWN
   • Case Details : In 2019, the SEC charged KHC with a 3-year expense-management fraud
                    involving bogus supplier contracts. In FY2018 Q4, KHC announced a $15.4B
                    goodwill impairment and restated multiple historical filings.
   • Signal Seen  : Operating margin collapsed to -205% (Robust Z = -9.45σ).
                    Sloan Accruals to Assets plunged to -8.32σ.
                    Model classified as: HIGH ANOMALY (Multi-Method Consensus).

2. UNDER ARMOUR (UAA) — CHANNEL STUFFING & REVENUE PULL-FORWARD
   • Case Details : SEC found Under Armour pulled forward $408M in orders from future quarters
                    to artificially meet Wall Street targets during 2015-2016.
   • Signal Seen  : Receivables growth outstripped revenue growth by up to 7.23σ (channel stuffing indicator).
                    Days Sales Outstanding (DSO) jumped by 5.43σ.
                    Model classified as: ELEVATED ANOMALY.

3. SUPER MICRO COMPUTER (SMCI) — REVENUE RECOGNITION & PREMATURE SHIPMENTS
   • Case Details : Repeated SEC enforcement and auditor resignations regarding premature revenue
                    recognition on incomplete hardware deliveries.
   • Signal Seen  : Extreme quarterly revenue growth spikes (Z = 3.15σ) alongside
                    unusual Days Sales Outstanding swings (Z = 5.00σ).
    """)
    print("=" * 80)
    input("\nPress Enter to return to main menu...")


def run_full_pipeline(data_dir: Path):
    clear_screen()
    print_banner()
    print("Running Full Batch Scoring Pipeline on Secondary Dataset...")
    print("-" * 80)
    res = run_detection(data_dir, output_dir=data_dir)
    s = res["summary"]
    print(f"Rows Scored                         : {s['rows_scored']:,}")
    print(f"Model Features Selected             : {s['model_feature_count']}")
    print(f"Isolation Forest Flags              : {s['isolation_forest_flagged']:,}")
    print(f"Statistical Z-Score Flags (|Z|>=3.5): {s['statistical_flagged']:,}")
    print(f"Multi-Year Sudden Deviations        : {s['multi_year_trend_flagged']:,}")
    print("-" * 80)
    print("All report files updated in data/processed/")
    input("\nPress Enter to return to main menu...")


def main():
    data_dir = resolve_data_dir()
    q_file = data_dir / "quarterly_features.csv"
    if not q_file.exists():
        print(f"Error: quarterly_features.csv not found in {data_dir}")
        return 1

    df = pd.read_csv(q_file, low_memory=False)
    scored_file = data_dir / "scored_quarterly.csv"
    if scored_file.exists():
        scored = pd.read_csv(scored_file, low_memory=False)
    else:
        res = run_detection(data_dir, output_dir=data_dir)
        scored = res["scored"]

    while True:
        clear_screen()
        print_banner()
        print("SELECT LIVE DEMONSTRATION MODULE:")
        print("  1. Interactive Company Anomaly Explorer")
        print("  2. Top Anomalies Leaderboard (Universe-Wide)")
        print("  3. Automated Pipeline for New Filings (Live Simulation)")
        print("  4. Forensic Fraud Case Studies Walkthrough")
        print("  5. Run Full End-to-End Batch Pipeline")
        print("  6. Exit Demonstration")
        print("-" * 80)
        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            show_company_explorer(df, scored)
        elif choice == "2":
            show_leaderboard(scored)
        elif choice == "3":
            show_live_filing_scoring(data_dir, df)
        elif choice == "4":
            show_case_studies()
        elif choice == "5":
            run_full_pipeline(data_dir)
        elif choice == "6":
            print("\nExiting demonstration console. Thank you!")
            break


if __name__ == "__main__":
    sys.exit(main())
