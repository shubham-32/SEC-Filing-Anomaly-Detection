import pptx

prs = pptx.Presentation("SEC_Anomaly_Detection_Deliverable1.pptx")
slides = list(prs.slides)
for idx, s in enumerate(slides[:5], 1):
    bg = s.background
    fill_c = "none"
    try:
        if bg and bg.fill:
            fill_c = f"type={bg.fill.type}"
            if hasattr(bg.fill, "fore_color") and bg.fill.fore_color:
                try:
                    fill_c += f", rgb={bg.fill.fore_color.rgb}"
                except:
                    pass
    except Exception as e:
        fill_c = str(e)
    print(f"Slide {idx} bg: {fill_c}")

# Let's inspect fonts in Slide 1 and Slide 2
for s_idx in [0, 1, 2]:
    s = slides[s_idx]
    print(f"\n--- SLIDE {s_idx+1} TEXTS ---")
    for sh in s.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                fn = p.font.name
                sz = p.font.size.pt if p.font.size else "inherit"
                bold = p.font.bold
                rgb = "inherit"
                try:
                    if p.font.color and p.font.color.rgb:
                        rgb = str(p.font.color.rgb)
                except:
                    pass
                if p.text.strip():
                    print(f"  [{sh.name}] font={fn}, size={sz}, bold={bold}, color={rgb} -> {p.text[:60]}")
