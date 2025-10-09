# Canonical Query Architecture: Building Intelligent AI Systems

## Overview

This document explains the **canonical query pattern** - a structured approach to building AI systems that handle business data queries. This pattern is implemented in **Lab 6** (Classification MCP Server) and **Lab 7** (Multi-Workflow Agent).

---

## Three Architectural Approaches

### Approach 1: Agent-Only Architecture

```mermaid
graph TB
    subgraph "Agent-Only Approach"
        Query[User Query] --> Agent[Single Agent]
        Agent --> Interpret[Query Interpretation LLM]
        Agent --> DataLoad[Data Loading]
        Agent --> Analysis[Analysis Logic]
        Agent --> Format[Response Formatting LLM]
        Format --> Response[Response]
    end

    style Agent fill:#ff6b6b,color:#fff
    style Interpret fill:#ffe8e8
    style Analysis fill:#ffe8e8
```

**Problems:**
- All logic embedded in one agent
- Code duplication across queries
- Tight coupling - hard to modify
- Difficult to scale

---

### Approach 2: Pure Data Tools

```mermaid
graph LR
    Query[User Query] --> Agent[Agent]
    Agent --> LLM1[LLM: Interpret Query]
    LLM1 --> MCP[MCP Server]
    MCP --> Data[Raw Data Tools]
    Data --> Calc[Calculations]
    Calc --> Agent
    Agent --> LLM2[LLM: Format Response]
    LLM2 --> Response[Response]

    style Agent fill:#ffd93d,color:#000
    style MCP fill:#fff4e1
```

**Better, but:**
- Query interpretation still ad-hoc
- Each agent must figure out which tool to use
- No standardized query patterns

---

### Approach 3: Classification & Templates (Labs 6 & 7)

```mermaid
graph LR
    Query[User Query] --> Server[MCP Server]
    Server --> Classify[Classification System]
    Server --> Templates[Template Catalog]
    Server --> Data[Structured Data]
    Server --> Vector[Vector Search]

    Classify --> Agent[Agent]
    Templates --> Agent
    Data --> Agent
    Vector --> Agent

    Agent --> LLM[LLM: Execute with Template]
    LLM --> Response[Response]

    style Server fill:#4CAF50,color:#fff
    style Classify fill:#2196F3,color:#fff
    style Templates fill:#FF9800,color:#fff
```

**Best approach:**
- Structured query interpretation
- Reusable templates
- Centralized query logic
- Server manages classification and data

---

## Lab 6: Classification MCP Server

### High-Level Architecture

```mermaid
flowchart LR
    Query([Natural Language]) -->|1. Classify or Search| Server[MCP Server]
    Server -->|2a. Canonical Query| Canonical[Structured Data CSV]
    Server -->|2b. Vector Search| Vector[Semantic Search ChromaDB]
    Canonical -->|3. Result| Answer([Answer])
    Vector -->|3. Result| Answer

    style Server fill:#4CAF50,color:#fff
    style Canonical fill:#2196F3,color:#fff
    style Vector fill:#FF9800,color:#fff
```

### Key Components

#### 1. Classification System (Keyword-Based)
- Maps natural language to canonical queries
- Uses keyword scoring and matching
- Returns confidence levels

#### 2. Canonical Query Catalog
```mermaid
graph TB
    Catalog[Canonical Query Catalog]
    Catalog --> Rev[revenue_stats]
    Catalog --> Emp[employee_analysis]
    Catalog --> Eff[efficiency_analysis]
    Catalog --> Prof[office_profile]

    Rev --> RevDesc[Calculate revenue statistics]
    Emp --> EmpDesc[Analyze employee distribution]
    Eff --> EffDesc[Revenue per employee metrics]
    Prof --> ProfDesc[Detailed office information]

    style Catalog fill:#4CAF50,color:#fff
    style Rev fill:#2196F3,color:#fff
    style Emp fill:#2196F3,color:#fff
    style Eff fill:#2196F3,color:#fff
    style Prof fill:#2196F3,color:#fff
```

#### 3. Vector Database Layer
- **Two collections**: Locations (PDF) and Analytics (CSV)
- **Semantic search**: Finds relevant data beyond keywords
- **Fuzzy matching**: Handles variations like "HQ" vs "headquarters"

#### 4. MCP Tools Provided
1. `classify_canonical_query()` - Classify user intent
2. `get_query_template()` - Get prompt template
3. `get_filtered_office_data()` - Get structured CSV data
4. `vector_search_locations()` - Search PDF embeddings
5. `vector_search_analytics()` - Search CSV embeddings
6. `get_weather()` - Weather API
7. `geocode_location()` - Location to coordinates

