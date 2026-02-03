#!/usr/bin/env bash
# Render.com Build Script for Evident.info Flask App

set -o errexit

echo "🔧 Evident.info - Render Build"
echo "Python version: $(python --version)"

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libpq-dev

echo "📦 Installing Python dependencies..."
pip install --upgrade pip

# Install requirements without heavy AI dependencies for Render
# (openai-whisper requires ffmpeg, pytorch, and causes build timeout)
echo "Installing core dependencies..."
pip install --no-cache-dir \
    Flask==3.1.0 \
    Flask-CORS==5.0.0 \
    Flask-SQLAlchemy==3.1.1 \
    Flask-Login==0.6.3 \
    Flask-Bcrypt==1.0.1 \
    Werkzeug==3.1.3 \
    gunicorn==23.0.0 \
    psycopg2-binary==2.9.10 \
    SQLAlchemy==2.0.36 \
    python-dotenv==1.0.1 \
    requests==2.32.5 \
    Pillow==11.0.0 \
    pypdf==5.1.0 \
    pdfplumber==0.11.4 \
    openai==2.15.0 \
    cryptography==44.0.0 \
    certifi==2024.12.14 \
    pytesseract==0.3.13 \
    pdf2image==1.17.0 \
    pyotp==2.9.0 \
    "qrcode[pil]==8.0" \
    stripe==11.4.0

echo "✅ Build complete!"
echo "⚠️  Note: openai-whisper not installed (requires ffmpeg/pytorch)"
echo "   Whisper transcription will be disabled in production"
echo "   Use OpenAI API for transcription instead"

