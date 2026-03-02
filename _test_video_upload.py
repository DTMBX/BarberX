"""
Evident MP4 Video Upload Test — BWC Evidence Pipeline
Tests single file upload, forensic metadata, duplicate detection, and upload stats.
"""
import requests
import json
import sys

BASE = "http://127.0.0.1:5000"
s = requests.Session()

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {label}")
    else:
        failed += 1
        print(f"  FAIL  {label}  {detail}")


# ── Step 1: Login ──────────────────────────────────────────
print("\n=== Step 1: Login ===")
r = s.post(
    f"{BASE}/auth/login",
    data={"email": "admin@evident.test", "password": "Evident2026!"},
    allow_redirects=False,
)
check("Login returns 302", r.status_code == 302, f"got {r.status_code}")

# ── Step 2: Upload flag-360p.mp4 (0.47 MB) ────────────────
print("\n=== Step 2: Upload flag-360p.mp4 (0.47 MB) — BWC-UNIT-001 ===")
with open(r"src\assets\media\renditions\flag-360p.mp4", "rb") as f:
    r = s.post(
        f"{BASE}/upload/single",
        files={"file": ("bwc-test-360p.mp4", f, "video/mp4")},
        data={"device_label": "BWC-UNIT-001"},
    )
check("HTTP 200", r.status_code == 200, f"got {r.status_code}")
d2 = r.json() if r.status_code == 200 else {}
if d2:
    check("Has evidence_id", bool(d2.get("evidence_id")))
    check("Has sha256", bool(d2.get("sha256")))
    check("MIME is video/mp4", d2.get("mime_type") == "video/mp4", d2.get("mime_type"))
    check("Not duplicate", d2.get("duplicate") is False, str(d2.get("duplicate")))
    check("Status completed", d2.get("processing_status") == "completed", d2.get("processing_status"))
    print(f"  >> evidence_id: {d2.get('evidence_id')}")
    print(f"  >> sha256:      {d2.get('sha256')}")
    print(f"  >> size_bytes:  {d2.get('size_bytes')}")
else:
    print(f"  Response: {r.text[:400]}")

# ── Step 3: Upload flag-720p.mp4 (2.27 MB) ────────────────
print("\n=== Step 3: Upload flag-720p.mp4 (2.27 MB) — BWC-UNIT-002 ===")
with open(r"src\assets\media\renditions\flag-720p.mp4", "rb") as f:
    r = s.post(
        f"{BASE}/upload/single",
        files={"file": ("bwc-test-720p.mp4", f, "video/mp4")},
        data={"device_label": "BWC-UNIT-002"},
    )
check("HTTP 200", r.status_code == 200, f"got {r.status_code}")
d3 = r.json() if r.status_code == 200 else {}
if d3:
    check("Has evidence_id", bool(d3.get("evidence_id")))
    check("Has sha256", bool(d3.get("sha256")))
    check("Different hash from 360p", d3.get("sha256") != d2.get("sha256"))
    print(f"  >> evidence_id: {d3.get('evidence_id')}")
    print(f"  >> sha256:      {d3.get('sha256')}")
    print(f"  >> size_bytes:  {d3.get('size_bytes')}")
else:
    print(f"  Response: {r.text[:400]}")

# ── Step 4: Upload flag-1080p.mp4 (3.28 MB) ───────────────
print("\n=== Step 4: Upload flag-1080p.mp4 (3.28 MB) — BWC-UNIT-001 ===")
with open(r"src\assets\media\renditions\flag-1080p.mp4", "rb") as f:
    r = s.post(
        f"{BASE}/upload/single",
        files={"file": ("bwc-test-1080p.mp4", f, "video/mp4")},
        data={"device_label": "BWC-UNIT-001"},
    )
check("HTTP 200", r.status_code == 200, f"got {r.status_code}")
d4 = r.json() if r.status_code == 200 else {}
if d4:
    check("Has evidence_id", bool(d4.get("evidence_id")))
    check("Has sha256", bool(d4.get("sha256")))
    print(f"  >> evidence_id: {d4.get('evidence_id')}")
    print(f"  >> sha256:      {d4.get('sha256')}")
    print(f"  >> size_bytes:  {d4.get('size_bytes')}")
else:
    print(f"  Response: {r.text[:400]}")

# ── Step 5: Upload flag.mp4 original (1.73 MB) ────────────
print("\n=== Step 5: Upload flag.mp4 original (1.73 MB) — BWC-UNIT-003 ===")
with open(r"src\assets\media\flag.mp4", "rb") as f:
    r = s.post(
        f"{BASE}/upload/single",
        files={"file": ("bwc-patrol-cam.mp4", f, "video/mp4")},
        data={"device_label": "BWC-UNIT-003"},
    )
check("HTTP 200", r.status_code == 200, f"got {r.status_code}")
d5 = r.json() if r.status_code == 200 else {}
if d5:
    check("Has evidence_id", bool(d5.get("evidence_id")))
    check("Has sha256", bool(d5.get("sha256")))
    print(f"  >> evidence_id: {d5.get('evidence_id')}")
    print(f"  >> sha256:      {d5.get('sha256')}")
    print(f"  >> size_bytes:  {d5.get('size_bytes')}")
else:
    print(f"  Response: {r.text[:400]}")

# ── Step 6: Duplicate detection (re-upload 360p) ──────────
print("\n=== Step 6: Duplicate Detection — re-upload flag-360p.mp4 ===")
with open(r"src\assets\media\renditions\flag-360p.mp4", "rb") as f:
    r = s.post(
        f"{BASE}/upload/single",
        files={"file": ("bwc-duplicate-test.mp4", f, "video/mp4")},
        data={"device_label": "BWC-UNIT-001"},
    )
check("HTTP 200", r.status_code == 200, f"got {r.status_code}")
d6 = r.json() if r.status_code == 200 else {}
if d6:
    check("Duplicate detected", d6.get("duplicate") is True, str(d6.get("duplicate")))
    check("Same sha256 as first upload", d6.get("sha256") == d2.get("sha256"))
    check("Same evidence_id reused", d6.get("evidence_id") == d2.get("evidence_id"))
    print(f"  >> duplicate:   {d6.get('duplicate')}")
    print(f"  >> evidence_id: {d6.get('evidence_id')}")
else:
    print(f"  Response: {r.text[:400]}")

# ── Step 7: Verify evidence (chain of custody check) ──────
if d2.get("evidence_id"):
    print(f"\n=== Step 7: Verify Evidence Integrity — {d2['evidence_id']} ===")
    r = s.get(f"{BASE}/upload/api/verify/{d2['evidence_id']}")
    check("Verify HTTP 200", r.status_code == 200, f"got {r.status_code}")
    if r.status_code == 200:
        v = r.json()
        print(json.dumps(v, indent=2))

# ── Step 8: Upload stats ──────────────────────────────────
print("\n=== Step 8: Upload Stats ===")
r = s.get(f"{BASE}/upload/api/stats")
check("Stats HTTP 200", r.status_code == 200, f"got {r.status_code}")
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))

# ── Summary ───────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed, {passed+failed} total")
print(f"{'='*50}")
sys.exit(0 if failed == 0 else 1)
