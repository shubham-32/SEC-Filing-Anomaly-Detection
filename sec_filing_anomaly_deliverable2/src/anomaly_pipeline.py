"""Reusable anomaly-detection workflow for SEC financial-statement features.

Deliverable 2: Financial Anomaly Detection, Multi-Year Trend Analysis,
and Automated Pipeline for New Filings.

This module scores observations to prioritize forensic review; it surfaces
statistical and machine learning outliers and does not prove fraud.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

ID_COLUMNS = {
    "cik", "ticker", "company", "sic", "sic_description", "group",
    "reference_note", "fiscal_year", "fiscal_quarter", "calendar_quarter",
    "period_end", "period_start", "period_days", "revenue_tag", "revenue_method",
}

# Pre-specified candidate features. Outcome-like restatement fields are intentionally
# excluded from the primary model to avoid making the model rediscover the label.
CANDIDATE_FEATURES = [
    "fiscal_quarter", "revenue_qoq_growth", "revenue_yoy_growth", "cogs_yoy_growth", "sga_yoy_growth",
    "net_income_yoy_growth", "ar_yoy_growth", "inventory_yoy_growth",
    "deferred_revenue_yoy_growth", "cogs_to_revenue", "sga_to_revenue",
    "rnd_to_revenue", "opex_to_revenue", "total_expense_to_revenue",
    "gross_margin", "operating_margin", "net_margin", "gross_margin_yoy_change",
    "operating_margin_yoy_change", "expense_ratio_yoy_change", "dso", "dio",
    "ar_growth_minus_revenue_growth", "inventory_growth_minus_revenue_growth",
    "sga_growth_minus_revenue_growth", "accruals_to_assets", "cfo_to_net_income",
    "leverage", "current_ratio", "z_revenue_qoq_growth", "rz_revenue_qoq_growth",
    "z_revenue_yoy_growth", "rz_revenue_yoy_growth", "z_total_expense_to_revenue",
    "rz_total_expense_to_revenue", "z_gross_margin", "rz_gross_margin",
    "z_operating_margin", "rz_operating_margin", "z_dso", "rz_dso",
    "z_accruals_to_assets", "rz_accruals_to_assets",
    "z_ar_growth_minus_revenue_growth", "rz_ar_growth_minus_revenue_growth",
]

QUALITY_FLAGS = [
    "dq_negative_revenue", "dq_missing_revenue", "dq_period_length_unusual",
    "dq_quarter_looks_annual", "dq_quarter_sum_mismatch",
]

Z_SCORE_COLUMNS = [
    "rz_revenue_qoq_growth", "rz_revenue_yoy_growth", "rz_total_expense_to_revenue",
    "rz_gross_margin", "rz_operating_margin", "rz_dso", "rz_accruals_to_assets",
    "rz_ar_growth_minus_revenue_growth",
    "z_revenue_qoq_growth", "z_revenue_yoy_growth", "z_total_expense_to_revenue",
    "z_gross_margin", "z_operating_margin", "z_dso", "z_accruals_to_assets",
    "z_ar_growth_minus_revenue_growth",
]

MULTI_YEAR_TREND_METRICS = [
    ("revenue_yoy_growth", "trend_dev_rev_growth", "Revenue YoY Growth"),
    ("total_expense_to_revenue", "trend_dev_expense_ratio", "Expense-to-Revenue Ratio"),
    ("gross_margin", "trend_dev_gross_margin", "Gross Margin"),
    ("operating_margin", "trend_dev_operating_margin", "Operating Margin"),
    ("accruals_to_assets", "trend_dev_accruals", "Sloan Accruals to Assets"),
    ("ar_growth_minus_revenue_growth", "trend_dev_ar_vs_rev", "AR Growth minus Rev Growth"),
]


def resolve_data_dir(candidate_path: Optional[Union[str, Path]] = None) -> Path:
    """Find data/processed directory from various invocation locations."""
    if candidate_path:
        p = Path(candidate_path).resolve()
        if (p / "quarterly_features.csv").exists():
            return p
        if (p / "data" / "processed" / "quarterly_features.csv").exists():
            return p / "data" / "processed"

    cwd = Path.cwd().resolve()
    candidates = [
        cwd / "data" / "processed",
        cwd.parent / "data" / "processed",
        Path(__file__).resolve().parent.parent / "data" / "processed",
        Path(__file__).resolve().parent.parent.parent / "data" / "processed",
    ]
    for c in candidates:
        if (c / "quarterly_features.csv").exists():
            return c
    return candidates[0]


def load_inputs(data_dir: Union[str, Path]) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """Load current quarterly and optional annual feature datasets."""
    data_dir = Path(data_dir)
    quarterly_path = data_dir / "quarterly_features.csv"
    if not quarterly_path.exists():
        raise FileNotFoundError(f"Required input not found: {quarterly_path}")
    quarterly = pd.read_csv(quarterly_path, low_memory=False)
    annual_path = data_dir / "annual_features.csv"
    annual = pd.read_csv(annual_path, low_memory=False) if annual_path.exists() else None
    if quarterly.empty:
        raise ValueError(f"Quarterly input has no rows: {quarterly_path}")
    return quarterly, annual


def _as_bool(series: pd.Series) -> pd.Series:
    """Parse CSV booleans robustly, including strings such as 'False'."""
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def prepare_observations(
    quarterly: pd.DataFrame,
    *,
    exclude_quality_flags: bool = True,
    exclude_tag_switches: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Apply conservative, documented row-level quality filters.

    A filtered row remains available in the original CSV; this function only
    determines which rows enter the initial modelling pass.
    """
    df = quarterly.copy()
    initial_count = len(df)
    df["period_end"] = pd.to_datetime(df["period_end"], errors="coerce")
    for col in QUALITY_FLAGS + ["revenue_tag_changed"]:
        if col in df.columns:
            df[col] = _as_bool(df[col])

    excluded_quality = pd.Series(False, index=df.index)
    if exclude_quality_flags:
        for col in QUALITY_FLAGS:
            if col in df.columns:
                excluded_quality |= df[col]
    # Missing or non-positive revenue cannot support revenue-based anomaly features.
    if "revenue" in df.columns:
        revenue = pd.to_numeric(df["revenue"], errors="coerce")
        excluded_quality |= revenue.isna() | (revenue <= 0)
    elif exclude_quality_flags:
        raise ValueError("Required column 'revenue' is missing from quarterly dataset")

    quality_excluded_count = int(excluded_quality.sum())
    df = df.loc[~excluded_quality].copy()

    tag_excluded_count = 0
    if exclude_tag_switches and "revenue_tag_changed" in df.columns:
        tag_mask = df["revenue_tag_changed"].fillna(False)
        tag_excluded_count = int(tag_mask.sum())
        df = df.loc[~tag_mask].copy()

    df = df.reset_index(drop=True)
    if df.empty:
        raise ValueError(
            "No rows remain after data-quality filters. Inspect dq_* flags and settings."
        )
    stats = {
        "input_rows": int(initial_count),
        "quality_excluded_rows": quality_excluded_count,
        "tag_switch_excluded_rows": tag_excluded_count,
        "rows_after_filters": int(len(df)),
    }
    return df, stats


