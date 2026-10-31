import pptx

prs = pptx.Presentation("SEC_Anomaly_Detection_Deliverable2.pptx")
print(f"Slide count: {len(prs.slides)}")
print(f"Width: {prs.slide_width.inches:.2f}\", Height: {prs.slide_height.inches:.2f}\"")

for idx, s in enumerate(prs.slides, 1):
    texts = []
    for sh in s.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                txt = p.text.strip()
                if txt and len(txt) > 3:
                    texts.append(txt)
    t = texts[0] if texts else "No text"
    sub = texts[1] if len(texts) > 1 else ""
    print(f"Slide {idx:2d}: {t[:35]:<35} | {sub[:50]} (shapes: {len(s.shapes)})")

