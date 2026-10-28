"""Reusable anomaly-detection workflow for SEC financial-statement features.

This module scores observations; it does not determine that fraud occurred.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
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


def load_inputs(data_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame | None]:
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
) -> tuple[pd.DataFrame, dict[str, int]]:
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
) -> list[str]:
    """Select numeric candidate features that have enough observed coverage."""
    selected: list[str] = []
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
        result["statistical_score_method"] = "unavailable"
        return result

    matrix = result[score_columns].apply(pd.to_numeric, errors="coerce")
    # Do not allow a missing feature to become zero (which would imply normality).
    result["statistical_anomaly_score"] = matrix.abs().max(axis=1, skipna=True)
    result["statistical_anomaly_features"] = matrix.abs().ge(threshold).sum(axis=1)
    result["statistical_anomaly"] = result["statistical_anomaly_score"].ge(threshold).fillna(False)
    result["statistical_score_method"] = "robust_trailing_z" if preferred else "trailing_z"
    result["statistical_threshold"] = threshold
    return result


def isolation_forest_results(
    observations: pd.DataFrame,
    feature_columns: Iterable[str],
    *,
    contamination: float = 0.05,
    random_state: int = 42,
) -> tuple[pd.DataFrame, Pipeline]:
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


def attach_beneish_baseline(scored: pd.DataFrame, annual: pd.DataFrame | None) -> pd.DataFrame:
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


def summarize_results(scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
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
        for score in ["if_anomaly_score", "statistical_anomaly_score"]:
            if score in scored.columns:
                agg_spec[f"mean_{score}"] = (score, "mean")
                agg_spec[f"max_{score}"] = (score, "max")
        for flag in ["if_anomaly", "statistical_anomaly"]:
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


def run_detection(
    data_dir: str | Path,
    *,
    output_dir: str | Path | None = None,
    contamination: float = 0.05,
    z_threshold: float = 3.5,
    exclude_quality_flags: bool = True,
    exclude_tag_switches: bool = True,
) -> dict[str, object]:
    """Run cleaning, statistical scoring, Isolation Forest, and output generation."""
    data_dir = Path(data_dir)
    output_dir = Path(output_dir) if output_dir else data_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    quarterly, annual = load_inputs(data_dir)
    clean, filter_stats = prepare_observations(
        quarterly,
        exclude_quality_flags=exclude_quality_flags,
        exclude_tag_switches=exclude_tag_switches,
    )
    features = select_features(clean)
    scored = robust_zscore_results(clean, threshold=z_threshold)
    scored, model = isolation_forest_results(
        scored, features, contamination=contamination,
    )
    # Annual Beneish outputs are joined only after model scoring to prevent target leakage.
    scored = attach_beneish_baseline(scored, annual)
    comparison, company_ranking = summarize_results(scored)
    beneish_comparison = build_beneish_comparison(scored)

    score_cols = [c for c in [
        "if_anomaly_score", "if_anomaly", "statistical_anomaly_score",
        "statistical_anomaly", "statistical_anomaly_features",
    ] if c in scored.columns]
    sort_col = "if_anomaly_score" if "if_anomaly_score" in scored else "statistical_anomaly_score"
    top = scored.sort_values(sort_col, ascending=False).head(100).copy()

    quarterly_out = output_dir / "scored_quarterly.csv"
    top_out = output_dir / "anomaly_top100.csv"
    comparison_out = output_dir / "model_comparison.csv"
    ranking_out = output_dir / "company_anomaly_ranking.csv"
    beneish_out = output_dir / "beneish_comparison.csv"
    summary_out = output_dir / "run_summary.json"
    scored.to_csv(quarterly_out, index=False)
    top.to_csv(top_out, index=False)
    comparison.to_csv(comparison_out, index=False)
    company_ranking.to_csv(ranking_out, index=False)
    beneish_comparison.to_csv(beneish_out, index=False)

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
        "rows_scored": int(len(scored)),
        "isolation_forest_flagged": int(scored["if_anomaly"].sum()),
        "statistical_flagged": int(scored["statistical_anomaly"].sum()),
        "outputs": {
            "scored_quarterly": str(quarterly_out),
            "top100": str(top_out),
            "model_comparison": str(comparison_out),
            "company_ranking": str(ranking_out),
            "beneish_comparison": str(beneish_out),
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
        "summary": summary,
        "model": model,
    }
