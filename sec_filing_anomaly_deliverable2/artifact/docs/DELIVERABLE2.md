# Deliverable 2 — Financial Anomaly Detection and New-Filing Pipeline

## Objective

Identify unusual company-quarter financial patterns in the EDGAR-derived secondary dataset. The system surfaces observations for further investigation; it does **not** classify any company or quarter as fraudulent.

## Inputs

- `data/processed/quarterly_features.csv` — primary company-quarter feature panel from Deliverable 1.
- `data/processed/annual_features.csv` — annual financial features and Beneish M-Score baseline.
- `data_dictionary.csv` — feature definitions.

## Methods

### 1. Data-quality filtering

The scoring workflow does not edit the original Deliverable 1 CSV. It prepares a modelling copy and by default excludes rows flagged for negative/missing revenue, unusual period length, an annual value mis-tagged as a quarter, or quarter/annual revenue mismatch. It also excludes rows where the revenue XBRL tag changed, because growth features may reflect a reporting-tag change instead of business performance. The exact row counts filtered are saved in `run_summary.json`.

These are pragmatic first-pass filters, not replacements for a full reconciliation audit. Always review exclusions and the data-coverage report before making a substantive conclusion.

### 2. Statistical detection

The dataset already contains trailing Z-score (`z_*`) and robust trailing Z-score (`rz_*`) features calculated from prior quarters. The detection step computes a per-row score as the maximum absolute available robust Z-score; ordinary trailing Z-scores are used only if robust scores are unavailable. The default threshold is 3.5. This score points to outlying metrics, not to a fraud probability.

### 3. Isolation Forest

The workflow selects pre-defined numeric growth, ratio, margin, earnings-quality and trailing-Z-score features. It does not feed company identifiers, company/group labels, or restatement outcome fields into the model. Features with more than 45% missing values or no variation in the retained sample are not selected. Remaining missing values are median-imputed; robust scaling is applied before a 300-tree Isolation Forest. The default `contamination=0.05` marks the most unusual 5% of retained observations according to the model's internal threshold. **This is a threshold setting, not an estimate that 5% of observations are fraudulent.**

### 4. Group comparison and weak labels

`group` (control/reference) is used only after fitting to compare descriptive flag rates and review ranks. The reference group is a company-level weak label based on reported accounting events, not verified ground truth for every quarter. Consequently, do not present the reference/control flag-rate difference as model precision, recall, or proof of superior fraud prediction.

### 5. Beneish M-Score benchmark

Annual Beneish M-Score and `beneish_flag` are joined after quarterly model scoring, solely for post-hoc comparison. They are not model inputs. The M-Score is an additional screening indicator; it also can produce false positives and is not proof of manipulation.

## Outputs

Files are written to `data/processed/`:

- `scored_quarterly.csv` — retained quarters with Z-score and Isolation Forest outputs, plus annual Beneish fields where available.
- `anomaly_top100.csv` — highest-ranked retained quarters, sorted by Isolation Forest anomaly score.
- `model_comparison.csv` — descriptive row counts and flag rates for the two methods.
- `company_anomaly_ranking.csv` — aggregated company-level ranking summary.
- `beneish_comparison.csv` — company-year comparison between quarterly alerts and annual Beneish results.
- `run_summary.json` — filter counts, selected features, model settings and paths.

## Run locally

Install requirements:

```bash
python -m pip install -r requirements.txt
```

Run modelling on the current committed dataset:

```bash
python run_pipeline.py
```

Refresh the EDGAR data and then rerun modelling:

```bash
# PowerShell
$env:SEC_USER_AGENT = "Your Name you@example.com"
python run_pipeline.py --refresh-extraction --clear-cache

# macOS/Linux
export SEC_USER_AGENT="Your Name you@example.com"
python run_pipeline.py --refresh-extraction --clear-cache
```

`--clear-cache` is recommended for a refresh because the existing extraction notebook caches raw SEC responses. It requires `--refresh-extraction`. The runner executes the extraction notebook in a temporary output location so the committed notebook's cell outputs are not overwritten. It does not remove or alter the original source notebook.

## Scheduled run

The workflow `.github/workflows/refresh-anomalies.yml` can be run manually or weekly. Add a repository Actions secret named `SEC_USER_AGENT` with a compliant identifying string such as `Project Name contact@example.com`. The workflow uploads the generated CSV and JSON reports as a downloadable Actions artifact; it does not automatically commit refreshed raw data or score files back into the repository.

## Interpretation and limitations

1. Anomaly score is not fraud probability. A flag means an observation deserves a closer look.
2. Mergers, divestitures, seasonality, fiscal calendars, accounting changes and tagging differences can create legitimate anomalies.
3. The extraction pipeline has reported company-year quarter/annual revenue mismatches; the default modelling filters exclude rows carrying relevant quality flags, but users should inspect the filtering report.
4. The data covers US-GAAP facts available from the SEC Company Facts API and can miss custom tags, segment data or IFRS filers.
5. Historical scoring is retrospective. A production real-time fraud-warning claim would require point-in-time feature reconstruction, leakage checks, event-dated labels and prospective evaluation.
6. The reference company list is small and heterogeneous. Model comparisons are descriptive only until labels are verified at quarter/event level.

## Suggested manual review protocol

For each top-ranked quarter, review the contributing ratio/growth changes, the previous-year quarter, revenue-tag and data-quality indicators, filing accession history/restatement indicators, contemporaneous company announcements, and the relevant SEC filing. Record whether the signal appears to be a data issue, legitimate operating change, or an unresolved red flag. Do not call the observation fraud without independent evidence.
