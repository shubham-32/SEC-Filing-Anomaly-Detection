import numpy as np
import pandas as pd

from src.anomaly_pipeline import (
    isolation_forest_results,
    prepare_observations,
    robust_zscore_results,
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

    results = run_detection(tmp_path, contamination=0.05)
    for filename in [
        "scored_quarterly.csv", "anomaly_top100.csv", "model_comparison.csv",
        "company_anomaly_ranking.csv", "beneish_comparison.csv", "run_summary.json",
    ]:
        assert (tmp_path / filename).exists(), filename
    assert results["summary"]["rows_scored"] > 0
    assert "beneish_flag" in results["scored"].columns
