"""Generate Deliverable 2 PowerPoint presentation perfectly matched to Deliverable 1 style & theme.

Matches 100%:
- Color palette: #13232B (dark slate), #E3A03A (amber gold), #2E6F6A (category teal), #F1F4F4 (card bg), #5E6E75 (muted), #1C2A30 (body)
- Typography: Cambria (headings, titles, KPI numbers), Calibri (kickers, body, footers)
- Explicit run-level formatting: font name, size, bold, color on every text run
- Dimensions: 13.333" x 7.5" (16:9 widescreen)
- Header/footer layout: exact coordinate alignment
- Icon blocks: 0.85" x 0.85" amber squares with embedded icons
- Smooth narrative transition from Slide 13 of Deliverable 1
"""
import os
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "docs" / "figures"
ICON_DIR = ROOT / "ppt_icons"

# Exact Deliverable 1 Palette
C_DARK_BG   = RGBColor(19, 35, 43)    # #13232B Title Slide Bg & Deep Slate
C_AMBER     = RGBColor(227, 160, 58)  # #E3A03A Warm Gold / Accent / Stat Highlight
C_TEAL      = RGBColor(46, 111, 106)  # #2E6F6A Category Kicker / Tracker
C_CARD_BG   = RGBColor(241, 244, 244) # #F1F4F4 Card Fill
C_TEXT_DARK = RGBColor(28, 42, 48)    # #1C2A30 Body Text
C_HEAD_DARK = RGBColor(19, 35, 43)    # #13232B Slide Title & Heading
C_MUTED     = RGBColor(94, 110, 117)  # #5E6E75 Secondary Text & Footers
C_LIGHT_SUB = RGBColor(201, 211, 214) # #C9D3D6 Title Subtitle
C_WHITE     = RGBColor(255, 255, 255)
C_BORDER    = RGBColor(241, 244, 244)

FONT_HEAD = "Cambria"
FONT_BODY = "Calibri"

def add_para(tf, text, font_name=FONT_BODY, font_size=12, bold=False, color=C_TEXT_DARK, space_after=0, is_first=False, align=PP_ALIGN.LEFT):
    """Add paragraph and enforce explicit run formatting."""
    p = tf.paragraphs[0] if is_first else tf.add_paragraph()
    p.text = text
    p.alignment = align
    p.font.name = font_name
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.space_after = Pt(space_after)
    for r in p.runs:
        r.font.name = font_name
        r.font.size = Pt(font_size)
        r.font.bold = bold
        r.font.color.rgb = color
    return p

def add_slide_header(slide, kicker_text, title_text):
    """Standard header matching Deliverable 1 slides."""
    # Kicker / Category Tracker
    tb_k = slide.shapes.add_textbox(Inches(0.60), Inches(0.42), Inches(10.0), Inches(0.30))
    tf_k = tb_k.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_top = tf_k.margin_right = tf_k.margin_bottom = 0
    add_para(tf_k, kicker_text.upper(), font_name=FONT_BODY, font_size=12, bold=True, color=C_TEAL, is_first=True)

    # Main Title
    tb_t = slide.shapes.add_textbox(Inches(0.60), Inches(0.72), Inches(12.13), Inches(0.75))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    add_para(tf_t, title_text, font_name=FONT_HEAD, font_size=32, bold=True, color=C_HEAD_DARK, is_first=True)

def add_slide_footer(slide, slide_num):
    """Standard footer matching Deliverable 1."""
    # Left footer
    tb_l = slide.shapes.add_textbox(Inches(0.60), Inches(7.00), Inches(8.00), Inches(0.25))
    tf_l = tb_l.text_frame
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
    add_para(tf_l, "SEC Filing Anomaly Detection  ·  Deliverable 2: Machine Learning & Anomaly Detection",
             font_name=FONT_BODY, font_size=10, bold=False, color=C_MUTED, is_first=True)

    # Right footer (slide number)
    tb_r = slide.shapes.add_textbox(Inches(12.23), Inches(7.00), Inches(0.50), Inches(0.25))
    tf_r = tb_r.text_frame
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
    add_para(tf_r, str(slide_num), font_name=FONT_BODY, font_size=10, bold=False, color=C_MUTED, is_first=True, align=PP_ALIGN.RIGHT)

