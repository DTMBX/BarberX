# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

sys.exit(2)  # Not found


import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../utils")))
from court_stamp import extract_court_stamp

if len(sys.argv) < 2:
    print("Usage: python extract_court_stamp_ocr.py <pdfPath>")
    sys.exit(1)

pdf_path = sys.argv[1]
result = extract_court_stamp(pdf_path)
if result:
    print(result)
    sys.exit(0)
else:
    sys.exit(2)  # Not found
