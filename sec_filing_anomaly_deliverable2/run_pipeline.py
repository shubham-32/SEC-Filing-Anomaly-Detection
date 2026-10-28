"""Run Deliverable 2 and optionally refresh SEC EDGAR extraction first.

Examples:
  python run_pipeline.py
  SEC_USER_AGENT="Name email@example.com" python run_pipeline.py --refresh-extraction --clear-cache
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "processed"
EXTRACTION_NOTEBOOK = ROOT / "01_edgar_data_extraction.ipynb"


def refresh_extraction(*, clear_cache: bool) -> None:
    user_agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not user_agent:
        raise RuntimeError(
            "Set SEC_USER_AGENT to 'Your Name your@email.com' before refreshing SEC data. "
            "The SEC requires an identifying User-Agent for automated requests."
        )
    if not EXTRACTION_NOTEBOOK.exists():
        raise FileNotFoundError(f"Extraction notebook not found: {EXTRACTION_NOTEBOOK}")
    if clear_cache:
        cache_dir = ROOT / "edgar_cache"
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            print(f"Removed cached SEC responses: {cache_dir}")
    with tempfile.TemporaryDirectory(prefix="sec-edgar-refresh-") as temp_dir:
        cmd = [
            sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook",
            "--execute", str(EXTRACTION_NOTEBOOK), "--output", "extraction_run.ipynb",
            "--output-dir", temp_dir, "--ExecutePreprocessor.timeout=1800",
        ]
        print("Refreshing the EDGAR dataset by executing the extraction notebook...")
        subprocess.run(cmd, cwd=ROOT, env=os.environ.copy(), check=True)
    print("Extraction refresh completed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SEC financial anomaly detection")
    parser.add_argument("--refresh-extraction", action="store_true", help="execute the existing EDGAR extraction notebook first")
    parser.add_argument("--clear-cache", action="store_true", help="delete edgar_cache before extraction to fetch fresh SEC responses; requires --refresh-extraction")
    parser.add_argument("--contamination", type=float, default=0.05, help="Isolation Forest flagging fraction (default: 0.05; not fraud prevalence)")
    parser.add_argument("--z-threshold", type=float, default=3.5, help="absolute robust/trailing Z threshold (default: 3.5)")
    args = parser.parse_args()

    if args.clear_cache and not args.refresh_extraction:
        parser.error("--clear-cache requires --refresh-extraction")
    if args.refresh_extraction:
        refresh_extraction(clear_cache=args.clear_cache)

    if not (DATA_DIR / "quarterly_features.csv").exists():
        parser.error(f"No quarterly_features.csv found in {DATA_DIR}. Run with --refresh-extraction first.")
    sys.path.insert(0, str(ROOT))
    from src.anomaly_pipeline import run_detection

    result = run_detection(
        DATA_DIR,
        output_dir=DATA_DIR,
        contamination=args.contamination,
        z_threshold=args.z_threshold,
    )
    summary = result["summary"]
    print("\nAnomaly-detection run completed")
    print(f"Rows scored: {summary['rows_scored']:,}")
    print(f"Features used: {summary['model_feature_count']}")
    print(f"Isolation Forest flagged: {summary['isolation_forest_flagged']:,}")
    print(f"Statistical method flagged: {summary['statistical_flagged']:,}")
    print(f"Outputs: {DATA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
