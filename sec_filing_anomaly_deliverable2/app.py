"""Streamlit Web Application: SEC Filing Financial Anomaly Detection System.

Task ID: FDA-2 | Fraud Detection Through Financial Anomalies
Course: Big Data Analytics (Semester 7)
Designed for Live Project Evaluation & Examination Demonstrations.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.anomaly_pipeline import (
    load_pipeline_model,
    resolve_data_dir,
    run_detection,
    score_new_filing,
)

# -----------------------------------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SEC Filing Forensic Anomaly Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Custom Styling (Dark/Modern Forensic Terminal Theme)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 12px;
    }
    .badge-high {
        background-color: #ffebee;
        color: #c62828;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        border: 1px solid #ef9a9a;
    }
    .badge-elevated {
        background-color: #fff8e1;
        color: #f57f17;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        border: 1px solid #ffe082;
    }
    .badge-normal {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        border: 1px solid #a5d6a7;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        font-weight: 600;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data & Model Caching
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_datasets():
    data_dir = resolve_data_dir()
    q_file = data_dir / "quarterly_features.csv"
    scored_file = data_dir / "scored_quarterly.csv"
    top_file = data_dir / "anomaly_top100.csv"
    company_file = data_dir / "company_anomaly_ranking.csv"
    trends_file = data_dir / "multi_year_trend_anomalies.csv"
    beneish_file = data_dir / "beneish_comparison.csv"

    if not q_file.exists():
        st.error(f"Dataset not found in {data_dir}. Please run the pipeline first.")
        st.stop()

    df = pd.read_csv(q_file, low_memory=False)
    
    if scored_file.exists():
        scored = pd.read_csv(scored_file, low_memory=False)
    else:
        res = run_detection(data_dir, output_dir=data_dir)
        scored = res["scored"]

    top100 = pd.read_csv(top_file, low_memory=False) if top_file.exists() else scored.head(100)
    ranking = pd.read_csv(company_file, low_memory=False) if company_file.exists() else pd.DataFrame()
    trends = pd.read_csv(trends_file, low_memory=False) if trends_file.exists() else pd.DataFrame()
    beneish = pd.read_csv(beneish_file, low_memory=False) if beneish_file.exists() else pd.DataFrame()

    return {
        "raw": df,
        "scored": scored,
        "top100": top100,
        "ranking": ranking,
        "trends": trends,
        "beneish": beneish,
        "data_dir": data_dir,
    }

@st.cache_resource(show_spinner=False)
def load_ml_model(data_dir: Path):
    model_file = data_dir / "isolation_forest_model.joblib"
    if model_file.exists():
        model, features, _ = load_pipeline_model(model_file)
        return model, features
    res = run_detection(data_dir, output_dir=data_dir)
    return res["model"], res["summary"]["model_features"]

# Load Data
data_bundle = load_datasets()
df = data_bundle["raw"]
scored = data_bundle["scored"]
top100 = data_bundle["top100"]
ranking = data_bundle["ranking"]
trends = data_bundle["trends"]
beneish = data_bundle["beneish"]
data_dir = data_bundle["data_dir"]
model, model_features = load_ml_model(data_dir)

# -----------------------------------------------------------------------------
# Sidebar Navigation & System Meta
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("SEC Forensic System")
    st.caption("**Task ID:** FDA-2 | Financial Anomalies")
    st.caption("**Course:** Big Data Analytics (Sem 7)")
    
    st.markdown("---")
    menu = st.radio(
        "Navigation Modules",
        [
            "📊 Executive Overview",
            "🔍 Company Anomaly Explorer",
            "⚡ Live Filing Scoring Pipeline",
            "🚨 Real-World Fraud Case Studies",
            "🤖 Model & Trend Analytics",
            "🏆 Top 100 Anomaly Leaderboard",
        ],
        index=0,
    )
    
    st.markdown("---")
    st.markdown("### 📋 System Inventory")
    st.metric("Total Quarters Scored", f"{len(scored):,}")
    st.metric("Companies Tracked", f"{scored['ticker'].nunique()}")
    st.metric("Model Feature Count", f"{len(model_features)}")
    
    ref_count = (scored["group"] == "reference").sum()
    ctrl_count = (scored["group"] == "control").sum()
    st.caption(f"**Cohort Split:** {ctrl_count} Control / {ref_count} Reference")
    
    st.markdown("---")
    st.caption("Live Demonstration Suite • Antigravity 2.0")

# -----------------------------------------------------------------------------
# Module 1: Executive Overview
# -----------------------------------------------------------------------------
if menu == "📊 Executive Overview":
    st.header("Executive Overview: SEC Filing Financial Anomaly Detection")
    st.write(
        "Automated forensic analytics system ingesting **12+ fiscal years (FY2014–FY2026)** of point-in-time SEC EDGAR XBRL filings "
        "to detect earnings manipulation, accounting irregularities, and structural financial deviations."
    )
    st.markdown("---")

    # High Level KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total SEC Filings Analyzed",
            value=f"{len(scored):,}",
            delta="12 Fiscal Years (2014-2026)",
        )
    with col2:
        if_anom_cnt = int(scored["if_anomaly"].sum())
        st.metric(
            label="Isolation Forest Outliers",
            value=f"{if_anom_cnt}",
            delta=f"{if_anom_cnt / len(scored):.1%} Universe Flag Rate",
            delta_color="inverse",
        )
    with col3:
        stat_cnt = int(scored["statistical_anomaly"].sum())
        st.metric(
            label="Statistical Shocks (|Z| ≥ 3.5σ)",
            value=f"{stat_cnt}",
            delta="Rolling MAD Trailing Window",
            delta_color="inverse",
        )
    with col4:
        trend_cnt = int(scored["multi_year_sudden_deviation"].sum())
        st.metric(
            label="Multi-Year Trend Breaks",
            value=f"{trend_cnt}",
            delta="Trailing 3-Year Rolling Drift",
            delta_color="inverse",
        )

    st.markdown("### 📈 Reference vs. Control Group Discrimination")
    st.info(
        "💡 **Key Validation:** The system was tested on a dual-cohort universe: "
        "**Reference Group** (companies with documented SEC enforcement actions/restatements like KHC, UAA, SMCI) "
        "versus **Control Group** (healthy blue-chips like AAPL, MSFT, JNJ). "
        "The models exhibit higher flag rates and extreme anomaly scores in the Reference group."
    )

    col_left, col_right = st.columns(2)
    with col_left:
        # Score distribution by group
        fig_dist = px.histogram(
            scored,
            x="if_anomaly_score",
            color="group",
            nbins=40,
            barmode="overlay",
            title="Isolation Forest Anomaly Score Distribution (Reference vs Control)",
            labels={"if_anomaly_score": "Isolation Forest Anomaly Score (Higher = More Abnormal)", "group": "Cohort"},
            color_discrete_map={"reference": "#e53935", "control": "#1e88e5"},
            marginal="box",
        )
        fig_dist.update_layout(height=420, legend=dict(yanchor="top", y=0.95, xanchor="right", x=0.95))
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_right:
        # Flag rate comparison bar chart
        ref_mask = scored["group"] == "reference"
        ctrl_mask = scored["group"] == "control"
        
        rates = pd.DataFrame({
            "Method": [
                "Isolation Forest ML", "Isolation Forest ML",
                "Statistical Z-Score", "Statistical Z-Score",
                "Multi-Year Trend Break", "Multi-Year Trend Break"
            ],
            "Cohort": ["Reference (Scandal)", "Control (Blue-Chip)", "Reference (Scandal)", "Control (Blue-Chip)", "Reference (Scandal)", "Control (Blue-Chip)"],
            "Flag Rate (%)": [
                round(scored[ref_mask]["if_anomaly"].mean() * 100, 2),
                round(scored[ctrl_mask]["if_anomaly"].mean() * 100, 2),
                round(scored[ref_mask]["statistical_anomaly"].mean() * 100, 2),
                round(scored[ctrl_mask]["statistical_anomaly"].mean() * 100, 2),
                round(scored[ref_mask]["multi_year_sudden_deviation"].mean() * 100, 2),
                round(scored[ctrl_mask]["multi_year_sudden_deviation"].mean() * 100, 2),
            ]
        })
        fig_rates = px.bar(
            rates,
            x="Method",
            y="Flag Rate (%)",
            color="Cohort",
            barmode="group",
            text="Flag Rate (%)",
            title="Forensic Flag Detection Rates by Method & Cohort",
            color_discrete_map={"Reference (Scandal)": "#d32f2f", "Control (Blue-Chip)": "#1976d2"},
        )
        fig_rates.update_traces(textposition="outside")
        fig_rates.update_layout(height=420, yaxis_range=[0, max(rates["Flag Rate (%)"]) + 10])
        st.plotly_chart(fig_rates, use_container_width=True)

    # Sector & Company summary
    st.markdown("### 🏢 Universe Anomaly Leaderboard by Company")
    if not ranking.empty:
        st.dataframe(
            ranking.rename(
                columns={
                    "ticker": "Ticker",
                    "company": "Company Name",
                    "group": "Group",
                    "total_quarters": "Total Quarters",
                    "if_flags": "IF Alerts",
                    "stat_flags": "Z-Score Alerts",
                    "trend_flags": "Trend Breaks",
                    "flag_rate": "Flag Rate",
                    "mean_if_score": "Mean IF Score",
                    "max_if_score": "Peak IF Score",
                }
            ).style.format({"Flag Rate": "{:.1%}", "Mean IF Score": "{:.4f}", "Peak IF Score": "{:.4f}"}),
            use_container_width=True,
            height=320,
        )

# -----------------------------------------------------------------------------
# Module 2: Interactive Company Anomaly Explorer
# -----------------------------------------------------------------------------
elif menu == "🔍 Company Anomaly Explorer":
    st.header("Interactive Company Anomaly & Multi-Year Trend Explorer")
    st.write("Inspect 10+ year quarterly trajectories, trailing statistical bounds, and structural trend breaks.")
    st.markdown("---")

    tickers = sorted(scored["ticker"].unique())
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        default_idx = tickers.index("KHC") if "KHC" in tickers else 0
        selected_ticker = st.selectbox("Select Company Ticker:", tickers, index=default_idx)

    company_sub = scored[scored["ticker"] == selected_ticker].sort_values("period_end").reset_index(drop=True)
    comp_name = company_sub["company"].iloc[0] if "company" in company_sub else selected_ticker
    group = company_sub["group"].iloc[0] if "group" in company_sub else "unknown"

    with col_sel2:
        badge_cls = "badge-high" if group == "reference" else "badge-normal"
        st.markdown(
            f"### **{comp_name}** (`{selected_ticker}`) &nbsp;&nbsp; "
            f"<span class='{badge_cls}'>{group.upper()} COHORT</span>",
            unsafe_allow_html=True,
        )
        st.caption(f"SIC Code: {company_sub['sic'].iloc[0]} | Industry: {company_sub.get('sic_description', pd.Series(['N/A'])).iloc[0]}")

    st.markdown("#### Company Anomaly Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quarters Evaluated", len(company_sub))
    c2.metric("Isolation Forest Alerts", int(company_sub["if_anomaly"].sum()))
    c3.metric("Z-Score Shocks (|Z| ≥ 3.5σ)", int(company_sub["statistical_anomaly"].sum()))
    c4.metric("Multi-Year Trend Deviations", int(company_sub["multi_year_sudden_deviation"].sum()))

    # Interactive Trajectory Plots
    st.markdown("### 📉 Multi-Year Trajectory & Anomaly Points")
    metric_choice = st.selectbox(
        "Select Financial Metric to Graph:",
        [
            ("revenue_yoy_growth", "Revenue YoY Growth (Annual Pace)"),
            ("operating_margin", "Operating Margin (Profitability)"),
            ("total_expense_to_revenue", "Expense-to-Revenue Ratio"),
            ("accruals_to_assets", "Sloan Accruals to Assets (Earnings Quality)"),
            ("ar_growth_minus_revenue_growth", "AR Growth minus Revenue Growth (Channel Stuffing Index)"),
            ("if_anomaly_score", "Isolation Forest Multidimensional Anomaly Score"),
        ],
        format_func=lambda x: x[1],
    )
    metric_col = metric_choice[0]
    metric_name = metric_choice[1]

    if metric_col in company_sub.columns:
        fig_timeline = go.Figure()

        # Regular timeline trace
        fig_timeline.add_trace(
            go.Scatter(
                x=pd.to_datetime(company_sub["period_end"]),
                y=company_sub[metric_col],
                mode="lines+markers",
                name=metric_name,
                line=dict(color="#1f77b4", width=2.5),
                marker=dict(size=6),
            )
        )

        # Highlight anomalies
        anom_mask = company_sub["if_anomaly"] | company_sub["statistical_anomaly"] | company_sub["multi_year_sudden_deviation"]
        anom_df = company_sub[anom_mask]

        if not anom_df.empty:
            fig_timeline.add_trace(
                go.Scatter(
                    x=pd.to_datetime(anom_df["period_end"]),
                    y=anom_df[metric_col],
                    mode="markers",
                    name="Anomaly Flagged Quarter",
                    marker=dict(color="#d32f2f", size=12, symbol="diamond-dot", line=dict(width=2, color="white")),
                    text=[
                        f"FY{r.fiscal_year} Q{r.fiscal_quarter}<br>IF Score: {r.if_anomaly_score:.3f}<br>Stat Z: {r.statistical_anomaly_score:.2f}σ"
                        for _, r in anom_df.iterrows()
                    ],
                    hoverinfo="text+x+y",
                )
            )

        fig_timeline.update_layout(
            title=f"{metric_name} Over Time for {selected_ticker} (Red Diamonds = Anomaly Quarters)",
            xaxis_title="Filing Period End Date",
            yaxis_title=metric_name,
            height=450,
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

    # Detailed Table of Flagged Quarters
    st.markdown("#### Flagged Historical Quarters Detail")
    anom_rows = company_sub[anom_mask].copy()
    if anom_rows.empty:
        st.success("✅ No quarters triggered anomaly flags for this company.")
    else:
        disp_cols = [
            "fiscal_year", "fiscal_quarter", "period_end", "if_anomaly_score",
            "statistical_anomaly_score", "max_trend_deviation",
            "revenue_yoy_growth", "operating_margin", "total_expense_to_revenue",
            "if_anomaly", "statistical_anomaly", "multi_year_sudden_deviation"
        ]
        available_cols = [c for c in disp_cols if c in anom_rows.columns]
        st.dataframe(
            anom_rows[available_cols].style.format({
                "if_anomaly_score": "{:.4f}",
                "statistical_anomaly_score": "{:.2f}σ",
                "max_trend_deviation": "{:.2f}σ",
                "revenue_yoy_growth": "{:.1%}",
                "operating_margin": "{:.1%}",
                "total_expense_to_revenue": "{:.1%}",
            }),
            use_container_width=True,
        )

# -----------------------------------------------------------------------------
# Module 3: Live Automated Filing Scoring Pipeline
# -----------------------------------------------------------------------------
elif menu == "⚡ Live Filing Scoring Pipeline":
    st.header("Automated Pipeline for New Filings (Live Scoring Engine)")
    st.write(
        "Simulates or executes real-time ingestion of newly received SEC filings. "
        "Applies feature engineering, rolling statistical baselines, 12-quarter multi-year trend analysis, "
        "and Isolation Forest inference to generate an instantaneous Forensic Audit Scorecard."
    )
    st.markdown("---")

    # Ingestion Presets
    st.markdown("### 1. Select Incoming SEC Filing Simulation")
    preset_choice = st.selectbox(
        "Choose a filing to ingest and score through the automated pipeline:",
        [
            ("KHC", "Kraft Heinz (KHC) — FY2018 Q4 (Goodwill Write-Down & Procurement Scandal)"),
            ("UAA", "Under Armour (UAA) — FY2016 Q4 (Channel Stuffing & Accelerated Shipments)"),
            ("SMCI", "Super Micro Computer (SMCI) — FY2022 Q4 (Extreme Revenue Acceleration)"),
            ("MSFT", "Microsoft (MSFT) — FY2026 Q4 (Healthy Control Blue-Chip Baseline)"),
            ("AAPL", "Apple (AAPL) — FY2025 Q4 (Stable Blue-Chip Control)"),
            ("CUSTOM", "Custom Ticker from Secondary Dataset"),
        ],
        format_func=lambda x: x[1],
    )

    target_ticker = preset_choice[0]
    if target_ticker == "CUSTOM":
        target_ticker = st.text_input("Enter Ticker Symbol:", value="COST").strip().upper()

    company_data = df[df["ticker"] == target_ticker].sort_values("period_end").reset_index(drop=True)
    if company_data.empty:
        st.error(f"Ticker '{target_ticker}' not found in local secondary dataset.")
        st.stop()

    # Split history vs latest filing
    hist = company_data.iloc[:-1]
    new_filing = company_data.iloc[-1].to_dict()

    st.markdown("### 2. Filing Metadata")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Ticker Symbol", target_ticker)
    mc2.metric("Fiscal Period", f"FY{new_filing.get('fiscal_year', 'N/A')} Q{new_filing.get('fiscal_quarter', 'N/A')}")
    mc3.metric("Filing Period End", str(new_filing.get("period_end", "N/A"))[:10])
    mc4.metric("Prior Quarters History", len(hist))

    st.markdown("---")
    if st.button("🚀 Ingest & Run Forensic Audit", type="primary", use_container_width=True):
        with st.spinner("Processing XBRL tags, computing ratios, and evaluating multi-method models..."):
            scorecard = score_new_filing(new_filing, hist, model=model, feature_columns=model_features)

        st.success("✅ Forensic Pipeline Execution Complete!")

        # Risk Classification Banner
        risk = scorecard["risk_level"]
        if "HIGH ANOMALY" in risk:
            st.error(f"### 🚨 AUDIT RISK CLASSIFICATION: {risk}")
        elif "ELEVATED" in risk:
            st.warning(f"### ⚠️ AUDIT RISK CLASSIFICATION: {risk}")
        else:
            st.success(f"### 🛡️ AUDIT RISK CLASSIFICATION: {risk}")

        # Scorecard Metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(
                "Isolation Forest Score",
                f"{scorecard['isolation_forest_score']:.4f}",
                delta="Flagged Outlier" if scorecard["isolation_forest_flag"] else "Normal Range",
                delta_color="inverse" if scorecard["isolation_forest_flag"] else "normal",
            )
        with col_m2:
            st.metric(
                "Statistical Z-Score",
                f"{scorecard['statistical_anomaly_score']:.2f}σ",
                delta="Extreme Shock" if scorecard["statistical_anomaly_flag"] else "Within Tolerances",
                delta_color="inverse" if scorecard["statistical_anomaly_flag"] else "normal",
            )
        with col_m3:
            st.metric(
                "Max Multi-Year Trend Deviation",
                f"{scorecard['max_multi_year_deviation']:.2f}σ",
                delta="Structural Trend Break" if scorecard["multi_year_deviation_flag"] else "Stable Baseline",
                delta_color="inverse" if scorecard["multi_year_deviation_flag"] else "normal",
            )

        st.markdown("---")
        sc_col1, sc_col2 = st.columns(2)

        with sc_col1:
            st.markdown("#### 🚩 Contributing Red Flags")
            red_flags = scorecard.get("contributing_red_flags", [])
            if red_flags:
                rf_df = pd.DataFrame(red_flags)
                st.dataframe(rf_df, use_container_width=True)
            else:
                st.write("✨ No metric exceeded the individual forensic alert thresholds.")

        with sc_col2:
            st.markdown("#### 🔍 Prioritized Audit Recommendations")
            for rec in scorecard.get("audit_recommendations", []):
                st.markdown(f"- 📋 **{rec}**")

# -----------------------------------------------------------------------------
# Module 4: Real-World Fraud Case Studies
# -----------------------------------------------------------------------------
elif menu == "🚨 Real-World Fraud Case Studies":
    st.header("Forensic Validation: Detection of Documented Fraud Schemes")
    st.write(
        "Demonstrating the pipeline's detection accuracy against landmark accounting scandals "
        "and SEC enforcement actions in the Reference Group."
    )
    st.markdown("---")

    case_tabs = st.tabs([
        "1. Kraft Heinz (Procurement Fraud)",
        "2. Under Armour (Channel Stuffing)",
        "3. Super Micro Computer (Revenue Timing)",
    ])

    with case_tabs[0]:
        st.subheader("Kraft Heinz Company (KHC) — FY2018 Q4 Goodwill Impairment & Expense Fraud")
        st.markdown(
            """
            - **SEC Enforcement Action:** In 2019, the SEC charged Kraft Heinz with a 3-year expense-management fraud. 
              Procurement personnel manipulated supplier contracts to prematurely recognize cost savings.
            - **The Catastrophe:** In FY2018 Q4, KHC reported a **$15.4 Billion goodwill impairment**, causing operating income to collapse.
            - **Model Findings:**
              - **Operating Margin:** Collapsed to **-205%** (Trailing Robust Z = **-9.45σ**).
              - **Sloan Accruals to Assets:** Plunged to **-8.32σ**.
              - **Consensus Risk Level:** **HIGH ANOMALY** (All 3 detection mechanisms triggered simultaneously).
            """
        )
        khc_data = scored[scored["ticker"] == "KHC"].sort_values("period_end")
        fig_khc = px.line(
            khc_data,
            x="period_end",
            y="operating_margin",
            markers=True,
            title="KHC Operating Margin Crash into FY2018 Q4 Scandal",
            labels={"operating_margin": "Operating Margin", "period_end": "Period End"},
        )
        fig_khc.add_annotation(
            x="2018-12-29",
            y=-2.05,
            text="FY2018 Q4: -205% Margin ($15.4B Write-down)",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red",
            font=dict(color="red", size=12),
        )
        st.plotly_chart(fig_khc, use_container_width=True)

    with case_tabs[1]:
        st.subheader("Under Armour (UAA) — FY2015-FY2016 Channel Stuffing Scheme")
        st.markdown(
            """
            - **SEC Enforcement Action:** In 2021, Under Armour paid $438M to settle SEC charges. 
              The company pulled forward $408M in orders from future quarters to artificially meet Wall Street revenue targets.
            - **The Forensic Signature:** While revenue growth appeared strong, **Accounts Receivable grew at an unnatural pace**, 
              diverging sharply from reported collections.
            - **Model Findings:**
              - **AR Growth minus Revenue Growth:** Surged to **+7.23σ** deviation during the pull-forward period.
              - **Days Sales Outstanding (DSO):** Rose by **+5.43σ**.
              - **Consensus Risk Level:** **ELEVATED ANOMALY** (Flagged immediately as an uncharacteristic balance sheet divergence).
            """
        )
        uaa_data = scored[scored["ticker"] == "UAA"].sort_values("period_end")
        fig_uaa = px.line(
            uaa_data,
            x="period_end",
            y=["revenue_yoy_growth", "ar_yoy_growth"],
            title="Under Armour: Accounts Receivable Growth Divergence (Channel Stuffing Signature)",
            labels={"value": "YoY Growth Rate", "period_end": "Period End", "variable": "Metric"},
        )
        st.plotly_chart(fig_uaa, use_container_width=True)

    with case_tabs[2]:
        st.subheader("Super Micro Computer (SMCI) — Revenue Recognition & Shipments")
        st.markdown(
            """
            - **Historical Context:** Repeated SEC restatements and auditor resignations regarding premature revenue 
              recognition on incomplete hardware deliveries.
            - **The Forensic Signature:** Unprecedented surges in quarterly revenue growth paired with sudden DSO volatility.
            - **Model Findings:**
              - **Revenue YoY Growth:** Trailing Z-Score of **+3.15σ**.
              - **DSO Swings:** Z-Score of **+5.00σ**.
              - **Consensus Risk Level:** **HIGH ANOMALY**.
            """
        )
        smci_data = scored[scored["ticker"] == "SMCI"].sort_values("period_end")
        fig_smci = px.line(
            smci_data,
            x="period_end",
            y="revenue_yoy_growth",
            markers=True,
            title="SMCI Revenue Growth Acceleration Volatility",
            labels={"revenue_yoy_growth": "Revenue YoY Growth", "period_end": "Period End"},
        )
        st.plotly_chart(fig_smci, use_container_width=True)

# -----------------------------------------------------------------------------
# Module 5: Model & Trend Analytics
# -----------------------------------------------------------------------------
elif menu == "🤖 Model & Trend Analytics":
    st.header("Forensic Analytics Architecture & Methodology")
    st.write("Detailed breakdown of the three complementary detection engines specified in Task FDA-2.")
    st.markdown("---")

    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.markdown(
            """
            ### 🌲 Isolation Forest ML
            - **Ensemble:** 300 Decision Trees
            - **Feature Space:** 42 financial ratios & growth metrics
            - **Scaling:** `RobustScaler` (10th–90th quantile)
            - **Imputation:** Median (`SimpleImputer`)
            - **Contamination:** 5.0% calibration
            - **Role:** Identifies subtle multidimensional combinations of balance sheet & income statement anomalies.
            """
        )
    with mcol2:
        st.markdown(
            """
            ### 📊 Statistical Z-Score
            - **Baseline:** Prior 8 quarters (`shift(1)` to prevent look-ahead bias)
            - **Robust Formulation:**
              $$RZ = \\frac{x - \\text{Median}}{1.4826 \\times \\text{MAD}}$$
            - **Threshold:** $|RZ| \\ge 3.5\\sigma$
            - **Role:** Captures single-quarter extreme shocks and sudden swings in core ratios.
            """
        )
    with mcol3:
        st.markdown(
            """
            ### 📈 Multi-Year Trends
            - **Baseline:** Trailing 12-quarter (3-year) rolling window
            - **Parameters:** $\\mu_{12Q}$ and $\\sigma_{12Q}$
            - **Threshold:** $|\\text{Trend Dev}| \\ge 2.5\\sigma$
            - **Inconsistent Checks:**
              - Revenue accelerates while margin crashes
              - Revenue accelerates while OCF collapses
            - **Role:** Detects structural drift across multi-year reporting cycles.
            """
        )

    st.markdown("---")
    st.markdown("### 🏛️ Post-Hoc Annual Benchmark: Beneish M-Score")
    st.write(
        "Quarterly anomaly alerts are benchmarked against the 8-variable Beneish M-Score. "
        "An M-Score greater than **-1.78** flags a high probability of earnings manipulation."
    )
    if not beneish.empty:
        st.dataframe(beneish, use_container_width=True)

# -----------------------------------------------------------------------------
# Module 6: Top 100 Anomaly Leaderboard
# -----------------------------------------------------------------------------
elif menu == "🏆 Top 100 Anomaly Leaderboard":
    st.header("Top 100 Highest-Ranked Anomalous Filings")
    st.write("Universe-wide ranking sorted by multidimensional Isolation Forest anomaly score.")
    st.markdown("---")

    filter_group = st.radio("Filter Cohort:", ["All Universe", "Reference (Scandal)", "Control (Blue-Chip)"], horizontal=True)
    disp_top = top100.copy()
    if filter_group == "Reference (Scandal)":
        disp_top = disp_top[disp_top["group"] == "reference"]
    elif filter_group == "Control (Blue-Chip)":
        disp_top = disp_top[disp_top["group"] == "control"]

    st.caption(f"Showing {len(disp_top)} observations")
    
    show_cols = [
        "ticker", "company", "group", "fiscal_year", "fiscal_quarter", "period_end",
        "if_anomaly_score", "statistical_anomaly_score", "max_trend_deviation",
        "revenue_yoy_growth", "operating_margin", "total_expense_to_revenue"
    ]
    show_cols = [c for c in show_cols if c in disp_top.columns]
    
    st.dataframe(
        disp_top[show_cols].style.format({
            "if_anomaly_score": "{:.4f}",
            "statistical_anomaly_score": "{:.2f}σ",
            "max_trend_deviation": "{:.2f}σ",
            "revenue_yoy_growth": "{:.1%}",
            "operating_margin": "{:.1%}",
            "total_expense_to_revenue": "{:.1%}",
        }),
        use_container_width=True,
        height=550,
    )

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "SEC Filing Anomaly Detection System | Task ID: FDA-2 | Big Data Analytics (Semester 7) | "
    "Point-in-Time Point Data FY2014–FY2026. Models prioritize forensic review and do not constitute legal proof of fraud."
)
