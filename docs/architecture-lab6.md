# Lab 6 Architecture: Building a Classification MCP Server

## Overview
Lab 6 transforms the MCP server to use canonical query classification, creating a scalable architecture where the server manages query interpretation and templates.

## Detailed Architecture Diagram

```mermaid
graph TB
    subgraph "Classification MCP Server :8000"
        subgraph "Query Classification"
            Classifier[Keyword Classifier]
            Mapper[Query → Canonical Mapping]
        end

        subgraph "Canonical Query System"
            Queries[Canonical Queries: • revenue_stats • employee_analysis • efficiency_analysis • office_profile]
        end

        subgraph "Data Layer"
            CSV[(offices.csv)]
            Pandas[Pandas DataFrame]
        end

        subgraph "Tool Endpoints"
            Tool1[@mcp.tool classify_canonical_query]
            Tool2[@mcp.tool get_query_template]
            Tool3[@mcp.tool get_filtered_office_data]
            Tool4[@mcp.tool get_weather]
            Tool5[@mcp.tool geocode_location]
        end

        Classifier --> Mapper
        Mapper --> Queries
        Queries --> Tool2
        Pandas --> CSV

        Tool1 --> Classifier
        Tool3 --> Pandas
    end

    Client[Agent/Client] <-->|MCP Protocol| Tool1
    Client <-->|MCP Protocol| Tool2
    Client <-->|MCP Protocol| Tool3

    style Classifier fill:#e1f5ff
    style Queries fill:#fff4e1
    style Pandas fill:#e8f5e9
    style CSV fill:#ffe8e8
```

## Presentation Slide Diagram (Simple)

```mermaid
flowchart LR
    Query([Natural Language]) -->|1. Classify| Server[MCP Server Classification]
    Server -->|2. Map to| Canonical[Canonical Query]
    Canonical -->|3. Execute| Data[(CSV Data)]
    Data -->|4. Result| Answer([Structured Answer])

    style Server fill:#4CAF50,color:#fff
    style Canonical fill:#2196F3,color:#fff
    style Data fill:#FF9800,color:#fff
```

## Classification Flow

```mermaid
sequenceDiagram
    participant Agent
    participant MCP as MCP Server
    participant Classifier as Keyword Classifier
    participant Template as Template Engine
    participant Data as Data Layer
    participant LLM as Agent's LLM

    Note over Agent,MCP: Step 1: Classification
    Agent->>MCP: "Which office has the most employees?"
    MCP->>Classifier: classify_canonical_query()
    Classifier->>Classifier: Keyword matching & scoring
    Classifier->>MCP: {"suggested_query": "employee_analysis", "confidence": 0.85}
    MCP->>Agent: Classification result

    Note over Agent,MCP: Step 2: Get Template
    Agent->>MCP: get_query_template("employee_analysis")
    MCP->>Template: Fetch template & requirements
    Template->>MCP: {"template": "...", "data_requirements": ["employees", "city"]}
    MCP->>Agent: Template

    Note over Agent,Data: Step 3: Get Data
    Agent->>MCP: get_filtered_office_data(["employees", "city"])
    MCP->>Data: Load & filter CSV
    Data->>MCP: DataFrame → dict
    MCP->>Agent: {"data": [...], "count": 8}

    Note over Agent,LLM: Step 4: Execute LLM
    Agent->>LLM: Template + Data
    LLM->>LLM: Analyze & generate response
    LLM->>Agent: "New York office has the most employees (120)"
```

## Component Details

### 1. Canonical Query System

**Defined Queries:**
```python
CANONICAL_QUERIES = {
    "revenue_stats": {
        "description": "Calculate revenue statistics",
        "example_queries": ["What's the average revenue?",
                           "Which office has the highest revenue?"]
    },
    "employee_analysis": {
        "description": "Analyze employee distribution",
        "example_queries": ["Which office has the most employees?"]
    },
    "efficiency_analysis": {
        "description": "Calculate revenue per employee",
        "example_queries": ["Which office is most efficient?"]
    },
    "growth_analysis": {
        "description": "Analyze office growth patterns by year",
        "parameters": [{"name": "year_threshold", "type": "int"}],
        "example_queries": ["What offices opened after 2014?"]
    },
    "office_profile": {
        "description": "Detailed profile of a specific office",
        "parameters": [{"name": "city", "type": "str"}],
        "example_queries": ["Tell me about the Chicago office"]
    }
}
```

### 2. Keyword-Based Classifier

