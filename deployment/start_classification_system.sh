#!/bin/bash
# start_classification_system.sh - Quick start script for the classification-based canonical queries system

echo "Starting Classification-Based Canonical Queries System"
echo "======================================================"

# Set environment variable for deployment (use 1b model)
export OLLAMA_MODEL=${OLLAMA_MODEL:-llama3.2:1b}
echo "Using model: $OLLAMA_MODEL"
echo

# Check if required dependencies are installed
echo "📋 Checking dependencies..."
python3 -c "import pandas, litellm, chromadb, sentence_transformers, fastmcp, langchain_ollama" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install pandas litellm chromadb sentence-transformers fastmcp langchain-ollama
fi

# Check if office data exists
if [ ! -f "data/offices.csv" ]; then
    echo "❌ Office data not found at data/offices.csv"
    echo "Please ensure the office data file exists before running."
    exit 1
fi

echo "✅ Dependencies checked"
echo

# Start the MCP server in the background
echo "🖥️  Starting MCP classification Server..."
echo "   Server will run on: http://127.0.0.1:8000/mcp/"
echo "   Press Ctrl+C to stop both server and agent"
echo

# Kill any existing server on port 8000
pkill -f "mcp_server_classification.py" 2>/dev/null

# Start server and capture its PID
python3 mcp_server_classification.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Check if server started successfully
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ MCP Server started successfully (PID: $SERVER_PID)"
    echo
    
    # Start the agent
    echo "Starting classification Agent..."
    echo "   Type 'demo' to see sample queries"
    echo "   Type 'exit' to quit"
    echo
    
    # Set up cleanup on script exit
    trap "echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null; exit 0" INT TERM
    
    # Run the agent (this will block until user exits)
    python3 rag_agent_classification.py
    
    # Clean up server when agent exits
    echo "Stopping server..."
    kill $SERVER_PID 2>/dev/null
else
    echo "❌ Failed to start MCP Server"
    exit 1
fi
