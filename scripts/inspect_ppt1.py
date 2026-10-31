import json

with open("ppt1_structure.json", "r", encoding="utf-8") as f:
    slides = json.load(f)

with open("ppt1_dump.txt", "w", encoding="utf-8") as out:
    for s in slides:
        out.write(f"=== SLIDE {s['slide']} ===\n")
        for t in s["texts"]:
            f = t["font"]
            font_str = f"{f.get('font','-')}|{f.get('size','-')}pt|b={f.get('bold','-')}|c={f.get('color','-')}"
            out.write(f"  [{font_str}] {t['text']}\n")
        out.write("\n")

print("Saved ppt1_dump.txt")