---

## Lab 7: Multi-Workflow Routing Agent

### High-Level Architecture

```mermaid
flowchart TD
    Query([User Query]) -->|Detect Intent| Router{Intent Router}
    Router -->|Data Query| Path1[Classification Workflow]
    Router -->|Weather Query| Path2[RAG Workflow]

    Path1 -->|MCP Tools| Server[MCP Server]
    Path2 -->|MCP + RAG| Server

    Server --> Result([Answer])

    style Router fill:#FF9800,color:#fff
    style Path1 fill:#4CAF50,color:#fff
    style Path2 fill:#2196F3,color:#fff
    style Server fill:#9C27B0,color:#fff
```

### Dual Workflow System

#### Workflow 1: Classification (Structured Data)

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant MCP
    participant LLM

    User->>Agent: "Which office has highest revenue?"
    Agent->>MCP: classify_canonical_query()
    MCP->>Agent: "revenue_stats"
    Agent->>MCP: get_query_template()
    MCP->>Agent: Template + requirements
    Agent->>MCP: get_filtered_office_data()
    MCP->>Agent: Structured data
    Agent->>LLM: Execute template + data
    LLM->>User: "New York: $85.5M"
```

**Best for:**
- Structured business data (CSV/SQL)
- Predictable questions
- Numerical analysis
- Fast, accurate responses

---

#### Workflow 2: RAG (Unstructured Data)

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant VDB as Vector DB
    participant MCP
    participant LLM

    User->>Agent: "Weather at Paris office?"
    Agent->>VDB: Search "Paris office"
    VDB->>Agent: "Paris, 48.8566, 2.3522"
    Agent->>MCP: get_weather(48.8566, 2.3522)
    MCP->>Agent: Weather data
    Agent->>LLM: Generate summary
    LLM->>User: "Paris: 72°F, Clear"
```

**Best for:**
- Unstructured documents
- Semantic search needs
- External API calls
- Open-ended queries

---

## Classification Workflow (Step-by-Step)

### Step 1: Natural Language Input

```
User Query: "What's our average revenue?"
```

### Step 2: Classification

```mermaid
flowchart LR
    Input[User Query] --> Keywords[Extract Keywords]
    Keywords --> Match[Match to Examples]
    Match --> Score[Calculate Scores]
    Score --> Best[Best Match: revenue_stats]

    style Best fill:#4CAF50,color:#fff
```

**Server returns:**
```json
{
  "suggested_query": "revenue_stats",
  "confidence": 0.85,
  "alternatives": ["efficiency_analysis"]
}
```

### Step 3: Get Template

```mermaid
flowchart LR
    Request[get_query_template] --> Fetch[Fetch from Catalog]
    Fetch --> Template[Return Template]
    Template --> Requirements[Data Requirements]

    style Template fill:#FF9800,color:#fff
```

**Server returns:**
```json
{
  "template": "Analyze revenue data: {data}\n\nCalculate:\n1. Average\n2. Highest\n3. Total",
  "data_requirements": ["revenue_million", "city"]
}
```

### Step 4: Get Data

```mermaid
flowchart LR
    Request[get_filtered_office_data] --> Filter[Apply Filters]
    Filter --> Select[Select Columns]
    Select --> Return[Return JSON]

    style Return fill:#2196F3,color:#fff
```

**Server returns:**
```json
{
  "data": [
    {"city": "New York", "revenue_million": 85.5},
    {"city": "Chicago", "revenue_million": 62.3}
  ],
  "count": 8
}
```

### Step 5: Execute LLM (Client-Side)

```mermaid
flowchart LR
    Template[Template] --> Combine[Combine with Data]
    Data[Data] --> Combine
    Combine --> LLM[Local LLM]
    LLM --> Response[Natural Response]

    style LLM fill:#9C27B0,color:#fff
    style Response fill:#4CAF50,color:#fff
```

**LLM produces:**
```
Based on our office data:
- Average revenue: $68.4M
- Highest: New York at $85.5M
- Total revenue: $547.2M across 8 offices
```

---

## Comparison: Three Approaches

### Query Interpretation

| Approach | Method | Consistency | Scalability |
|----------|--------|-------------|-------------|
| Agent-Only | Ad-hoc LLM | ⚠️ Low | ❌ Poor |
| Pure Data Tools | Ad-hoc LLM | ⚠️ Medium | ⚠️ Medium |
| **Classification** | **Structured** | ✅ **High** | ✅ **Excellent** |

### Template Management

