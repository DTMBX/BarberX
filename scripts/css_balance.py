#!/usr/bin/env python3
from pathlib import Path

p = Path("assets/css/style.css")
text = p.read_text(encoding="utf-8")
lines = text.splitlines()
bal = 0
for i, l in enumerate(lines):
    opens = l.count("{")
    closes = l.count("}")
    bal += opens - closes
    if i >= 6400 and i <= 7080:
        print(f"{i + 1:5d} {bal:4d} {l.rstrip()}")
print("FINAL_BALANCE", bal)
