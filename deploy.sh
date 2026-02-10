#!/bin/bash
# Deploy to Railway - Helper Script

echo "🚀 Invoice Generator - Railway Deployment Helper"
echo "================================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

echo ""
echo "📝 Next steps:"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   👉 https://github.com/new"
echo ""
echo "2. Run these commands (replace YOUR-USERNAME and YOUR-REPO):"
echo ""
echo "   git add ."
echo "   git commit -m \"Invoice generator ready for deployment\""
echo "   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git"
echo "   git push -u origin main"
echo ""
echo "3. Deploy on Railway:"
echo "   👉 https://railway.app"
echo "   - Sign in with GitHub"
echo "   - Click 'New Project'"
echo "   - Select 'Deploy from GitHub repo'"
echo "   - Choose your repository"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