| Approach | Storage | Reusability | Versioning |
|----------|---------|-------------|------------|
| Agent-Only | Hardcoded | ❌ None | Manual |
| Pure Data Tools | Hardcoded | ❌ None | Manual |
| **Classification** | **Server** | ✅ **High** | ✅ **Centralized** |

### Development Experience

| Approach | Add New Query | Testing | Maintenance |
|----------|--------------|---------|-------------|
| Agent-Only | Modify agent code | Complex | Scattered |
| Pure Data Tools | Agent + Server changes | Medium | Split |
| **Classification** | **Server config only** | ✅ **Easy** | ✅ **Centralized** |

---

## Benefits of Classification Approach

### For Developers
- **Easy to extend**: Add queries via server config
- **Consistent patterns**: Templates ensure uniform behavior
- **Isolated testing**: Test classification, templates, and data separately
- **Version control**: All query logic in one place

### For Operations
- **Scalable**: One server serves multiple agents
- **Centralized monitoring**: Track query usage and performance
- **Easy updates**: Deploy new queries without changing agents
- **Consistent quality**: Same query interpretation everywhere

### For Users
- **Better accuracy**: Structured classification vs guessing
- **Predictable results**: Templates ensure consistent answers
- **Faster responses**: Pre-optimized queries
- **More capabilities**: Easy to add new analysis types

---

## Adding New Canonical Queries

### Server-Side Only (No Agent Changes!)

```python
# In MCP server configuration
CANONICAL_QUERIES["market_analysis"] = {
    "description": "Analyze market performance by region",
    "parameters": [
        {"name": "region", "type": "str", "required": True}
    ],
    "data_requirements": ["city", "state", "revenue_million", "employees"],
    "prompt_template": """
        Analyze market performance for {region}.

        Data: {data}

        Provide:
        1. Total revenue for region
        2. Number of offices
        3. Average office size
        4. Growth trends
    """,
    "example_queries": [
        "How is the West Coast performing?",
        "Show me East Coast market analysis",
        "Analyze Southern region performance"
    ]
}
```

**That's it!** The classification system automatically:
- Recognizes queries matching the examples
- Provides the template to agents
- Supplies the required data
- Validates parameters

---

## Architecture Evolution

```mermaid
graph LR
    Lab1[Lab 1: Local LLM] --> Lab2[Lab 2: Simple Agent]
    Lab2 --> Lab3[Lab 3: MCP Tools]
    Lab3 --> Lab6[Lab 6: Classification]
    Lab6 --> Lab7[Lab 7: Multi-Workflow]

    Lab3 --> Lab4[Lab 4: Vectors]
    Lab4 --> Lab5[Lab 5: RAG]
    Lab5 --> Lab7

    style Lab6 fill:#4CAF50,color:#fff
    style Lab7 fill:#FF9800,color:#fff
```

**Lab 6**: Classification system with dual data sources (structured + semantic)

**Lab 7**: Intelligent routing between classification and RAG workflows

---

## Key Takeaways

### 1. Separation of Concerns
```mermaid
graph TB
    Server[MCP Server] --> Class[Classification]
    Server --> Templates[Template Management]
    Server --> Data[Data Access]
    Server --> Vector[Vector Search]

    Agent[Agent] --> Route[Workflow Routing]
    Agent --> Execute[LLM Execution]
    Agent --> Format[Response Formatting]

    style Server fill:#4CAF50,color:#fff
    style Agent fill:#2196F3,color:#fff
```

**Server responsibilities**: Query catalog, classification, templates, data
**Agent responsibilities**: Workflow selection, LLM execution, user interaction

### 2. Extensibility
- Add new canonical queries without changing agent code
- Update templates without redeploying agents
- Centralized query evolution

### 3. Consistency
- Every agent uses same classification logic
- Templates ensure uniform LLM prompts
- Standardized data access patterns

### 4. Scalability
- One server supports unlimited agents
- Cached classifications and templates
- Efficient data access

### 5. Intelligent Routing (Lab 7)
- Automatically chooses best workflow
- Structured queries → Classification
- Unstructured queries → RAG
- Optimal performance for each query type

---

## Summary

The **canonical query architecture** transforms AI systems from ad-hoc implementations into **managed, scalable services**:

✅ **Structured classification** replaces guessing
✅ **Template management** ensures consistency
✅ **Centralized logic** simplifies development
✅ **Multi-workflow routing** optimizes performance
✅ **Server-side intelligence** enables reusability

This pattern is production-ready and scales from single agents to enterprise deployments.

---

**For training purposes only. (C) 2025 Tech Skills Transformations and Brent C. Laster - all rights reserved.**
