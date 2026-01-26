#!/usr/bin/env bash
# Minimal build script for diagnosis

set -o errexit

echo "🔧 BarberX - Minimal Diagnostic Build"
echo "Python version: $(python --version)"

echo "📦 Installing minimal dependencies..."
pip install --upgrade pip
pip install --no-cache-dir \
    Flask==3.1.0 \
    Flask-CORS==5.0.0 \
    gunicorn==23.0.0

echo "✅ Minimal build complete!"
echo "📋 Installed packages:"
pip list | grep -i flask
