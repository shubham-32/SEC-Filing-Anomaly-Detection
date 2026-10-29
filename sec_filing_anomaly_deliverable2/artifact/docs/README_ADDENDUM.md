## Deliverable 2 — Anomaly detection

The repository includes `02_ml_anomaly_detection.ipynb` for the analysis and `run_pipeline.py` for repeatable execution. Install dependencies with `python -m pip install -r requirements.txt`, then run `python run_pipeline.py` to score the committed secondary dataset. Outputs are written under `data/processed/`.

To refresh EDGAR data before scoring, set the `SEC_USER_AGENT` environment variable to an identifying name and email, then run `python run_pipeline.py --refresh-extraction --clear-cache`. See [`docs/DELIVERABLE2.md`](docs/DELIVERABLE2.md) for methods, output descriptions, interpretation limits, and scheduled execution setup. The weekly/manual workflow is at `.github/workflows/refresh-anomalies.yml` and requires an Actions secret called `SEC_USER_AGENT`.
