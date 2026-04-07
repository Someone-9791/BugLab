#!/bin/bash

# Test script to verify PyQt6 UI is working correctly

set -e

# Change to script directory
cd "$(dirname "$0")"
source bin/activate

echo "=========================================="
echo "PythonDebugEnv - UI Test Script"
echo "=========================================="
echo ""

# Clean log file
rm -f /tmp/pythondebuguienv.log

echo "Starting UI process..."
python3 test_ui_pyqt.py > /tmp/ui_test.log 2>&1 &
UI_PID=$!

echo "UI PID: $UI_PID"
echo ""

# Wait for startup
sleep 2

# Check if process is alive
if ps -p $UI_PID > /dev/null 2>&1; then
    echo "✅ UI process is running"
else
    echo "❌ UI process crashed"
    echo "Log:"
    cat /tmp/ui_test.log
    exit 1
fi

# Check log file
echo ""
echo "Log messages:"
if [ -f /tmp/pythondebuguienv.log ]; then
    cat /tmp/pythondebuguienv.log
else
    echo "⚠️  No log file yet"
fi

echo ""
echo "Monitoring UI for 10 seconds..."
echo ""

for i in {1..5}; do
    sleep 2
    if ps -p $UI_PID > /dev/null 2>&1; then
        echo "✅ At ${i}x2 seconds: Still running"
    else
        echo "❌ At ${i}x2 seconds: Crashed!"
        echo "Final log:"
        cat /tmp/pythondebuguienv.log
        exit 1
    fi
done

echo ""
echo "=========================================="
echo "✅ TEST PASSED - UI is stable!"
echo "=========================================="
echo ""
echo "The UI is now running in the background (PID: $UI_PID)"
echo "You can interact with it or kill it with: kill $UI_PID"
echo ""
echo "Full log available at: /tmp/pythondebuguienv.log"
echo "Console output at: /tmp/ui_test.log"
