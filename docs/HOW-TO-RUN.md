# 🚀 Correct Way to Run the System

## ❌ Wrong (what you tried):
```bash
python start_classification_system.sh
```

## ✅ Correct Ways:

### Option 1: Run the bash script directly
```bash
./start_classification_system.sh
```

### Option 2: Run with bash command
```bash
bash start_classification_system.sh
```

### Option 3: Manual start (2 terminals)

**Terminal 1 - Start Server:**
```bash
python3 mcp_server_classification.py
```

**Terminal 2 - Start Agent:**
```bash
python3 rag_agent2_classification.py
```

## Quick Fix for Your Current Directory

Run one of these commands:

```bash
# Make script executable and run
chmod +x start_classification_system.sh
./start_classification_system.sh
```

OR

```bash
# Run with bash directly
bash start_classification_system.sh
```

## File Types Explanation

- **`.sh`** files = Bash scripts → Run with `bash` or `./`
- **`.py`** files = Python scripts → Run with `python3`

## Expected Output

When you run it correctly, you should see:
```
🚀 Starting Classification-Based Canonical Queries System
======================================================
📋 Checking dependencies...
✅ Dependencies checked

🖥️ Starting MCP Classification Server...
   Server will run on: http://127.0.0.1:8000/mcp/
   Press Ctrl+C to stop both server and agent

✅ MCP Server started successfully (PID: XXXX)

🤖 Starting Classification Agent...
   Type 'demo' to see sample queries
   Type 'exit' to quit

RAG Agent with MCP Classification & Prompt Templates
Make sure mcp_server_classification.py is running first!
Type 'exit' to quit, 'demo' for sample queries.

Query: 
```