#!/bin/bash
# shutdown_ollama.sh - Stop Ollama service

echo "========================================"
echo "Ollama Shutdown Script"
echo "========================================"
echo ""

# Check if Ollama is running
if pgrep -x "ollama" > /dev/null; then
    echo "Stopping Ollama service..."
    pkill ollama
    sleep 2

    # Verify it stopped
    if pgrep -x "ollama" > /dev/null; then
        echo "⚠ Ollama still running, forcing shutdown..."
        pkill -9 ollama
    fi

    echo "✓ Ollama stopped"
else
    echo "ℹ Ollama is not currently running"
fi

echo ""
echo "========================================"
echo "Shutdown complete"
echo "========================================"
