#!/bin/bash
# Quick Netlify Deployment Script for BarberX.info

echo "🚀 BarberX.info - Netlify Deployment"
echo "===================================="
echo ""

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null
then
    echo "❌ Netlify CLI not found. Installing..."
    npm install -g netlify-cli
    echo "✅ Netlify CLI installed"
else
    echo "✅ Netlify CLI already installed"
fi

echo ""
echo "📋 Pre-deployment checklist:"
echo "  1. Testing local Jekyll build..."

# Test Jekyll build
bundle install --quiet
if bundle exec jekyll build; then
    echo "  ✅ Jekyll build successful"
else
    echo "  ❌ Jekyll build failed. Fix errors before deploying."
    exit 1
fi

echo "  2. Checking Git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "  ⚠️  You have uncommitted changes"
    echo "     Commit them before deploying? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        git add .
        echo "     Enter commit message:"
        read -r commit_msg
        git commit -m "$commit_msg"
        git push origin main
        echo "  ✅ Changes committed and pushed"
    fi
else
    echo "  ✅ Git working directory clean"
fi

echo ""
echo "🚀 Ready to deploy!"
echo ""
echo "Choose deployment option:"
echo "  1. Deploy to production (--prod)"
echo "  2. Deploy preview (draft)"
echo "  3. Initialize new site"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Deploying to PRODUCTION..."
        netlify deploy --prod
        ;;
    2)
        echo "Creating PREVIEW deployment..."
        netlify deploy
        ;;
    3)
        echo "Initializing new Netlify site..."
        netlify init
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment complete!"
echo "🌐 Visit your site:"
netlify open:site
