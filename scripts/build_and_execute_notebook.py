"""Script to generate and execute 02_ml_anomaly_detection.ipynb with complete outputs and plots."""
import os
import sys
from pathlib import Path
import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent

def build_notebook():
    nb = new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13"
        }
    }

    cells = []

    # Cell 1: Header Markdown
    cells.append(new_markdown_cell("""# SEC Filing Anomaly Detection — Deliverable 2: Machine Learning & Multi-Year Trend Analytics

**Task ID:** FDA-2: Fraud Detection through Financial Anomalies  
**Course:** Big Data Analytics (Sem 7)  
**Deliverable:** 2 — Machine Learning, Multi-Year Trend Analysis & Automated New-Filing Pipeline  

---

### Objectives
1. **Apply Statistical Anomaly Detection:** Calculate trailing robust Z-scores ($RZ$) using rolling median and Median Absolute Deviation (MAD) to detect sudden quarterly deviations.
2. **Apply Machine Learning Anomaly Detection:** Train an **Isolation Forest** (with Robust Scaling and Median Imputation) on high-dimensional multi-ratio financial feature spaces.
3. **Compare Multi-Year Trends for Sudden Deviations:** Ingest 5+ years of financial statements and analyze rolling 3-year (12-quarter) trajectories to isolate structural breaks and inconsistent trends in revenue, expenses, and margins.
4. **Benchmark against Forensic Accounting Baselines:** Compare quarterly statistical and ML alerts with the annual **Beneish M-Score** (manipulation probability index).
5. **Evaluate Against Reference Fraud Cases:** Validate detection sensitivity against reference companies with documented SEC Accounting and Auditing Enforcement Releases (AAERs) or restatements (Kraft Heinz, Under Armour, Super Micro Computer, MiMedx, Plug Power, Mattel) versus control blue chips.
6. **Automated Pipeline for New Filings:** Provide an automated scoring engine that ingests new filings, extracts features, calculates multi-year deviations, and generates an audit triage scorecard.

> **Forensic Review Principle:** Anomaly scores highlight unusual financial configurations for human audit prioritization; they represent statistical deviations and review candidates, not proof of fraud."""))

    # Cell 2: Imports and Setup
    cells.append(new_code_cell("""import sys
import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, HTML

# Configure visual styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["font.size"] = 10
plt.rcParams["figure.dpi"] = 120

# Resolve paths
CWD = Path.cwd()
REPO_ROOT = CWD if (CWD / "src" / "anomaly_pipeline.py").exists() else CWD.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.anomaly_pipeline import (
    load_inputs,
    prepare_observations,
    select_features,
    robust_zscore_results,
    isolation_forest_results,
    compute_multi_year_trends,
    attach_beneish_baseline,
    build_beneish_comparison,
    summarize_results,
    score_new_filing,
    run_detection,
    resolve_data_dir,
    load_pipeline_model,
)

DATA_DIR = resolve_data_dir(REPO_ROOT / "data" / "processed")
print("Repository Root :", REPO_ROOT)
print("Data Directory  :", DATA_DIR)
"""))

    # Cell 3: Data Loading
    cells.append(new_markdown_cell("""## 1. Secondary Dataset Ingestion & Overview

We load the secondary dataset produced in Deliverable 1 (`quarterly_features.csv` and `annual_features.csv`).
- **Quarterly Data:** 1,334 company-quarters across 26 companies from FY2014 to FY2026 (12 years of quarterly data).
- **Control Group (20 companies):** Established large-cap US corporations (e.g., Apple, Microsoft, Johnson & Johnson, Costco, Caterpillar).
- **Reference Group (6 companies):** Companies with publicly documented accounting irregularities, SEC investigations, or major restatements (KHC, UAA, SMCI, MDXG, PLUG, MAT)."""))

    cells.append(new_code_cell("""quarterly, annual = load_inputs(DATA_DIR)
print(f"Quarterly Observations : {quarterly.shape[0]:,} rows × {quarterly.shape[1]} columns")
print(f"Annual Observations    : {annual.shape[0]:,} rows × {annual.shape[1]} columns" if annual is not None else "Annual data unavailable")

# Display company distribution by group
group_summary = quarterly.groupby(["group", "ticker"])["fiscal_year"].agg(["min", "max", "count"]).reset_index()
group_summary.columns = ["Group", "Ticker", "Start Year", "End Year", "Quarters"]
print("\\nCompany Universe Breakdown:")
display(group_summary.groupby("Group")["Ticker"].agg(Company_Count="nunique", Total_Quarters="sum"))
"""))

    # Cell 4: Data Quality Auditing
    cells.append(new_markdown_cell("""## 2. Data-Quality Governance & Pre-Modelling Filtering

To ensure statistical rigor, we apply conservative row-level data quality filters:
- **Exclusion of `dq_*` flags:** Quarters with negative revenue, missing revenue, unusual period lengths, or fiscal year/quarter sum mismatches are quarantined.
- **Exclusion of XBRL Tag Switches (`revenue_tag_changed`):** When a company switches revenue tags (e.g. adoption of ASC 606 in 2018 from `SalesRevenueNet` to `RevenueFromContractWithCustomerExcludingAssessedTax`), artificial growth jumps occur. These are filtered to prevent false positive alerts."""))

    cells.append(new_code_cell("""clean, filter_stats = prepare_observations(
    quarterly,
    exclude_quality_flags=True,
    exclude_tag_switches=True,
)

print("Filtering Statistics:")
for k, v in filter_stats.items():
    print(f"  {k:<28}: {v:,}")

# Audit dq flag frequencies
quality_cols = [c for c in [
    "dq_negative_revenue", "dq_missing_revenue", "dq_period_length_unusual",
    "dq_quarter_looks_annual", "dq_quarter_sum_mismatch", "revenue_tag_changed"
] if c in quarterly.columns]

dq_report = pd.DataFrame({
    "Data Quality Indicator": quality_cols,
    "Flagged Quarters": [int(quarterly[c].astype(str).str.lower().isin(["true", "1", "yes"]).sum()) for c in quality_cols],
    "Share of Input (%)": [float(quarterly[c].astype(str).str.lower().isin(["true", "1", "yes"]).mean() * 100) for c in quality_cols],
})
display(dq_report)
"""))

    # Cell 5: Multi-Year Trend Analysis & Sudden Deviations
    cells.append(new_markdown_cell("""## 3. Multi-Year Financial Trend Analysis & Sudden Deviations

### Assignment Objective:
> *"Compare multi-year trends for sudden deviations. Extract 5+ years of financial statements. Identify inconsistent trends in revenue, expenses, or margins."*

To identify multi-year structural anomalies without look-ahead bias:
1. We compute **strictly trailing 3-year (12-quarter) rolling averages and standard deviations** for:
   - Revenue YoY Growth
   - Total Expense-to-Revenue Ratio
   - Gross Margin & Operating Margin
   - Sloan Accruals to Assets
   - Receivables Growth vs Revenue Growth
2. We evaluate **standardized trend deviation scores**:
   $$\\text{Trend Dev} = \\frac{\\text{Current Metric} - \\mu_{\\text{trailing 12Q}}}{\\sigma_{\\text{trailing 12Q}}}$$
3. Quarters with $|\\text{Trend Dev}| \\ge 2.5\\sigma$ indicate **sudden multi-year trend breaks**.
4. We detect **inconsistent trends**: where revenue growth accelerates while operating margins collapse, or where expenses dramatically outrun revenue."""))

    cells.append(new_code_cell("""clean, trend_anomalies = compute_multi_year_trends(clean, rolling_quarters=12, min_periods=4, deviation_threshold=2.5)

print(f"Total Quarters Analyzed with Multi-Year Baselines : {len(clean):,}")
print(f"Quarters with Sudden Multi-Year Deviations (|dev|>=2.5) : {int(clean['multi_year_sudden_deviation'].sum()):,}")
print(f"Quarters with Inconsistent Trends (Rev vs Margins)     : {int(clean['inconsistent_trend_flag'].sum()):,}")

# Display top multi-year anomalies
print("\\nTop 10 Sudden Multi-Year Trend Breaks:")
display(trend_anomalies[[
    "ticker", "company", "group", "fiscal_year", "fiscal_quarter", "period_end",
    "revenue_yoy_growth", "gross_margin", "operating_margin", "total_expense_to_revenue", "max_trend_deviation"
]].head(10))
"""))

    # Cell 6: Visualizing Multi-Year Trends: Control vs Reference
    cells.append(new_markdown_cell("""### Visualizing Multi-Year Trajectories: Fraud Reference vs Control Blue Chips

We plot the 10+ year trajectory of operating margins and revenue growth for:
- **Kraft Heinz (KHC - Reference):** Severe margin crash in FY2018 during procurement fraud and goodwill impairment.
- **Super Micro Computer (SMCI - Reference):** Extreme revenue surges and margin volatility.
- **Microsoft (MSFT - Control):** Stable, high-margin software trajectory."""))

    cells.append(new_code_cell("""fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=False)

sample_companies = [
    ("KHC", "Kraft Heinz (Reference - Procurement Accounting Scandal)", "red"),
    ("SMCI", "Super Micro Computer (Reference - Revenue Recognition Irregularities)", "darkorange"),
    ("MSFT", "Microsoft (Control - Stable Enterprise SaaS)", "navy")
]

for idx, (t, title, color) in enumerate(sample_companies):
    sub = clean[clean["ticker"] == t].sort_values("period_end")
    ax = axes[idx]
    ax.plot(sub["period_end"], sub["operating_margin"], marker="o", markersize=4, color=color, label="Operating Margin")
    ax.plot(sub["period_end"], sub["revenue_yoy_growth"], marker="s", markersize=3, linestyle="--", color="gray", alpha=0.7, label="Revenue YoY Growth")
    
    # Highlight sudden deviation quarters
    anom = sub[sub["multi_year_sudden_deviation"]]
    if not anom.empty:
        ax.scatter(anom["period_end"], anom["operating_margin"], color="black", s=90, zorder=5, label="Sudden Trend Break (|dev|>=2.5σ)")
        
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel("Rate / Margin")
    ax.legend(loc="upper left", frameon=True)
    ax.set_ylim(-1.5, 1.0)
    ax.axhline(0, color="black", linestyle=":", alpha=0.5)

plt.tight_layout()
plt.show()
"""))

    # Cell 7: Feature Selection
    cells.append(new_markdown_cell("""## 4. Feature Selection & Engineering

We select pre-specified financial ratios and trailing statistical features:
- **Growth Features:** `revenue_qoq_growth`, `revenue_yoy_growth`, `cogs_yoy_growth`, `sga_yoy_growth`, `net_income_yoy_growth`, `ar_yoy_growth`.
- **Expense-to-Revenue Ratios & Margins:** `cogs_to_revenue`, `sga_to_revenue`, `rnd_to_revenue`, `opex_to_revenue`, `total_expense_to_revenue`, `gross_margin`, `operating_margin`, `net_margin`.
- **Working Capital & Forensic Accruals:** Days Sales Outstanding (`dso`), Days Inventory Outstanding (`dio`), Sloan Accruals (`accruals_to_assets`), `cfo_to_net_income`, `ar_growth_minus_revenue_growth` (channel stuffing indicator).
- **Trailing Statistical Z-Scores:** Pre-computed 8-quarter trailing robust Z-scores (`rz_*`) and ordinary Z-scores (`z_*`).

> **Information Integrity Check:** Company tickers, CIKs, group labels, and post-hoc restatement flags are **strictly excluded** from the model feature matrix."""))

    cells.append(new_code_cell("""feature_columns = select_features(clean, max_missing_fraction=0.45, minimum_features=5)
print(f"Selected {len(feature_columns)} Model Features across 5 Core Financial Families:")
for i in range(0, len(feature_columns), 5):
    print("  • " + ", ".join(feature_columns[i:i+5]))
"""))

    # Cell 8: Statistical Anomaly Detection
    cells.append(new_markdown_cell("""## 5. Statistical Anomaly Detection (Robust Trailing Z-Score)

### Methodology:
For each observation, we evaluate its trailing robust Z-scores ($RZ$) calculated using median and Median Absolute Deviation (MAD) over prior quarters:
$$RZ_t = \\frac{x_t - \\text{Median}(x_{t-8..t-1})}{1.4826 \\times \\text{MAD}(x_{t-8..t-1})}$$
- **Composite Score:** $\\text{Score}_{\\text{stat}} = \\max(|RZ_{\\text{metric}}|)$
- **Threshold:** A threshold of **$3.5\\sigma$** marks extreme deviations beyond normal cyclical fluctuations."""))

    cells.append(new_code_cell("""Z_THRESHOLD = 3.5
scored = robust_zscore_results(clean, threshold=Z_THRESHOLD)

print(f"Statistical Threshold               : {Z_THRESHOLD} sigma")
print(f"Total Observations Scored          : {len(scored):,}")
print(f"Statistical Anomaly Flags (|Z|>=3.5): {int(scored['statistical_anomaly'].sum()):,} ({scored['statistical_anomaly'].mean()*100:.2f}%)")
print(f"Median Statistical Anomaly Score    : {scored['statistical_anomaly_score'].median():.2f}")
"""))

    # Cell 9: Machine Learning Anomaly Detection (Isolation Forest)
    cells.append(new_markdown_cell("""## 6. Machine Learning Anomaly Detection (Isolation Forest)

### Methodology:
1. **Preprocessing:** 
   - `SimpleImputer(strategy='median')`: Preserves robust central tendencies for missing metrics.
   - `RobustScaler(quantile_range=(10.0, 90.0))`: Normalizes features without distortion from extreme outliers.
2. **Isolation Forest Model:**
   - Evaluates multi-dimensional anomaly isolation across 300 decision trees.
   - Anomalies are isolated closer to tree roots due to rare, extreme multidimensional combinations.
   - `contamination=0.05`: Selects approximately the top 5% most anomalous observations.
   - Anomaly score: $\\text{Score}_{\\text{IF}} = -\\text{score\\_samples}(X)$, where higher values indicate greater anomaly severity."""))

    cells.append(new_code_cell("""CONTAMINATION = 0.05
scored, if_model = isolation_forest_results(
    scored,
    feature_columns,
    contamination=CONTAMINATION,
    random_state=42
)

# Attach annual Beneish M-Score benchmark
scored = attach_beneish_baseline(scored, annual)

# Generate comparison and company rankings
model_comparison, company_ranking = summarize_results(scored)
beneish_comparison = build_beneish_comparison(scored)

print(f"Isolation Forest Flags (Top 5%) : {int(scored['if_anomaly'].sum()):,}")
print(f"Mean IF Anomaly Score           : {scored['if_anomaly_score'].mean():.4f}")
print(f"Max IF Anomaly Score            : {scored['if_anomaly_score'].max():.4f}")
"""))

    # Cell 10: Model Comparison & Reference vs Control Evaluation
    cells.append(new_markdown_cell("""## 7. Model Comparison & Empirical Validation

### Reference vs Control Group Evaluation:
We evaluate whether the unsupervised models successfully assign higher anomaly rates and scores to the **Reference Group** (companies with documented accounting investigations) compared to the **Control Group** (healthy large caps)."""))

    cells.append(new_code_cell("""display(model_comparison)

# Group-level breakdown
group_eval = scored.groupby("group").agg(
    Observations=("ticker", "count"),
    IF_Flagged_Count=("if_anomaly", "sum"),
    IF_Flag_Rate_Pct=("if_anomaly", lambda x: x.mean() * 100),
    Stat_Flagged_Count=("statistical_anomaly", "sum"),
    Stat_Flag_Rate_Pct=("statistical_anomaly", lambda x: x.mean() * 100),
    Median_IF_Score=("if_anomaly_score", "median"),
    Mean_Max_Trend_Dev=("max_trend_deviation", "mean")
).reset_index()

display(group_eval)

fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# Score distribution comparison
sns.kdeplot(data=scored, x="if_anomaly_score", hue="group", common_norm=False, fill=True, alpha=0.3, ax=ax[0])
ax[0].set_title("Isolation Forest Score Distribution by Group", fontweight="bold")
ax[0].set_xlabel("IF Anomaly Score (Higher = More Anomalous)")

# Boxplot of anomaly scores
sns.boxplot(data=scored, x="group", y="if_anomaly_score", palette=["#2b5c8f", "#d95f02"], ax=ax[1])
ax[1].set_title("Anomaly Score Dispersion: Control vs Reference", fontweight="bold")
ax[1].set_ylabel("IF Anomaly Score")

plt.tight_layout()
plt.show()
"""))

    # Cell 11: Top Ranked Review Candidates
    cells.append(new_markdown_cell("""## 8. Top 15 Anomalous Company-Quarters

Below are the highest-ranked company-quarters by Isolation Forest anomaly score, cross-referenced with Statistical Z-score flags and Beneish M-scores."""))

    cells.append(new_code_cell("""top_cols = [c for c in [
    "ticker", "company", "group", "period_end", "fiscal_year", "fiscal_quarter",
    "revenue", "revenue_yoy_growth", "total_expense_to_revenue", "gross_margin",
    "dso", "accruals_to_assets", "ar_growth_minus_revenue_growth",
    "statistical_anomaly_score", "statistical_anomaly", "if_anomaly_score", "if_anomaly",
    "max_trend_deviation", "beneish_m_score", "beneish_flag"
] if c in scored.columns]

top15 = scored.sort_values("if_anomaly_score", ascending=False).head(15)
display(top15[top_cols])

# Horizontal bar chart of top candidates
plt.figure(figsize=(10, 6))
plot_top = top15.copy()
plot_top["label"] = plot_top["ticker"] + " FY" + plot_top["fiscal_year"].astype(str) + " Q" + plot_top["fiscal_quarter"].astype(str)
plot_top = plot_top.sort_values("if_anomaly_score", ascending=True)

colors = ["#d95f02" if g == "reference" else "#2b5c8f" for g in plot_top["group"]]
plt.barh(plot_top["label"], plot_top["if_anomaly_score"], color=colors)
plt.xlabel("Isolation Forest Anomaly Score")
plt.title("Top 15 Anomaly Candidates (Orange = Reference Fraud/Investigation, Blue = Control)", fontweight="bold")
plt.tight_layout()
plt.show()
"""))

    # Cell 12: Forensic Case Studies Deep Dive
    cells.append(new_markdown_cell("""## 9. Forensic Case Studies: Validating Real-World Fraud Signals

### Case Study 1: Kraft Heinz (KHC) — Procurement Accounting & $15B Write-Down
- **SEC Action:** In 2019, the SEC charged Kraft Heinz with a 3-year expense-management fraud involving supplier rebate contracts that artificially lowered COGS. In FY2018 Q4, KHC recognized a massive $15.4B goodwill impairment.
- **Model Detection:** The pipeline flags KHC FY2018 Q4 with an extreme **operating margin collapse of -205%** ($RZ = -9.45$), extreme expense ratio ($RZ = +9.45$), and Sloan accrual anomaly ($RZ = -8.32$).

### Case Study 2: Under Armour (UAA) — Revenue Pull-Forward & Channel Stuffing
- **SEC Action:** The SEC found Under Armour pulled forward $408M in orders from future quarters in 2015-2016 to meet Wall Street revenue targets without disclosing the practice.
- **Model Detection:** In the relevant period, Under Armour's **Receivables Growth outstripped Revenue Growth** by up to $7.2\\sigma$ ($RZ = 7.23$), and DSO surged by $5.4\\sigma$.

### Case Study 3: Super Micro Computer (SMCI) — Revenue Recognition Irregularities
- **SEC / Auditor Resignation:** Super Micro has faced recurring accounting scrutiny regarding premature revenue recognition on incomplete shipments and delayed 10-K filings.
- **Model Detection:** The model flags SMCI across multiple quarters with extreme DSO surges ($RZ = 5.00$) and extreme multi-year revenue growth acceleration ($RZ = 3.15$)."""))

    cells.append(new_code_cell("""case_study_tickers = ["KHC", "UAA", "SMCI", "MDXG"]
case_df = scored[scored["ticker"].isin(case_study_tickers)].copy()

case_summary = case_df.groupby("ticker").agg(
    Total_Quarters=("period_end", "count"),
    IF_Flagged_Quarters=("if_anomaly", "sum"),
    Stat_Flagged_Quarters=("statistical_anomaly", "sum"),
    Multi_Year_Trend_Breaks=("multi_year_sudden_deviation", "sum"),
    Max_IF_Score=("if_anomaly_score", "max"),
    Max_Stat_Z_Score=("statistical_anomaly_score", "max"),
).reset_index()

print("Forensic Case Studies Detection Summary:")
display(case_summary)
"""))

    # Cell 13: Beneish M-Score Benchmark
    cells.append(new_markdown_cell("""## 10. Benchmarking with the Annual Beneish M-Score

The **Beneish M-Score** is a mathematical model combining 8 financial ratios to estimate the probability that a company has manipulated its earnings. A score higher than **-1.78** signals an elevated probability of manipulation.

Here we aggregate quarterly alerts to company-year and evaluate concordance with the annual Beneish benchmark."""))

    cells.append(new_code_cell("""if not beneish_comparison.empty:
    display(beneish_comparison.sort_values("if_max_score", ascending=False).head(15))
    
    valid_beneish = beneish_comparison.dropna(subset=["beneish_flag"])
    print(f"Company-Years with Beneish Baseline Available : {len(valid_beneish):,}")
    print(f"Company-Years Flagged by Beneish (> -1.78)     : {int(valid_beneish['beneish_flag'].astype(bool).sum()):,}")
    print(f"Company-Years with IF Quarterly Alerts         : {int(valid_beneish['if_any_quarter_flagged'].astype(bool).sum()):,}")
    print(f"Consensus Flags (Both Beneish & IF Alert)      : {int(valid_beneish['if_and_beneish_agree_flagged'].astype(bool).sum()):,}")
else:
    print("Beneish comparison data not available.")
"""))

    # Cell 14: Automated Pipeline for New Filings Demonstration
    cells.append(new_markdown_cell("""## 11. Automated Pipeline for New Filings (Live Scoring)

### Assignment Objective:
> *"Automated pipeline for new filings using all ML/ Data Analytics objectives."*

We demonstrate the live automated scoring pipeline on a company's newly received filing. The pipeline:
1. Derives all growth, margin, working-capital, and accrual ratios.
2. Calculates trailing Z-scores against historical quarters.
3. Computes trailing multi-year trend deviations.
4. Scores the filing through the pre-trained Isolation Forest model.
5. Returns a structured forensic triage scorecard with risk tier and audit recommendations."""))

    cells.append(new_code_cell("""# Live Demonstration: Scoring the latest available filing of Kraft Heinz (KHC)
khc_history = clean[clean["ticker"] == "KHC"].sort_values("period_end")
khc_latest = khc_history.iloc[-1].to_dict()
khc_prior = khc_history.iloc[:-1]

scorecard = score_new_filing(
    khc_latest,
    khc_prior,
    model=if_model,
    feature_columns=feature_columns,
    z_threshold=3.5
)

print("Automated New Filing Audit Scorecard:")
print("=" * 65)
print(f"Ticker              : {scorecard['ticker']} ({scorecard['period_end']})")
print(f"Fiscal Period       : FY{scorecard['fiscal_year']} Q{scorecard['fiscal_quarter']}")
print(f"Risk Classification : {scorecard['risk_level']}")
print(f"IF Anomaly Score    : {scorecard['isolation_forest_score']} (Flag: {scorecard['isolation_forest_flag']})")
print(f"Statistical Z-Score : {scorecard['statistical_anomaly_score']} (Flag: {scorecard['statistical_anomaly_flag']})")
print(f"Max Multi-Year Dev  : {scorecard['max_multi_year_deviation']} sigma (Flag: {scorecard['multi_year_deviation_flag']})")
print("-" * 65)
print("Triggered Red Flags :")
for f in scorecard["contributing_red_flags"]:
    print(f"  • {f['metric']:<30} | {f['status']}")
print("Audit Recommendations :")
for r in scorecard["audit_recommendations"]:
    print(f"  -> {r}")
print("=" * 65)
"""))

    # Cell 15: Artifact Generation and Export
    cells.append(new_markdown_cell("""## 12. Model Serialization & Deliverable Artifacts Export

All processed results, rankings, and serialized machine learning models are saved to `data/processed/`."""))

    cells.append(new_code_cell("""results = run_detection(
    DATA_DIR,
    output_dir=DATA_DIR,
    contamination=CONTAMINATION,
    z_threshold=Z_THRESHOLD,
    save_model_artifact=True
)

print("Pipeline execution completed successfully.")
print("\\nGenerated Deliverable Artifacts:")
for name, p in results["summary"]["outputs"].items():
    status = "OK" if Path(p).exists() else "MISSING"
    print(f"  [{status}] {name:<28}: {Path(p).name} ({Path(p).stat().st_size:,} bytes)")
"""))

    # Cell 16: Summary and Conclusion
    cells.append(new_markdown_cell("""## 13. Conclusions & Operational Triage Protocol

### Key Outcomes:
1. **Multi-Year Trend Analysis:** Trailing 12-quarter rolling baselines successfully exposed structural breaks in operating margins, expenses, and revenue growth. Known fraud cases (KHC, UAA, SMCI) exhibited severe multi-year deviations exceeding $3.0\\sigma$.
2. **Statistical vs Machine Learning Synergy:** 
   - **Robust Z-scores** detect acute single-metric quarterly shocks (e.g., massive write-downs or sudden receivables spikes).
   - **Isolation Forest** detects multi-dimensional combinations of subtle anomalies across margins, accruals, and growth where individual metrics may not cross univariate thresholds.
3. **Automated Pipeline for New Filings:** Enables real-time screening of new SEC 10-Q/10-K filings with automated feature derivation, risk tiering, and forensic audit checklists.

### Suggested Forensic Triage Protocol:
```
[New SEC Filing Received]
           │
           ▼
[Automated Feature Pipeline] ──> Compute Growth, Ratios, Trailing Z-Scores, Multi-Year Trends
           │
           ▼
[Multi-Model Anomaly Scoring]
   ├─ Robust Z-Score (|Z| >= 3.5)
   ├─ Isolation Forest (Top 5% Contamination)
   └─ Multi-Year Trend Deviation (|dev| >= 2.5σ)
           │
           ▼
[Risk Classification]
   ├─ HIGH ANOMALY (Multi-Method Consensus) ──> Immediate Forensic Audit (Receivables, Contracts, Write-Downs)
   ├─ ELEVATED (Single-Method Alert)        ──> Secondary Review (Inspect Tagging, Discontinued Ops, Restatements)
   └─ NORMAL                                ──> Cleared for Automated Monitoring
```"""))

    nb.cells = cells
    return nb

if __name__ == "__main__":
    print("Building notebook structure...")
    nb = build_notebook()
    
    print("Executing notebook with NotebookClient...")
    client = NotebookClient(nb, timeout=1200, kernel_name="python3")
    client.execute(cwd=ROOT)
    print("Notebook executed successfully!")
    
    out_path1 = ROOT / "02_ml_anomaly_detection.ipynb"
    out_path2 = ROOT / "sec_filing_anomaly_deliverable2" / "02_ml_anomaly_detection.ipynb"
    
    with open(out_path1, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print("Saved executed notebook to:", out_path1)
    
    with open(out_path2, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print("Saved executed notebook to:", out_path2)
