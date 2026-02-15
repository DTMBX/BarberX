#!/bin/bash

# GitHub Pages Deployment Setup Script
# This script helps configure the repository for GitHub Pages deployment

echo "🚀 GitHub Pages Deployment Setup"
echo "=================================="
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Get repository information
echo "📝 Detecting repository information..."
echo ""

# Try to get remote URL
REMOTE_URL=$(git config --get remote.origin.url)

if [ -z "$REMOTE_URL" ]; then
    echo "⚠️  No remote origin found. Please set up your GitHub repository first:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo ""
    read -p "Enter your GitHub repository URL: " REMOTE_URL
fi

echo "Remote URL: $REMOTE_URL"
echo ""

# Extract username and repo name from URL
if [[ $REMOTE_URL =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
    USERNAME="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
    
    echo "✅ Detected GitHub repository:"
    echo "   Username: $USERNAME"
    echo "   Repository: $REPO"
    echo ""
else
    echo "⚠️  Could not parse GitHub URL"
    read -p "Enter your GitHub username: " USERNAME
    read -p "Enter your repository name: " REPO
    echo ""
fi

# Confirm with user
echo "🔧 Configuration to apply:"
echo "   - Base path: /$REPO/"
echo "   - Homepage: https://$USERNAME.github.io/$REPO/"
echo "   - Repository URL: https://github.com/$USERNAME/$REPO.git"
echo ""
read -p "Is this correct? (y/n): " CONFIRM

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "❌ Setup cancelled"
    exit 0
fi

echo ""
echo "⚙️  Updating configuration files..."

# Update vite.config.ts
if [ -f "vite.config.ts" ]; then
    echo "   - Updating vite.config.ts..."
    sed -i.bak "s|base: process.env.GITHUB_ACTIONS ? '/spark-template/' : '/'|base: process.env.GITHUB_ACTIONS ? '/$REPO/' : '/'|g" vite.config.ts
    rm -f vite.config.ts.bak
    echo "     ✅ vite.config.ts updated"
else
    echo "     ⚠️  vite.config.ts not found"
fi

# Update package.json
if [ -f "package.json" ]; then
    echo "   - Updating package.json..."
    
    # Create backup
    cp package.json package.json.bak
    
    # Update URLs using sed (cross-platform compatible)
    sed -i.tmp "s|https://github.com/YOUR_USERNAME/YOUR_REPO.git|https://github.com/$USERNAME/$REPO.git|g" package.json
    sed -i.tmp "s|https://github.com/YOUR_USERNAME/YOUR_REPO/issues|https://github.com/$USERNAME/$REPO/issues|g" package.json
    sed -i.tmp "s|https://YOUR_USERNAME.github.io/YOUR_REPO/|https://$USERNAME.github.io/$REPO/|g" package.json
    
    rm -f package.json.tmp package.json.bak
    echo "     ✅ package.json updated"
else
    echo "     ⚠️  package.json not found"
fi

# Update README.md
if [ -f "README.md" ]; then
    echo "   - Updating README.md..."
    sed -i.bak "s|YOUR_USERNAME|$USERNAME|g" README.md
    sed -i.bak "s|YOUR_REPO|$REPO|g" README.md
    rm -f README.md.bak
    echo "     ✅ README.md updated"
fi

echo ""
echo "✅ Configuration complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Enable GitHub Pages in your repository:"
echo "   - Go to: https://github.com/$USERNAME/$REPO/settings/pages"
echo "   - Under 'Build and deployment', select 'GitHub Actions'"
echo ""
echo "2. Commit and push changes:"
echo "   git add ."
echo "   git commit -m 'Configure for GitHub Pages deployment'"
echo "   git push origin main"
echo ""
echo "3. Monitor deployment:"
echo "   - Go to: https://github.com/$USERNAME/$REPO/actions"
echo "   - Watch the 'Deploy to GitHub Pages' workflow"
echo ""
echo "4. Access your site:"
echo "   - https://$USERNAME.github.io/$REPO/"
echo ""
echo "🎉 Happy deploying!"
