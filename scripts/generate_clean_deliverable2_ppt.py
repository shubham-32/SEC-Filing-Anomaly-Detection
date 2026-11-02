"""Generate Deliverable 2 PowerPoint presentation following user instructions:
- Clean, concise, low text density (no heavy technical jargon)
- Covers all 6 required sections:
  1. Title, introduction, objectives
  2. Key features
  3. Technologies, tools, frameworks
  4. Details of all deliverables implemented & achieved
  5. Relevant visualisations & results (embedding the 4 figures)
  6. Final outcomes and conclusions
- Perfectly adopts Deliverable 1 design style & theme:
  - Palette: #13232B (dark slate), #E3A03A (amber gold), #2E6F6A (teal), #F1F4F4 (cards), #1C2A30 (text)
  - Fonts: Cambria (headings & titles), Calibri (body & kickers)
  - 16:9 widescreen layout with consistent headers, footers & icon boxes
"""
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "docs" / "figures"
ICON_DIR = ROOT / "ppt_icons"

# Deliverable 1 Color Palette
C_DARK_BG   = RGBColor(19, 35, 43)    # #13232B Dark Slate
C_AMBER     = RGBColor(227, 160, 58)  # #E3A03A Warm Gold / Accent
C_TEAL      = RGBColor(46, 111, 106)  # #2E6F6A Category Kicker / Tracker
C_CARD_BG   = RGBColor(241, 244, 244) # #F1F4F4 Card Fill
C_TEXT_DARK = RGBColor(28, 42, 48)    # #1C2A30 Body Text
C_HEAD_DARK = RGBColor(19, 35, 43)    # #13232B Headings
C_MUTED     = RGBColor(94, 110, 117)  # #5E6E75 Secondary Text / Footers
C_LIGHT_SUB = RGBColor(201, 211, 214) # #C9D3D6 Title Subtitle
C_WHITE     = RGBColor(255, 255, 255)

FONT_HEAD = "Cambria"
FONT_BODY = "Calibri"

def add_para(tf, text, font_name=FONT_BODY, font_size=12, bold=False, color=C_TEXT_DARK, space_after=0, is_first=False, align=PP_ALIGN.LEFT):
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
    # Kicker
    tb_k = slide.shapes.add_textbox(Inches(0.60), Inches(0.42), Inches(10.0), Inches(0.30))
    tf_k = tb_k.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_top = tf_k.margin_right = tf_k.margin_bottom = 0
    add_para(tf_k, kicker_text.upper(), font_name=FONT_BODY, font_size=12, bold=True, color=C_TEAL, is_first=True)

    # Title
    tb_t = slide.shapes.add_textbox(Inches(0.60), Inches(0.72), Inches(12.13), Inches(0.75))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    add_para(tf_t, title_text, font_name=FONT_HEAD, font_size=32, bold=True, color=C_HEAD_DARK, is_first=True)

def add_slide_footer(slide, slide_num):
    tb_l = slide.shapes.add_textbox(Inches(0.60), Inches(7.00), Inches(8.00), Inches(0.25))
    tf_l = tb_l.text_frame
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
    add_para(tf_l, "SEC Filing Anomaly Detection  ·  Deliverable 2: Final Project Presentation",
             font_name=FONT_BODY, font_size=10, bold=False, color=C_MUTED, is_first=True)

    tb_r = slide.shapes.add_textbox(Inches(12.23), Inches(7.00), Inches(0.50), Inches(0.25))
    tf_r = tb_r.text_frame
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
    add_para(tf_r, str(slide_num), font_name=FONT_BODY, font_size=10, bold=False, color=C_MUTED, is_first=True, align=PP_ALIGN.RIGHT)

def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BG):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

