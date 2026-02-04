#!/usr/bin/env python3
"""
Evident AI Tools - Quick Test Script
Tests all AI tool endpoints and dependencies
"""

import os
import sys

print("=" * 60)
print("Evident AI Tools - Dependency & Functionality Test")
print("=" * 60)

# Test 1: Core Python packages
print("\n[1/6] Testing Python Dependencies...")
dependencies = {
    "flask": "Flask",
    "flask_sqlalchemy": "Flask-SQLAlchemy",
    "flask_login": "Flask-Login",
    "openai": "OpenAI",
    "whisper": "OpenAI Whisper",
    "pytesseract": "PyTesseract",
    "PIL": "Pillow",
    "pypdf": "PyPDF",
    "langchain": "LangChain",
    "sentence_transformers": "Sentence Transformers",
}

missing = []
installed = []

for module, name in dependencies.items():
    try:
        __import__(module)
        installed.append(f"  ✓ {name}")
    except ImportError:
        missing.append(f"  ✗ {name} (module: {module})")

print("\nInstalled:")
for item in installed:
    print(item)

if missing:
    print("\nMissing:")
    for item in missing:
        print(item)

# Test 2: Optional dependencies
print("\n[2/6] Testing Optional Dependencies...")
optional = {
    "spacy": "spaCy (for NER)",
    "chromadb": "ChromaDB (for vector search)",
    "faiss": "FAISS (for similarity search)",
}

optional_installed = []
optional_missing = []

for module, name in optional.items():
    try:
        __import__(module)
        optional_installed.append(f"  ✓ {name}")
    except ImportError:
        optional_missing.append(f"  ⚠ {name} - Optional, tools will work without it")

if optional_installed:
    print("\nOptional packages installed:")
    for item in optional_installed:
        print(item)

if optional_missing:
    print("\nOptional packages not installed:")
    for item in optional_missing:
        print(item)

# Test 3: Tesseract OCR binary
print("\n[3/6] Testing Tesseract OCR Binary...")
try:
    import io

    import pytesseract
    from PIL import Image

    # Try to get tesseract version
    try:
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract OCR binary found: v{version}")
    except Exception as e:
        print(f"  ✗ Tesseract binary not found or not in PATH")
        print(f"    Error: {e}")
        print(f"    Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        print(f"    Or via chocolatey: choco install tesseract")
except Exception as e:
    print(f"  ✗ Cannot test Tesseract: {e}")

# Test 4: Flask app imports
print("\n[4/6] Testing Flask App Imports...")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Test critical imports from app.py
    print("  Testing tier_gating module...")
    try:
        from tier_gating import TierLevel, check_usage_limit, require_tier

        print("    ✓ tier_gating imports successful")
    except Exception as e:
        print(f"    ✗ tier_gating import failed: {e}")

    print("  Testing models_auth module...")
    try:
        from models_auth import UsageTracking, User

        print("    ✓ models_auth imports successful")
    except Exception as e:
        print(f"    ⚠ models_auth import failed (may need database): {e}")

    print("  Testing app configuration...")
    try:
        # Don't import full app, just check if file exists
        if os.path.exists("app.py"):
            print("    ✓ app.py found")
        else:
            print("    ✗ app.py not found")
    except Exception as e:
        print(f"    ✗ Error: {e}")

except Exception as e:
    print(f"  ✗ Flask app test failed: {e}")

# Test 5: Check required directories
print("\n[5/6] Checking Required Directories...")
required_dirs = [
    "templates",
    "templates/tools",
    "templates/auth",
    "static",
    "uploads",
    "analysis_results",
]

for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"  ✓ {dir_path}/")
    else:
        print(f"  ⚠ {dir_path}/ - Will be created on first run")

# Test 6: Check new tool templates
print("\n[6/6] Checking New Tool Templates...")
tool_templates = [
    "templates/tools-hub.html",
    "templates/tools/ocr.html",
    "templates/bwc-dashboard.html",
    "templates/legal-analysis.html",
    "templates/batch-pdf-upload.html",
]

for template in tool_templates:
    if os.path.exists(template):
        print(f"  ✓ {template}")
    else:
        print(f"  ✗ {template} - Missing!")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if not missing:
    print("✓ All required dependencies installed")
else:
    print(f"✗ {len(missing)} required dependencies missing")

if optional_missing:
    print(f"⚠ {len(optional_missing)} optional dependencies not installed (tools will still work)")

print("\nRECOMMENDATIONS:")
print("1. Install Tesseract OCR binary for OCR functionality:")
print("   Download: https://github.com/UB-Mannheim/tesseract/wiki")
print("   Or: choco install tesseract")
print("\n2. SpaCy is optional - legal analysis works without it")
print("\n3. To test the Flask app, run:")
print("   python app.py")
print("\n4. Access the tools hub at:")
print("   http://localhost:5000/tools")

print("\n" + "=" * 60)


