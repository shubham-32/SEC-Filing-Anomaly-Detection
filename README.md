# SEC Filing Financial Anomaly Detection System

**Task ID:** FDA-2: Fraud Detection through Financial Anomalies  
**Course:** Big Data Analytics (Semester 7)  
**Deliverables Completed:**  
- **Deliverable 1:** Data Extraction, XBRL Standardization & Secondary Dataset  
- **Deliverable 2:** Machine Learning, Multi-Year Trend Analysis & Automated New-Filing Pipeline  

---

## 1. Project Overview

This project builds an automated end-to-end forensic analytics system to identify financial anomalies in US public company SEC EDGAR filings that could indicate fraudulent financial reporting, earnings manipulation, or severe operational distress.

The system combines:
1. **Automated SEC EDGAR Data Extraction (Deliverable 1):** Ingests raw XBRL filings, resolves reporting tag switches (ASC 606), derives discrete quarters, and constructs a point-in-time secondary dataset across 12 fiscal years (FY2014–FY2026).
2. **Multi-Year Financial Trend Analytics (Deliverable 2):** Evaluates trailing 12-quarter (3-year) rolling baselines to detect structural breaks and inconsistent divergences (e.g. accelerating revenue growth while operating cash flows or margins collapse).
3. **Statistical Anomaly Detection (Deliverable 2):** Computes trailing robust Z-scores using rolling median and Median Absolute Deviation (MAD) over prior quarters, isolating extreme quarterly shocks ($|Z| \ge 3.5\sigma$).
4. **Machine Learning Anomaly Detection (Deliverable 2):** Implements a 300-tree **Isolation Forest** pipeline with robust scaling to detect subtle multidimensional patterns across 42 financial features.
5. **Annual Beneish M-Score Benchmark (Deliverable 2):** Compares quarterly alerts against the classic 8-variable forensic manipulation probability index.
6. **Automated Pipeline for New Filings (Deliverable 2):** An automated CLI engine that scores new filings on the fly, evaluates risk consensus, and generates an actionable forensic audit scorecard.

---

## 2. Repository Structure

```
├── README.md                                 # Complete project documentation (Deliverables 1 & 2)
├── 01_edgar_data_extraction.ipynb            # Deliverable 1: Extraction & secondary dataset build
├── 02_ml_anomaly_detection.ipynb             # Deliverable 2: Fully executed ML & trend analysis notebook
├── run_pipeline.py                           # Automated pipeline CLI for batch and new filing scoring
├── live_demo.py                              # Interactive evaluation console for live project demonstration
├── data_dictionary.csv                       # Feature definitions and XBRL lineage
├── SEC_Anomaly_Detection_Deliverable1.pptx   # Deliverable 1 presentation deck
├── SEC_Anomaly_Detection_Deliverable2.pptx   # Deliverable 2 presentation deck (16 widescreen slides)
│
├── data/
│   └── processed/                            # Secondary dataset and generated ML artifacts
│       ├── quarterly_features.csv            # Main secondary dataset (1,334 company-quarters, 94 features)
│       ├── annual_features.csv               # Annual financial ratios and Beneish M-Scores
│       ├── facts_long.csv                    # Audit trail of 47,514 raw XBRL facts mapped to accession numbers
│       ├── coverage_report.csv               # Company data completeness audit
│       ├── scored_quarterly.csv              # Full dataset with ML scores, Z-scores, and trend flags
│       ├── anomaly_top100.csv                # Top 100 highest-ranked anomalous company-quarters
│       ├── model_comparison.csv              # Statistical vs Isolation Forest comparison table
│       ├── company_anomaly_ranking.csv       # Company-level anomaly frequency leaderboard
│       ├── beneish_comparison.csv            # Concordance between quarterly alerts and annual M-Scores
│       ├── multi_year_trend_anomalies.csv    # Quarters exhibiting multi-year structural trend breaks
│       ├── isolation_forest_model.joblib     # Pre-trained scikit-learn model artifact
│       └── run_summary.json                  # Pipeline execution metadata and parameters
│
├── src/
│   ├── __init__.py                           # Package marker
│   └── anomaly_pipeline.py                   # Core ML, statistical, trend, and scoring engine
│
├── tests/
│   ├── __init__.py                           # Test package marker
│   └── test_anomaly_pipeline.py              # 6 unit and integration test suites
│
├── docs/
│   ├── DELIVERABLE2.md                       # Comprehensive Deliverable 2 methodology documentation
│   └── figures/                              # High-resolution generated visualization charts
│       ├── score_distribution.png            # Isolation Forest KDE distribution (Reference vs Control)
│       ├── multi_year_trends.png             # 10+ year trajectory comparison (KHC, SMCI, MSFT)
│       ├── top_anomalies_barchart.png        # Top 15 anomaly candidates bar chart
│       └── case_studies_signals.png          # Real-world scandal signals (KHC write-down, UAA channel stuffing)
│
└── sec_filing_anomaly_deliverable2/          # Standalone deliverable 2 package (synchronized)
```

