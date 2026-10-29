"""Unit and integration tests for SEC filing anomaly detection pipeline."""
import numpy as np
import pandas as pd

from src.anomaly_pipeline import (
    compute_multi_year_trends,
    isolation_forest_results,
    load_pipeline_model,
    prepare_observations,
    robust_zscore_results,
    save_pipeline_model,
    score_new_filing,
    select_features,
    summarize_results,
)


def sample_frame(n=80):
    rng = np.random.default_rng(7)
    return pd.DataFrame({
        "ticker": [f"T{i % 8}" for i in range(n)],
        "group": ["reference" if i % 8 == 0 else "control" for i in range(n)],
        "period_end": pd.date_range("2018-03-31", periods=n, freq="QE"),
        "revenue": rng.uniform(100, 1000, n),
        "revenue_qoq_growth": rng.normal(0.02, 0.08, n),
        "revenue_yoy_growth": rng.normal(0.05, 0.10, n),
        "gross_margin": rng.normal(0.35, 0.04, n),
        "operating_margin": rng.normal(0.12, 0.03, n),
        "total_expense_to_revenue": rng.normal(0.85, 0.05, n),
        "dso": rng.normal(35, 5, n),
        "accruals_to_assets": rng.normal(0.01, 0.02, n),
        "ar_growth_minus_revenue_growth": rng.normal(0.0, 0.05, n),
        "z_revenue_yoy_growth": rng.normal(0, 1, n),
        "rz_revenue_yoy_growth": rng.normal(0, 1, n),
        "rz_gross_margin": rng.normal(0, 1, n),
        "dq_negative_revenue": False,
        "dq_missing_revenue": False,
        "dq_period_length_unusual": False,
        "dq_quarter_looks_annual": False,
        "dq_quarter_sum_mismatch": False,
        "revenue_tag_changed": False,
    })


def test_quality_filters_and_feature_selection():
    df = sample_frame(20)
    df.loc[0, "dq_quarter_looks_annual"] = True
    df.loc[1, "revenue_tag_changed"] = True
    clean, stats = prepare_observations(df)
    assert len(clean) == 18
    assert stats["quality_excluded_rows"] == 1
    assert stats["tag_switch_excluded_rows"] == 1
    features = select_features(clean)
    assert "group" not in features
    assert "ticker" not in features
    assert "revenue_yoy_growth" in features


def test_scoring_and_comparison_outputs():
    df = sample_frame()
    # Plant one clear synthetic anomaly; this validates mechanics, not real-world efficacy.
    df.loc[4, "rz_revenue_yoy_growth"] = 8.0
    df.loc[4, "revenue_yoy_growth"] = 3.0
    zscored = robust_zscore_results(df)
    assert bool(zscored.loc[4, "statistical_anomaly"])
    features = select_features(zscored)
    scored, _model = isolation_forest_results(zscored, features, contamination=0.05)
    assert scored["if_anomaly_score"].notna().all()
    assert scored["if_anomaly"].dtype == bool
    comparison, companies = summarize_results(scored)
    assert set(comparison["method"]) == {"Robust/trailing Z-score", "Isolation Forest"}
    assert "ticker" in companies.columns


def test_multi_year_trend_analysis():
    df = sample_frame(96)
    # Plant extreme sudden deviation on quarter 68 (which has sufficient prior history)
    df.loc[68, "revenue_yoy_growth"] = 15.0  # 1500% surge
    df.loc[68, "operating_margin"] = -2.50  # severe collapse
    df_trends, anomalies = compute_multi_year_trends(df)
    assert "trend_dev_rev_growth" in df_trends.columns
    assert "max_trend_deviation" in df_trends.columns
    assert "multi_year_sudden_deviation" in df_trends.columns
    flagged = df_trends[df_trends["revenue_yoy_growth"] == 15.0]
    assert len(flagged) == 1
    assert bool(flagged.iloc[0]["multi_year_sudden_deviation"]) == True


def test_score_new_filing():
    df = sample_frame(48)
    clean, _ = prepare_observations(df)
    features = select_features(clean)
    scored, model = isolation_forest_results(clean, features, contamination=0.05)

    new_quarter = {
        "ticker": "T0",
        "fiscal_year": 2026,
        "fiscal_quarter": 1,
        "period_end": "2026-03-31",
        "revenue": 5000.0,
        "revenue_yoy_growth": 1.85,
        "gross_margin": 0.15,
        "operating_margin": -0.45,
        "total_expense_to_revenue": 1.45,
        "dso": 95.0,
        "accruals_to_assets": 0.25,
        "ar_growth_minus_revenue_growth": 0.90,
        "rz_revenue_yoy_growth": 6.5,
        "rz_gross_margin": -4.2,
        "rz_dso": 5.1,
    }
    result = score_new_filing(new_quarter, df, model=model, feature_columns=features)
    assert result["ticker"] == "T0"
    assert "risk_level" in result
    assert result["statistical_anomaly_flag"] == True
    assert len(result["contributing_red_flags"]) > 0


def test_model_serialization(tmp_path):
    df = sample_frame(40)
    clean, _ = prepare_observations(df)
    features = select_features(clean)
    _, model = isolation_forest_results(clean, features, contamination=0.05)

    model_file = tmp_path / "test_model.joblib"
    save_pipeline_model(model, features, model_file, metadata={"test": True})
    assert model_file.exists()

    loaded_model, loaded_features, meta = load_pipeline_model(model_file)
    assert len(loaded_features) == len(features)
    assert meta["test"] == True


def test_full_run_writes_all_report_files(tmp_path):
    from src.anomaly_pipeline import run_detection

    df = sample_frame(96)
    df["fiscal_year"] = 2018 + (df.index // 4 % 12)
    # Ensure the final input has sufficient variance and a planted extreme period.
    df.loc[10, "rz_revenue_yoy_growth"] = 9.0
    df.loc[10, "revenue_yoy_growth"] = 2.5
    df.to_csv(tmp_path / "quarterly_features.csv", index=False)
    annual = pd.DataFrame([
        {"ticker": f"T{i}", "fiscal_year": year,
         "beneish_m_score": -1.4 if i == 0 else -2.4,
         "beneish_flag": i == 0}
        for i in range(8) for year in range(2018, 2030)
    ])
    annual.to_csv(tmp_path / "annual_features.csv", index=False)

    results = run_detection(tmp_path, output_dir=tmp_path, contamination=0.05)
    for filename in [
        "scored_quarterly.csv", "anomaly_top100.csv", "model_comparison.csv",
        "company_anomaly_ranking.csv", "beneish_comparison.csv",
        "multi_year_trend_anomalies.csv", "run_summary.json", "isolation_forest_model.joblib",
    ]:
        assert (tmp_path / filename).exists(), filename
    assert results["summary"]["rows_scored"] > 0
    assert "beneish_flag" in results["scored"].columns
