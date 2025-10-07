# 🚀 How to Run the Classification-Based Canonical Queries System

## Prerequisites ✅

1. **Install dependencies:**
```bash
pip install pandas litellm chromadb sentence-transformers fastmcp langchain-ollama
```

2. **Check office data exists:**
```bash
ls data/offices.csv
# Should show: data/offices.csv
```

3. **Ensure Ollama is running (for LLM calls):**
```bash
ollama serve
ollama pull llama3.2
```

## Method 1: Automatic Start (Recommended) 🎯

```bash
# One command starts everything
./start_classification_system.sh
```

**What this does:**
- ✅ Checks dependencies
- 🖥️ Starts MCP server in background  
- 🤖 Starts interactive agent
- 🛑 Cleans up when you exit

## Method 2: Manual Start (Step by Step) 📋

### Terminal 1: Start MCP Server
```bash
python3 mcp_server_classification.py
```

**Expected output:**
```
Starting Canonical Query Classification MCP Server...
Available tools:
  🌤️ Weather: get_weather, convert_c_to_f  
  🔍 Classification: list_canonical_queries, classify_canonical_query
  📋 Templates: get_query_template, validate_query_parameters
  📊 Data: get_office_dataset, get_filtered_office_data

Server endpoint: POST http://127.0.0.1:8000/mcp/
```

### Terminal 2: Start Agent
```bash
python3 rag_agent2_classification.py
```

**Expected output:**
```
RAG Agent with MCP Classification & Prompt Templates
Make sure mcp_server_classification.py is running first!
Type 'exit' to quit, 'demo' for sample queries.

Query: 
```

## Sample Queries to Try 💬

### Data Analysis Queries
```
What's the average revenue across our offices?
Which office has the most employees?
Tell me about the Chicago office
What offices opened after 2014?
Which office is most efficient?
Show me revenue statistics
```

### Weather Queries (if you have RAG data)
```
What's the weather like at our Paris office?
How's the weather in New York?
```

### Demo Mode
Type `demo` to see all sample queries run automatically.

## Example Session 🎬

```
Query: What's the average revenue?

🔍 Classifying canonical query...
📋 Suggested query: revenue_stats (confidence: 0.80)
📝 Getting prompt template...
📊 Fetching data: ['revenue_million']
🤖 Executing LLM with template...

Based on the office revenue data analysis:

**Revenue Statistics Summary:**

1. **Average Revenue**: $44.50 million across all offices
2. **Revenue Range**: $18.2M (minimum) to $85.5M (maximum) 
3. **Total Portfolio**: $445.0 million across 10 offices
4. **Performance Distribution**: Shows healthy diversity with our flagship New York office leading at $85.5M, while our newer locations like Miami ($18.2M) represent growth opportunities.

The portfolio demonstrates strong performance with most offices generating substantial revenue above $20M annually.

Query: exit
```

## Troubleshooting 🔧

### "Connection refused" error
```
❌ Error calling MCP server: Connection refused
```
**Solution**: Make sure the MCP server is running first in another terminal.

### "Office data not found" error
```
❌ Office data not found at data/offices.csv
```
**Solution**: Make sure you're in the correct directory and the CSV file exists.

### "No module named X" error
```
❌ ModuleNotFoundError: No module named 'pandas'
```
**Solution**: Install dependencies:
```bash
pip install pandas litellm chromadb sentence-transformers fastmcp langchain-ollama
```

### LLM connection issues  
```
❌ Could not connect to Ollama
```
**Solution**: Start Ollama:
```bash
ollama serve
ollama pull llama3.2
```

## System Architecture 🏗️

```
User Query
    ↓
┌─────────────────────┐    ┌──────────────────────┐
│  MCP Server         │    │  Agent               │
│  (Port 8000)        │    │                      │
│                     │    │ 1. Route query       │
│ 🔍 Classify query   │◄───┤ 2. Call classification  │
│ 📝 Return template  │    │ 3. Get template      │
│ 📊 Provide data     │    │ 4. Retrieve data     │
│                     │    │ 5. Execute LLM       │
│ (No LLM calls)      │    │ 6. Format response   │
└─────────────────────┘    └──────────────────────┘
                                  ↓
                            Formatted Response
```

## Key Benefits 🌟

- **Consistent**: Template-driven LLM responses
- **Scalable**: New queries added server-side only
- **Testable**: Each component tested independently  
- **Maintainable**: Centralized query logic
- **Reusable**: Multiple agents can share the same server

## Adding New Queries 📈

Edit `mcp_server_classification.py` and add to `CANONICAL_QUERIES`:

```python
CANONICAL_QUERIES["new_analysis"] = {
    "description": "Your new analysis type",
    "parameters": [],
    "data_requirements": ["column1", "column2"],
    "prompt_template": "Your LLM prompt template here...",
    "example_queries": ["Example query 1", "Example query 2"]
}
```

Restart the server and the new query is available automatically!

## Files Overview 📁

- **`mcp_server_classification.py`** - MCP server with classification & templates
- **`rag_agent2_classification.py`** - Agent using classification workflow
- **`start_classification_system.sh`** - Automated startup script
- **`test_classification_system.py`** - Test suite
- **`QUICKSTART.md`** - This guide!