#!/bin/bash

# Vercel Environment Variables Setup Script
# This script sets up all necessary environment variables for the Vercel deployment

echo "🔧 Setting up Vercel Environment Variables..."
echo "Project: astramech (prj_PML13yysmZWv7xaUkwy0Vh67zKCY)"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install with: npm i -g vercel"
    exit 1
fi

# Production environment variables
echo "Setting production environment variables..."

# Flask Configuration
vercel env add SECRET_KEY production <<< "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
vercel env add FLASK_ENV production <<< "production"

# Ngrok Configuration
vercel env add NGROK_URL production <<< "https://astramech.ngrok.app"
vercel env add NGROK_AUTHTOKEN production <<< "2mtkS18m9XOwl8cFgBxpWHyXgio_4wLygqUmXu7Fqz43DhN2w"

# Ollama Configuration (from .env)
vercel env add OLLAMA_API_KEY production <<< "c6f1e109560b4b098ff80b99c5942d42.DdN4aonYSge8plew0dvp3XO_"
vercel env add OLLAMA_BASE_URL production <<< "http://localhost:11434"
vercel env add OLLAMA_MODEL production <<< "llama3.1:8b"

# Pinecone Configuration
vercel env add PINECONE_API_KEY production <<< "pcsk_5F4Kxb_EpxvT1nERpkNoUPo5uNk7UiARTGpB6GRJ5TKSpApKpoYRguLGb89WHvnRupSVh"

# Project Configuration
vercel env add PROJECT_NAME production <<< "AstraMech"
vercel env add LOG_LEVEL production <<< "INFO"

# Session Configuration
vercel env add MAX_FILE_SIZE production <<< "16777216"
vercel env add ALLOWED_EXTENSIONS production <<< "pdf,xlsx,xls,csv"

echo ""
echo "✅ Environment variables configured for production"
echo ""
echo "📝 To set preview/development environments, run:"
echo "   vercel env add <VAR_NAME> preview"
echo "   vercel env add <VAR_NAME> development"
echo ""
echo "🚀 Ready to deploy! Run: vercel --prod"