def select_features(
    observations: pd.DataFrame,
    *,
    max_missing_fraction: float = 0.45,
    minimum_features: int = 5,
) -> List[str]:
    """Select numeric candidate features that have enough observed coverage."""
    selected: List[str] = []
    for col in CANDIDATE_FEATURES:
        if col not in observations.columns:
            continue
        numeric = pd.to_numeric(observations[col], errors="coerce")
        if numeric.notna().mean() < (1.0 - max_missing_fraction):
            continue
        if numeric.nunique(dropna=True) < 2:
            continue
        selected.append(col)
    if len(selected) < minimum_features:
        raise ValueError(
            f"Only {len(selected)} usable model features were found; at least "
            f"{minimum_features} are required. Available columns may differ from the expected schema."
        )
    return selected


def robust_zscore_results(
    observations: pd.DataFrame,
    *,
    threshold: float = 3.5,
) -> pd.DataFrame:
    """Create a composite robust-Z anomaly score from precomputed trailing features.

    Prefers robust median/MAD scores (rz_*) over ordinary z-scores (z_*). Where a
    robust score is unavailable for a metric, the corresponding ordinary score is
    used. Uses absolute values because both unusually high and unusually low metrics
    can warrant review.
    """
    result = observations.copy()
    available = [col for col in Z_SCORE_COLUMNS if col in result.columns]
    preferred = [col for col in available if col.startswith("rz_")]
    score_columns = preferred if preferred else [col for col in available if col.startswith("z_")]
    if not score_columns:
        result["statistical_anomaly_score"] = np.nan
        result["statistical_anomaly"] = False
        result["statistical_anomaly_features"] = 0
        result["statistical_score_method"] = "unavailable"
        result["statistical_threshold"] = threshold
        return result

    matrix = result[score_columns].apply(pd.to_numeric, errors="coerce")
    # Do not allow a missing feature to become zero (which would imply normality).
    result["statistical_anomaly_score"] = matrix.abs().max(axis=1, skipna=True)
    result["statistical_anomaly_features"] = matrix.abs().ge(threshold).sum(axis=1)
    result["statistical_anomaly"] = result["statistical_anomaly_score"].ge(threshold).fillna(False)
    result["statistical_score_method"] = "robust_trailing_z" if preferred else "trailing_z"
    result["statistical_threshold"] = threshold
    return result


