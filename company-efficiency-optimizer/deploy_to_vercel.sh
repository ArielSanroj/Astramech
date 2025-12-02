#!/bin/bash

# Deploy AstraMech to Vercel with ngrok integration

echo "🚀 Deploying AstraMech to Vercel..."
echo "Project: astramech (prj_PML13yysmZWv7xaUkwy0Vh67zKCY)"
echo "Ngrok URL: https://astramech.ngrok.app"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install with: npm i -g vercel"
    exit 1
fi

# Check if project is linked
if [ ! -d ".vercel" ]; then
    echo "⚠️  Project not linked. Linking now..."
    vercel link --yes --project prj_PML13yysmZWv7xaUkwy0Vh67zKCY
fi

# Show current deployment status
echo "📊 Current Vercel project status:"
vercel ls 2>/dev/null | head -5

echo ""
echo "🔍 Pre-deployment checks..."

# Check required files
REQUIRED_FILES=("api/index.py" "vercel.json" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ Missing: $file"
        exit 1
    fi
done

echo ""
read -p "Deploy to production? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying to production..."
    vercel --prod
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Deployment successful!"
        echo ""
        echo "📍 Your deployment URLs:"
        echo "   • Vercel: Check the output above"
        echo "   • Ngrok: https://astramech.ngrok.app"
        echo ""
        echo "🔗 Vercel Dashboard:"
        echo "   https://vercel.com/arielsanrojs-projects/astramech"
        echo ""
        echo "💡 Next steps:"
        echo "   1. Visit your Vercel URL to test"
        echo "   2. Configure custom domain if needed"
        echo "   3. Set up monitoring and alerts"
    else
        echo ""
        echo "❌ Deployment failed. Check the errors above."
        exit 1
    fi
else
    echo "Deployment cancelled."
fi
