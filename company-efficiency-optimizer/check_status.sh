#!/bin/bash

# Check status of Flask app and ngrok

echo "🔍 Checking Astramech Services Status"
echo "======================================"

# Check Flask app
echo ""
echo "Flask Application (Port 5002):"
if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null ; then
    PID=$(lsof -ti:5002)
    echo "  ✅ Running (PID: $PID)"
    ps -p $PID -o command= | head -1
else
    echo "  ❌ Not running"
fi

# Check ngrok
echo ""
echo "Ngrok Tunnel (Port 4040):"
if lsof -Pi :4040 -sTCP:LISTEN -t >/dev/null ; then
    echo "  ✅ Running"
    echo "  📊 Inspector: http://localhost:4040"
    # Try to get tunnel status
    if command -v curl &> /dev/null; then
        echo ""
        echo "Tunnel Status:"
        curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -A 2 "public_url" || echo "  (Could not fetch tunnel details)"
    fi
else
    echo "  ❌ Not running"
fi

# Check ngrok config
echo ""
echo "Ngrok Configuration:"
if [ -f "$HOME/Library/Application Support/ngrok/ngrok.yml" ]; then
    echo "  ✅ Config file exists"
    if grep -q "authtoken" "$HOME/Library/Application Support/ngrok/ngrok.yml" 2>/dev/null; then
        echo "  ✅ Authtoken configured"
    else
        echo "  ⚠️  Authtoken not found in config"
    fi
else
    echo "  ❌ Config file not found"
fi

echo ""
echo "======================================"
echo ""

# Provide suggestions
if ! lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null ; then
    echo "💡 To start Flask: python3 run.py"
fi

if ! lsof -Pi :4040 -sTCP:LISTEN -t >/dev/null ; then
    echo "💡 To start ngrok: ./start_ngrok.sh"
    echo "💡 Or start both: ./start_with_ngrok.sh"
fi

if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null && lsof -Pi :4040 -sTCP:LISTEN -t >/dev/null ; then
    echo "🎉 All services are running!"
    echo "🌐 Access your app at: https://astramech.ngrok.app"
    echo "🔍 Debug at: http://localhost:4040"
fi
