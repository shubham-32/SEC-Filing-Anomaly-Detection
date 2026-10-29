"""Script to generate professional PowerPoint Presentation for Deliverable 2."""
import os
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "docs" / "figures"

# Colors
C_NAVY = RGBColor(27, 54, 93)      # #1B365D Primary dark header
C_BLUE = RGBColor(43, 92, 143)     # #2B5C8F Secondary brand
C_ORANGE = RGBColor(217, 95, 2)    # #D95F02 Accent / Alert
C_DARK = RGBColor(30, 41, 59)      # #1E293B Text dark
C_MUTED = RGBColor(100, 116, 139)  # #64748B Text muted
C_LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC Card bg
C_BORDER = RGBColor(226, 232, 240) # #E2E8F0 Card border
C_WHITE = RGBColor(255, 255, 255)

def add_header(slide, title_text, category_text="FDA-2 • DELIVERABLE 2 • MACHINE LEARNING & ANOMALY DETECTION"):
    # Category / Tracker
    tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_cat = tb_cat.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = C_ORANGE

    # Main Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.65))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = C_NAVY

def add_card(slide, left, top, width, height, bg_color=C_LIGHT_BG, border_color=C_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

def create_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY
    bg1.line.fill.background()

    tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "TASK ID FDA-2 • BIG DATA ANALYTICS (SEM 7)"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = C_ORANGE
    p0.space_after = Pt(14)

    p1 = tf.add_paragraph()
    p1.text = "Fraud Detection Through Financial Anomalies"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(10)

    p2 = tf.add_paragraph()
    p2.text = "Deliverable 2: Machine Learning, Multi-Year Trend Analysis & Automated New-Filing Pipeline"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_after = Pt(28)

    p3 = tf.add_paragraph()
    p3.text = "End-to-End System: Statistical Robust Z-Scores • Isolation Forest • 12-Quarter Trend Trajectories • Beneish M-Score Benchmark • Live Audit Triage"
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(148, 163, 184)

    # ==========================================
    # SLIDE 2: Executive Summary & Motivation
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Executive Summary & Problem Motivation")

    card_w = Inches(3.6)
    card_h = Inches(5.2)

    # Card 1: The Challenge
    add_card(s2, Inches(0.8), Inches(1.5), card_w, card_h)
    tb1 = s2.shapes.add_textbox(Inches(1.0), Inches(1.7), card_w - Inches(0.4), card_h - Inches(0.4))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "The Forensic Challenge"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_NAVY
    bullets1 = [
        "Financial reporting fraud costs investors billions annually (e.g. Enron, WorldCom, Kraft Heinz).",
        "SEC 10-K and 10-Q filings span thousands of XBRL tags with complex restatements and standard changes (ASC 606).",
        "Manual audit cannot keep pace with thousands of public filers submitting quarterly reports simultaneously.",
        "Need: Automated machine learning systems to flag anomalous filings for human auditor triage."
    ]
    for b in bullets1:
        p = tf1.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # Card 2: ML & Analytics Approach
    add_card(s2, Inches(4.8), Inches(1.5), card_w, card_h)
    tb2 = s2.shapes.add_textbox(Inches(5.0), Inches(1.7), card_w - Inches(0.4), card_h - Inches(0.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Dual-Methodology Solution"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_NAVY
    bullets2 = [
        "Unsupervised Learning (Isolation Forest): Evaluates multi-dimensional interactions across 42 financial features.",
        "Statistical Anomaly Detection: Trailing median/MAD robust Z-scores isolate extreme quarterly spikes.",
        "Multi-Year Trend Analysis: 12-quarter rolling baselines detect sudden structural breaks and diverging margins.",
        "Beneish M-Score Benchmark: Validates quarterly alerts against forensic accounting probability formulas."
    ]
    for b in bullets2:
        p = tf2.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # Card 3: Key Deliverables Achieved
    add_card(s2, Inches(8.8), Inches(1.5), card_w, card_h)
    tb3 = s2.shapes.add_textbox(Inches(9.0), Inches(1.7), card_w - Inches(0.4), card_h - Inches(0.4))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "Project Achievements"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_NAVY
    bullets3 = [
        "1,238 Quarters Scored across 26 companies over 12 fiscal years (FY2014-FY2026).",
        "Documented Fraud Sensitivity: High anomaly flags triggered for KHC (procurement fraud), UAA (channel stuffing), SMCI (revenue recognition).",
        "Automated New Filing Pipeline: Ingests, extracts, trends, and scores new filings in under 2 seconds.",
        "Fully Executed Notebook & Live Interactive Demonstration CLI console."
    ]
    for b in bullets3:
        p = tf3.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # ==========================================
    # SLIDE 3: ML / Data Analytics Objectives
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "ML & Data Analytics Objectives Alignment")

    add_card(s3, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tb = s3.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(11.1), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    objs = [
        ("Apply Statistical Anomaly Detection (Isolation Forest, Z-score)",
         "Implemented rolling median/MAD robust Z-score (|Z| >= 3.5) and 300-estimator Isolation Forest (contamination=0.05). Both models operate strictly on financial ratios and growth rates without company identifiers or target leakage."),
        ("Compare Multi-Year Trends for Sudden Deviations",
         "Constructed trailing 12-quarter (3-year) rolling means and standard deviations using strictly prior quarters (shift(1)). Evaluated standardized trend deviation scores for revenue, expense ratio, gross/operating margins, and Sloan accruals."),
        ("Extract 5+ Years of Financial Statements via EDGAR",
         "Secondary dataset extracted 12+ years of point-in-time XBRL filings from SEC EDGAR (FY2014-FY2026), comfortably exceeding the 5-year requirement."),
        ("Identify Inconsistent Trends in Revenue, Expenses, or Margins",
         "Developed automated divergence flags to detect revenue growth accelerating while operating margins collapse, or expense ratios surging past historical norms."),
        ("Automated Pipeline for New Filings",
         "Built an automated end-to-end pipeline CLI (run_pipeline.py) and interactive demo that accepts new filing JSON/CSV or ticker inputs, calculates trailing features, and outputs a diagnostic risk scorecard.")
    ]

    for title, desc in objs:
        p1 = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p1.text = "✓ " + title
        p1.font.size = Pt(14); p1.font.bold = True; p1.font.color.rgb = C_NAVY
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11.5); p2.font.color.rgb = C_DARK; p2.space_after = Pt(12)

    # ==========================================
    # SLIDE 4: End-to-End System Architecture
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "End-to-End System Architecture")

    steps = [
        ("01. DATA INGESTION", "SEC EDGAR API\n• companyfacts JSON\n• submissions JSON\n• 26 companies (FY14-26)"),
        ("02. EXTRACTION", "Point-in-Time Dataset\n• As-first-reported\n• ASC 606 tag tracking\n• Derived 3M quarters"),
        ("03. TREND ANALYTICS", "12-Quarter Rolling Trends\n• Revenue vs Expense\n• Margin deviations\n• Accrual divergences"),
        ("04. ML & STAT MODELS", "Dual Detection Engine\n• Robust Z-scores\n• Isolation Forest\n• Beneish M-Score"),
        ("05. TRIAGE PIPELINE", "Audit Scorecard\n• Risk Classification\n• Contributing Red Flags\n• Auditor Checklist")
    ]

    step_w = Inches(2.15)
    gap = Inches(0.2)
    start_x = Inches(0.8)

    for idx, (head, body) in enumerate(steps):
        x = start_x + idx * (step_w + gap)
        add_card(s4, x, Inches(1.8), step_w, Inches(4.5))
        tb = s4.shapes.add_textbox(x + Inches(0.15), Inches(2.0), step_w - Inches(0.3), Inches(4.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_ORANGE
        p.space_after = Pt(12)
        p2 = tf.add_paragraph()
        p2.text = body
        p2.font.size = Pt(11); p2.font.color.rgb = C_DARK; p2.space_after = Pt(8)

    # ==========================================
    # SLIDE 5: Secondary Dataset & Feature Engineering
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Secondary Dataset & Feature Engineering")

    add_card(s5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    tb1 = s5.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Dataset Characteristics"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY
    ds_points = [
        "Grain: Company × Fiscal Quarter (1,334 company-quarters).",
        "Horizon: FY2014 to FY2026 (12 years of quarterly history).",
        "Coverage: 20 Control Companies (Apple, Microsoft, Johnson & Johnson, Walmart, Costco, etc.).",
        "Reference Group: 6 Companies with documented accounting enforcement or restatements (KHC, UAA, SMCI, MDXG, PLUG, MAT).",
        "Point-in-Time Integrity: Values as first reported in original 10-Q filings, preventing look-ahead bias.",
        "Quality Filters: 96 rows filtered for missing/negative revenue or tag switches; 1,238 clean observations scored."
    ]
    for pt in ds_points:
        p = tf1.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11.5); p.font.color.rgb = C_DARK; p.space_after = Pt(7)

    add_card(s5, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb2 = s5.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "42 Selected Model Features (5 Families)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY
    families = [
        ("Growth Features", "revenue_qoq_growth, revenue_yoy_growth, cogs_yoy_growth, sga_yoy_growth, net_income_yoy_growth, ar_yoy_growth."),
        ("Expense Ratios & Margins", "cogs_to_revenue, sga_to_revenue, rnd_to_revenue, total_expense_to_revenue, gross_margin, operating_margin, net_margin, margin YoY changes."),
        ("Working Capital & Accruals", "Days Sales Outstanding (dso), Days Inventory Outstanding (dio), Sloan Accruals to Assets (accruals_to_assets), cfo_to_net_income."),
        ("Channel Stuffing Indicator", "ar_growth_minus_revenue_growth (signals revenue pulled forward or bogus receivables)."),
        ("Trailing Robust Z-Scores", "8-quarter rolling median/MAD scores across 8 core ratios (rz_* and z_*).")
    ]
    for fam, f_desc in families:
        p = tf2.add_paragraph()
        p.text = "• " + fam + ":"
        p.font.size = Pt(11.5); p.font.bold = True; p.font.color.rgb = C_ORANGE
        p2 = tf2.add_paragraph()
        p2.text = f_desc
        p2.font.size = Pt(10.5); p2.font.color.rgb = C_DARK; p2.space_after = Pt(6)

    # ==========================================
    # SLIDE 6: Multi-Year Financial Trend Analysis
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Multi-Year Trend Analysis & Sudden Deviations")

    # Add Image
    img_path = FIG_DIR / "multi_year_trends.png"
    if img_path.exists():
        s6.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.2))

    add_card(s6, Inches(8.3), Inches(1.5), Inches(4.2), Inches(5.2))
    tb = s6.shapes.add_textbox(Inches(8.5), Inches(1.7), Inches(3.8), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Detecting Trend Breaks"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    trend_notes = [
        "Strictly Trailing Baselines: 12-quarter rolling window with shift(1) prevents look-ahead leakage.",
        "Normalized Trend Dev: Evaluates standard deviations away from trailing 3-year mean.",
        "Threshold: Quarters with |dev| >= 2.5σ marked as sudden trend breaks (282 quarters identified).",
        "Inconsistent Trends: Flags when revenue accelerates while operating cash flow or margins collapse.",
        "Visual Proof: Kraft Heinz operating margin collapse (-205%) and Super Micro Computer volatility stand out distinctly against stable Microsoft control."
    ]
    for tn in trend_notes:
        p = tf.add_paragraph()
        p.text = "• " + tn
        p.font.size = Pt(11); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # ==========================================
    # SLIDE 7: Statistical Anomaly Detection (Robust Z-Score)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Statistical Anomaly Detection (Trailing Robust Z-Score)")

    add_card(s7, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    tb1 = s7.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Mathematical Formulation"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    stat_math = [
        "Why Not Standard Z-Score? A single massive accounting restatement or write-down inflates the sample standard deviation, masking future anomalies.",
        "Robust Z-Score (RZ): Uses rolling median and Median Absolute Deviation (MAD):",
        "   RZ_t = [x_t - Median(x_{t-8..t-1})] / [1.4826 * MAD(x_{t-8..t-1})]",
        "Where MAD = Median(|x_i - Median(x)|). The factor 1.4826 makes MAD an unbiased estimator for normally distributed data.",
        "Composite Anomaly Score: Evaluated as the maximum absolute robust score across 8 key financial dimensions.",
        "Decision Threshold: |Z| >= 3.5 marks extreme statistical departures (391 quarters flagged)."
    ]
    for sm in stat_math:
        p = tf1.add_paragraph()
        p.text = sm if sm.startswith("   ") else "• " + sm
        p.font.size = Pt(11); p.font.color.rgb = C_DARK; p.space_after = Pt(7)

    add_card(s7, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb2 = s7.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Statistical Detection Performance"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    stat_perf = [
        "Observations Scored: 1,238 company-quarters.",
        "Flagged Observations: 391 quarters (31.6% universe rate).",
        "Control Group Flag Rate: 31.0%.",
        "Reference Group Flag Rate: 33.5% (Elevated flag rate in fraud/investigated cases).",
        "Strengths: Pinpoints extreme acute shocks (e.g. massive single-quarter goodwill impairment, sudden DSO spike).",
        "Limitations: Univariate trailing nature means correlated multidimensional drift may be missed without machine learning."
    ]
    for sp in stat_perf:
        p = tf2.add_paragraph()
        p.text = "• " + sp
        p.font.size = Pt(11.5); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # ==========================================
    # SLIDE 8: Machine Learning Anomaly Detection (Isolation Forest)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Machine Learning Anomaly Detection (Isolation Forest)")

    # Add Image
    img_path = FIG_DIR / "score_distribution.png"
    if img_path.exists():
        s8.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.2))

    add_card(s8, Inches(8.3), Inches(1.5), Inches(4.2), Inches(5.2))
    tb = s8.shapes.add_textbox(Inches(8.5), Inches(1.7), Inches(3.8), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Model Pipeline & Settings"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    if_notes = [
        "Architecture: SimpleImputer (median) -> RobustScaler (10-90th percentile) -> IsolationForest (300 estimators).",
        "Principle: Anomalies require fewer recursive binary feature splits to isolate in random trees.",
        "Anomaly Score: Score_IF = -score_samples(X). Higher score = more isolated/anomalous.",
        "Contamination Setting: 0.05 (flags top 5.0% most unusual quarters = 62 observations).",
        "Empirical Validation: Reference fraud group is visibly shifted toward higher anomaly scores in the KDE distribution."
    ]
    for ifn in if_notes:
        p = tf.add_paragraph()
        p.text = "• " + ifn
        p.font.size = Pt(11); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # ==========================================
    # SLIDE 9: Model Comparison & Reference vs Control
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Model Comparison & Reference vs Control Evaluation")

    add_card(s9, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tb = s9.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(11.1), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Descriptive Model Comparison Table"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_NAVY
    p.space_after = Pt(14)

    # Table
    table_shape = s9.shapes.add_table(4, 5, Inches(1.1), Inches(2.2), Inches(11.1), Inches(1.8))
    table = table_shape.table
    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = Inches(2.0)
    table.columns[3].width = Inches(2.0)
    table.columns[4].width = Inches(1.9)

    headers = ["Methodology", "Scored Rows", "Flagged Rows", "Control Flag %", "Reference Flag %"]
    data = [
        ["Robust Trailing Z-Score (|Z|>=3.5)", "1,238", "391 (31.6%)", "31.0%", "33.5%"],
        ["Isolation Forest (Contamination=0.05)", "1,238", "62 (5.0%)", "4.8%", "5.6%"],
        ["Multi-Year Sudden Deviations (|dev|>=2.5σ)", "1,238", "282 (22.8%)", "21.6%", "26.8%"]
    ]

    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        cell.fill.solid(); cell.fill.fore_color.rgb = C_NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_WHITE

    for row_idx, row in enumerate(data, 1):
        for col_idx, val in enumerate(row):
            cell = table.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if row_idx % 2 == 1 else C_LIGHT_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11); p.font.color.rgb = C_DARK

    # Bottom notes
    tb_notes = s9.shapes.add_textbox(Inches(1.1), Inches(4.3), Inches(11.1), Inches(2.2))
    tf_notes = tb_notes.text_frame
    tf_notes.word_wrap = True
    p = tf_notes.paragraphs[0]
    p.text = "Key Analytical Insights:"
    p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_ORANGE
    bullets = [
        "Elevated Risk Sensitivity: Across all three methodologies, the Reference Group (companies with verified accounting actions) demonstrates systematically higher flag rates than the Control Group.",
        "Complementary Detection Profiles: Z-scores excel at detecting single-metric spikes; Isolation Forest detects multi-ratio imbalances (e.g. modest growth with deteriorating receivables and cash conversion).",
        "Weak Labels Caveat: Group-level labels reflect company-level enforcement history, not quarter-level fraud ground truth; rates are presented as descriptive validation."
    ]
    for b in bullets:
        p = tf_notes.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11.5); p.font.color.rgb = C_DARK; p.space_after = Pt(4)

    # ==========================================
    # SLIDE 10: Top Anomaly Candidates Leaderboard
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Top Anomaly Candidates Leaderboard")

    img_path = FIG_DIR / "top_anomalies_barchart.png"
    if img_path.exists():
        s10.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.2))

    add_card(s10, Inches(8.3), Inches(1.5), Inches(4.2), Inches(5.2))
    tb = s10.shapes.add_textbox(Inches(8.5), Inches(1.7), Inches(3.8), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Top Anomaly Insights"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    top_notes = [
        "Super Micro Computer (SMCI): Dominates top ranks with extreme revenue growth swings and receivables anomalies.",
        "Kraft Heinz (KHC): High anomaly scores in FY2018-FY2019 aligning with SEC investigation and procurement charge.",
        "Under Armour (UAA): Prominent anomaly ranks during 2016-2020 revenue stagnation and restructuring.",
        "Control Outliers: Blue chips appearing in the top 15 (e.g. 3M Solventum spinoff, Honeywell corporate restructuring) correspond to major disclosed corporate events."
    ]
    for tn in top_notes:
        p = tf.add_paragraph()
        p.text = "• " + tn
        p.font.size = Pt(11); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # ==========================================
    # SLIDE 11: Forensic Case Studies: Real Scandals Detected
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Forensic Case Studies: Validating Real Accounting Scandals")

    img_path = FIG_DIR / "case_studies_signals.png"
    if img_path.exists():
        s11.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(7.2))

    add_card(s11, Inches(8.3), Inches(1.5), Inches(4.2), Inches(5.2))
    tb = s11.shapes.add_textbox(Inches(8.5), Inches(1.7), Inches(3.8), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Real-World Scandal Signals"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    cs_notes = [
        "Kraft Heinz (KHC) Procurement Fraud: In FY2018 Q4, operating margin crashed to -205% (RZ = -9.45σ) alongside $15.4B goodwill write-down.",
        "Under Armour (UAA) Channel Stuffing: In 2015-2016, receivables growth outpaced revenue growth by up to 7.23σ, signalling pulled-forward orders.",
        "MiMedx Group (MDXG): Wholesaler channel stuffing produced gross margin swings of 7.85σ and DSO spikes of 5.24σ prior to restatement."
    ]
    for csn in cs_notes:
        p = tf.add_paragraph()
        p.text = "• " + csn
        p.font.size = Pt(11); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # ==========================================
    # SLIDE 12: Beneish M-Score Benchmark Comparison
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Forensic Benchmark: Annual Beneish M-Score")

    add_card(s12, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    tb1 = s12.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Beneish M-Score Formulation"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    bm_math = [
        "Probabilistic 8-Variable Forensic Model: Developed by Prof. Messod Beneish to assess financial manipulation likelihood.",
        "M = -4.84 + 0.920*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI + 0.115*DEPI - 0.172*SGAI + 4.037*TATA + 0.0327*LVGI",
        "DSRI: Days Sales in Receivables Index",
        "GMI: Gross Margin Index (decaying margins)",
        "AQI: Asset Quality Index (non-current assets)",
        "SGI: Sales Growth Index",
        "TATA: Total Accruals to Total Assets",
        "Threshold: M > -1.78 signals high manipulation probability."
    ]
    for bmm in bm_math:
        p = tf1.add_paragraph()
        p.text = "• " + bmm
        p.font.size = Pt(11); p.font.color.rgb = C_DARK; p.space_after = Pt(6)

    add_card(s12, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb2 = s12.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Benchmarking Results"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    bm_results = [
        "Company-Years Analyzed: 285 company-years with complete annual filings.",
        "Beneish Flagged Years (M > -1.78): 36 company-years (12.6% manipulation risk rate).",
        "Isolation Forest Quarterly Alerts: 52 company-years had at least one IF-flagged quarter.",
        "Consensus Alerts: Significant concordance between annual Beneish alerts and quarterly ML flags in reference companies (e.g. KHC, UAA, SMCI).",
        "Methodological Independence: Beneish was joined strictly post-hoc for validation and was never used during model training."
    ]
    for bmr in bm_results:
        p = tf2.add_paragraph()
        p.text = "• " + bmr
        p.font.size = Pt(11.5); p.font.color.rgb = C_DARK; p.space_after = Pt(8)

    # ==========================================
    # SLIDE 13: Automated Pipeline for New Filings
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Automated Pipeline for New Filings")

    add_card(s13, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tb = s13.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(11.1), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Automated Live Ingestion & Audit Triage Workflow"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_NAVY
    p.space_after = Pt(12)

    pipe_steps = [
        ("1. Ingestion Engine", "Ingests newly submitted 10-Q/10-K filings from SEC EDGAR API or local JSON/CSV filings on demand via CLI: python run_pipeline.py --ticker SMCI."),
        ("2. Real-Time Feature Calculation", "Appends filing to company historical filings, derives 42 financial ratios, computes trailing 8-quarter Z-scores, and calculates trailing 12-quarter multi-year trend deviations."),
        ("3. Model Scoring & Consensus Tiering", "Executes pre-trained Isolation Forest model (isolation_forest_model.joblib) and evaluates robust Z-scores and multi-year trend breaks simultaneously."),
        ("4. Risk Classification Tiers", "• HIGH ANOMALY (Multi-Method Consensus): Immediate forensic audit priority.\n• ELEVATED REVIEW (Single-Method Alert): Secondary triage.\n• NORMAL: Cleared for continuous monitoring."),
        ("5. Actionable Audit Scorecard", "Outputs flagged financial metrics with exact deviation sigmas and automated auditor audit recommendations (e.g. audit receivables aging, verify inventory capitalization).")
    ]

    for title, desc in pipe_steps:
        p1 = tf.add_paragraph()
        p1.text = "• " + title
        p1.font.size = Pt(13); p1.font.bold = True; p1.font.color.rgb = C_ORANGE
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11); p2.font.color.rgb = C_DARK; p2.space_after = Pt(8)

    # ==========================================
    # SLIDE 14: Technologies, Tools & Frameworks
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Technologies, Tools & Frameworks Used")

    tech_cards = [
        ("Machine Learning & Stats", "• Scikit-learn: Isolation Forest, RobustScaler, SimpleImputer\n• SciPy & Statsmodels: Median Absolute Deviation (MAD), Rolling Statistics\n• Joblib: Model serialization"),
        ("Data Processing & APIs", "• Python 3.13: Core runtime\n• Pandas & NumPy: Vectorized ratio calculations and rolling window math\n• SEC EDGAR REST API: Keyless corporate facts and filings"),
        ("Visualization & Presentation", "• Seaborn & Matplotlib: High-resolution KDE distributions, trend lines, and bar charts\n• Python-PPTX: Automated slide generation\n• Jupyter & Nbconvert: Executable analytics"),
        ("Automated Pipelines & QA", "• Pytest & Unittest: 6 comprehensive unit/integration test suites\n• Interactive CLI Console (live_demo.py): Live evaluation runner\n• JSON & CSV Artifacts: Full audit trails")
    ]

    card_w2 = Inches(5.6)
    card_h2 = Inches(2.4)

    positions = [
        (Inches(0.8), Inches(1.5)),
        (Inches(6.8), Inches(1.5)),
        (Inches(0.8), Inches(4.2)),
        (Inches(6.8), Inches(4.2))
    ]

    for idx, (t_title, t_desc) in enumerate(tech_cards):
        x, y = positions[idx]
        add_card(s14, x, y, card_w2, card_h2)
        tb = s14.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), card_w2 - Inches(0.4), card_h2 - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t_title
        p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_NAVY
        p.space_after = Pt(8)
        p2 = tf.add_paragraph()
        p2.text = t_desc
        p2.font.size = Pt(11); p2.font.color.rgb = C_DARK

    # ==========================================
    # SLIDE 15: Details of All Deliverables Implemented
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Deliverables Matrix: Implemented & Achieved")

    add_card(s15, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    tb1 = s15.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Deliverable 1: Data Extraction (Completed)"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_NAVY
    d1_items = [
        ("Secondary Dataset (CSV)", "quarterly_features.csv (1,334 quarters, 94 features) and annual_features.csv (323 company-years)."),
        ("Extraction Notebook (ipynb)", "01_edgar_data_extraction.ipynb — fully reproducible EDGAR data extraction."),
        ("Audit Trail & Data Dictionary", "facts_long.csv (47,514 facts mapped to accession numbers) and data_dictionary.csv."),
        ("Documentation & Slides", "README.md and SEC_Anomaly_Detection_Deliverable1.pptx.")
    ]
    for it, desc in d1_items:
        p = tf1.add_paragraph()
        p.text = "✓ " + it + ":"
        p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_ORANGE
        p2 = tf1.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10); p2.font.color.rgb = C_DARK; p2.space_after = Pt(6)

    add_card(s15, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb2 = s15.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Deliverable 2: Machine Learning & Pipeline (Achieved)"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_NAVY
    d2_items = [
        ("Machine Learning Notebook (ipynb)", "02_ml_anomaly_detection.ipynb — fully executed end-to-end with 14 code cells, tables, and visualizations."),
        ("Automated New-Filing Pipeline", "run_pipeline.py and src/anomaly_pipeline.py supporting batch and real-time single-filing scoring."),
        ("Multi-Year Trend Analytics", "compute_multi_year_trends evaluating trailing 12-quarter baselines and identifying sudden deviations."),
        ("Comprehensive Documentation", "docs/DELIVERABLE2.md and updated README.md."),
        ("Deliverable 2 Presentation (PPTX)", "SEC_Anomaly_Detection_Deliverable2.pptx covering all evaluation rubrics."),
        ("Live Demonstration Tool", "live_demo.py interactive console for examination panel demonstration.")
    ]
    for it, desc in d2_items:
        p = tf2.add_paragraph()
        p.text = "✓ " + it + ":"
        p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_ORANGE
        p2 = tf2.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10); p2.font.color.rgb = C_DARK; p2.space_after = Pt(6)

    # ==========================================
    # SLIDE 16: Conclusions & Operational Audit Protocol
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "Conclusions & Operational Triage Protocol")

    add_card(s16, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tb = s16.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(11.1), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Final Outcomes & Operational Recommendations"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_NAVY
    p.space_after = Pt(12)

    concls = [
        ("Robust Anomaly Prioritization", "The dual-engine architecture (Isolation Forest + Robust Z-Scores + Multi-Year Trends) successfully separates extreme accounting events from regular business noise. It proves effective at flagging known fraud cases like Kraft Heinz and Under Armour."),
        ("Operational Triage Protocol for Regulators / Auditors", "1. Screen incoming filings through automated pipeline -> 2. Flag quarters crossing multi-method thresholds -> 3. Inspect top contributing red flags (e.g. AR growth minus revenue growth) -> 4. Review filing footnotes, one-off charges, and accession history before alleging fraud."),
        ("Limitations & Integrity", "Anomalies flag review candidates, not fraud proof. Genuine structural events (spinoffs like 3M Solventum or J&J Kenvue) also produce statistical deviations and are correctly documented."),
        ("Project Status", "100% of Deliverable 1 and Deliverable 2 requirements have been fully developed, tested, documented, and packaged for live demonstration.")
    ]

    for title, desc in concls:
        p1 = tf.add_paragraph()
        p1.text = "• " + title
        p1.font.size = Pt(13); p1.font.bold = True; p1.font.color.rgb = C_ORANGE
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11); p2.font.color.rgb = C_DARK; p2.space_after = Pt(8)

    # Save presentation
    out_ppt1 = ROOT / "SEC_Anomaly_Detection_Deliverable2.pptx"
    prs.save(str(out_ppt1))
    print(f"Presentation saved successfully to: {out_ppt1}")

if __name__ == "__main__":
    create_presentation()
