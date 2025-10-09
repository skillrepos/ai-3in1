# Canonical Queries: Three Architectural Approaches

## 🏆 **RECOMMENDED**: Classification & Prompt Templates

Your insight about classification and prompt templates is spot-on! This represents the most sophisticated and scalable approach.

## Architecture Comparison

### **Approach 1: Agent-Only** ❌
```
┌─────────────────────────────────────┐
│             Agent                   │
│                                     │
│ • Query interpretation (LLM)       │
│ • Data loading & analysis           │
│ • Response formatting (LLM)        │
│ • All logic embedded in agent      │
└─────────────────────────────────────┘
```
**Problems**: Code duplication, tight coupling, hard to scale

### **Approach 2: Pure Data Tools** ⚠️  
```
┌─────────────────┐    ┌─────────────────┐
│   MCP Server    │    │      Agent      │
│                 │    │                 │
│ • Raw data      │◄───┤ • Query interp  │
│ • Calculations  │    │ • LLM calls     │
│ • No LLM calls  │    │ • Formatting    │
└─────────────────┘    └─────────────────┘
```
**Better**: Separates data from LLM, but query interpretation still ad-hoc

### **Approach 3: Classification & Templates** ✅
```
┌─────────────────┐    ┌─────────────────┐
│   MCP Server    │    │      Agent      │
│                 │    │                 │
│ • Query catalog │    │ • LLM execution │
│ • Classification│◄───┤ • Workflow      │
│ • Templates     │    │ • Results       │
│ • Raw data      │    │                 │
└─────────────────┘    └─────────────────┘
```
**Best**: Structured query interpretation + reusable templates

## Detailed Comparison

### Query Interpretation

| Approach | Method | Consistency | Scalability |
|----------|--------|-------------|-------------|
| Agent-Only | Ad-hoc LLM | Low | Poor |
| Pure Data | Ad-hoc LLM | Medium | Medium |
| **Classification** | **Structured server-side** | **High** | **Excellent** |

### Prompt Management

| Approach | Storage | Reusability | Versioning |
|----------|---------|-------------|------------|
| Agent-Only | Hardcoded | None | Manual |
| Pure Data | Hardcoded | None | Manual |
| **Templates** | **Server catalog** | **High** | **Centralized** |

### Development Experience

| Approach | New Queries | Testing | Maintenance |
|----------|-------------|---------|-------------|
| Agent-Only | Modify agent | Complex | Scattered |
| Pure Data | Add tool + agent code | Medium | Split |
| **Classification** | **Server config only** | **Easy** | **Centralized** |

## Classification Workflow

### 1. **Query Classification** 🔍
```python
# Client sends natural language
user_query = "What's our average revenue?"

# Server determines canonical query  
classification = await mcp.call_tool("classify_canonical_query", {
    "user_query": user_query
})
# Returns: {"suggested_query": "revenue_stats", "confidence": 0.8}
```

### 2. **Template Retrieval** 📝
```python  
# Client gets structured prompt template
template = await mcp.call_tool("get_query_template", {
    "query_name": "revenue_stats"
})
# Returns: {"template": "Analyze revenue data...", "data_requirements": [...]}
```

### 3. **Data Provision** 📊
```python
# Client gets required data
data = await mcp.call_tool("get_filtered_office_data", {
    "columns": ["revenue_million", "city"]
})
# Returns: {"data": [...], "count": 10}
```

### 4. **LLM Execution** 🤖
```python
# Client executes LLM with template + data (locally)
llm = ChatOllama(model="llama3.2")
response = llm.invoke([{
    "role": "user", 
    "content": template.format(data=json.dumps(data))
}])
```

## Benefits of Classification Approach

### **For Developers** 👨‍💻
- **New canonical queries**: Just add to server config
- **Consistent prompts**: Templates ensure uniform LLM behavior  
- **Easy testing**: Each component testable in isolation
- **Version control**: All query logic in server configuration

### **For Operations** 🏗️
- **Scalability**: Server handles query catalog for multiple agents
- **Monitoring**: Centralized query analytics and performance
- **Updates**: Deploy new queries without agent changes
- **Consistency**: Same query interpretation across all clients

### **For Users** 👥
- **Better accuracy**: Structured classification vs ad-hoc interpretation
- **Predictable results**: Template-driven LLM responses
- **Faster responses**: Pre-optimized queries and data access
- **Extensibility**: Easy to add new analysis capabilities

## Implementation Files

### **Classification Server** (`mcp_server_canonical.py`)
- 📋 Canonical query catalog with descriptions and examples
- 🔍 Intelligent query classification based on user input
- 📝 Prompt template management and parameter validation
- 📊 Filtered data access with requirements specification
- ✅ Query parameter validation and suggestions

### **Classification Agent** (`rag_agent2_canonical.py`)
- 🎯 Automatic query routing (weather vs data analysis)
- 🔗 Classification workflow orchestration
- 🤖 Local LLM execution with server-provided templates
- 📈 Consistent result formatting and error handling

## Adding New Canonical Queries

With the classification approach, adding new queries is trivial:

```python
# Just add to server configuration - no agent changes needed!
CANONICAL_QUERIES["market_analysis"] = {
    "description": "Analyze market performance by region",
    "parameters": [{"name": "region", "type": "str", "required": True}],
    "data_requirements": ["city", "state", "revenue_million", "employees"],
    "prompt_template": "Analyze market performance for {region}...",
    "example_queries": ["How is the West Coast performing?"]
}
```

## Conclusion

The **classification & prompt templates** approach represents the most sophisticated and scalable architecture:

1. **Separates concerns** properly: catalog/classification (server) vs execution (client)
2. **Enables reusability** through standardized query interpretation
3. **Provides consistency** via managed prompt templates  
4. **Scales elegantly** by centralizing query logic
5. **Simplifies development** by reducing agent complexity

This architecture transforms canonical queries from hardcoded agent logic into a **managed query service** that multiple agents can leverage consistently.

---

**For training purposes only. (C) 2025 Tech Skills Transformations and Brent C. Laster - all rights reserved.**