---

## 3. Quick Start Guide

### 3.1 Install Dependencies
```bash
pip install pandas numpy scikit-learn scipy statsmodels matplotlib seaborn python-pptx joblib nbformat nbclient nbconvert
```

### 3.2 Run the Automated Pipeline
```bash
# 1. Batch scoring of the secondary dataset:
python run_pipeline.py

# 2. Score a specific company's latest filing on demand:
python run_pipeline.py --ticker SMCI
python run_pipeline.py --ticker KHC
python run_pipeline.py --ticker AAPL

# 3. Score a custom filing JSON or CSV file:
python run_pipeline.py --filing-file path/to/filing.json
```

### 3.3 Launch the Live Interactive Demonstration Console
For project evaluation and viva demonstrations:
```bash
python live_demo.py
```
**Interactive Modes:**
1. **Interactive Company Anomaly Explorer:** View any company's 10-year quarterly history, flag rates, and sudden deviation quarters.
2. **Top Anomalies Leaderboard:** Universe-wide ranking of the most anomalous filings.
3. **Automated Pipeline for New Filings (Live Simulation):** Ingest and score live filings for KHC, UAA, SMCI, or MSFT in under two seconds.
4. **Forensic Fraud Case Studies:** Walkthrough the exact signals behind documented scandals.
5. **Run Full Batch Pipeline:** One-click re-scoring and artifact refresh.

### 3.4 Run the Unit & Integration Tests
```bash
python -c "from tests import test_anomaly_pipeline as t; t.test_quality_filters_and_feature_selection(); t.test_scoring_and_comparison_outputs(); t.test_multi_year_trend_analysis(); t.test_score_new_filing(); print('All tests passed!')"
```

---

## 4. Methodology & Key Findings

### 4.1 Secondary Dataset (Deliverable 1)
- **Scope:** 26 companies across 12 fiscal years (FY2014–FY2026), comprising 1,334 company-quarters and 94 features.
- **Control Group (20 companies):** Established blue chips (Apple, Microsoft, Johnson & Johnson, Costco, Caterpillar, Walmart, etc.).
- **Reference Group (6 companies):** Companies with documented SEC enforcement actions or restatements (Kraft Heinz, Under Armour, Super Micro Computer, MiMedx, Plug Power, Mattel).
- **Point-in-Time Data:** Retains numbers **as first reported** to prevent look-ahead bias and avoid artificial distortions from post-spinoff recasts.

### 4.2 Multi-Year Financial Trend Analysis (Deliverable 2)
- Trailing 12-quarter (3-year) rolling means ($\mu_{12Q}$) and standard deviations ($\sigma_{12Q}$) strictly prior to the evaluated quarter (`shift(1)`).
- **Sudden Deviation:** $|\text{Trend Dev}| \ge 2.5\sigma$ marks structural trend breaks (282 quarters flagged).
- **Inconsistent Trends:** Identifies quarters where revenue growth accelerates while operating margins or operating cash flows suddenly collapse.

### 4.3 Statistical Anomaly Detection (Deliverable 2)
- Uses rolling median and Median Absolute Deviation (MAD) over prior quarters:
  $$RZ_t = \frac{x_t - \text{Median}(x_{t-8..t-1})}{1.4826 \times \text{MAD}(x_{t-8..t-1})}$$
- **Threshold:** $|Z| \ge 3.5\sigma$ (391 quarters flagged; 33.5% reference flag rate vs 31.0% control flag rate).

