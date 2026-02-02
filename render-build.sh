#!/bin/bash
# Evident Platform - Render Build Script
# Handles both Python Flask app and optional Jekyll static site

set -e

echo "==> Evident Platform Build Script"
echo "==> Detecting build environment..."

# Check if this is a Python environment
if command -v python3 &> /dev/null || command -v python &> /dev/null; then
    echo "==> Python detected, installing dependencies..."
    pip install -r requirements.txt
    echo "==> Python dependencies installed successfully!"
fi

# Check if Ruby/Jekyll should be built (only if Ruby is properly configured)
if command -v ruby &> /dev/null && command -v bundle &> /dev/null; then
    echo "==> Ruby detected, attempting Jekyll build..."
    if bundle install; then
        bundle exec jekyll build
        echo "==> Jekyll build completed!"
    else
        echo "==> Jekyll build skipped (bundle install failed)"
    fi
else
    echo "==> Ruby/Bundler not available, skipping Jekyll build"
    echo "==> (Jekyll static site should be deployed via Netlify or GitHub Pages)"
fi

echo "==> Build complete!"