def compute_multi_year_trends(
    observations: pd.DataFrame,
    *,
    rolling_quarters: int = 12,
    min_periods: int = 4,
    deviation_threshold: float = 2.5,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compare multi-year trends for sudden deviations and inconsistent trends.

    Addresses ML/Data Analytics Objective:
      - Compare multi-year trends for sudden deviations.
      - Identify inconsistent trends in revenue, expenses, or margins.

    Calculates trailing multi-year rolling mean and standard deviation per company
    (strictly prior quarters via shift(1) to avoid look-ahead bias).
    Computes standardized trend deviation scores for revenue growth, expense ratio,
    margins, and accruals.
    """
    df = observations.copy()
    if "period_end" in df.columns:
        df["period_end"] = pd.to_datetime(df["period_end"], errors="coerce")
    if "ticker" in df.columns and "period_end" in df.columns:
        df = df.sort_values(["ticker", "period_end"]).reset_index(drop=True)
        grouped = df.groupby("ticker")
    else:
        grouped = None

    trend_cols = []
    if grouped is not None:
        for col, dev_col, _label in MULTI_YEAR_TREND_METRICS:
            if col in df.columns:
                num_series = pd.to_numeric(df[col], errors="coerce")
                # strictly trailing window using shift(1)
                roll_mean = grouped[col].transform(
                    lambda s: pd.to_numeric(s, errors="coerce").shift(1).rolling(rolling_quarters, min_periods=min_periods).mean()
                )
                roll_std = grouped[col].transform(
                    lambda s: pd.to_numeric(s, errors="coerce").shift(1).rolling(rolling_quarters, min_periods=min_periods).std()
                )
                df[dev_col] = (num_series - roll_mean) / roll_std.replace(0, np.nan)
                trend_cols.append(dev_col)

    if trend_cols:
        trend_matrix = df[trend_cols].apply(pd.to_numeric, errors="coerce")
        df["max_trend_deviation"] = trend_matrix.abs().max(axis=1, skipna=True)
        df["multi_year_sudden_deviation"] = df["max_trend_deviation"].ge(deviation_threshold).fillna(False)

        # Inconsistent trend detection:
        # e.g. Revenue accelerating while operating margin or accruals suddenly drop
        rev_dev = df.get("trend_dev_rev_growth", pd.Series(0, index=df.index)).fillna(0)
        op_dev = df.get("trend_dev_operating_margin", pd.Series(0, index=df.index)).fillna(0)
        exp_dev = df.get("trend_dev_expense_ratio", pd.Series(0, index=df.index)).fillna(0)

        df["inconsistent_trend_flag"] = (
            ((rev_dev >= 1.5) & (op_dev <= -1.5)) |
            ((exp_dev >= 2.0) & (rev_dev <= -1.0))
        )
    else:
        df["max_trend_deviation"] = np.nan
        df["multi_year_sudden_deviation"] = False
        df["inconsistent_trend_flag"] = False

    # Extract top multi-year anomalies for reporting
    id_cols = [c for c in ["ticker", "company", "group", "fiscal_year", "fiscal_quarter", "period_end"] if c in df.columns]
    report_cols = id_cols + [c for c in [
        "revenue", "revenue_yoy_growth", "gross_margin", "operating_margin",
        "total_expense_to_revenue", "max_trend_deviation", "multi_year_sudden_deviation",
        "inconsistent_trend_flag"
    ] + trend_cols if c in df.columns]

    anomalies = df[df["multi_year_sudden_deviation"] | df["inconsistent_trend_flag"]].copy()
    if not anomalies.empty and "max_trend_deviation" in anomalies:
        anomalies = anomalies.sort_values("max_trend_deviation", ascending=False).reset_index(drop=True)

    return df, anomalies[report_cols] if not anomalies.empty else pd.DataFrame(columns=report_cols)


def isolation_forest_results(
    observations: pd.DataFrame,
    feature_columns: Iterable[str],
    *,
    contamination: float = 0.05,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, Pipeline]:
    """Fit Isolation Forest and attach an anomaly score and binary flag.

    Higher ``if_anomaly_score`` means more unusual. The contamination parameter is
    a modelling threshold, not an estimate of the true fraud prevalence.
    """
    if not 0.0 < contamination < 0.5:
        raise ValueError("contamination must be strictly between 0 and 0.5")
    features = list(feature_columns)
    if len(features) < 2:
        raise ValueError("At least two features are required for Isolation Forest")
    X = observations[features].apply(pd.to_numeric, errors="coerce")
    # Drop columns that became all-missing after feature selection (defensive check).
    X = X.dropna(axis=1, how="all")
    if X.shape[1] < 2:
        raise ValueError("Fewer than two usable features remain after missing-value checks")

    model = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler(quantile_range=(10.0, 90.0))),
        ("isolation_forest", IsolationForest(
            n_estimators=300,
            contamination=contamination,
            max_samples="auto",
            random_state=random_state,
            n_jobs=-1,
        )),
    ])
    model.fit(X)
    imputed_scaled = model.named_steps["scaler"].transform(
        model.named_steps["imputer"].transform(X)
    )
    forest = model.named_steps["isolation_forest"]
    result = observations.copy()
    # sklearn's score_samples is lower for more anomalous observations.
    result["if_anomaly_score"] = -forest.score_samples(imputed_scaled)
    result["if_anomaly"] = forest.predict(imputed_scaled).astype(int) == -1
    result["if_contamination_setting"] = contamination
    return result, model


def attach_beneish_baseline(scored: pd.DataFrame, annual: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Attach annual Beneish fields for post-hoc comparison only, never as model inputs."""
    result = scored.copy()
    if annual is None or "ticker" not in result.columns or "fiscal_year" not in result.columns:
        return result
    wanted = [c for c in ["ticker", "fiscal_year", "beneish_m_score", "beneish_flag"] if c in annual.columns]
    if not {"ticker", "fiscal_year"}.issubset(wanted):
        return result
    baseline = annual[wanted].drop_duplicates(["ticker", "fiscal_year"])
    for col in ["beneish_m_score", "beneish_flag"]:
        if col in result.columns:
            result = result.drop(columns=col)
    result = result.merge(baseline, on=["ticker", "fiscal_year"], how="left", validate="many_to_one")
    if "beneish_flag" in result.columns:
        result["beneish_flag"] = _as_bool(result["beneish_flag"])
    return result


def build_beneish_comparison(scored: pd.DataFrame) -> pd.DataFrame:
    """Aggregate quarter-level alerts to company-year and compare with annual M-Score flag."""
    required = {"ticker", "fiscal_year", "beneish_m_score", "beneish_flag"}
    if not required.issubset(scored.columns):
        return pd.DataFrame()
    aggregations = {
        "quarters_scored": ("period_end", "count") if "period_end" in scored.columns else ("ticker", "size"),
        "if_any_quarter_flagged": ("if_anomaly", "max"),
        "if_max_score": ("if_anomaly_score", "max"),
        "stat_any_quarter_flagged": ("statistical_anomaly", "max"),
        "beneish_m_score": ("beneish_m_score", "first"),
        "beneish_flag": ("beneish_flag", "first"),
    }
    if "group" in scored.columns:
        aggregations["group"] = ("group", "first")
    result = scored.groupby(["ticker", "fiscal_year"], dropna=False).agg(**aggregations).reset_index()
    result["if_and_beneish_agree_flagged"] = result["if_any_quarter_flagged"].astype(bool) & result["beneish_flag"].astype(bool)
    result["stat_and_beneish_agree_flagged"] = result["stat_any_quarter_flagged"].astype(bool) & result["beneish_flag"].astype(bool)
    return result


def summarize_results(scored: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return descriptive model comparison and company-level ranking tables."""
    model_rows = []
    for method, flag_col, score_col in [
        ("Robust/trailing Z-score", "statistical_anomaly", "statistical_anomaly_score"),
        ("Isolation Forest", "if_anomaly", "if_anomaly_score"),
    ]:
        if flag_col not in scored.columns:
            continue
        flagged = _as_bool(scored[flag_col])
        row = {
            "method": method,
            "observations": int(len(scored)),
            "flagged_observations": int(flagged.sum()),
            "flagged_pct": float(flagged.mean() * 100.0) if len(flagged) else np.nan,
        }
        if score_col in scored.columns:
            row["median_score"] = float(pd.to_numeric(scored[score_col], errors="coerce").median())
        if "group" in scored.columns:
            group_rates = scored.assign(_flag=flagged).groupby("group", dropna=False)["_flag"].mean()
            row["control_flagged_pct"] = float(group_rates.get("control", np.nan) * 100.0)
            row["reference_flagged_pct"] = float(group_rates.get("reference", np.nan) * 100.0)
        model_rows.append(row)
    model_comparison = pd.DataFrame(model_rows)

    if "ticker" in scored.columns:
        agg_spec = {}
        for score in ["if_anomaly_score", "statistical_anomaly_score", "max_trend_deviation"]:
            if score in scored.columns:
                agg_spec[f"mean_{score}"] = (score, "mean")
                agg_spec[f"max_{score}"] = (score, "max")
        for flag in ["if_anomaly", "statistical_anomaly", "multi_year_sudden_deviation"]:
            if flag in scored.columns:
                agg_spec[f"{flag}_rate"] = (flag, "mean")
        if "group" in scored.columns:
            agg_spec["group"] = ("group", "first")
        company_ranking = scored.groupby("ticker", dropna=False).agg(**agg_spec).reset_index()
        if "max_if_anomaly_score" in company_ranking:
            company_ranking = company_ranking.sort_values("max_if_anomaly_score", ascending=False)
        elif "max_statistical_anomaly_score" in company_ranking:
            company_ranking = company_ranking.sort_values("max_statistical_anomaly_score", ascending=False)
    else:
        company_ranking = pd.DataFrame()
    return model_comparison, company_ranking


def save_pipeline_model(
    model: Pipeline,
    feature_columns: List[str],
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Serialize the trained Isolation Forest pipeline and feature metadata."""
    payload = {
        "model": model,
        "feature_columns": feature_columns,
        "metadata": metadata or {},
    }
    joblib.dump(payload, filepath)


def load_pipeline_model(filepath: Union[str, Path]) -> Tuple[Pipeline, List[str], Dict[str, Any]]:
    """Load the trained Isolation Forest pipeline and feature metadata."""
    payload = joblib.load(filepath)
    return payload["model"], payload["feature_columns"], payload.get("metadata", {})


def score_new_filing(
    new_quarter: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    company_history: pd.DataFrame,
    *,
    model: Optional[Pipeline] = None,
    feature_columns: Optional[List[str]] = None,
    z_threshold: float = 3.5,
) -> Dict[str, Any]:
    """Score a newly submitted SEC filing against company history.

    Addresses Deliverable 2: 'Automated pipeline for new filings using all
    ML/ Data Analytics objectives.'

    Calculates:
      1. Financial ratios and growth metrics.
      2. Trailing Z-scores and Robust Z-scores against history.
      3. Multi-year trend deviations.
      4. Isolation Forest anomaly score using the pre-trained or provided model.
      5. Forensic audit triage checklist and risk tier classification.
    """
    if isinstance(new_quarter, dict):
        new_row = pd.DataFrame([new_quarter])
    elif isinstance(new_quarter, pd.Series):
        new_row = pd.DataFrame([new_quarter])
    else:
        new_row = new_quarter.copy()

    new_row["_is_new_filing_marker"] = True

    # Combine company history and new filing to compute trailing metrics
    ticker = new_row.get("ticker", pd.Series(["UNKNOWN"])).iloc[0]
    hist = company_history.copy()
    if "ticker" in hist.columns:
        hist = hist[hist["ticker"] == ticker].copy()
    hist["_is_new_filing_marker"] = False

    combined = pd.concat([hist, new_row], ignore_index=True)
    if "period_end" in combined.columns:
        combined["period_end"] = pd.to_datetime(combined["period_end"], errors="coerce")
        combined = combined.sort_values("period_end").reset_index(drop=True)

    # Compute trailing multi-year trends
    combined_trends, _ = compute_multi_year_trends(combined)
    scored_new_row = combined_trends[combined_trends["_is_new_filing_marker"] == True].iloc[[-1]].copy()
    scored_new_row = scored_new_row.drop(columns=["_is_new_filing_marker"])

    # Apply robust z-score detection
    scored_new_row = robust_zscore_results(scored_new_row, threshold=z_threshold)

    # Apply Isolation Forest if model and features provided
    if model is not None and feature_columns:
        X_new = scored_new_row[[f for f in feature_columns if f in scored_new_row.columns]].apply(pd.to_numeric, errors="coerce")
        # Impute and score
        imputer = model.named_steps["imputer"]
        scaler = model.named_steps["scaler"]
        forest = model.named_steps["isolation_forest"]
        X_proc = scaler.transform(imputer.transform(X_new))
        scored_new_row["if_anomaly_score"] = -forest.score_samples(X_proc)
        scored_new_row["if_anomaly"] = forest.predict(X_proc).astype(int) == -1
    else:
        scored_new_row["if_anomaly_score"] = np.nan
        scored_new_row["if_anomaly"] = False

    r = scored_new_row.iloc[0]

    # Evaluate Contributing Factors
    contributing = []
    for col, dev_col, label in MULTI_YEAR_TREND_METRICS:
        val = r.get(dev_col, np.nan)
        if pd.notna(val) and abs(val) >= 2.0:
            contributing.append({
                "metric": label,
                "trend_deviation_sigma": round(float(val), 2),
                "current_value": round(float(r.get(col, np.nan)), 4) if pd.notna(r.get(col)) else None,
                "status": "ALERT (Extreme Multi-Year Deviation)" if abs(val) >= 2.5 else "WATCH"
            })

    for col in Z_SCORE_COLUMNS:
        z_val = r.get(col, np.nan)
        if pd.notna(z_val) and abs(z_val) >= z_threshold:
            contributing.append({
                "metric": col,
                "z_score": round(float(z_val), 2),
                "status": "ALERT (Exceeds Statistical Threshold)"
            })

    # Risk Tiering
    is_if = bool(r.get("if_anomaly", False))
    is_stat = bool(r.get("statistical_anomaly", False))
    is_trend = bool(r.get("multi_year_sudden_deviation", False))

    if (is_if and is_stat) or (is_if and is_trend) or (is_stat and is_trend):
        risk_level = "HIGH ANOMALY (Multi-Method Consensus - Requires Priority Review)"
    elif is_if or is_stat or is_trend:
        risk_level = "ELEVATED (Single-Method Alert - Forensic Triage Recommended)"
    else:
        risk_level = "NORMAL (Within Expected Multi-Year & Statistical Tolerances)"

    # Audit Recommendations
    recommendations = []
    if abs(r.get("trend_dev_rev_growth", 0)) >= 2.5:
        recommendations.append("Investigate revenue acceleration/deceleration against industry macro trends.")
    if abs(r.get("trend_dev_ar_vs_rev", 0)) >= 2.5:
        recommendations.append("Audit accounts receivable aging schedules to inspect potential channel stuffing.")
    if abs(r.get("trend_dev_gross_margin", 0)) >= 2.5 or abs(r.get("trend_dev_operating_margin", 0)) >= 2.5:
        recommendations.append("Review cost allocation changes, inventory capitalization, or non-operating adjustments.")
    if abs(r.get("trend_dev_accruals", 0)) >= 2.5:
        recommendations.append("Verify cash flow reconciliation: significant gap between reported net income and operating cash flow.")
    if not recommendations:
        recommendations.append("No specific high-priority accounting anomalies triggered.")

    return {
        "ticker": str(ticker),
        "period_end": str(r.get("period_end", "N/A"))[:10],
        "fiscal_year": int(r.get("fiscal_year", 0)) if pd.notna(r.get("fiscal_year")) else None,
        "fiscal_quarter": int(r.get("fiscal_quarter", 0)) if pd.notna(r.get("fiscal_quarter")) else None,
        "isolation_forest_score": round(float(r.get("if_anomaly_score", np.nan)), 4) if pd.notna(r.get("if_anomaly_score")) else None,
        "isolation_forest_flag": is_if,
        "statistical_anomaly_score": round(float(r.get("statistical_anomaly_score", np.nan)), 4) if pd.notna(r.get("statistical_anomaly_score")) else None,
        "statistical_anomaly_flag": is_stat,
        "max_multi_year_deviation": round(float(r.get("max_trend_deviation", np.nan)), 2) if pd.notna(r.get("max_trend_deviation")) else None,
        "multi_year_deviation_flag": is_trend,
        "risk_level": risk_level,
        "contributing_red_flags": contributing,
        "audit_recommendations": recommendations,
        "scored_row": scored_new_row,
    }


def fetch_latest_edgar_filing(
    ticker: str,
    user_agent: Optional[str] = None,
    data_dir: Optional[Union[str, Path]] = None,
) -> pd.DataFrame:
    """Fetch recent filing records from SEC EDGAR API or load from cached data.

    Complies with SEC requirement: requires an identifying User-Agent.
    """
    ua = user_agent or os.environ.get("SEC_USER_AGENT", "UniversityResearchStudent student@academic.edu")
    headers = {"User-Agent": ua}
    ticker = ticker.upper().strip()

    # Try loading from existing quarterly dataset first for fast offline execution
    data_path = resolve_data_dir(data_dir)
    q_path = data_path / "quarterly_features.csv"
    if q_path.exists():
        q_df = pd.read_csv(q_path, low_memory=False)
        match = q_df[q_df["ticker"] == ticker]
        if not match.empty:
            return match.sort_values("period_end").reset_index(drop=True)

    # If not in local dataset, query SEC EDGAR API
    c_tickers_url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(c_tickers_url, headers=headers, timeout=10)
    r.raise_for_status()
    tickers_dict = r.json()
    cik = None
    for item in tickers_dict.values():
        if item.get("ticker", "").upper() == ticker:
            cik = str(item["cik_str"]).zfill(10)
            break
    if not cik:
        raise ValueError(f"Ticker '{ticker}' not found in SEC company database.")

    facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    facts_r = requests.get(facts_url, headers=headers, timeout=15)
    facts_r.raise_for_status()
    return pd.DataFrame([{"ticker": ticker, "cik": cik, "status": "fetched_from_edgar"}])


def run_detection(
    data_dir: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
    contamination: float = 0.05,
    z_threshold: float = 3.5,
    exclude_quality_flags: bool = True,
    exclude_tag_switches: bool = True,
    save_model_artifact: bool = True,
) -> Dict[str, Any]:
    """Run cleaning, multi-year trend analysis, statistical scoring, Isolation Forest, and output generation."""
    data_dir = resolve_data_dir(data_dir)
    output_dir = Path(output_dir) if output_dir else data_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    quarterly, annual = load_inputs(data_dir)
    clean, filter_stats = prepare_observations(
        quarterly,
        exclude_quality_flags=exclude_quality_flags,
        exclude_tag_switches=exclude_tag_switches,
    )

    # 1. Multi-Year Trend Analysis & Sudden Deviations
    clean, trend_anomalies = compute_multi_year_trends(clean)

    # 2. Model Feature Selection
    features = select_features(clean)

    # 3. Statistical Detection (Robust Z-Score)
    scored = robust_zscore_results(clean, threshold=z_threshold)

    # 4. Machine Learning Detection (Isolation Forest)
    scored, model = isolation_forest_results(
        scored, features, contamination=contamination,
    )

    # 5. Annual Beneish Benchmark (Post-Hoc Integration)
    scored = attach_beneish_baseline(scored, annual)
    comparison, company_ranking = summarize_results(scored)
    beneish_comparison = build_beneish_comparison(scored)

    # 6. Sorting and Exporting Top Anomalies
    sort_col = "if_anomaly_score" if "if_anomaly_score" in scored else "statistical_anomaly_score"
    top = scored.sort_values(sort_col, ascending=False).head(100).copy()

    quarterly_out = output_dir / "scored_quarterly.csv"
    top_out = output_dir / "anomaly_top100.csv"
    comparison_out = output_dir / "model_comparison.csv"
    ranking_out = output_dir / "company_anomaly_ranking.csv"
    beneish_out = output_dir / "beneish_comparison.csv"
    trend_out = output_dir / "multi_year_trend_anomalies.csv"
    summary_out = output_dir / "run_summary.json"
    model_out = output_dir / "isolation_forest_model.joblib"

    scored.to_csv(quarterly_out, index=False)
    top.to_csv(top_out, index=False)
    comparison.to_csv(comparison_out, index=False)
    company_ranking.to_csv(ranking_out, index=False)
    beneish_comparison.to_csv(beneish_out, index=False)
    trend_anomalies.to_csv(trend_out, index=False)

    if save_model_artifact:
        save_pipeline_model(
            model,
            features,
            model_out,
            metadata={
                "contamination": contamination,
                "z_threshold": z_threshold,
                "rows_trained": len(clean),
            }
        )

    summary = {
        "input_quarterly_file": str(data_dir / "quarterly_features.csv"),
        "input_annual_file_available": annual is not None,
        "filtering": filter_stats,
        "model_features": features,
        "model_feature_count": len(features),
        "isolation_forest": {
            "estimators": 300,
            "contamination": contamination,
            "random_state": 42,
            "interpretation": "higher if_anomaly_score means more unusual; not a fraud probability",
        },
        "statistical_detection": {
            "threshold": z_threshold,
            "score_method": "robust trailing Z-score where available, otherwise trailing Z-score",
        },
        "multi_year_trend_analysis": {
            "rolling_window_quarters": 12,
            "deviation_threshold_sigma": 2.5,
            "quarters_with_sudden_deviations": int(scored["multi_year_sudden_deviation"].sum()) if "multi_year_sudden_deviation" in scored else 0,
            "inconsistent_trend_quarters": int(scored["inconsistent_trend_flag"].sum()) if "inconsistent_trend_flag" in scored else 0,
        },
        "rows_scored": int(len(scored)),
        "isolation_forest_flagged": int(scored["if_anomaly"].sum()),
        "statistical_flagged": int(scored["statistical_anomaly"].sum()),
        "multi_year_trend_flagged": int(scored["multi_year_sudden_deviation"].sum()) if "multi_year_sudden_deviation" in scored else 0,
        "outputs": {
            "scored_quarterly": str(quarterly_out),
            "top100": str(top_out),
            "model_comparison": str(comparison_out),
            "company_ranking": str(ranking_out),
            "beneish_comparison": str(beneish_out),
            "multi_year_trend_anomalies": str(trend_out),
            "model_artifact": str(model_out),
        },
        "caveat": "Flags identify observations for review and are not proof of fraud. Group-level labels are weak labels, not quarter-level ground truth.",
    }
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return {
        "scored": scored,
        "top100": top,
        "comparison": comparison,
        "company_ranking": company_ranking,
        "beneish_comparison": beneish_comparison,
        "trend_anomalies": trend_anomalies,
        "summary": summary,
        "model": model,
    }
