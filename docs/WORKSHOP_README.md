# AI Agent Workshop - Student Guide

## 🎯 What You'll Learn

In this workshop, you'll build a **real AI agent** that:
- Answers questions about business data
- Fetches live weather information
- Uses LLMs intelligently to understand and respond
- Connects to external APIs via MCP (Model Context Protocol)

## 📚 Workshop Structure

### Part 1: Understanding the Architecture (30 min)
- How AI agents work
- RAG (Retrieval-Augmented Generation) explained
- MCP and tool calling
- See: `docs/ARCHITECTURE.md`

### Part 2: The Core Agent (45 min)
- Query classification
- LLM decision making
- Data analysis workflow
- See: `docs/PSEUDOCODE_AGENT.md`

### Part 3: MCP Server (30 min)
- Building tool servers
- Weather API integration
- Error handling and retries
- See: `docs/PSEUDOCODE_MCP_SERVER.md`

### Part 4: User Interface (30 min)
- Streamlit basics
- Async UI patterns
- User experience design
- See: `docs/PSEUDOCODE_STREAMLIT.md`

### Part 5: Deployment (15 min)
- Running locally
- Docker containerization
- Hugging Face Spaces

## 🏗️ System Components

```
streamlit_app.py
    ↓ calls
rag_agent_canonical.py
    ↓ uses
┌─────────────────┬──────────────┬────────────┐
│                 │              │            │
Ollama LLM    Office CSV    MCP Server    ChromaDB
(llama3.2:1b)  (data/)    (port 8000)   (vector DB)
```

## 🚀 Quick Start

### Prerequisites

**Required Knowledge:**
- ✅ Basic Python programming (functions, classes, async/await)
- ✅ Familiarity with command line / terminal
- ✅ Understanding of CSV data and basic data structures
- ✅ Helpful but not required: REST APIs, web development basics

**Required Software:**
```bash
# Install Python 3.11
# Install Ollama: https://ollama.com/

# Pull the model
ollama pull llama3.2:1b
```

**Time Commitment:**
- Full workshop: 2.5 hours (including breaks)
- Hands-on exercises: 45 minutes
- Q&A and exploration: 30 minutes

### Run Locally
```bash
# Install dependencies
pip install -r requirements/requirements.txt

# Terminal 1: Start MCP server
python mcp_server_canonical.py

# Terminal 2: Start Streamlit
streamlit run streamlit_app.py
```

Visit http://localhost:8501

## 📖 Key Files Explained

### `rag_agent_canonical.py` - The Brain
This is the AI agent. It:
1. Classifies queries (data vs weather)
2. Uses LLM to understand intent
3. Executes structured queries
4. Generates natural responses

**Read the pseudo-code**: `docs/PSEUDOCODE_AGENT.md`

### `mcp_server_canonical.py` - The Tools
This provides external capabilities:
- Weather API access
- Temperature conversion
- Office data retrieval

**Read the pseudo-code**: `docs/PSEUDOCODE_MCP_SERVER.md`

### `streamlit_app.py` - The Interface
Simple web UI that:
- Takes user input
- Shows progress
- Displays results

**Read the pseudo-code**: `docs/PSEUDOCODE_STREAMLIT.md`

### `data/offices.csv` - The Data
Sample business data with:
- Office locations (cities)
- Employee counts
- Revenue figures
- Opening years

## 🧪 Try These Queries

### Data Analysis Queries
```
"Which office has the highest revenue?"
"What's the average revenue across all offices?"
"Which office has the most employees?"
"How many offices do we have?"
```

### Weather Queries
```
"What's the weather in Seattle?"
"Current weather in Tokyo"
```

## 🎓 Learning Exercises

### Exercise 1: Add a New Canonical Query
Add "lowest_employees" to find the smallest office.

1. Open `rag_agent_canonical.py`
2. Find the `analyze_offices()` function
3. Add a new elif block:
```python
elif q == "lowest_employees":
    idx = df["employees"].idxmin()
    return f"{df.loc[idx, 'city']} has fewest employees: {df.loc[idx, 'employees']}"
```
4. Test it!

### Exercise 2: Add More Office Data
1. Open `data/offices.csv`
2. Add a new office row
3. Test queries to see your new data

### Exercise 3: Customize the UI
1. Open `streamlit_app.py`
2. Change the page title
3. Add new example queries
4. Modify the CSS styling

### Exercise 4: Add a New MCP Tool
Create a tool that calculates revenue per employee.

1. Open `mcp_server_canonical.py`
2. Add a new tool decorator:
```python
@mcp.tool
def revenue_per_employee(city: str) -> float:
    """Calculate revenue per employee for a city"""
    # Your code here
```

## 🔍 Understanding the LLM's Role

The LLM (llama3.2:1b) is used in **3 key places**:

### 1. Query Intent Recognition
```
User: "Which office makes the most money?"
LLM thinks: "This asks about revenue → use 'highest_revenue' query"
```

### 2. Natural Language Generation
```
Raw data: "New York office has highest revenue: $62.10M"
LLM generates: "Based on our data, the New York office leads with $62.10 million in revenue, making it our top-performing location."
```

### 3. Weather Summaries
```
Data: "Seattle, 13.2°C, Overcast"
LLM generates: "The Seattle office is experiencing overcast conditions with a temperature of 55.8°F (13.2°C)."
```

## 🐛 Troubleshooting

### "Connection refused" to Ollama
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, pull the model
ollama pull llama3.2:1b
```

### "File not found: data/offices.csv"
```bash
# Make sure you're in the project root
cd /path/to/aiapp1

# Check the file exists
ls data/offices.csv
```

### MCP server not responding
```bash
# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9

# Restart the server
python mcp_server_canonical.py
```

## 🌟 Advanced Topics

### Custom LLM Models
Replace `llama3.2:1b` with other models:
- `llama3.2` (larger, smarter, slower)
- `phi3` (Microsoft's model)
- `mistral` (Mistral AI)

### Vector Search (RAG)
The weather workflow uses ChromaDB for semantic search.
Try adding documents to improve location matching.

### Production Deployment
- Add authentication
- Rate limiting
- Error monitoring
- Model caching

## 📝 Workshop Deliverables

By the end, you should be able to:
1. ✅ Explain how the agent makes decisions
2. ✅ Add new canonical queries
3. ✅ Modify the MCP server
4. ✅ Customize the UI
5. ✅ Deploy to Hugging Face Spaces

## 🎉 Next Steps

- Read the architecture docs in `docs/`
- Follow the pseudo-code guides
- Try the learning exercises
- Build your own agent!

## 💡 Tips for Success

1. **Read the pseudo-code first** before diving into Python
2. **Run the test script** (`python test_local.py`) to verify components
3. **Use the logs** - lots of helpful debug output
4. **Start simple** - modify existing code before writing new code
5. **Ask questions** - the instructor is here to help!

## 📚 Additional Resources

- [Ollama Documentation](https://ollama.com/docs)
- [Streamlit Docs](https://docs.streamlit.io/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Guide](https://gofastmcp.com/)
