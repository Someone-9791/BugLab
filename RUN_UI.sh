#!/bin/bash

# PythonDebugEnv - Desktop UI Launcher

# Change to script directory
cd "$(dirname "$0")"
source bin/activate

echo "=========================================="
echo "PythonDebugEnv - Desktop Testing UI"
echo "=========================================="
echo ""

# Check if server is running
echo "Checking server status..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Server is running"
else
    echo "⚠️  Server not detected. Starting server..."
    nohup python3 -m uvicorn server.app:app --host 0.0.0.0 --port 8000 > /tmp/server.log 2>&1 &
    echo "   Server PID: $!"
    sleep 3
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Server started successfully"
    else
        echo "❌ Server failed to start. Check /tmp/server.log"
        exit 1
    fi
fi

echo ""
echo "Launching PyQt6 UI..."
python3 test_ui_pyqt.py

echo ""
echo "UI closed."
