#!/bin/bash

# Start both Flask app and ngrok tunnel together
# This script starts the Flask application in the background and then starts ngrok

echo "🚀 Starting Astramech with ngrok tunnel..."

# Set the authtoken
export NGROK_AUTHTOKEN="2mtkS18m9XOwl8cFgBxpWHyXgio_4wLygqUmXu7Fqz43DhN2w"

# Configure ngrok
ngrok config add-authtoken $NGROK_AUTHTOKEN

# Kill any existing Flask processes on port 5002
echo "🧹 Cleaning up existing processes..."
lsof -ti:5002 | xargs kill -9 2>/dev/null || true

# Start Flask app in the background
echo "🌐 Starting Flask application on port 5002..."
cd "$(dirname "$0")"
python3 run.py > flask.log 2>&1 &
FLASK_PID=$!
echo "   Flask PID: $FLASK_PID"

# Wait for Flask to start
echo "⏳ Waiting for Flask to start..."
sleep 3

# Check if Flask started successfully
if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Flask app started successfully"
else
    echo "❌ Flask app failed to start. Check flask.log for details"
    exit 1
fi

# Start ngrok tunnel
echo "🔗 Starting ngrok tunnel to astramech.ngrok.app..."
ngrok http --domain=astramech.ngrok.app 5002

# Cleanup on exit
trap "echo '🛑 Stopping Flask...'; kill $FLASK_PID 2>/dev/null" EXIT
