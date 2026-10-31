import pptx

prs = pptx.Presentation("SEC_Anomaly_Detection_Deliverable1.pptx")
slides = list(prs.slides)

for s_idx in [0, 1, 2]:
    s = slides[s_idx]
    print(f"\n=================== SLIDE {s_idx+1} RUNS ===================")
    for sh in s.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    fn = r.font.name
                    sz = r.font.size.pt if r.font.size else "inherit"
                    bold = r.font.bold
                    rgb = "inherit"
                    try:
                        if r.font.color and r.font.color.rgb:
                            rgb = str(r.font.color.rgb)
                    except:
                        pass
                    if r.text.strip():
                        print(f"  [{sh.name}] font={fn}, sz={sz}, b={bold}, c={rgb} -> {r.text[:50]!r}")