```python
@mcp.tool()
def classify_canonical_query(user_query: str) -> dict:
    """
    Classify which canonical query best matches user intent.

    Uses keyword matching and scoring to determine:
    "Which office makes the most money?" → "revenue_stats"
    "How many branches do we have?" → "employee_analysis"

    Returns:
        {"suggested_query": str, "confidence": float,
         "alternatives": list, "reason": str}
    """
    user_lower = user_query.lower()
    scores = {}

    # Score each canonical query based on keyword overlap
    for query_name, config in CANONICAL_QUERIES.items():
        score = 0
        examples = config["example_queries"]

        # Check keyword matches against example queries
        for example in examples:
            example_words = set(example.lower().split())
            user_words = set(user_lower.split())
            overlap = len(example_words.intersection(user_words))
            if overlap > 0:
                score += overlap / len(example_words)

        scores[query_name] = score

    best_query = max(scores, key=scores.get)
    confidence = min(scores[best_query], 1.0)

    return {
        "suggested_query": best_query,
        "confidence": confidence,
        "alternatives": [...],
        "reason": f"Best keyword match with confidence {confidence:.2f}"
    }
```

### 3. Template and Data Tools

The server provides prompt templates and data rather than executing queries:

```python
@mcp.tool
def get_query_template(query_name: str, city: str = None,
                       year_threshold: int = None) -> dict:
    """
    Get the prompt template for a canonical query.

    Returns:
        {"template": str, "data_requirements": list,
         "parameters_used": dict}
    """
    config = CANONICAL_QUERIES[query_name]
    template = config["prompt_template"]

    # Template contains {data} placeholder for client substitution
    return {
        "template": template,
        "data_requirements": config["data_requirements"],
        "parameters_used": parameters
    }

@mcp.tool
def get_filtered_office_data(columns: list = None,
                             filters: dict = None) -> dict:
    """
    Get filtered office data for specific analysis.

    Returns:
        {"data": list, "count": int, "filters_applied": dict}
    """
    df = pd.read_csv("data/offices.csv")

    # Apply filters and column selection
    # Return data as list of dicts
    return {
        "data": df.to_dict(orient="records"),
        "count": len(df),
        "columns": list(df.columns)
    }
```

### 4. Canonical Query Structure

```python
CANONICAL_QUERIES = {
    "revenue_stats": {
        "description": "Calculate revenue statistics across all offices",
        "parameters": [],
        "data_requirements": ["revenue_million", "city"],
        "prompt_template": """You are a financial analyst...
Office Revenue Data:
{data}

Please calculate and report:
1. Which office has the highest revenue
2. Which office has the lowest revenue
3. Average revenue across all offices
4. Total revenue across all offices""",
        "example_queries": [
            "What's the average revenue?",
            "Which office has the highest revenue?"
        ]
    },
    # ... more canonical queries
}
```

## Classification vs. Traditional Approach

```mermaid
graph TB
    subgraph "Traditional (Lab 3)"
        Q1[Query: Weather] --> T1[MCP Server]
        T1 --> W[Weather API]
        W --> R1[Result]
        Note1[Limited to predefined tools]
    end

    subgraph "Classification (Lab 6)"
        Q2[Query: Natural Language] --> C[Classify]
        C --> Can[Canonical Query]
        Can --> E[Execute]
        E --> CSV[(CSV Data)]
        CSV --> R2[Structured Result]
        Note2[Flexible, extensible system]
    end

    style C fill:#e1f5ff
    style Can fill:#fff4e1
    style E fill:#e8f5e9
```

## Data Flow: Complete Pipeline

1. **Natural Language Input**:
   ```
   "Which office has the highest revenue?"
   ```

2. **Classification** (Keyword-based):
   ```
   Keyword matching → Score queries → "revenue_stats" (confidence: 0.85)
   ```

3. **Template Retrieval**:
   ```python
   template = get_query_template("revenue_stats")
   # Returns: {
   #   "template": "You are a financial analyst...",
   #   "data_requirements": ["revenue_million", "city"]
   # }
   ```

4. **Data Retrieval**:
   ```python
   data = get_filtered_office_data(columns=["revenue_million", "city"])
   # Returns: {"data": [{city: "New York", revenue_million: 85.5}, ...]}
   ```

5. **LLM Execution** (Client-side):
   ```python
   prompt = template.format(data=json.dumps(data))
   response = llm.invoke(prompt)
   # Returns: "New York office has the highest revenue: $85.5 million."
   ```

## Query Mapping Examples