### 4.4 Machine Learning Anomaly Detection (Deliverable 2)
- 300-tree **Isolation Forest** trained on 42 financial ratios with `RobustScaler` (10th–90th percentile) and `SimpleImputer(median)`.
- **Contamination:** 0.05 (flags top 5.0% most unusual quarters = 62 observations).
- Higher flag rate in the Reference Group (5.6%) versus Control Group (4.8%).

### 4.5 Forensic Case Studies (Real-World Scandals Detected)
1. **Kraft Heinz (KHC) Procurement Fraud:** Operating margin crashed to **-205%** ($RZ = -9.45\sigma$) in FY2018 Q4 alongside a $15.4B goodwill write-down. Classified as **HIGH ANOMALY**.
2. **Under Armour (UAA) Channel Stuffing:** Receivables growth outstripped revenue growth by **$7.23\sigma$** (`ar_growth_minus_revenue_growth` $RZ = 7.23$) during the 2015-2016 pull-forward period.
3. **Super Micro Computer (SMCI) Revenue Recognition:** Extreme revenue growth acceleration ($RZ = 3.15\sigma$) and Days Sales Outstanding volatility ($RZ = 5.00\sigma$).

---

## 5. Summary of Project Deliverables

| Deliverable Component | Status | Location / Artifact |
|---|---|---|
| **Deliverable 1: Secondary Dataset** | Completed | `data/processed/quarterly_features.csv`, `annual_features.csv` |
| **Deliverable 1: Extraction Notebook** | Completed | `01_edgar_data_extraction.ipynb` |
| **Deliverable 1: Documentation** | Completed | `data_dictionary.csv`, `README.md` |
| **Deliverable 1: Presentation** | Completed | `SEC_Anomaly_Detection_Deliverable1.pptx` |
| **Deliverable 2: ML Analytics Notebook** | Completed | `02_ml_anomaly_detection.ipynb` (fully executed with outputs & plots) |
| **Deliverable 2: Automated Pipeline** | Completed | `run_pipeline.py` & `src/anomaly_pipeline.py` (batch & single filing scoring) |
| **Deliverable 2: Documentation** | Completed | `docs/DELIVERABLE2.md` & `README.md` |
| **Deliverable 2: Presentation** | Completed | `SEC_Anomaly_Detection_Deliverable2.pptx` (16 widescreen slides with embedded figures) |
| **Live Demonstration Tool** | Completed | `live_demo.py` (interactive CLI evaluation console) |
| **Automated Test Suite** | Completed | `tests/test_anomaly_pipeline.py` (6 unit/integration tests) |

---

## 6. Operational Forensic Triage Protocol

```
[New SEC Filing Received]
           │
           ▼
[Automated Feature Pipeline] ──> Compute Growth, Ratios, Trailing Z-Scores, Multi-Year Trends
           │
           ▼
[Multi-Method Anomaly Scoring]
   ├─ Robust Z-Score (|Z| >= 3.5)
   ├─ Isolation Forest (Top 5% Contamination)
   └─ Multi-Year Trend Deviation (|dev| >= 2.5σ)
           │
           ▼
[Risk Classification]
   ├─ HIGH ANOMALY (Multi-Method Consensus) ──> Immediate Priority Audit (Receivables, Contracts, Write-Downs)
   ├─ ELEVATED (Single-Method Alert)        ──> Secondary Review (Inspect Tagging, Discontinued Ops, Restatements)
   └─ NORMAL                                ──> Cleared for Automated Monitoring
```

---

## 7. Limitations & Honest Disclosures

1. **Anomaly Score is Not Fraud Proof:** An anomaly score highlights observations for human audit prioritization. Genuine corporate events (such as spinoffs, acquisitions, or accounting standard transitions) can cause extreme deviations.
2. **US-GAAP & USD Coverage:** Only US-GAAP filers in USD are extracted from the SEC EDGAR facts API. Foreign private issuers filing under IFRS on Form 20-F are not covered.
3. **Q4 Adjustment Volatility:** Derived Q4 figures absorb year-end audit adjustments and impairments, naturally exhibiting greater volatility than regular quarters.
4. **Weak Labels:** Reference group labels reflect company-level historical enforcement and restatement records, not quarter-level ground truth. Model comparisons are descriptive validation tools.
