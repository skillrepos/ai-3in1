# 🚨 Quick Fix Guide for Common Issues

Based on your error, here are the **immediate fixes** needed:

## ✅ **What's Working:**
- ✅ Office data is loaded correctly
- ✅ Dependencies are installed  
- ✅ Paris city extraction is working

## ❌ **What Needs Fixing:**

### 1. **Ollama Not Running** 🔥
**Error:** `Connection refused` when calling LLM

**Fix:**
```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull llama3.2

# Verify it's working
ollama list
```

### 2. **MCP Server Not Running** 🔥  
**Error:** `Client failed to connect: All connection attempts failed`

**Fix:**
```bash
# Start the MCP server first
python3 mcp_server_classification.py
```

## 🚀 **Correct Startup Sequence:**

### Terminal 1: Start Ollama
```bash
ollama serve
# Keep this running
```

### Terminal 2: Start MCP Server  
```bash
python3 mcp_server_classification.py
# Should show: Starting Canonical Query Classification MCP Server...
```

### Terminal 3: Start Agent
```bash
python3 rag_agent2_classification.py
# Should show: RAG Agent with MCP Classification & Prompt Templates
```

## 🧪 **Test Before Running:**
```bash
# Run diagnostics to check everything
python3 simple_test.py
```

## 📋 **Expected Working Flow:**

1. **Start Ollama:** `ollama serve`
2. **Start MCP Server:** `python3 mcp_server_classification.py`  
3. **Start Agent:** `python3 rag_agent2_classification.py`
4. **Test Query:** `What's the average revenue?`

## ⚠️ **Why the Errors Happened:**

1. **"float object has no attribute 'get'"** - Fixed by adding type checking
2. **"Geocoding 'What'"** - Fixed by improving city extraction  
3. **"Connection refused"** - Ollama not running
4. **MCP connection failed** - Server not started first

## 🎯 **Quick Test:**

After starting all services, try:
```
Query: What's the average revenue?
```

Should show:
```
📊 Detected data analysis query, using classification workflow...
🔍 Classifying canonical query...
📋 Suggested query: revenue_stats (confidence: 0.80)
📝 Getting prompt template...
📊 Fetching data: ['revenue_million']
🤖 Executing LLM with template...
[Response about revenue statistics]
```

## 🔧 **Still Having Issues?**

Run the diagnostic: `python3 simple_test.py`

It will tell you exactly what's broken and how to fix it!