```mermaid
graph LR
    subgraph "Natural Language Variations"
        N1[Which office makes the most money?]
        N2[What's the highest revenue branch?]
        N3[Top earning office?]
        N4[Most profitable location?]
    end

    subgraph "Canonical Query"
        C[revenue_stats]
    end

    subgraph "Client LLM Execution"
        E[Template + Data → LLM Analysis]
    end

    N1 --> C
    N2 --> C
    N3 --> C
    N4 --> C
    C --> E

    style C fill:#e1f5ff
    style E fill:#e8f5e9
```

## Architecture Benefits

### 1. Separation of Concerns
```mermaid
graph LR
    subgraph "Client Responsibilities"
        C1[Natural Language]
        C2[Display Results]
    end

    subgraph "Server Responsibilities"
        S1[Query Classification]
        S2[Template Management]
        S3[Data Access]
    end

    C1 --> S1
    S3 --> C2

    style C1 fill:#e8f5e9
    style S1 fill:#e1f5ff
```

### 2. Extensibility
Add new canonical queries without changing client:
```python
# Server side only - add new query definition
CANONICAL_QUERIES["team_size_analysis"] = {
    "description": "Analyze team size distribution",
    "parameters": [],
    "data_requirements": ["employees", "city"],
    "prompt_template": """Analyze team sizes:
{data}

Provide insights on team size distribution and patterns.""",
    "example_queries": [
        "How big are our teams?",
        "Show me team size analysis"
    ]
}
```

### 3. Consistency
Templates ensure structured, predictable LLM responses:
```
Template structure:
- System prompt (role/context)
- Data placeholder {data}
- Specific instructions (what to calculate/report)
- Output format guidance
```

## Key Differences from Lab 3

| Aspect | Lab 3 (Tools) | Lab 6 (Classification) |
|--------|---------------|----------------------|
| Query Type | Tool names | Natural language |
| Processing | Direct execution | Classify → Template → Data → Execute |
| Data Source | External APIs | Local CSV |
| Flexibility | Fixed tools | Extensible queries |
| Complexity | Low | Medium-High |
| LLM Usage | None (in server) | Client-side (for analysis) |
| Classification | None | Keyword-based |
| Server Role | Execute tools | Classify + Provide templates/data |
| Client Role | Call tools | Execute LLM with templates |

## Canonical Query Benefits

1. **Structured Queries**: Predefined, testable operations
2. **Data Validation**: Type-safe query parameters
3. **Performance**: Direct DataFrame operations
4. **Maintainability**: Clear query definitions
5. **Extensibility**: Easy to add new canonical queries
6. **Consistency**: Predictable response formats

## Implementation Patterns

### Pattern 1: Keyword Scoring
```python
def classify_canonical_query(user_query: str) -> dict:
    user_lower = user_query.lower()
    scores = {}

    for query_name, config in CANONICAL_QUERIES.items():
        score = 0
        # Score based on example query overlap
        for example in config["example_queries"]:
            example_words = set(example.lower().split())
            user_words = set(user_lower.split())
            overlap = len(example_words.intersection(user_words))
            if overlap > 0:
                score += overlap / len(example_words)

        scores[query_name] = score

    best_query = max(scores, key=scores.get)
    return {"suggested_query": best_query, "confidence": scores[best_query]}
```

### Pattern 2: Template with Parameters
```python
# Template has placeholders for both data and parameters
template = """Analyze offices opened after {year_threshold}.

Data: {data}

Provide growth insights..."""

# Server substitutes parameters, leaves {data} for client
formatted = template.format(year_threshold=2014)
# Client later substitutes {data} with actual office records
```

## Key Learning Points
- **Query Classification**: Natural language → Canonical form via keyword matching
- **Canonical Queries**: Predefined query definitions with templates
- **Template System**: Structured prompts for consistent LLM responses
- **Separation of Concerns**: Server classifies & provides templates, client executes LLM
- **Data Requirements**: Templates specify what data columns are needed
- **Client-Side LLM**: LLM execution happens on client with server-provided templates
- **Extensibility**: Add new canonical queries by updating server config only

## Architecture Characteristics
- **Type**: Classification-based query system
- **Complexity**: Medium-High
- **Dependencies**: FastMCP, Pandas, Ollama
- **Data Source**: CSV files (local)
- **Latency**: ~1-2 seconds (keyword classification + template/data retrieval)
- **Scalability**: Add queries without client changes
- **Flexibility**: Handles natural language variations

## Use Cases
1. **Business Analytics**: Query structured business data
2. **Data Exploration**: Natural language data queries
3. **Reporting**: Standardized query responses
4. **Multi-client Systems**: One server, many clients
5. **Version Management**: Server handles query evolution
