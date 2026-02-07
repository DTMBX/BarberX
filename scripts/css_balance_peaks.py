from pathlib import Path

p = Path("assets/css/style.css")
text = p.read_text(encoding="utf-8")
lines = text.splitlines()
bal = 0
max_bal = 0
max_idx = 0
for i, l in enumerate(lines):
    bal += l.count("{") - l.count("}")
    if bal > max_bal:
        max_bal = bal
        max_idx = i + 1
print("MAX_BAL", max_bal, "at line", max_idx)
# print context around max
for i in range(max(1, max_idx - 6), min(len(lines), max_idx + 6)):
    print(f"{i:5d}: {lines[i - 1]}")
print("\nFINAL_BAL", bal)
