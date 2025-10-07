# PDF Integration for Office Weather Queries

## Summary

Successfully integrated PDF reading functionality from Lab 5 into the canonical query classification agents, enabling natural language queries about office locations like "What's the weather at HQ?".

## What Was Added

### 📄 **PDF Processing**
- Automatic extraction of office data from `data/offices.pdf`
- ChromaDB vector database population on first run
- Semantic search capabilities for office information

### 🏢 **Office Data Integration**
```python
def populate_vector_db_from_pdf(collection: chromadb.Collection):
    """Extract text from offices.pdf and populate ChromaDB."""
    # Extracts office information including:
    # - Office names (HQ, West Coast Hub, etc.)
    # - Addresses and locations
    # - Employee counts and revenue data
```

### 🔍 **Enhanced Weather Queries**
```python
async def handle_weather_query(user_query: str) -> str:
    """Handle weather-related queries using RAG workflow with vector search."""
    # 1. Search vector database for office info
    # 2. Extract location from office data + user query
    # 3. Get weather via MCP tools
    # 4. Generate contextual response with LLM
```

## Files Updated

| File | Changes |
|------|---------|
| `rag_agent2_canonical.py` | ✅ Added PDF vector search |
| `rag_agent2_canonical_with_prompts.py` | ✅ Added PDF vector search |

## Example Queries Now Supported

### 🎯 **Office-Based Weather Queries**
```
"What's the weather at HQ?"
→ Finds: HQ 123 Main St, New York, NY 
→ Gets weather for New York

"Weather at our West Coast Hub"  
→ Finds: West Coast Hub 456 Market St, San Francisco, CA
→ Gets weather for San Francisco

"How's the temperature at headquarters?"
→ Multiple ways to refer to main office
→ Semantic search finds relevant office

"What's the weather like at our Chicago location?"
→ Combines city name with office context
→ Finds Chicago office and gets weather
```

### 📊 **Still Supports Data Queries**
```
"Which office has the highest revenue?"     → Classification workflow
"Tell me about the Chicago office"          → Classification workflow  
"What's the average revenue?"               → Classification workflow
```

## Technical Implementation

### 🔄 **Workflow for Weather Queries**
```
1. User Query: "What's the weather at HQ?"
2. Vector Search: Finds "HQ 123 Main St, New York, NY..."
3. Location Extraction: Extracts "New York, NY"
4. Geocoding: Converts to coordinates (40.7128, -74.0060)
5. MCP Weather Call: Gets current weather data
6. LLM Summary: Generates contextual response
```

### 📚 **Vector Database Content**
- Extracted 20 office entries from PDF
- Each entry includes: name, address, employees, revenue, services
- Automatically indexed with sentence embeddings
- Supports semantic search (e.g., "headquarters" → "HQ")

## Benefits

### 🎯 **Natural Language Support**
- Users can refer to offices by common names ("HQ", "headquarters", "main office")
- No need to remember exact city names or addresses
- Contextual understanding of business locations

### 🔗 **Unified System**
- Single agent handles both data analysis and weather queries
- Consistent interface for all business questions
- Leverages existing office data for location context

### 🚀 **Enhanced User Experience**
- More natural, business-oriented queries
- Automatic office location resolution
- Rich contextual responses mentioning office details

## Usage Examples

### 🖥️ **Command Line**
```bash
# Start the server
python mcp_server_canonical.py

# Run the agent
python rag_agent2_canonical.py

# Try queries:
Query: What's the weather at HQ?
Query: Weather at our West Coast Hub
Query: Which office has the highest revenue?
```

### 🌐 **Streamlit Web Interface**
```bash
streamlit run streamlit_app.py
# Enter queries like "What's the weather at HQ?" in the web interface
```

## Testing

Verified functionality:
- ✅ PDF extraction: 20 office entries loaded
- ✅ Vector search: Semantic matching works
- ✅ Office types identified: HQ, West Coast Hub, various offices
- ✅ Weather integration: Location extraction and API calls
- ✅ LLM responses: Contextual summaries with office details

The system now seamlessly combines structured office data with real-time weather information, enabling natural business-oriented queries!