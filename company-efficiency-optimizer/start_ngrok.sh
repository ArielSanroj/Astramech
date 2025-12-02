#!/bin/bash

# Start ngrok tunnel to Astramech Flask application
# This script configures and starts ngrok with the custom domain

echo "🚀 Starting ngrok tunnel for Astramech..."

# Set the authtoken
export NGROK_AUTHTOKEN="2mtkS18m9XOwl8cFgBxpWHyXgio_4wLygqUmXu7Fqz43DhN2w"

# Configure ngrok with authtoken
ngrok config add-authtoken $NGROK_AUTHTOKEN

# Check if Flask app is already running
if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Flask app is already running on port 5002"
else
    echo "⚠️  Flask app is not running on port 5002"
    echo "   Please start the Flask app first with: python3 run.py"
    echo "   Or run: ./start_with_ngrok.sh to start both together"
fi

# Start ngrok tunnel with custom domain
echo "🔗 Connecting to ngrok domain: astramech.ngrok.app"
ngrok http --domain=astramech.ngrok.app 5002