def add_icon_box(slide, left, top, icon_idx=None, bg_color=C_AMBER, size=0.85):
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
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_DARK_BG
    bg1.line.fill.background()

    add_icon_box(s1, Inches(0.60), Inches(0.90), icon_idx=1, bg_color=C_AMBER, size=0.90)

    tb1 = s1.shapes.add_textbox(Inches(0.60), Inches(2.20), Inches(10.00), Inches(0.35))
    tf1 = tb1.text_frame
    tf1.margin_left = tf1.margin_top = 0
    add_para(tf1, "TASK ID FDA-2  ·  BIG DATA ANALYTICS  ·  DELIVERABLE 2", font_name=FONT_BODY, font_size=14, bold=True, color=C_AMBER, is_first=True)

    tb2 = s1.shapes.add_textbox(Inches(0.60), Inches(2.65), Inches(11.50), Inches(1.90))
    tf2 = tb2.text_frame
    tf2.margin_left = tf2.margin_top = 0
    add_para(tf2, "Financial Anomaly Detection", font_name=FONT_HEAD, font_size=46, bold=True, color=C_WHITE, is_first=True)
    add_para(tf2, "in SEC Filings", font_name=FONT_HEAD, font_size=46, bold=True, color=C_WHITE)

    tb3 = s1.shapes.add_textbox(Inches(0.60), Inches(4.70), Inches(11.00), Inches(0.90))
    tf3 = tb3.text_frame; tf3.word_wrap = True
    tf3.margin_left = tf3.margin_top = 0
    add_para(tf3, "An Automated Big Data System for Early Detection of Accounting Irregularities, Multi-Year Trend Breaks, and Live Forensic Triage",
             font_name=FONT_BODY, font_size=18, bold=False, color=C_LIGHT_SUB, is_first=True)

    tb4 = s1.shapes.add_textbox(Inches(0.60), Inches(6.30), Inches(11.50), Inches(0.35))
    tf4 = tb4.text_frame
    tf4.margin_left = tf4.margin_top = 0
    add_para(tf4, "12 Fiscal Years  ·  26 Companies  ·  1,334 Quarters  ·  Machine Learning & Automated Live Pipeline",
             font_name=FONT_BODY, font_size=14, bold=False, color=C_AMBER, is_first=True)

    # =========================================================================
    # SLIDE 2: Project Introduction & Problem Motivation (Section 1)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(s2, "PROJECT INTRODUCTION", "Catching Accounting Anomalies Before They Surface as Scandals")
    add_slide_footer(s2, 2)

    card_w = Inches(3.85)
    card_h = Inches(4.70)
    card_y = Inches(1.75)

    # Card 1: Problem
    add_card(s2, Inches(0.60), card_y, card_w, card_h)
    add_icon_box(s2, Inches(0.95), Inches(2.05), icon_idx=2)
    tb = s2.shapes.add_textbox(Inches(0.95), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "The Forensic Problem", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s2.shapes.add_textbox(Inches(0.95), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    add_para(tf, "• Massive Financial Impact:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=True)
    add_para(tf, "Financial reporting fraud costs investors and markets billions each year.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)
    add_para(tf, "• Delayed Detection:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL)
    add_para(tf, "Accounting manipulation often takes 2 to 3 years to surface as restatements or SEC enforcement.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)
    add_para(tf, "• Early Warning Need:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL)
    add_para(tf, "Organizations need proactive automated flags to identify risks when filings are submitted.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK)

    # Card 2: Big Data Challenge
    add_card(s2, Inches(4.75), card_y, card_w, card_h)
    add_icon_box(s2, Inches(5.10), Inches(2.05), icon_idx=3)
    tb = s2.shapes.add_textbox(Inches(5.10), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "The Big Data Challenge", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s2.shapes.add_textbox(Inches(5.10), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    add_para(tf, "• High Data Volume:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=True)
    add_para(tf, "Over 100,000 raw XBRL facts across public 10-K and 10-Q corporate filings.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)
    add_para(tf, "• Missing Q4 Figures:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL)
    add_para(tf, "The SEC does not file standalone Q4 statements; they must be mathematically derived from annual totals.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)
    add_para(tf, "• Complex Tagging:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL)
    add_para(tf, "Accounting tag shifts (e.g. ASC 606) create artificial breaks if not standardized.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK)

    # Card 3: Solution
    add_card(s2, Inches(8.90), card_y, card_w, card_h)
    add_icon_box(s2, Inches(9.25), Inches(2.05), icon_idx=4)
    tb = s2.shapes.add_textbox(Inches(9.25), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Our Automated System", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s2.shapes.add_textbox(Inches(9.25), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    add_para(tf, "• Point-in-Time Integrity:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=True)
    add_para(tf, "Evaluates numbers as first filed to avoid look-ahead bias and restatement distortion.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)
    add_para(tf, "• Multi-Method Detection:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL)
    add_para(tf, "Combines Isolation Forest ML, trailing Z-scores, and 3-year rolling trends.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)
    add_para(tf, "• Instant Risk Triage:", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL)
    add_para(tf, "Delivers actionable forensic scorecards for incoming filings in under 2 seconds.", font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 3: Objectives Alignment (Section 1)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(s3, "PROJECT OBJECTIVES", "Clear Alignment with Task FDA-2 Requirements")
    add_slide_footer(s3, 3)

    obj_w = Inches(5.80)
    obj_h = Inches(2.20)
    xs = [Inches(0.60), Inches(6.80)]
    ys = [Inches(1.80), Inches(4.35)]

    objs = [
        ("1. Automated Data Extraction", "Ingest 12+ years of financial data from SEC EDGAR APIs across 26 companies, standardizing revenue tags and deriving discrete quarters.", 5),
        ("2. Statistical Anomaly Detection", "Apply trailing robust Z-scores using rolling median and MAD over prior quarters to catch sudden quarterly financial shocks without look-ahead bias.", 6),
        ("3. Multi-Year Trend Analysis", "Track 12-quarter (3-year) trailing rolling baselines to detect sudden structural breaks, margin collapse, and inconsistent revenue growth.", 7),
        ("4. Automated Real-Time Pipeline", "Engineer an end-to-end scoring pipeline and interactive UI that accepts new corporate filings and outputs an immediate audit scorecard.", 8),
    ]

    for idx, (head, desc, icon_i) in enumerate(objs):
        cx = xs[idx % 2]
        cy = ys[idx // 2]
        add_card(s3, cx, cy, obj_w, obj_h)
        add_icon_box(s3, cx + Inches(0.30), cy + Inches(0.30), icon_idx=icon_i, size=0.75)

        tb = s3.shapes.add_textbox(cx + Inches(1.25), cy + Inches(0.25), obj_w - Inches(1.50), Inches(0.40))
        tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, head, font_name=FONT_HEAD, font_size=18, bold=True, color=C_HEAD_DARK, is_first=True)

        tb_b = s3.shapes.add_textbox(cx + Inches(1.25), cy + Inches(0.70), obj_w - Inches(1.50), Inches(1.30))
        tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
        add_para(tb_b.text_frame, desc, font_name=FONT_BODY, font_size=13, color=C_TEXT_DARK, is_first=True)

    # =========================================================================
    # SLIDE 4: Key Features of the System (Section 2)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(s4, "KEY FEATURES", "Core Capabilities Built into the Detection Platform")
    add_slide_footer(s4, 4)

    feat_w = Inches(3.85)
    feat_h = Inches(2.20)
    fxs = [Inches(0.60), Inches(4.75), Inches(8.90)]
    fys = [Inches(1.80), Inches(4.35)]

    feats = [
        ("Point-in-Time Data", "Preserves figures exactly as first published. Eliminates look-ahead bias and spinoff restatement noise.", 9),
        ("Multi-Year Rolling Baselines", "Trailing 3-year rolling window flags long-term structural drift and revenue/expense divergence.", 10),
        ("Dual-Model Detection", "Combines statistical Z-scores for single-quarter spikes with Isolation Forest for complex multidimensional anomalies.", 11),
        ("Empirical Fraud Sensitivity", "Directly flags known SEC scandals: procurement fraud, channel stuffing, and premature revenue recognition.", 12),
        ("Actionable Audit Scorecards", "Translates model output into clear risk categories: HIGH ANOMALY, ELEVATED, or NORMAL, with auditor action items.", 13),
        ("Interactive Web UI", "Streamlit dashboard with Plotly timelines and live new-filing simulation for live project evaluations.", 14),
    ]

    for idx, (head, desc, icon_i) in enumerate(feats):
        cx = fxs[idx % 3]
        cy = fys[idx // 3]
        add_card(s4, cx, cy, feat_w, feat_h)
        add_icon_box(s4, cx + Inches(0.25), cy + Inches(0.25), icon_idx=icon_i, size=0.65)

        tb = s4.shapes.add_textbox(cx + Inches(1.05), cy + Inches(0.20), feat_w - Inches(1.20), Inches(0.40))
        tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, head, font_name=FONT_HEAD, font_size=16, bold=True, color=C_HEAD_DARK, is_first=True)

        tb_b = s4.shapes.add_textbox(cx + Inches(1.05), cy + Inches(0.65), feat_w - Inches(1.20), Inches(1.40))
        tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
        add_para(tb_b.text_frame, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, is_first=True)

    # =========================================================================
    # SLIDE 5: Technologies, Tools & Frameworks (Section 3)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(s5, "TECHNOLOGY STACK", "Modern, Production-Ready Open Source Tooling")
    add_slide_footer(s5, 5)

    tech_w = Inches(2.80)
    tech_h = Inches(4.70)
    txs = [Inches(0.60), Inches(3.70), Inches(6.80), Inches(9.90)]

    techs = [
        ("Data Extraction", 15, [
            ("SEC EDGAR APIs", "Automated raw XBRL fact downloads"),
            ("Requests & JSON", "Rate-limited API requests (<10 req/s)"),
            ("Local Caching", "Enables fast, 100% offline re-runs"),
            ("US-GAAP Taxonomy", "Resolves accounting tag changes")
        ]),
        ("Analytics & Stats", 16, [
            ("Pandas & NumPy", "Point-in-time dataset manipulation"),
            ("SciPy Stats", "Median Absolute Deviation (MAD)"),
            ("Statsmodels", "Rolling baseline computations"),
            ("Ratio Engine", "42 financial & earnings ratios")
        ]),
        ("Machine Learning", 17, [
            ("Scikit-Learn", "300-tree Isolation Forest model"),
            ("RobustScaler", "Protects against extreme outliers"),
            ("SimpleImputer", "Median handling of missing ratios"),
            ("Joblib", "Persistent model serialization")
        ]),
        ("UI & Deployment", 18, [
            ("Streamlit", "Interactive live web dashboard"),
            ("Plotly Express", "Interactive zooming & tooltips"),
            ("Pytest", "Automated unit & integration suites"),
            ("Python-pptx", "Automated executive reporting")
        ]),
    ]

    for idx, (category, icon_i, items) in enumerate(techs):
        cx = txs[idx]
        add_card(s5, cx, Inches(1.75), tech_w, tech_h)
        add_icon_box(s5, cx + Inches(0.25), Inches(2.05), icon_idx=icon_i, size=0.70)

        tb = s5.shapes.add_textbox(cx + Inches(0.25), Inches(2.95), tech_w - Inches(0.50), Inches(0.40))
        tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, category, font_name=FONT_HEAD, font_size=18, bold=True, color=C_HEAD_DARK, is_first=True)

        tb_b = s5.shapes.add_textbox(cx + Inches(0.25), Inches(3.45), tech_w - Inches(0.50), Inches(2.80))
        tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
        tf = tb_b.text_frame
        for i, (tool, desc) in enumerate(items):
            add_para(tf, f"• {tool}:", font_name=FONT_BODY, font_size=12, bold=True, color=C_TEAL, is_first=(i==0))
            add_para(tf, f"  {desc}", font_name=FONT_BODY, font_size=11, color=C_TEXT_DARK, space_after=6)

    # =========================================================================
    # SLIDE 6: Deliverable 1 Implemented & Achieved (Section 4)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_header(s6, "DELIVERABLE 1 DETAILS", "Data Extraction, XBRL Standardization & Secondary Dataset")
    add_slide_footer(s6, 6)

    d1_w = Inches(3.85)
    d1_h = Inches(4.70)

    # Card 1: Data Universe
    add_card(s6, Inches(0.60), Inches(1.75), d1_w, d1_h)
    add_icon_box(s6, Inches(0.95), Inches(2.05), icon_idx=19)
    tb = s6.shapes.add_textbox(Inches(0.95), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Data Scope & Scope", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s6.shapes.add_textbox(Inches(0.95), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    d1_scope = [
        ("12 Fiscal Years:", "Extracted filings from FY2014 through FY2026."),
        ("26 Public Companies:", "20 Control blue-chips + 6 Reference scandal firms."),
        ("1,334 Company-Quarters:", "Extensive longitudinal coverage per company."),
        ("106,153 Raw Facts:", "Ingested and standardized from SEC EDGAR.")
    ]
    for i, (head, desc) in enumerate(d1_scope):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=6)

    # Card 2: Technical Highlights
    add_card(s6, Inches(4.75), Inches(1.75), d1_w, d1_h)
    add_icon_box(s6, Inches(5.10), Inches(2.05), icon_idx=20)
    tb = s6.shapes.add_textbox(Inches(5.10), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Engineering Solutions", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s6.shapes.add_textbox(Inches(5.10), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    d1_sol = [
        ("Q4 Derivation Engine:", "Derived discrete Q4 and cash flows from YTD statements."),
        ("Point-in-Time Principle:", "Saved as-first-reported to eliminate look-ahead bias."),
        ("Accounting Standardization:", "Resolved tag transitions (ASC 606 revenue standards)."),
        ("93.4% Reconciliation:", "Quarters successfully reconcile to reported annual totals.")
    ]
    for i, (head, desc) in enumerate(d1_sol):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=6)

    # Card 3: Artifacts
    add_card(s6, Inches(8.90), Inches(1.75), d1_w, d1_h)
    add_icon_box(s6, Inches(9.25), Inches(2.05), icon_idx=21)
    tb = s6.shapes.add_textbox(Inches(9.25), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Delivered Artifacts", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s6.shapes.add_textbox(Inches(9.25), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    d1_art = [
        ("quarterly_features.csv:", "Main secondary dataset (94 columns per quarter)."),
        ("01_edgar_data_extraction.ipynb:", "Fully executed, reproducible extraction notebook."),
        ("data_dictionary.csv:", "Full lineage and definitions for all 94 features."),
        ("facts_long.csv:", "Audit trail of 47,514 deduplicated XBRL facts.")
    ]
    for i, (head, desc) in enumerate(d1_art):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=6)

    # =========================================================================
    # SLIDE 7: Deliverable 2 Implemented & Achieved (Section 4)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_header(s7, "DELIVERABLE 2 DETAILS", "Machine Learning, Multi-Year Trends & Automated Pipeline")
    add_slide_footer(s7, 7)

    d2_w = Inches(3.85)
    d2_h = Inches(4.70)

    # Card 1: Models
    add_card(s7, Inches(0.60), Inches(1.75), d2_w, d2_h)
    add_icon_box(s7, Inches(0.95), Inches(2.05), icon_idx=6)
    tb = s7.shapes.add_textbox(Inches(0.95), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Detection Models", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s7.shapes.add_textbox(Inches(0.95), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    d2_models = [
        ("Isolation Forest ML:", "300 trees trained on 42 financial ratios; flags top 5% multidimensional anomalies."),
        ("Robust Z-Scores:", "Rolling Median & MAD over prior 8 quarters captures sudden quarterly shocks."),
        ("Beneish M-Score Benchmark:", "Post-hoc validation against classic 8-variable manipulation formula.")
    ]
    for i, (head, desc) in enumerate(d2_models):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=6)

    # Card 2: Trends
    add_card(s7, Inches(4.75), Inches(1.75), d2_w, d2_h)
    add_icon_box(s7, Inches(5.10), Inches(2.05), icon_idx=7)
    tb = s7.shapes.add_textbox(Inches(5.10), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Multi-Year Trends", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s7.shapes.add_textbox(Inches(5.10), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    d2_trends = [
        ("12-Quarter Rolling Window:", "Trailing 3-year baseline tracks organic company growth."),
        ("Sudden Deviation Flags:", "Flags quarters deviating by >= 2.5 sigma from multi-year norms."),
        ("Inconsistent Trend Flags:", "Catches revenue growth accelerating while margins collapse.")
    ]
    for i, (head, desc) in enumerate(d2_trends):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=6)

    # Card 3: Pipeline & UI
    add_card(s7, Inches(8.90), Inches(1.75), d2_w, d2_h)
    add_icon_box(s7, Inches(9.25), Inches(2.05), icon_idx=13)
    tb = s7.shapes.add_textbox(Inches(9.25), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Pipeline & Live Tools", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s7.shapes.add_textbox(Inches(9.25), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    d2_pipeline = [
        ("Automated Pipeline CLI:", "run_pipeline.py scores any new filing in under 2 seconds."),
        ("Interactive Web Dashboard:", "app.py provides Plotly visualizations and live scoring console."),
        ("02_ml_anomaly_detection.ipynb:", "Fully executed notebook with all statistical figures and tables.")
    ]
    for i, (head, desc) in enumerate(d2_pipeline):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=6)

    # =========================================================================
    # SLIDE 8: Visualisation 1 — Multi-Year Financial Trends (Section 5)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_header(s8, "VISUALISATIONS & RESULTS", "Multi-Year Trajectories Expose Structural Trend Breaks")
    add_slide_footer(s8, 8)

    # Embedded Image
    fig_w = Inches(6.80)
    fig_h = Inches(4.70)
    add_card(s8, Inches(0.60), Inches(1.75), fig_w, fig_h)
    fig_path = FIG_DIR / "multi_year_trends.png"
    if fig_path.exists():
        s8.shapes.add_picture(str(fig_path), Inches(0.75), Inches(1.90), width=Inches(6.50), height=Inches(4.40))

    # Takeaways on Right
    card_r_w = Inches(5.03)
    add_card(s8, Inches(7.70), Inches(1.75), card_r_w, fig_h)
    tb = s8.shapes.add_textbox(Inches(8.00), Inches(2.05), card_r_w - Inches(0.60), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Key Visual Insights", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s8.shapes.add_textbox(Inches(8.00), Inches(2.55), card_r_w - Inches(0.60), Inches(3.60))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    pts_v1 = [
        ("Long-Term Context:", "Evaluates 10+ years of corporate performance to separate regular seasonality from genuine accounting distress."),
        ("Structural Break Detection:", "Red diamond markers indicate quarters exceeding 2.5 sigma deviation from trailing 3-year baselines."),
        ("Clear Contrast:", "Healthy blue-chips (e.g. Microsoft) maintain stable margins, while scandal companies (e.g. Kraft Heinz) exhibit sudden collapses.")
    ]
    for i, (head, desc) in enumerate(pts_v1):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)

    # =========================================================================
    # SLIDE 9: Visualisation 2 — Score Distribution & Cohort Separation (Section 5)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_header(s9, "VISUALISATIONS & RESULTS", "Isolation Forest Effectively Discriminates Scandal Firms")
    add_slide_footer(s9, 9)

    add_card(s9, Inches(0.60), Inches(1.75), fig_w, fig_h)
    fig_path = FIG_DIR / "score_distribution.png"
    if fig_path.exists():
        s9.shapes.add_picture(str(fig_path), Inches(0.75), Inches(2.10), width=Inches(6.50), height=Inches(4.00))

    add_card(s9, Inches(7.70), Inches(1.75), card_r_w, fig_h)
    tb = s9.shapes.add_textbox(Inches(8.00), Inches(2.05), card_r_w - Inches(0.60), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Model Discrimination", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s9.shapes.add_textbox(Inches(8.00), Inches(2.55), card_r_w - Inches(0.60), Inches(3.60))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    pts_v2 = [
        ("Separation of Cohorts:", "Reference group (companies with SEC actions) exhibits a prominent tail toward extreme anomaly scores."),
        ("5.0% Calibration:", "Isolation Forest flags the 62 most isolated multidimensional quarters in the entire universe."),
        ("Multi-Variable Synthesis:", "Uncovers subtle fraud signatures that single ratios miss by evaluating 42 balance sheet and income metrics simultaneously.")
    ]
    for i, (head, desc) in enumerate(pts_v2):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)

    # =========================================================================
    # SLIDE 10: Visualisation 3 — Top Anomalies Leaderboard (Section 5)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_header(s10, "VISUALISATIONS & RESULTS", "Universe Leaderboard Prioritizes High-Risk Quarters")
    add_slide_footer(s10, 10)

    add_card(s10, Inches(0.60), Inches(1.75), fig_w, fig_h)
    fig_path = FIG_DIR / "top_anomalies_barchart.png"
    if fig_path.exists():
        s10.shapes.add_picture(str(fig_path), Inches(0.75), Inches(1.95), width=Inches(6.50), height=Inches(4.30))

    add_card(s10, Inches(7.70), Inches(1.75), card_r_w, fig_h)
    tb = s10.shapes.add_textbox(Inches(8.00), Inches(2.05), card_r_w - Inches(0.60), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Auditor Prioritization", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s10.shapes.add_textbox(Inches(8.00), Inches(2.55), card_r_w - Inches(0.60), Inches(3.60))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    pts_v3 = [
        ("Ranked Triage Queue:", "Outputs an objective ranking of the top 100 most abnormal company-quarters across all 12 years."),
        ("Scandal Concentration:", "Documented fraud firms (Kraft Heinz, Under Armour, Super Micro, MiMedx) occupy the highest positions."),
        ("Control Firm Protection:", "Healthy control blue-chips consistently score in the safe, low-risk deciles.")
    ]
    for i, (head, desc) in enumerate(pts_v3):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)

    # =========================================================================
    # SLIDE 11: Visualisation 4 — Real-World Fraud Case Studies (Section 5)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_header(s11, "VISUALISATIONS & RESULTS", "Empirical Proof: Detecting Documented SEC Accounting Scandals")
    add_slide_footer(s11, 11)

    add_card(s11, Inches(0.60), Inches(1.75), fig_w, fig_h)
    fig_path = FIG_DIR / "case_studies_signals.png"
    if fig_path.exists():
        s11.shapes.add_picture(str(fig_path), Inches(0.75), Inches(2.20), width=Inches(6.50), height=Inches(3.80))

    add_card(s11, Inches(7.70), Inches(1.75), card_r_w, fig_h)
    tb = s11.shapes.add_textbox(Inches(8.00), Inches(2.05), card_r_w - Inches(0.60), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Documented Scandals Flagged", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s11.shapes.add_textbox(Inches(8.00), Inches(2.55), card_r_w - Inches(0.60), Inches(3.60))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    pts_v4 = [
        ("Kraft Heinz Procurement Fraud:", "Operating margin crashed to -205% (Robust Z = -9.45 sigma) alongside a $15.4B write-down. Model flagged as HIGH ANOMALY."),
        ("Under Armour Channel Stuffing:", "Receivables growth exceeded sales growth by +7.23 sigma during its $408M order pull-forward scheme. Model triggered immediate alert."),
        ("Super Micro Revenue Timing:", "Extreme revenue acceleration (+3.15 sigma) and DSO swings (+5.00 sigma) flagged prior to auditor resignation.")
    ]
    for i, (head, desc) in enumerate(pts_v4):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=6)

    # =========================================================================
    # SLIDE 12: Automated Pipeline & Interactive UI (Section 5)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_header(s12, "OPERATIONAL DEMONSTRATION", "Automated Real-Time Scoring & Interactive Web Dashboard")
    add_slide_footer(s12, 12)

    # 4 Architecture Steps across top
    pipe_w = Inches(2.80)
    pipe_h = Inches(2.20)
    pxs = [Inches(0.60), Inches(3.70), Inches(6.80), Inches(9.90)]

    steps = [
        ("1. Ingestion", "Accepts new filing JSON/CSV or ticker symbol.", 8),
        ("2. Baseline", "Computes trailing 8Q and 12Q history on the fly.", 9),
        ("3. Scoring", "Evaluates Isolation Forest & Z-scores in <2 seconds.", 10),
        ("4. Scorecard", "Renders risk tier & audit recommendations.", 11),
    ]

    for idx, (head, desc, icon_i) in enumerate(steps):
        cx = pxs[idx]
        add_card(s12, cx, Inches(1.75), pipe_w, pipe_h)
        add_icon_box(s12, cx + Inches(0.20), Inches(1.95), icon_idx=icon_i, size=0.65)
        tb = s12.shapes.add_textbox(cx + Inches(0.20), Inches(2.70), pipe_w - Inches(0.40), Inches(1.15))
        tb.text_frame.word_wrap = True; tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, head, font_name=FONT_HEAD, font_size=15, bold=True, color=C_HEAD_DARK, is_first=True)
        add_para(tb.text_frame, desc, font_name=FONT_BODY, font_size=11.5, color=C_TEXT_DARK)

    # Bottom Banner: Live Evaluation Tools
    add_card(s12, Inches(0.60), Inches(4.25), Inches(12.13), Inches(2.45))
    tb_bot = s12.shapes.add_textbox(Inches(0.95), Inches(4.45), Inches(11.40), Inches(2.10))
    tf_b = tb_bot.text_frame; tf_b.word_wrap = True; tf_b.margin_left = tf_b.margin_top = 0
    add_para(tf_b, "Live Demonstration Tools for Laptop Evaluation", font_name=FONT_HEAD, font_size=18, bold=True, color=C_HEAD_DARK, is_first=True)

    demo_features = [
        ("Interactive Streamlit App (app.py):", "Run via `streamlit run app.py` or double-click `run_dashboard.bat`. Provides Plotly financial timelines, anomaly markers, and instant live filing simulations."),
        ("Forensic Risk Triage Tiers:", "Categorizes filings into HIGH ANOMALY (priority audit), ELEVATED (secondary review), or NORMAL (cleared for automated monitoring)."),
        ("Terminal CLI Engine (live_demo.py):", "Interactive ASCII menu console for offline testing and fast company lookups.")
    ]
    for head, desc in demo_features:
        add_para(tf_b, f"• {head}", font_name=FONT_BODY, font_size=12, bold=True, color=C_TEAL)
        add_para(tf_b, f"  {desc}", font_name=FONT_BODY, font_size=11.5, color=C_TEXT_DARK, space_after=3)

    # =========================================================================
    # SLIDE 13: Final Outcomes & Key Metrics (Section 6)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_slide_header(s13, "FINAL OUTCOMES", "Quantitative Project Achievements & Impact")
    add_slide_footer(s13, 13)

    stat_w = Inches(2.80)
    stat_h = Inches(4.70)
    sxs = [Inches(0.60), Inches(3.70), Inches(6.80), Inches(9.90)]

    outcomes = [
        ("1,238", "Quarters Scored", C_HEAD_DARK, 2, [
            "12 full fiscal years covered (FY2014-FY2026).",
            "Point-in-time XBRL integrity without look-ahead bias.",
            "Standardized across 26 major US public companies."
        ]),
        ("100%", "Scandal Sensitivity", C_AMBER, 11, [
            "Successfully triggered on Kraft Heinz procurement fraud.",
            "Detected Under Armour channel stuffing signature.",
            "Flagged Super Micro revenue recognition swings."
        ]),
        ("1.8s", "Live Pipeline Latency", C_HEAD_DARK, 10, [
            "Rapid on-demand scoring of newly submitted filings.",
            "Computes trailing baselines and ML scores in real time.",
            "Generates immediate audit scorecard & recommendations."
        ]),
        ("100%", "Test Pass Rate", C_HEAD_DARK, 13, [
            "6 comprehensive unit & integration test suites passed.",
            "Verifies feature engineering, ML models, and trend flags.",
            "Production-ready Python package in src/anomaly_pipeline.py."
        ]),
    ]

    for idx, (num, label, num_col, icon_i, bullets) in enumerate(outcomes):
        cx = sxs[idx]
        add_card(s13, cx, Inches(1.75), stat_w, stat_h)
        add_icon_box(s13, cx + Inches(0.25), Inches(2.05), icon_idx=icon_i, size=0.65)

        tb = s13.shapes.add_textbox(cx + Inches(0.25), Inches(2.80), stat_w - Inches(0.50), Inches(0.70))
        tb.text_frame.margin_left = tb.text_frame.margin_top = 0
        add_para(tb.text_frame, num, font_name=FONT_HEAD, font_size=38, bold=True, color=num_col, is_first=True)

        tb_l = s13.shapes.add_textbox(cx + Inches(0.25), Inches(3.50), stat_w - Inches(0.50), Inches(0.35))
        tb_l.text_frame.margin_left = tb_l.text_frame.margin_top = 0
        add_para(tb_l.text_frame, label, font_name=FONT_HEAD, font_size=15, bold=True, color=C_HEAD_DARK, is_first=True)

        tb_b = s13.shapes.add_textbox(cx + Inches(0.25), Inches(3.90), stat_w - Inches(0.50), Inches(2.40))
        tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
        tf = tb_b.text_frame
        for i, b in enumerate(bullets):
            add_para(tf, "• " + b, font_name=FONT_BODY, font_size=11.5, color=C_TEXT_DARK, space_after=5, is_first=(i==0))

    # =========================================================================
    # SLIDE 14: Conclusions & Project Summary (Section 6)
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_slide_header(s14, "CONCLUSIONS", "Summary of Work Achieved & Practical Impact")
    add_slide_footer(s14, 14)

    c_w = Inches(3.85)
    c_h = Inches(4.70)

    # Card 1: Feasibility
    add_card(s14, Inches(0.60), Inches(1.75), c_w, c_h)
    add_icon_box(s14, Inches(0.95), Inches(2.05), icon_idx=14)
    tb = s14.shapes.add_textbox(Inches(0.95), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Core Conclusions", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s14.shapes.add_textbox(Inches(0.95), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    conc_pts = [
        ("Effective Risk Triage:", "Unsupervised machine learning and multi-year trend tracking successfully triage financial filings without requiring true fraud labels during training."),
        ("Multi-Method Synergy:", "Isolation Forest catches subtle joint deviations, while Z-scores isolate single-quarter shocks, creating a robust consensus filter.")
    ]
    for i, (head, desc) in enumerate(conc_pts):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)

    # Card 2: Operational Value
    add_card(s14, Inches(4.75), Inches(1.75), c_w, c_h)
    add_icon_box(s14, Inches(5.10), Inches(2.05), icon_idx=12)
    tb = s14.shapes.add_textbox(Inches(5.10), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Practical Impact", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s14.shapes.add_textbox(Inches(5.10), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    impact_pts = [
        ("Auditor Productivity:", "Compresses manual audit review time from weeks to seconds by providing specific red-flag indicators."),
        ("Early Warning:", "Quarterly detection surfaces accounting inconsistencies months before annual 10-K filings and restatements.")
    ]
    for i, (head, desc) in enumerate(impact_pts):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)

    # Card 3: Complete Deliverables
    add_card(s14, Inches(8.90), Inches(1.75), c_w, c_h)
    add_icon_box(s14, Inches(9.25), Inches(2.05), icon_idx=22)
    tb = s14.shapes.add_textbox(Inches(9.25), Inches(3.10), Inches(3.15), Inches(0.40))
    tb.text_frame.margin_left = tb.text_frame.margin_top = 0
    add_para(tb.text_frame, "Deliverables Complete", font_name=FONT_HEAD, font_size=20, bold=True, color=C_HEAD_DARK, is_first=True)

    tb_b = s14.shapes.add_textbox(Inches(9.25), Inches(3.60), Inches(3.15), Inches(2.65))
    tb_b.text_frame.word_wrap = True; tb_b.text_frame.margin_left = tb_b.text_frame.margin_top = 0
    tf = tb_b.text_frame
    hand_pts = [
        ("Full Submission Package:", "All Deliverables 1 & 2 requirements completed, documented, and tested."),
        ("Interactive Viva Ready:", "Streamlit UI (app.py) & batch scripts ready for laptop evaluation demonstration.")
    ]
    for i, (head, desc) in enumerate(hand_pts):
        add_para(tf, f"• {head}", font_name=FONT_BODY, font_size=13, bold=True, color=C_TEAL, is_first=(i==0))
        add_para(tf, desc, font_name=FONT_BODY, font_size=12, color=C_TEXT_DARK, space_after=8)

    # Save
    out_path = ROOT / "SEC_Anomaly_Detection_Deliverable2.pptx"
    prs.save(str(out_path))
    print(f"Successfully saved clean presentation to {out_path}")

    # Synchronize to subpackage
    sub_path = ROOT / "sec_filing_anomaly_deliverable2" / "SEC_Anomaly_Detection_Deliverable2.pptx"
    if sub_path.parent.exists():
        prs.save(str(sub_path))
        print(f"Synchronized clean presentation to {sub_path}")

if __name__ == "__main__":
    build_presentation()
