#!/bin/bash

# Start ngrok in the background with the astramech domain

echo "🚀 Starting ngrok tunnel to astramech.ngrok.app in background..."

# Ensure authtoken is configured
ngrok config add-authtoken 2mtkS18m9XOwl8cFgBxpWHyXgio_4wLygqUmXu7Fqz43DhN2w 2>/dev/null

# Kill any existing ngrok processes
pkill -f ngrok 2>/dev/null || true

# Start ngrok in background
nohup ngrok http --domain=astramech.ngrok.app 5002 > ngrok.log 2>&1 &
NGROK_PID=$!

echo "   Ngrok PID: $NGROK_PID"
echo "   Log file: ngrok.log"

# Wait for ngrok to start
sleep 2

# Check if ngrok started successfully
if lsof -Pi :4040 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Ngrok started successfully!"
    echo ""
    echo "🌐 Public URL: https://astramech.ngrok.app"
    echo "🔍 Inspector: http://localhost:4040"
    echo "📋 Log: tail -f ngrok.log"
    echo ""
    
    # Try to fetch tunnel info
    sleep 1
    if command -v curl &> /dev/null; then
        echo "📊 Tunnel Info:"
        curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'   URL: {data[\"tunnels\"][0][\"public_url\"]}') if data.get('tunnels') else None" 2>/dev/null || echo "   Fetching..."
    fi
else
    echo "❌ Ngrok failed to start. Check ngrok.log for details"
    cat ngrok.log
    exit 1
fi
