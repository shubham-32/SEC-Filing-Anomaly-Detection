import pptx

p1 = pptx.Presentation("SEC_Anomaly_Detection_Deliverable1.pptx")
p2 = pptx.Presentation("SEC_Anomaly_Detection_Deliverable2.pptx")

print("=== PPT1 Slide 2 vs PPT2 Slide 2 Style Check ===")
s1_2 = p1.slides[1]
s2_2 = p2.slides[1]

def get_runs_info(slide):
    info = []
    for sh in slide.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.text.strip():
                        c = "inherit"
                        try:
                            if r.font.color and r.font.color.type == 1:
                                c = str(r.font.color.rgb)
                        except:
                            pass
                        info.append({
                            "text": r.text.strip()[:30],
                            "font": r.font.name,
                            "size": r.font.size.pt if r.font.size else "inherit",
                            "bold": r.font.bold,
                            "color": c
                        })
    return info

runs1 = get_runs_info(s1_2)
runs2 = get_runs_info(s2_2)

print("\nPPT1 Slide 2 Samples:")
for r in runs1[:6]:
    print(f"  {r['font']} | {r['size']}pt | bold={r['bold']} | color=#{r['color']} -> {r['text']}")

print("\nPPT2 Slide 2 Samples:")
for r in runs2[:6]:
    print(f"  {r['font']} | {r['size']}pt | bold={r['bold']} | color=#{r['color']} -> {r['text']}")