def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BG):
    """Add card shape matching PPT1."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

def add_icon_box(slide, left, top, icon_idx=None, bg_color=C_AMBER, size=0.85):
    """Add amber square icon container matching PPT1."""
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(size), Inches(size))
    box.fill.solid()
    box.fill.fore_color.rgb = bg_color
    box.line.color.rgb = bg_color
    
    if icon_idx:
        icon_path = ICON_DIR / f"icon_{icon_idx}.png"
        if icon_path.exists():
            pad = Inches(0.22)
            slide.shapes.add_picture(str(icon_path), left + pad, top + pad, width=Inches(0.41), height=Inches(0.41))
    return box

def build_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title Slide (Matches Deliverable 1 Slide 1 Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_DARK_BG
    bg1.line.fill.background()

    # Icon top left
    add_icon_box(s1, Inches(0.60), Inches(0.90), icon_idx=1, bg_color=C_AMBER, size=0.90)

    # Text 1: Kicker
    tb1 = s1.shapes.add_textbox(Inches(0.60), Inches(2.20), Inches(10.00), Inches(0.35))
    tf1 = tb1.text_frame
    tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0
    add_para(tf1, "DELIVERABLE 2  ·  MACHINE LEARNING & ANOMALY DETECTION", font_name=FONT_BODY, font_size=14, bold=True, color=C_AMBER, is_first=True)

    # Text 2: Main Title
    tb2 = s1.shapes.add_textbox(Inches(0.60), Inches(2.65), Inches(11.50), Inches(1.90))
    tf2 = tb2.text_frame
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
    add_para(tf2, "Detecting Financial Anomalies", font_name=FONT_HEAD, font_size=48, bold=True, color=C_WHITE, is_first=True)
    add_para(tf2, "in SEC Filings: Final Deliverables", font_name=FONT_HEAD, font_size=48, bold=True, color=C_WHITE)

    # Text 3: Subtitle / Purpose
    tb3 = s1.shapes.add_textbox(Inches(0.60), Inches(4.70), Inches(11.00), Inches(0.90))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_top = tf3.margin_right = tf3.margin_bottom = 0
    add_para(tf3, "From Extracted Point-in-Time XBRL Features to Multi-Year Trend Breaks, Statistical Robust Z-Scores, Isolation Forest Inference, and an Automated Real-Time Triage Pipeline",
             font_name=FONT_BODY, font_size=18, bold=False, color=C_LIGHT_SUB, is_first=True)

    # Text 4: Metadata Bar
    tb4 = s1.shapes.add_textbox(Inches(0.60), Inches(6.30), Inches(11.50), Inches(0.35))
    tf4 = tb4.text_frame
    tf4.margin_left = tf4.margin_top = tf4.margin_right = tf4.margin_bottom = 0
    add_para(tf4, "26 companies  ·  1,238 scored quarters  ·  42 financial ratios  ·  3 detection engines  ·  FY2014–FY2026",
             font_name=FONT_BODY, font_size=14, bold=False, color=C_AMBER, is_first=True)

    # =========================================================================
    # SLIDE 2: Transition & Foundation (Smooth Bridge from Deliverable 1)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(s2, "TRANSITION & FOUNDATION", "Building Directly on the Deliverable 1 Secondary Dataset")
    add_slide_footer(s2, 2)

    card_w = Inches(3.85)
    card_h = Inches(4.60)
    card_y = Inches(1.80)

    # Card 1: Deliverable 1 Foundation
    add_card(s2, Inches(0.60), card_y, card_w, card_h)
    add_icon_box(s2, Inches(1.00), Inches(2.10), icon_idx=2, bg_color=C_AMBER)
    tb = s2.shapes.add_textbox(Inches(1.00), Inches(3.15), Inches(3.05), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Deliverable 1 Legacy", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb = s2.shapes.add_textbox(Inches(1.00), Inches(3.65), Inches(3.05), Inches(2.60))
    tb.text_frame.word_wrap = True; tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    tf = tb.text_frame
    pts_d1 = [
        "Ingested 106,153 raw XBRL facts across 12 fiscal years (FY2014–FY2026).",
        "Standardized 23 primary line items with ASC 606 revenue tag resolution.",
        "Built point-in-time secondary dataset (1,334 company-quarters, 94 features) with no look-ahead bias.",
        "Derived standalone Q4 and quarterly cash flows from YTD totals."
    ]
    for i, pt in enumerate(pts_d1):
        add_para(tf, "• " + pt, font_name=FONT_BODY, font_size=13, color=C_TEXT_DARK, space_after=5, is_first=(i==0))

    # Card 2: The Deliverable 1 Hand-Off
    add_card(s2, Inches(4.75), card_y, card_w, card_h)
    add_icon_box(s2, Inches(5.15), Inches(2.10), icon_idx=3, bg_color=C_AMBER)
    tb = s2.shapes.add_textbox(Inches(5.15), Inches(3.15), Inches(3.05), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "The Deliverable 1 Promise", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb = s2.shapes.add_textbox(Inches(5.15), Inches(3.65), Inches(3.05), Inches(2.60))
    tb.text_frame.word_wrap = True; tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    tf = tb.text_frame
    pts_prom = [
        "Slide 13 of Deliverable 1 pledged:\n  1. Z-score baseline ranking\n  2. Isolation Forest model\n  3. Reference vs. Control evaluation",
        "Data quality audit in D1 identified 21 reconciliation mismatches clustering around spin-offs and restatements.",
        "D1 early checks showed top raw deviations matched real corporate events."
    ]
    for i, pt in enumerate(pts_prom):
        add_para(tf, "• " + pt, font_name=FONT_BODY, font_size=13, color=C_TEXT_DARK, space_after=6, is_first=(i==0))

    # Card 3: Deliverable 2 Execution
    add_card(s2, Inches(8.90), card_y, card_w, card_h)
    add_icon_box(s2, Inches(9.30), Inches(2.10), icon_idx=4, bg_color=C_AMBER)
    tb = s2.shapes.add_textbox(Inches(9.30), Inches(3.15), Inches(3.05), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Deliverable 2 Completion", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb = s2.shapes.add_textbox(Inches(9.30), Inches(3.65), Inches(3.05), Inches(2.60))
    tb.text_frame.word_wrap = True; tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    tf = tb.text_frame
    pts_d2 = [
        "Dual statistical & ML anomaly detection fully implemented and calibrated.",
        "12-quarter trailing rolling baselines detecting multi-year structural trend breaks.",
        "Annual Beneish M-Score concordance cross-validation.",
        "Automated pipeline and interactive Streamlit UI for live viva demonstration."
    ]
    for i, pt in enumerate(pts_d2):
        add_para(tf, "• " + pt, font_name=FONT_BODY, font_size=13, color=C_TEXT_DARK, space_after=6, is_first=(i==0))

    # =========================================================================
    # SLIDE 3: At a Glance (Deliverable 2 Quantitative Output)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(s3, "AT A GLANCE", "What the Deliverable 2 Analytics Produced")
    add_slide_footer(s3, 3)

    stats = [
        ("1,238", "clean company-quarters scored after quality filtering", C_HEAD_DARK),
        ("42", "multidimensional financial ratios used in ML model", C_HEAD_DARK),
        ("62", "Isolation Forest outliers detected (5.0% calibration)", C_HEAD_DARK),
        ("391", "statistical shocks isolated (|RZ| ≥ 3.5σ)", C_AMBER),
        ("282", "quarters flagged with multi-year trend breaks", C_HEAD_DARK),
        ("1.8s", "latency to ingest, trend, and score new filings", C_HEAD_DARK),
    ]

    col_w = Inches(3.85)
    row_h = Inches(2.15)
    xs = [Inches(0.60), Inches(4.75), Inches(8.90)]
    ys = [Inches(1.80), Inches(4.35)]

    for idx, (num, desc, num_color) in enumerate(stats):
        cx = xs[idx % 3]
        cy = ys[idx // 3]
        add_card(s3, cx, cy, col_w, row_h)

        tb = s3.shapes.add_textbox(cx + Inches(0.35), cy + Inches(0.20), col_w - Inches(0.70), Inches(0.90))
        tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, num, font_name=FONT_HEAD, font_size=46, bold=True, color=num_color, is_first=True)

        tb_d = s3.shapes.add_textbox(cx + Inches(0.35), cy + Inches(1.15), col_w - Inches(0.70), Inches(0.85))
        tb_d.text_frame.word_wrap = True; tb_d.text_frame.margin_left = tb_d.text_frame.margin_top = 0
        add_para(tb_d.text_frame, desc, font_name=FONT_BODY, font_size=14, bold=False, color=C_MUTED, is_first=True)

    # =========================================================================
    # SLIDE 4: ML & Data Analytics Objectives
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(s4, "OBJECTIVES ALIGNMENT", "Task FDA-2 Requirements Fully Operationalized")
    add_slide_footer(s4, 4)

    add_card(s4, Inches(0.60), Inches(1.80), Inches(12.13), Inches(4.90))
    tb = s4.shapes.add_textbox(Inches(0.95), Inches(2.05), Inches(11.40), Inches(4.45))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    reqs = [
        ("Statistical Anomaly Detection (Isolation Forest, Z-score)",
         "Implemented rolling median/MAD robust Z-scores (|Z| >= 3.5) and a 300-tree Isolation Forest with RobustScaler across 42 financial features. Models operate strictly on ratio features to prevent scale or ticker leakage."),
        ("Multi-Year Trend Analysis for Sudden Deviations",
         "Constructed trailing 12-quarter (3-year) rolling means and standard deviations strictly prior to the evaluated quarter (shift(1)). Detected structural trend breaks (|dev| >= 2.5 sigma) across revenue, expense ratios, margins, and accruals."),
        ("Extract 5+ Years of Financial Statements via EDGAR",
         "Secondary dataset extracts 12 fiscal years of point-in-time XBRL filings from SEC EDGAR (FY2014–FY2026), covering 26 companies and 1,334 company-quarters, exceeding the 5-year requirement."),
        ("Identify Inconsistent Trends in Revenue, Expenses, or Margins",
         "Formulated automated divergence logic flagging quarters where revenue growth accelerates while operating margins collapse, or where receivables outstrip revenue growth (channel stuffing signature)."),
        ("Automated Pipeline for New Filings",
         "Engineered an automated end-to-end CLI (run_pipeline.py) and interactive Streamlit web dashboard (app.py) that ingest new filings, calculate trailing baselines, and render diagnostic Forensic Audit Scorecards.")
    ]

    for i, (title, desc) in enumerate(reqs):
        add_para(tf, "✓  " + title, font_name=FONT_HEAD, font_size=14.5, bold=True, color=C_HEAD_DARK, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, bold=False, color=C_TEXT_DARK, space_after=10)

    # =========================================================================
    # SLIDE 5: Three Complementary Forensic Lenses
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(s5, "METHODOLOGY", "Three Complementary Forensic Detection Engines")
    add_slide_footer(s5, 5)

    methods = [
        ("Statistical Z-Score", "Rolling Median & MAD", 5, [
            "Baseline: Trailing 8 quarters prior to evaluated quarter (shift(1)).",
            "Robust Formulation: RZ = (x - Median) / (1.4826 * MAD).",
            "Threshold: |RZ| >= 3.5 sigma.",
            "Role: Captures sudden single-quarter volatility shocks and ratio spikes."
        ]),
        ("Isolation Forest ML", "Multidimensional Subspacing", 6, [
            "Ensemble: 300 decision trees with RobustScaler (10th-90th quantile).",
            "Feature Space: 42 financial ratios & growth rates.",
            "Contamination: 0.05 calibration (top 5% most isolated filings).",
            "Role: Detects subtle cross-statement combinations that evade 1D thresholds."
        ]),
        ("Multi-Year Trends", "Trailing 12-Quarter Drift", 7, [
            "Baseline: 12-quarter (3-year) rolling mean and standard deviation.",
            "Structural Deviation: |Trend Dev| >= 2.5 sigma.",
            "Inconsistent Trends: Accelerating revenue paired with margin collapse.",
            "Role: Exposes gradual operational drift and multi-year structural breaks."
        ]),
    ]

    for idx, (title, sub, icon_i, points) in enumerate(methods):
        cx = Inches(0.60) + idx * Inches(4.15)
        add_card(s5, cx, Inches(1.80), Inches(3.85), Inches(4.80))
        add_icon_box(s5, cx + Inches(0.40), Inches(2.15), icon_idx=icon_i)

        tb = s5.shapes.add_textbox(cx + Inches(0.40), Inches(3.20), Inches(3.05), Inches(0.70))
        tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, title, font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)
        add_para(tb.text_frame, sub, font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL)

        tb_b = s5.shapes.add_textbox(cx + Inches(0.40), Inches(4.00), Inches(3.05), Inches(2.40))
        tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
        for i, pt in enumerate(points):
            add_para(tb_b.text_frame, "• " + pt, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=4, is_first=(i==0))

    # =========================================================================
    # SLIDE 6: Statistical Robust Z-Scores
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_header(s6, "STATISTICAL DETECTION", "Isolating Quarterly Shocks Without Look-Ahead Bias")
    add_slide_footer(s6, 6)

    add_card(s6, Inches(0.60), Inches(1.80), Inches(5.80), Inches(4.80))
    tb1 = s6.shapes.add_textbox(Inches(0.95), Inches(2.05), Inches(5.10), Inches(4.30))
    tf1 = tb1.text_frame; tf1.word_wrap = True; tf1.margin_left = tf1.margin_top = 0
    add_para(tf1, "Why Robust Z-Scores Matter", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)
    points_z = [
        "Financial data exhibits severe non-normality and extreme outliers that contaminate traditional sample means and standard deviations.",
        "A single massive write-down distorts classic Z-scores for subsequent quarters (masking effect).",
        "Solution: Rolling Median and Median Absolute Deviation (MAD) over prior 8 quarters:",
        "    RZ_t = (x_t - Median(x_{t-8..t-1})) / (1.4826 * MAD(x_{t-8..t-1}))",
        "Zero Look-Ahead Bias: Baselines are strictly lagged with shift(1); the evaluated quarter never contaminates its own baseline.",
        "Result: 391 company-quarters flagged with extreme shocks (|RZ| >= 3.5)."
    ]
    for pt in points_z:
        add_para(tf1, pt, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=5)

    add_card(s6, Inches(6.80), Inches(1.80), Inches(5.90), Inches(4.80))
    tb2 = s6.shapes.add_textbox(Inches(7.15), Inches(2.05), Inches(5.20), Inches(4.30))
    tf2 = tb2.text_frame; tf2.word_wrap = True; tf2.margin_left = tf2.margin_top = 0
    add_para(tf2, "Key Monitored Ratio Shocks", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    shocks = [
        ("Revenue YoY / QoQ Growth", "Sudden demand collapse or inorganic revenue spikes."),
        ("Total Expense-to-Revenue", "Operating cost inflation or unrecognized expenses."),
        ("Operating & Gross Margin", "Uncharacteristic profitability drops or margin preservation during revenue slowdowns."),
        ("Days Sales Outstanding (DSO)", "Collection slowdowns or premature billings."),
        ("Sloan Accruals to Assets", "Large divergences between accounting net income and operating cash flow."),
        ("AR Growth minus Rev Growth", "Direct empirical signature of channel stuffing."),
    ]
    for title, desc in shocks:
        add_para(tf2, "• " + title + ":", font_name=FONT_BODY, font_size=12.5, bold=True, color=C_TEAL)
        add_para(tf2, "   " + desc, font_name=FONT_BODY, font_size=11.5, bold=False, color=C_TEXT_DARK, space_after=3)

    # =========================================================================
    # SLIDE 7: Machine Learning — Isolation Forest
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_header(s7, "MACHINE LEARNING DETECTION", "300-Tree Isolation Forest on 42 Multidimensional Features")
    add_slide_footer(s7, 7)

    add_card(s7, Inches(0.60), Inches(1.80), Inches(5.20), Inches(4.80))
    tb = s7.shapes.add_textbox(Inches(0.90), Inches(2.05), Inches(4.60), Inches(4.30))
    tf = tb.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_top = 0
    add_para(tf, "Model Specifications", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)
    ml_pts = [
        "Unsupervised Ensemble: 300 isolation trees isolating anomalies based on path length.",
        "High-Dimensional Feature Space: 42 financial ratios spanning growth, profitability, working capital, and earnings quality.",
        "Robust Preprocessing: RobustScaler (10th-90th percentile) prevents extreme values from distorting distance metrics.",
        "Median Imputation: SimpleImputer(median) handles sporadic missing ratios.",
        "Contamination Rate: Calibrated to 0.05 (flags top 5% most anomalous observations = 62 quarters).",
        "Discriminative Validity: Flags 5.6% of Reference Group quarters vs 4.8% of Control Group quarters."
    ]
    for pt in ml_pts:
        add_para(tf, "• " + pt, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=5)

    # Embedded Figure: score_distribution.png
    add_card(s7, Inches(6.15), Inches(1.80), Inches(6.58), Inches(4.80))
    fig1_path = FIG_DIR / "score_distribution.png"
    if fig1_path.exists():
        s7.shapes.add_picture(str(fig1_path), Inches(6.30), Inches(2.00), width=Inches(6.28), height=Inches(4.40))

    # =========================================================================
    # SLIDE 8: Multi-Year Trend Analysis & Sudden Deviations
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_header(s8, "MULTI-YEAR TRENDS", "12-Quarter Rolling Baselines Expose Structural Breaks")
    add_slide_footer(s8, 8)

    add_card(s8, Inches(0.60), Inches(1.80), Inches(5.20), Inches(4.80))
    tb = s8.shapes.add_textbox(Inches(0.90), Inches(2.05), Inches(4.60), Inches(4.30))
    tf = tb.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_top = 0
    add_para(tf, "Trend Deviation Methodology", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)
    tr_pts = [
        "Trailing 12-Quarter Window: 3 full fiscal years of prior performance establish company-specific baselines.",
        "Strict Time Ordering: Prior quarters only (shift(1)); immune to look-ahead bias.",
        "Standardized Deviation Score: Deviation = (x_t - Mean_12Q) / Std_12Q.",
        "Threshold: |Trend Dev| >= 2.5 sigma marks structural breaks (282 quarters flagged).",
        "Inconsistent Trend Flags: Identifies quarters where revenue growth accelerates while operating margins collapse, or operating cash flows deteriorate.",
        "Longitudinal Context: Isolates genuine operational shifts from quarterly seasonality."
    ]
    for pt in tr_pts:
        add_para(tf, "• " + pt, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=5)

    # Embedded Figure: multi_year_trends.png
    add_card(s8, Inches(6.15), Inches(1.80), Inches(6.58), Inches(4.80))
    fig2_path = FIG_DIR / "multi_year_trends.png"
    if fig2_path.exists():
        s8.shapes.add_picture(str(fig2_path), Inches(6.30), Inches(2.00), width=Inches(6.28), height=Inches(4.40))

    # =========================================================================
    # SLIDE 9: Annual Benchmark — Beneish M-Score Concordance
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_header(s9, "FORENSIC BENCHMARK", "Concordance with the Classic 8-Variable Beneish M-Score")
    add_slide_footer(s9, 9)

    add_card(s9, Inches(0.60), Inches(1.80), Inches(6.00), Inches(4.80))
    tb1 = s9.shapes.add_textbox(Inches(0.95), Inches(2.05), Inches(5.30), Inches(4.30))
    tf1 = tb1.text_frame; tf1.word_wrap = True; tf1.margin_left = tf1.margin_top = 0
    add_para(tf1, "The Beneish M-Score Model", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)
    pts_b = [
        "Classic 8-variable forensic model predicting earnings manipulation probability.",
        "Calculated on annual filings (10-K) for all companies in annual_features.csv.",
        "Eight Forensic Indices:",
        "  • DSRI (Days Sales in Receivables)",
        "  • GMI (Gross Margin Index)",
        "  • AQI (Asset Quality Index)",
        "  • SGI (Sales Growth Index)",
        "  • DEPI (Depreciation Index)",
        "  • SGAI (Sales & General Admin Expense Index)",
        "  • LVGI (Leverage Index)",
        "  • TATA (Total Accruals to Total Assets)",
        "Threshold: M-Score > -1.78 indicates high probability of accounting manipulation."
    ]
    for pt in pts_b:
        add_para(tf1, pt, font_name=FONT_BODY, font_size=11.5, color=C_TEXT_DARK, space_after=2)

    add_card(s9, Inches(7.00), Inches(1.80), Inches(5.73), Inches(4.80))
    tb2 = s9.shapes.add_textbox(Inches(7.35), Inches(2.05), Inches(5.03), Inches(4.30))
    tf2 = tb2.text_frame; tf2.word_wrap = True; tf2.margin_left = tf2.margin_top = 0
    add_para(tf2, "Quarterly vs. Annual Concordance", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    pts_c = [
        "Post-Hoc Cross-Validation: Quarterly ML/statistical alerts successfully correlate with high annual Beneish M-Scores.",
        "High Concordance in Reference Group:",
        "  • Kraft Heinz (KHC): High M-Scores during FY2017-FY2018 align with quarterly margin collapse alerts.",
        "  • Under Armour (UAA): DSRI and SGI elevated during 2015-2016 channel stuffing quarters.",
        "  • Super Micro (SMCI): High SGI and AQI match quarterly revenue growth spikes.",
        "Key Advantage of Quarterly Pipeline: Flags accounting abnormalities 6 to 9 months before annual 10-K filings are published!"
    ]
    for pt in pts_c:
        add_para(tf2, "• " + pt, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=6)

    # =========================================================================
    # SLIDE 10: Universe Leaderboard & Cohort Discrimination
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_header(s10, "LEADERBOARD & COHORT SPLIT", "Reference Scandal Group Exhibits Higher Anomaly Concentration")
    add_slide_footer(s10, 10)

    # Embedded Figure: top_anomalies_barchart.png
    add_card(s10, Inches(0.60), Inches(1.80), Inches(6.80), Inches(4.80))
    fig3_path = FIG_DIR / "top_anomalies_barchart.png"
    if fig3_path.exists():
        s10.shapes.add_picture(str(fig3_path), Inches(0.75), Inches(2.00), width=Inches(6.50), height=Inches(4.40))

    add_card(s10, Inches(7.70), Inches(1.80), Inches(5.03), Inches(4.80))
    tb = s10.shapes.add_textbox(Inches(8.00), Inches(2.05), Inches(4.43), Inches(4.30))
    tf = tb.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_top = 0
    add_para(tf, "Empirical Validation", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)
    val_pts = [
        "Statistical Discrimination: Reference group companies exhibit higher anomaly rates (5.6% IF flag rate) than Control blue-chips (4.8%).",
        "Concentration of Top Anomalies: Reference companies (KHC, UAA, SMCI, MDXG, PLUG) dominate top 50 ranks.",
        "Control Group Baseline: Healthy blue-chips (Costco, Home Depot, Microsoft, Apple) cluster in the lowest anomaly deciles.",
        "Expected Corporate Events: Genuine spinoffs in control companies (e.g. 3M, JNJ) are cleanly explained by disclosed restructuring, not fraud."
    ]
    for pt in val_pts:
        add_para(tf, "• " + pt, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=7)

    # =========================================================================
    # SLIDE 11: Real-World Case Studies (KHC & UAA)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_header(s11, "FORENSIC CASE STUDIES", "Real-World Accounting Scandals Correctly Identified")
    add_slide_footer(s11, 11)

    # Embedded Figure: case_studies_signals.png
    add_card(s11, Inches(0.60), Inches(1.80), Inches(6.80), Inches(4.80))
    fig4_path = FIG_DIR / "case_studies_signals.png"
    if fig4_path.exists():
        s11.shapes.add_picture(str(fig4_path), Inches(0.75), Inches(2.00), width=Inches(6.50), height=Inches(4.40))

    add_card(s11, Inches(7.70), Inches(1.80), Inches(5.03), Inches(4.80))
    tb = s11.shapes.add_textbox(Inches(8.00), Inches(2.05), Inches(4.43), Inches(4.30))
    tf = tb.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_top = 0
    add_para(tf, "Documented Scandals Detected", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    cases = [
        ("Kraft Heinz (KHC - FY18 Q4)",
         "Procurement fraud & $15.4B goodwill impairment. Operating margin crashed to -205% (RZ = -9.45 sigma). Sloan accruals plunged to -8.32 sigma. Flagged as HIGH ANOMALY."),
        ("Under Armour (UAA - 2015-16)",
         "SEC $438M settlement for channel stuffing ($408M orders pulled forward). Receivables outstripped revenue growth by +7.23 sigma. DSO jumped by +5.43 sigma."),
        ("Super Micro (SMCI - 2022-24)",
         "Premature revenue recognition on incomplete hardware shipments. Extreme revenue growth volatility (+3.15 sigma) paired with massive DSO swings (+5.00 sigma).")
    ]
    for name, desc in cases:
        add_para(tf, name, font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL)
        add_para(tf, desc, font_name=FONT_BODY, font_size=11, bold=False, color=C_TEXT_DARK, space_after=4)

    # =========================================================================
    # SLIDE 12: Automated Pipeline for New Filings & Triage Scorecard
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_header(s12, "OPERATIONAL PIPELINE", "Automated Real-Time Scoring & Forensic Audit Scorecard")
    add_slide_footer(s12, 12)

    stages = [
        ("1. Ingestion", "Ingests new 10-Q/10-K filing JSON, CSV, or live EDGAR API download.", 8),
        ("2. Baseline Construction", "Computes trailing 8Q median/MAD and 12Q rolling means from prior filings.", 9),
        ("3. Multi-Engine Inference", "Applies Isolation Forest, robust Z-scores, and multi-year trend deviations.", 10),
        ("4. Audit Scorecard", "Renders risk tier (HIGH, ELEVATED, NORMAL), red flags, and audit action items.", 11),
    ]

    for idx, (head, desc, icon_i) in enumerate(stages):
        cx = Inches(0.60) + idx * Inches(3.10)
        add_card(s12, cx, Inches(1.80), Inches(2.90), Inches(2.20))
        add_icon_box(s12, cx + Inches(0.25), Inches(2.00), icon_idx=icon_i, size=0.70)
        tb = s12.shapes.add_textbox(cx + Inches(0.25), Inches(2.80), Inches(2.40), Inches(1.10))
        tb.text_frame.word_wrap = True; tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, head, font_name=FONT_HEAD, font_size=14, bold=True, color=C_HEAD_DARK, is_first=True)
        add_para(tb.text_frame, desc, font_name=FONT_BODY, font_size=11, bold=False, color=C_TEXT_DARK)

    # Triage Scorecard Banner below
    add_card(s12, Inches(0.60), Inches(4.25), Inches(12.13), Inches(2.45))
    tb_b = s12.shapes.add_textbox(Inches(0.95), Inches(4.45), Inches(11.40), Inches(2.10))
    tf_b = tb_b.text_frame; tf_b.word_wrap = True; tf_b.margin_left = tf_b.margin_top = 0
    add_para(tf_b, "Operational Forensic Triage Protocol", font_name=FONT_HEAD, font_size=18, bold=True, color=C_HEAD_DARK, is_first=True)

    triage_tiers = [
        ("HIGH ANOMALY (Multi-Method Consensus)", "Isolation Forest + Robust Z-Score or Multi-Year Trend break trigger simultaneously. Immediate human audit prioritized (inspect accounts receivable aging, goodwill write-downs, contract terms)."),
        ("ELEVATED (Single-Method Alert)", "One engine triggers an alert. Secondary forensic review recommended (inspect custom tag mapping, discontinued operations, or acquisition recasts)."),
        ("NORMAL (Within Expected Tolerances)", "All financial ratios within historical statistical boundaries. Cleared for automated continuous monitoring.")
    ]
    for tier, exp in triage_tiers:
        add_para(tf_b, "• " + tier + ":", font_name=FONT_BODY, font_size=12, bold=True, color=C_TEAL)
        add_para(tf_b, "   " + exp, font_name=FONT_BODY, font_size=11, bold=False, color=C_TEXT_DARK, space_after=3)

    # =========================================================================
    # SLIDE 13: Live Demonstration Suite (Streamlit & CLI)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_slide_header(s13, "LIVE DEMONSTRATION", "Interactive Web Application & Terminal Evaluation Console")
    add_slide_footer(s13, 13)

    add_card(s13, Inches(0.60), Inches(1.80), Inches(5.90), Inches(4.80))
    add_icon_box(s13, Inches(1.00), Inches(2.10), icon_idx=12)
    tb = s13.shapes.add_textbox(Inches(1.00), Inches(3.10), Inches(5.10), Inches(3.30))
    tf = tb.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_top = 0
    add_para(tf, "Streamlit Web Dashboard (app.py)", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)
    app_pts = [
        "1-Click Windows Launcher: run_dashboard.bat starts local dashboard on http://localhost:8501.",
        "Interactive Plotly Timelines: Zoomable multi-year financial charts with red anomaly marker overlays.",
        "Live Ingestion Simulator: Select incoming filings (KHC, UAA, SMCI, MSFT) and generate real-time audit scorecards with one click.",
        "Case Study Walkthroughs: Visual deep-dives into historical accounting scandals.",
        "Top 100 Searchable Leaderboard: Filterable universe ranking.",
        "Runs 100% Offline: Zero internet required during examination."
    ]
    for pt in app_pts:
        add_para(tf, "• " + pt, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=5)

    add_card(s13, Inches(6.80), Inches(1.80), Inches(5.93), Inches(4.80))
    add_icon_box(s13, Inches(7.20), Inches(2.10), icon_idx=13)
    tb2 = s13.shapes.add_textbox(Inches(7.20), Inches(3.10), Inches(5.13), Inches(3.30))
    tf2 = tb2.text_frame; tf2.word_wrap = True; tf2.margin_left = tf2.margin_top = 0
    add_para(tf2, "Terminal CLI Console (live_demo.py)", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)
    cli_pts = [
        "Evaluation Console: python live_demo.py provides interactive ASCII terminal menus for viva defense.",
        "Instant Company Profiler: Query any company ticker (26 tickers) to view full 10-year quarterly flags.",
        "Batch Pipeline Trigger: Run end-to-end retraining and artifact export on the fly.",
        "Automated Test Suite: tests/test_anomaly_pipeline.py passes 6 unit and integration test suites.",
        "CLI Scorer: python run_pipeline.py --ticker SMCI executes headless audit triage in under 2 seconds."
    ]
    for pt in cli_pts:
        add_para(tf2, "• " + pt, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=5)

    # =========================================================================
    # SLIDE 14: Methodological Limitations & Honest Disclosures
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_slide_header(s14, "LIMITATIONS", "Known Forensic Gaps and Methodological Disclosures")
    add_slide_footer(s14, 14)

    limitations = [
        ("Anomaly ≠ Proof of Fraud", "Statistical and ML outliers flag filings for prioritized human review; genuine business disruptions also cause extreme deviations.", 14),
        ("US-GAAP & USD Only", "Foreign filers reporting under IFRS on Form 20-F are not ingested by the SEC EDGAR facts API.", 15),
        ("Derived Q4 Volatility", "Derived Q4 figures absorb year-end audit adjustments, naturally exhibiting higher baseline volatility.", 16),
        ("Corporate Restructuring Breaks", "Major mergers and spin-offs (e.g. 3M, JNJ) create structural jumps that require manual audit verification.", 17),
        ("Custom XBRL Tags", "Company-specific non-standard extension tags are excluded; covered in coverage_report.csv.", 18),
        ("Weak Evaluation Labels", "Reference group labels reflect historical SEC enforcement actions, not transaction-level fraud ground truth.", 19),
    ]

    for idx, (title, desc, icon_i) in enumerate(limitations):
        cx = Inches(0.60) + (idx % 3) * Inches(4.15)
        cy = Inches(1.80) + (idx // 3) * Inches(2.45)
        add_card(s14, cx, cy, Inches(3.85), Inches(2.25))
        add_icon_box(s14, cx + Inches(0.25), cy + Inches(0.20), icon_idx=icon_i, size=0.65)
        tb = s14.shapes.add_textbox(cx + Inches(0.25), cy + Inches(0.95), Inches(3.35), Inches(1.20))
        tb.text_frame.word_wrap = True; tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, title, font_name=FONT_HEAD, font_size=15, bold=True, color=C_HEAD_DARK, is_first=True)
        add_para(tb.text_frame, desc, font_name=FONT_BODY, font_size=11, bold=False, color=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 15: Full & Final Deliverables Matrix
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_slide_header(s15, "DELIVERABLES CHECKLIST", "Complete Project Handover & Verification Matrix")
    add_slide_footer(s15, 15)

    add_card(s15, Inches(0.60), Inches(1.80), Inches(12.13), Inches(4.85))
    tb = s15.shapes.add_textbox(Inches(0.90), Inches(2.00), Inches(11.50), Inches(4.50))
    tf = tb.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_top = 0

    deliv_items = [
        ("Deliverable 1: Secondary Dataset (CSV)", "data/processed/quarterly_features.csv (1,334 company-quarters, 94 features) & annual_features.csv with Beneish M-scores."),
        ("Deliverable 1: Extraction Notebook", "01_edgar_data_extraction.ipynb (reproducible point-in-time XBRL extraction from SEC EDGAR API)."),
        ("Deliverable 1: Documentation & Lineage", "data_dictionary.csv (94 feature definitions) & SEC_Anomaly_Detection_Deliverable1.pptx."),
        ("Deliverable 2: ML & Analytics Notebook", "02_ml_anomaly_detection.ipynb (fully executed with Isolation Forest, Z-scores, multi-year trends, and plots)."),
        ("Deliverable 2: Automated Scoring Pipeline", "run_pipeline.py & src/anomaly_pipeline.py (batch & single-filing real-time scoring engine)."),
        ("Deliverable 2: Live Demonstration Dashboard", "app.py & run_dashboard.bat (interactive Streamlit web dashboard for live laptop viva evaluation)."),
        ("Deliverable 2: Documentation & Methodology", "docs/DELIVERABLE2.md & comprehensive root README.md."),
        ("Deliverable 2: Presentation Deck", "SEC_Anomaly_Detection_Deliverable2.pptx (15 widescreen slides perfectly styled to Deliverable 1)."),
        ("Deliverable 2: Automated Test Suite", "tests/test_anomaly_pipeline.py (6 unit/integration suites verifying all pipeline functions).")
    ]

    for i, (title, desc) in enumerate(deliv_items):
        p1 = add_para(tf, "✓  " + title + ": ", font_name=FONT_BODY, font_size=12, bold=True, color=C_TEAL, is_first=(i==0))
        r = p1.add_run()
        r.text = desc
        r.font.name = FONT_BODY; r.font.size = Pt(11.5); r.font.bold = False; r.font.color.rgb = C_TEXT_DARK
        p1.space_after = Pt(4)

    # Save presentation
    output_path = ROOT / "SEC_Anomaly_Detection_Deliverable2.pptx"
    prs.save(str(output_path))
    print(f"Successfully saved {output_path}")

    # Synchronize into sec_filing_anomaly_deliverable2
    sub_path = ROOT / "sec_filing_anomaly_deliverable2" / "SEC_Anomaly_Detection_Deliverable2.pptx"
    if sub_path.parent.exists():
        prs.save(str(sub_path))
        print(f"Synchronized to {sub_path}")

if __name__ == "__main__":
    build_presentation()
