#!/bin/bash

# Test Vercel deployment

echo "🧪 Testing Vercel Deployment"
echo "=============================="
echo ""

# Get latest deployment URL
DEPLOYMENT_URL=$(cd /Users/arielsanroj/Astramech/company-efficiency-optimizer && vercel ls --json 2>/dev/null | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(data['deployments'][0]['url']) if data.get('deployments') else 'astramech.vercel.app'" 2>/dev/null || echo "astramech.vercel.app")

echo "Testing URL: https://$DEPLOYMENT_URL"
echo ""

# Test endpoints
endpoints=(
  "/"
  "/api/health"
  "/questionnaire"
  "/agents/supervincent"
  "/agents/clioalpha"
)

for endpoint in "${endpoints[@]}"; do
  echo -n "Testing $endpoint ... "
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://$DEPLOYMENT_URL$endpoint" --max-time 10)
  
  if [ "$status" = "200" ]; then
    echo "✅ OK (200)"
  elif [ "$status" = "404" ]; then
    echo "❌ NOT FOUND (404)"
  elif [ "$status" = "500" ]; then
    echo "⚠️  SERVER ERROR (500)"
  elif [ "$status" = "401" ]; then
    echo "🔒 UNAUTHORIZED (401)"
  else
    echo "⚠️  Status: $status"
  fi
done

echo ""
echo "=============================="
echo ""
echo "📊 Deployment Status:"
cd /Users/arielsanroj/Astramech/company-efficiency-optimizer && vercel ls 2>&1 | head -6
echo ""
echo "🔗 URLs:"
echo "  Production: https://astramech.vercel.app"
echo "  Latest: https://$DEPLOYMENT_URL"
echo "  Dashboard: https://vercel.com/arielsanrojs-projects/astramech"
