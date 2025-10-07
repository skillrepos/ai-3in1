# AI Agent Architecture Overview

## System Components

This application demonstrates a **multi-agent AI system** with the following components:

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                   (Streamlit Web App)                       │
│                   streamlit_app.py                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP (localhost:8501)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAG AGENT                                 │
│              (rag_agent_canonical.py)                       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Query      │  │  Canonical   │  │   Weather    │    │
│  │ Classifier   │  │    Query     │  │   Workflow   │    │
│  │              │  │   Handler    │  │   (RAG)      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└──────────────┬──────────────┬──────────────┬──────────────┘
               │              │              │
        ┌──────┴──────┐       │       ┌──────┴──────┐
        │             │       │       │             │
        ▼             ▼       ▼       ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Ollama LLM  │ │  ChromaDB   │ │Office Data  │ │ MCP Server  │
│ llama3.2:1b │ │  (vectors)  │ │  (CSV)      │ │ Port 8000   │
│ Port 11434  │ │ chroma_db/  │ │ data/       │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └──────┬──────┘
                                                        │
                                                        ▼
                                                ┌─────────────┐
                                                │ Open-Meteo  │
                                                │ Weather API │
                                                └─────────────┘
```

### Detailed Component Breakdown

```
LAYER 1: PRESENTATION
┌────────────────────────────────────┐
│ streamlit_app.py                   │
│ - User input handling              │
│ - Progress visualization           │
│ - Result display                   │
│ - Error handling UI                │
└────────────────────────────────────┘

LAYER 2: ORCHESTRATION
┌────────────────────────────────────┐
│ rag_agent_canonical.py             │
│ - Query classification             │
│ - Workflow routing                 │
│ - LLM integration                  │
│ - Response generation              │
└────────────────────────────────────┘

LAYER 3: DATA & TOOLS
┌──────────┬──────────┬──────────────┐
│ CSV Data │ ChromaDB │ MCP Server   │
│ Offices  │ Vectors  │ 8 Tools      │
└──────────┴──────────┴──────────────┘

LAYER 4: AI & EXTERNAL APIs
┌────────────────┬───────────────────┐
│ Ollama LLM     │ Weather APIs      │
│ Local inference│ External data     │
└────────────────┴───────────────────┘
```

## Key Concepts for Students

### 1. **RAG (Retrieval-Augmented Generation)**
- Combines database retrieval with AI generation
- First: Find relevant data
- Then: Use AI to interpret and present it

### 2. **Canonical Queries**
- Structured, predefined queries (like "highest_revenue", "most_employees")
- Converts natural language → structured query → data analysis

### 3. **LLM Agent**
- Uses AI model (Ollama) to:
  - Understand user intent
  - Choose the right query
  - Generate natural language responses

### 4. **MCP (Model Context Protocol)**
- Standard way for AI to call external tools
- Our MCP server provides weather data

## Data Flow

```
User Question
    ↓
Query Classifier (LLM decides: data query or weather?)
    ↓
┌───────────────┴───────────────┐
│                               │
Data Analysis Path         Weather Path
│                               │
Load CSV Data              RAG Vector Search
↓                               ↓
LLM picks canonical query  Extract Location
↓                               ↓
Execute query on data      Call MCP Weather API
↓                               ↓
LLM generates response     LLM generates summary
│                               │
└───────────────┬───────────────┘
                ↓
         Display to User
```

## Why Two Different Workflows?

This system uses **two distinct approaches** for different types of queries. Understanding why helps you design better AI systems.

### Canonical Query Workflow (Data Analysis)
**Best for: Structured data analysis**

```
Example: "Which office has the highest revenue?"
```

**Why this approach?**
- Data is structured (CSV with consistent columns)
- Questions are predictable (revenue, employees, counts)
- Accuracy is critical (business decisions depend on correct numbers)
- Fast execution (no need to search large documents)

**How it works:**
1. LLM understands intent: "User wants highest revenue"
2. Maps to canonical query: `highest_revenue`
3. Executes predefined analysis on CSV data
4. LLM formats the result naturally

**Benefit:** Reliable, fast, and accurate for structured business data.

---

### RAG Weather Workflow (Document Search + External API)
**Best for: Unstructured data + external lookups**

```
Example: "What's the weather in Seattle?"
```

**Why this approach?**
- No structured database of weather info
- Location might be mentioned in documents
- Needs real-time external API call
- Requires semantic search to find location

**How it works:**
1. Vector search finds documents mentioning location
2. Extract location from unstructured text
3. Call external weather API via MCP
4. LLM generates natural summary

**Benefit:** Handles unstructured data and external integrations.

---

### When to Use Each Approach?

| Use Canonical Queries When: | Use RAG Workflow When: |
|------------------------------|------------------------|
| ✅ Data is structured (CSV, SQL) | ✅ Data is unstructured (docs, text) |
| ✅ Questions are predictable | ✅ Questions are open-ended |
| ✅ Accuracy is critical | ✅ Semantic search is needed |
| ✅ Fast responses needed | ✅ External APIs required |

**Key Insight:** The best AI systems combine multiple approaches based on the task at hand!

## Workshop Learning Objectives

Students will learn:
1. How to build an AI agent that uses real data
2. How to integrate LLMs with structured databases
3. How to use MCP to extend AI capabilities
4. How to classify and route different types of queries
5. How to present AI responses in a user-friendly interface
6. **When to use canonical queries vs. RAG workflows**
