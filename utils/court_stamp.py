# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

import pytesseract
from pdf2image import convert_from_path


def extract_court_stamp(pdf_path):
    """
    Extract court stamp from the first page of a PDF using OCR.
    Returns the matched line or None if not found.
    """
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    if not images:
        return None
    text = pytesseract.image_to_string(images[0])
    for line in text.split("\n"):
        if "Filed" in line and "Court" in line:
            return line.strip()
        if "Filed" in line and any(char.isdigit() for char in line):
            return line.strip()
    return None
