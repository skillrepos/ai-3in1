#!/bin/bash
# startup_ollama.sh - Start and warm up Ollama for lab exercises

echo "========================================"
echo "Ollama Startup & Warmup Script"
echo "========================================"
echo ""

# Step 1: Check and install Ollama if needed
echo "Step 1: Checking for Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is already installed"
else
    echo "  Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✓ Ollama installed"
fi
echo ""

# Step 2: Start Ollama service
echo "Step 2: Starting Ollama service..."
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!
echo "✓ Ollama started (PID: $OLLAMA_PID)"
echo ""

# Wait for Ollama to be ready
echo "Step 3: Waiting for Ollama to be ready..."
sleep 3
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "  Waiting for Ollama server..."
    sleep 1
done
echo "✓ Ollama server is ready"
echo ""

# Step 4: Pull llama3.2 model if not present
echo "Step 4: Checking for llama3.2 model..."
if ollama list | grep -q "llama3.2"; then
    echo "✓ llama3.2 model already present"
else
    echo "  Pulling llama3.2 model (this may take a few minutes)..."
    ollama pull llama3.2
    echo "✓ llama3.2 model downloaded"
fi
echo ""

# Step 5: Warm up the model with a simple query
echo "Step 5: Warming up llama3.2 model..."
echo "  Running test inference to load model into memory..."
curl -s -X POST http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello",
  "stream": false
}' > /dev/null
echo "✓ Model warmed up and ready"
echo ""

# Step 6: Display status
echo "========================================"
echo "Status: Ollama Ready for Labs"
echo "========================================"
echo ""
echo "Available models:"
ollama list
echo ""
echo "Ollama API endpoint: http://localhost:11434"
echo "Ollama PID: $OLLAMA_PID"
echo ""
echo "To stop Ollama later, run:"
echo "  kill $OLLAMA_PID"
echo "  or use: pkill ollama"
echo ""
echo "Ready for lab exercises!"
echo "========================================"
