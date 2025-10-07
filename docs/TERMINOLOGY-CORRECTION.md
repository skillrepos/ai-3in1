# Terminology Correction: "Elicitation" → "Classification"

## Summary

The codebase has been updated to use accurate terminology that reflects what the system actually does. The previous use of "elicitation" was misleading since the implementation does not use formal MCP elicitation constructs.

## Files Renamed

- `mcp_server_elicitation.py` → `mcp_server_canonical.py`
- `rag_agent2_elicitation.py` → `rag_agent2_canonical.py` 
- `ELICITATION-ARCHITECTURE.md` → `CANONICAL-QUERY-ARCHITECTURE.md`

## Functions Renamed

- `elicit_canonical_query()` → `classify_canonical_query()`
- `handle_canonical_query_with_elicitation()` → `handle_canonical_query_with_classification()`

## Terminology Updated

| Old (Misleading) | New (Accurate) |
|------------------|----------------|
| Elicitation-Based RAG Agent | Canonical Query Classification Agent |
| elicitation workflow | classification workflow |
| elicitation process | classification process |
| elicitation tools | classification tools |

## What the System Actually Does

✅ **Pattern Matching**: Compares user queries to predefined example queries
✅ **Keyword Scoring**: Uses simple word overlap algorithms  
✅ **Rule-Based Classification**: Hard-coded logic for different query types
✅ **Template Substitution**: Basic string formatting for prompts

## What It Does NOT Do (Formal MCP Elicitation)

❌ **Sampling Protocols**: No MCP sampling mechanisms
❌ **Resource URIs**: No formal resource references
❌ **Structured Schemas**: No MCP-compliant response formats
❌ **LLM-based Elicitation**: No prompt-based elicitation

## To Run the System

```bash
# Start the classification server
python mcp_server_canonical.py

# Run the canonical query agent
python rag_agent2_canonical.py

# Or run the Streamlit web interface
streamlit run streamlit_app.py
```

The system now has accurate naming that reflects its actual implementation as a pattern-matching canonical query classification system.