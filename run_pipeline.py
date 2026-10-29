"""Run Deliverable 2 Anomaly Detection Pipeline and Automated New-Filing Scoring.

Supports:
  1. Batch scoring of current/refreshed EDGAR dataset.
  2. Single-company or new-filing scoring with forensic audit diagnosis.
  3. Optional EDGAR extraction refresh.

Examples:
  # 1. Full batch run on secondary dataset:
  python run_pipeline.py

  # 2. Score a specific company's latest filing (e.g. Super Micro Computer or Kraft Heinz):
  python run_pipeline.py --ticker SMCI
  python run_pipeline.py --ticker KHC
  python run_pipeline.py --ticker AAPL

  # 3. Score a new custom filing from a JSON/CSV file:
  python run_pipeline.py --filing-file new_filing.json

  # 4. Refresh extraction from SEC EDGAR first:
  SEC_USER_AGENT="YourName email@example.com" python run_pipeline.py --refresh-extraction --clear-cache
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Add project root and src to path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if (ROOT / "sec_filing_anomaly_deliverable2").exists() and str(ROOT / "sec_filing_anomaly_deliverable2") not in sys.path:
    sys.path.insert(0, str(ROOT / "sec_filing_anomaly_deliverable2"))

from src.anomaly_pipeline import (
    load_pipeline_model,
    resolve_data_dir,
    run_detection,
    save_pipeline_model,
    score_new_filing,
)


def refresh_extraction(root_dir: Path, *, clear_cache: bool) -> None:
    """Execute the existing EDGAR extraction notebook in a temporary directory."""
    user_agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not user_agent:
        raise RuntimeError(
            "Set SEC_USER_AGENT to 'Your Name your@email.com' before refreshing SEC data. "
            "The SEC requires an identifying User-Agent for automated requests."
        )

    # Locate extraction notebook
    candidates = [
        root_dir / "01_edgar_data_extraction.ipynb",
        root_dir.parent / "01_edgar_data_extraction.ipynb",
        root_dir / "notebooks" / "01_edgar_data_extraction.ipynb",
    ]
    extraction_notebook = None
    for c in candidates:
        if c.exists():
            extraction_notebook = c
            break
    if not extraction_notebook:
        raise FileNotFoundError("Extraction notebook '01_edgar_data_extraction.ipynb' not found.")

    cache_dir = extraction_notebook.parent / "edgar_cache"
    if clear_cache and cache_dir.exists():
        shutil.rmtree(cache_dir)
        print(f"Removed cached SEC responses: {cache_dir}")

    with tempfile.TemporaryDirectory(prefix="sec-edgar-refresh-") as temp_dir:
        cmd = [
            sys.executable, "-m", "nbconvert", "--to", "notebook",
            "--execute", str(extraction_notebook), "--output", "extraction_run.ipynb",
            "--output-dir", temp_dir, "--ExecutePreprocessor.timeout=1800",
        ]
        print("Refreshing EDGAR dataset by executing the extraction notebook...")
        subprocess.run(cmd, cwd=extraction_notebook.parent, env=os.environ.copy(), check=True)
    print("Extraction refresh completed successfully.")


def print_scorecard(scorecard: dict) -> None:
    """Print a clean forensic audit scorecard to stdout."""
    print("\n" + "=" * 70)
    print(f"  SEC FILING AUDIT SCORECARD: {scorecard['ticker']} ({scorecard['period_end']})")
    print("=" * 70)
    print(f"  Fiscal Period           : FY{scorecard['fiscal_year']} Q{scorecard['fiscal_quarter']}")
    print(f"  Risk Classification     : {scorecard['risk_level']}")
    print("-" * 70)
    print(f"  Isolation Forest Score  : {scorecard['isolation_forest_score']}  [Flagged: {scorecard['isolation_forest_flag']}]")
    print(f"  Statistical Z Score     : {scorecard['statistical_anomaly_score']}  [Flagged: {scorecard['statistical_anomaly_flag']}]")
    print(f"  Max Multi-Year Dev      : {scorecard['max_multi_year_deviation']} sigma [Flagged: {scorecard['multi_year_deviation_flag']}]")
    print("-" * 70)
    print("  Triggered Red Flags:")
    if scorecard["contributing_red_flags"]:
        for f in scorecard["contributing_red_flags"]:
            dev_str = f"dev={f.get('trend_deviation_sigma', f.get('z_score', 'N/A'))}"
            print(f"   * {f['metric']:<32} | {dev_str:<12} | {f['status']}")
    else:
        print("   * None (All indicators within normal statistical boundaries)")

    print("-" * 70)
    print("  Audit Recommendations:")
    for rec in scorecard["audit_recommendations"]:
        print(f"   -> {rec}")
    print("=" * 70 + "\n")


def score_single_ticker(ticker: str, data_dir: Path) -> int:
    """Score the latest available filing for a company and display diagnosis."""
    import pandas as pd

    q_file = data_dir / "quarterly_features.csv"
    if not q_file.exists():
        print(f"Error: dataset not found at {q_file}")
        return 1

    df = pd.read_csv(q_file, low_memory=False)
    sub = df[df["ticker"].str.upper() == ticker.upper()].sort_values("period_end")
    if sub.empty:
        print(f"Error: Ticker '{ticker}' not found in {q_file}. Available: {sorted(df['ticker'].unique())}")
        return 1

    # Load trained model if available, otherwise train on the fly
    model_file = data_dir / "isolation_forest_model.joblib"
    if model_file.exists():
        model, features, _ = load_pipeline_model(model_file)
    else:
        print("Model artifact not found; training model on secondary dataset first...")
        run_res = run_detection(data_dir, output_dir=data_dir)
        model = run_res["model"]
        features = run_res["summary"]["model_features"]

    # History is all prior quarters; target is latest quarter
    hist = sub.iloc[:-1]
    latest = sub.iloc[-1].to_dict()

    scorecard = score_new_filing(latest, hist, model=model, feature_columns=features)
    print_scorecard(scorecard)
    return 0


def score_custom_file(filing_path: str, data_dir: Path) -> int:
    """Score a custom JSON or CSV filing against the historical benchmark."""
    import pandas as pd

    p = Path(filing_path)
    if not p.exists():
        print(f"Error: filing file not found at {p}")
        return 1

    if p.suffix.lower() == ".json":
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        new_row = data if isinstance(data, dict) else data[0]
    else:
        df_custom = pd.read_csv(p)
        new_row = df_custom.iloc[-1].to_dict()

    ticker = new_row.get("ticker", "CUSTOM")
    q_file = data_dir / "quarterly_features.csv"
    hist = pd.read_csv(q_file, low_memory=False) if q_file.exists() else pd.DataFrame()

    model_file = data_dir / "isolation_forest_model.joblib"
    if model_file.exists():
        model, features, _ = load_pipeline_model(model_file)
    else:
        run_res = run_detection(data_dir, output_dir=data_dir)
        model = run_res["model"]
        features = run_res["summary"]["model_features"]

    scorecard = score_new_filing(new_row, hist, model=model, feature_columns=features)
    print_scorecard(scorecard)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SEC Filing Financial Anomaly Detection & New Filing Pipeline")
    parser.add_argument("--data-dir", type=str, default=None, help="path to directory containing quarterly_features.csv")
    parser.add_argument("--output-dir", type=str, default=None, help="directory to save scored outputs")
    parser.add_argument("--contamination", type=float, default=0.05, help="Isolation Forest anomaly threshold (default: 0.05)")
    parser.add_argument("--z-threshold", type=float, default=3.5, help="Robust/trailing Z-score threshold (default: 3.5)")
    parser.add_argument("--refresh-extraction", action="store_true", help="execute EDGAR extraction notebook first")
    parser.add_argument("--clear-cache", action="store_true", help="clear edgar_cache before refreshing extraction")
    parser.add_argument("--ticker", type=str, default=None, help="score latest filing for a specific company ticker")
    parser.add_argument("--filing-file", type=str, default=None, help="path to a JSON or CSV file containing a new filing to score")

    args = parser.parse_args()

    data_dir = resolve_data_dir(args.data_dir)
    output_dir = Path(args.output_dir) if args.output_dir else data_dir

    if args.clear_cache and not args.refresh_extraction:
        parser.error("--clear-cache requires --refresh-extraction")

    if args.refresh_extraction:
        refresh_extraction(ROOT, clear_cache=args.clear_cache)

    # 1. Custom filing file scoring
    if args.filing_file:
        return score_custom_file(args.filing_file, data_dir)

    # 2. Single company filing scoring
    if args.ticker:
        return score_single_ticker(args.ticker, data_dir)

    # 3. Default: Full dataset scoring
    if not (data_dir / "quarterly_features.csv").exists():
        parser.error(f"quarterly_features.csv not found in {data_dir}. Run with --refresh-extraction or specify --data-dir.")

    print(f"\nRunning Deliverable 2 Anomaly Detection Pipeline on: {data_dir}")
    print(f"Parameters: contamination={args.contamination}, z_threshold={args.z_threshold}")

    result = run_detection(
        data_dir,
        output_dir=output_dir,
        contamination=args.contamination,
        z_threshold=args.z_threshold,
    )
    summary = result["summary"]

    print("\n" + "=" * 65)
    print("  DELIVERABLE 2 PIPELINE EXECUTION SUMMARY")
    print("=" * 65)
    print(f"  Rows Scored                         : {summary['rows_scored']:,}")
    print(f"  Model Features Selected             : {summary['model_feature_count']}")
    print(f"  Isolation Forest Flags              : {summary['isolation_forest_flagged']:,} (top {args.contamination*100:.1f}%)")
    print(f"  Statistical Z-Score Flags (|Z|>=3.5): {summary['statistical_flagged']:,}")
    print(f"  Multi-Year Sudden Deviations        : {summary['multi_year_trend_flagged']:,}")
    print("-" * 65)
    print("  Generated Reports & Artifacts:")
    for name, path in summary["outputs"].items():
        print(f"   * {name:<28}: {Path(path).name}")
    print("=" * 65 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
