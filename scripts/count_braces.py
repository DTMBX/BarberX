from pathlib import Path

p = Path("assets/css/style.css")
text = p.read_text(encoding="utf-8")
opens = text.count("{")
closes = text.count("}")
print("opens", opens, "closes", closes, "diff", opens - closes)
