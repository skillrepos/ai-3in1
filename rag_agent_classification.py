#!/usr/bin/env python3
"""
RAG Agent with MCP Classification & Vector Search
──────────────────────────────────────────────────

This agent uses MCP server for ALL data access (centralized data layer):

CANONICAL QUERY WORKFLOW (for structured analytics):


WEATHER WORKFLOW (for location-based queries):


ARCHITECTURE:

DATA SOURCES (all accessed via MCP):
• offices.csv → Structured analytics + Vector embeddings in MCP's ChromaDB
• offices.pdf → Location data + Vector embeddings in MCP's ChromaDB
"""

import asyncio
import json
import os
import re
from typing import Optional, Tuple

from fastmcp import Client
from fastmcp.exceptions import ToolError
from langchain_ollama import ChatOllama

# ╔══════════════════════════════════════════════════════════════════╗
# 1. Configuration                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
MCP_ENDPOINT = "http://127.0.0.1:8000/mcp/"
TOP_K        = 5
MODEL        = os.getenv("OLLAMA_MODEL", "llama3.2")

# Regex patterns for location extraction
COORD_RE        = re.compile(r"\b(-?\d{1,2}(?:\.\d+)?)[,\s]+(-?\d{1,3}(?:\.\d+)?)\b")
CITY_STATE_RE   = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z]{2})\b")
CITY_COUNTRY_RE = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z][a-z]{2,})\b")
CITY_RE         = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b")
STOPWORDS = {"office", "hq", "center", "centre"}


# ╔══════════════════════════════════════════════════════════════════╗
# 2. Location extraction helpers (from previous labs)                ║
# ╚══════════════════════════════════════════════════════════════════╝
def find_coords(texts: List[str]) -> Optional[Tuple[float, float]]:
    for txt in texts:
        for m in COORD_RE.finditer(txt):
            lat, lon = map(float, m.groups())
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
    return None

def find_city_state(texts: List[str]) -> Optional[str]:
    for txt in texts:
        if (m := CITY_STATE_RE.search(txt)):
            return m.group(0)
    return None

def find_city_country(texts: List[str]) -> Optional[str]:
    for txt in texts:
        if (m := CITY_COUNTRY_RE.search(txt)):
            return m.group(0)
    return None

def guess_city(texts: List[str]) -> Optional[str]:
    """
    Extract city names from text using a simple but reliable approach.
    """
    # Known city names for better matching
    known_cities = {
        "paris", "london", "new york", "chicago", "boston", "seattle", 
        "denver", "miami", "atlanta", "austin", "san francisco", "los angeles"
    }
    
    # Words that are definitely not cities
    non_cities = {
        "what", "where", "how", "when", "why", "who", "which", "the", "our", "at", 
        "tell", "about", "me", "weather", "average", "revenue", "office", "offices",
        "employees", "most", "like", "show", "temperature", "climate", "is", "are",
        "has", "have", "and", "or", "but", "this", "that", "these", "those", "with"
    }
    
    for txt in texts:
        txt_lower = txt.lower()
        
        # First, check for known cities
        for city in known_cities:
            if city in txt_lower:
                return city.title()
        
        # Then look for city-like patterns with context
        words = txt.split()
        for i, word in enumerate(words):
            punctuation = '.,!?\'\"'
            clean_word = word.strip(punctuation).lower()
            
            # Skip common non-cities
            if clean_word in non_cities or len(clean_word) <= 2:
                continue
            
            # Look for words after location prepositions
            prev_word = words[i-1].lower() if i > 0 else ""
            if prev_word in ["in", "at", "about", "to", "from"]:
                # Handle two-word cities like "New York"
                if (i+1 < len(words) and 
                    len(words[i+1].strip(punctuation)) > 2 and
                    words[i+1].strip(punctuation).isalpha()):
                    next_word_clean = words[i+1].strip(punctuation).lower()
                    two_word = f"{clean_word} {next_word_clean}"
                    if two_word not in non_cities:
                        return two_word.title()
                
                # Single word city
                if clean_word.isalpha():
                    return clean_word.title()
                    
    return None

async def geocode_via_mcp(name: str, mcp_client: Client) -> Optional[Tuple[float, float]]:
    """
    Use the MCP server's geocoding tool to get coordinates.
    If "City, XX" fails, retry with just "City".
    """
    async def _lookup(n: str):
        try:
            result = await mcp_client.call_tool("geocode_location", {"name": n})
            geo_data = unwrap(result)

            if not isinstance(geo_data, dict):
                return None

            if "error" in geo_data:
                print(f"Geocoding error: {geo_data['error']}")
                return None

            lat = geo_data.get("latitude")
            lon = geo_data.get("longitude")

            if lat is not None and lon is not None:
                return (lat, lon)

        except Exception as e:
            print(f"Geocoding failed: {type(e).__name__}")

        return None

    coords = await _lookup(name)
    if coords:
        return coords
    if "," in name:                              # retry with simpler string
        return await _lookup(name.split(",", 1)[0].strip())
    return None

def unwrap(obj):
    """Unwrap FastMCP result objects, but preserve dict structure when possible."""
    if hasattr(obj, "structured_content") and obj.structured_content:
        return unwrap(obj.structured_content)
    if hasattr(obj, "data") and obj.data:
        return unwrap(obj.data)
    if isinstance(obj, list) and len(obj) == 1:
        return unwrap(obj[0])
    
    # Only unwrap to numeric if it's clearly a single numeric value
    if isinstance(obj, dict):
        # If it's a dict with one numeric value AND no other meaningful keys, unwrap it
        numeric_vals = [v for v in obj.values() if isinstance(v, (int, float))]
        if (len(obj) == 1 and len(numeric_vals) == 1 and 
            list(obj.keys())[0] in ['value', 'result', 'data']):
            return numeric_vals[0]
        # Otherwise preserve the dict structure
        return obj
    
    return obj

# ╔══════════════════════════════════════════════════════════════════╗
# 3. Classification-Based Canonical Query Handler                    ║
# ╚══════════════════════════════════════════════════════════════════╝
async def handle_canonical_query_with_classification(user_query: str) -> str:
    async with Client(MCP_ENDPOINT) as mcp:
        try:
            print("[1/4] Classifying canonical query...")           
            classification = unwrap(classify_result)

            # Debug: Check what we got back
            if not isinstance(classification, dict):
                return f"Classification error: Expected dict, got {type(classification)}: {classification}"

            if not classification.get("suggested_query"):
                return f"Sorry, I couldn't determine how to analyze: '{user_query}'"

            suggested_query = classification["suggested_query"]
            confidence = classification["confidence"]
            
            print(f"[Result] Suggested query: {suggested_query} (confidence: {confidence:.2f})")
            
            parameters = {}
            
            # Handle parameterized queries
            if suggested_query == "growth_analysis":
                # Extract year from user query
                year_match = re.search(r'\b(19|20)\d{2}\b', user_query)
                if year_match:
                    parameters["year_threshold"] = int(year_match.group())
                else:
                    parameters["year_threshold"] = 2014  # default
            
            elif suggested_query == "office_profile":
                # Extract city name - avoid question words
                user_lower = user_query.lower()
                excluded_words = {"office", "tell", "about", "the", "which", "what", "where", "how", "when", "why", "who", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
                
                # Look for actual city names in the query
                for word in user_query.split():
                    clean_word = word.strip('.,!?').title()
                    if (len(clean_word) > 2 and 
                        clean_word.lower() not in excluded_words and
                        clean_word.isalpha()):
                        parameters["city"] = clean_word
                        break
                
                if "city" not in parameters:
                    return "Please specify which office you'd like to know about (e.g., 'Tell me about the Chicago office')."
            
            if parameters:
                print(f"Using parameters: {parameters}")
                validation_result = await mcp.call_tool("validate_query_parameters", {
                    "query_name": suggested_query,
                    "parameters": parameters
                })
                validation = unwrap(validation_result)
                
                if not validation.get("valid"):
                    missing = validation.get("missing", [])
                    if missing:
                        return f"Missing required parameters: {', '.join(missing)}"
            
            print("[2/4] Getting prompt template...")
            template_args = {"query_name": suggested_query}
            if "city" in parameters:
                template_args["city"] = parameters["city"]
            if "year_threshold" in parameters:
                template_args["year_threshold"] = parameters["year_threshold"]
                
            template_info = unwrap(template_result)
            
            if "error" in template_info:
                return f"Template error: {template_info['error']}"
            
            template = template_info["template"]
            data_requirements = template_info["data_requirements"]
            
            print(f"[3/4] Fetching data: {data_requirements}") 
                "columns": data_requirements
            })
            data_info = unwrap(data_result)
            
            if "error" in data_info:
                return f"Data error: {data_info['error']}"
            
            office_data = data_info["data"]
            
            print("[4/4] Executing LLM with template...")
            
            # Format template with data
            formatted_prompt = template.format(data=json.dumps(office_data, indent=2))
            
            print(f"📄 Data count: {len(office_data)} records")
            print(f"📄 Prompt length: {len(formatted_prompt)} characters")
            
            try:
                # Use more specific LLM settings with fallback
                result = response.content.strip()
                print(f"✅ LLM response received ({len(result)} chars)")
                return result
                
            except Exception as llm_error:
                print(f"❌ LLM error: {llm_error}")
                print("🔄 Using calculated fallback...")
                # Fallback: provide a simple calculation-based response

                    max_emp = max(office_data, key=lambda x: x['employees'])
                    total_emp = sum(x['employees'] for x in office_data)
                    avg_emp = total_emp / len(office_data)
                    return (f"**Employee Analysis (Calculated)**\n\n"
                           f"1. Office with most employees: {max_emp['city']} ({max_emp['employees']} employees)\n"
                           f"2. Total employees: {total_emp}\n"
                           f"3. Average per office: {avg_emp:.1f}\n"
                           f"4. Distribution: {len(office_data)} offices analyzed")

                    # Find offices with highest/lowest revenue
                    max_office = max(office_data, key=lambda x: x['revenue_million'])
                    min_office = min(office_data, key=lambda x: x['revenue_million'])
                    revenues = [x['revenue_million'] for x in office_data]
                    avg_rev = sum(revenues) / len(revenues)
                    total_rev = sum(revenues)
                    return (f"**Revenue Statistics (Calculated)**\n\n"
                           f"1. Highest revenue: {max_office['city']} (${max_office['revenue_million']}M)\n"
                           f"2. Lowest revenue: {min_office['city']} (${min_office['revenue_million']}M)\n"
                           f"3. Average revenue: ${avg_rev:.1f}M\n"
                           f"4. Total revenue: ${total_rev}M")
                else:
                    return f"Analysis unavailable due to LLM error: {llm_error}"
            
        except ToolError as e:
            return f"MCP error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

# ╔══════════════════════════════════════════════════════════════════╗
# 4. Weather workflow using MCP Vector Search                        ║
# ╚══════════════════════════════════════════════════════════════════╝
async def handle_weather_query(prompt: str) -> str:
    """
    
    """
    async with Client(MCP_ENDPOINT) as mcp:
        print(f"Searching for office location: '{prompt}'")
        try:
            search_data = unwrap(search_result)

            if "error" in search_data:
                return f"Error searching for location: {search_data['error']}"

            matches = search_data.get("matches", [])
            if not matches:
                return f"Could not find any office matching '{prompt}'. Try being more specific."

            top_hit = matches[0]["document"]
            print(f"\n📍 Top RAG hit: {top_hit[:100]}...\n")

        except Exception as e:
            return f"Failed to search for location: {e}"       

        if not coords:
            return "Could not determine location for weather lookup."

        lat, lon = coords
        print(f"Using coordinates: {lat:.4f}, {lon:.4f}")
        try:
            w_raw = await mcp.call_tool("get_weather", {"lat": lat, "lon": lon})
            weather = unwrap(w_raw)

            # Handle case where weather might be unwrapped too much
            if isinstance(weather, (int, float)):
                return f"Invalid weather data format received: {weather}"

            if not isinstance(weather, dict):
                return f"Weather data is not in expected format: {type(weather)}"

            # Check for error response from the weather service
            if "error" in weather:
                return f"Weather service error: {weather['error']}"

            temp_c = weather.get("temperature")
            cond = weather.get("conditions", "Unknown")

            if temp_c is None:
                return "Temperature data not available from weather service."

            temp_f = float(unwrap(tf_raw))

            # Generate summary
            safe_line = re.sub(r"\d+\s+\S+(?:\s+\S+)*,?\s*", "", top_hit, count=1).strip()
            city_part = ", ".join(top_hit.split(",", 2)[1:]).strip() or "N/A"

            llm = ChatOllama(model=MODEL, temperature=0.2)

            system_msg = (
                "You are a helpful business assistant. Provide a concise weather summary."
            )

            user_msg = (
                f"Create a weather summary:\n"
                f"• Office: {safe_line}\n"
                f"• Location: {city_part}\n"
                f"• Weather: {cond}, {temp_f:.1f} °F\n\n"
                "Format: Office name + location, current weather, interesting fact about the city."
            )

            summary = llm.invoke([
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]).content.strip()

            return summary

        except ToolError as e:
            return f"Weather error: {e}"

# ╔══════════════════════════════════════════════════════════════════╗
# 6. Main query router                                               ║
# ╚══════════════════════════════════════════════════════════════════╝
async def process_query(user_query: str) -> str:
    """
    """
    user_lower = user_query.lower()
    
    # Weather-related keywords 
    
    # Data analysis keywords

    # Default to classification for ambiguous queries
    print("[INFO] Ambiguous query, trying classification workflow...")
    return await handle_canonical_query_with_classification(user_query)

# ╔══════════════════════════════════════════════════════════════════╗
# 7. Command-line interface                                          ║
# ╚══════════════════════════════════════════════════════════════════╝
async def demo_classification_workflow():
    """Demonstrate the classification workflow with sample queries."""
    print("Classification-Based Canonical Query Demo")
    print("=" * 50)
    
    sample_queries = [
        "What's the average revenue across our offices?",
        "Which office has the highest revenue?",
        "Which office has the most employees?", 
        "Tell me about the Chicago office",
        "What offices opened after 2014?",
        "Which office is most efficient?",
        "What's the weather like at our Paris office?"
    ]
    
    for query in sample_queries:
        print(f"\nUser: {query}")
        print("-" * 40)
        result = await process_query(query)
        print(f"Agent: {result}")
        print()

if __name__ == "__main__":
    print("=" * 70)
    print("RAG Agent with MCP-Centric Architecture")
    print("=" * 70)
    print("\nArchitecture:")
    print("  🔹 MCP Server = Data Layer")
    print("     - Owns vector database (ChromaDB)")
    print("     - Manages embeddings for PDF + CSV")
    print("     - Provides semantic search tools")
    print("  🔹 RAG Agent = Orchestration Layer")
    print("     - Routes queries to appropriate workflows")
    print("     - Executes LLM with MCP data")
    print("     - NO local file reading or embeddings")
    print("\nData Sources (all via MCP):")
    print("  • PDF (locations) → Vector search")
    print("  • CSV (analytics) → Structured queries + Vector search")
    print("\nPrerequisites:")
    print("  ⚠️  MCP server MUST be running first!")
    print("     Run: python labs/common/lab6_mcp_server_solution.txt")
    print("\nCommands:")
    print("  • Type 'exit' to quit")
    print("  • Type 'demo' for sample queries")
    print("\nExample Queries:")
    print("  🌤️  Weather: 'What is the weather at HQ?'")
    print("  📊 Analytics: 'Which office has the most employees?'")
    print("  🔍 Semantic: 'Show me offices with high revenue'")
    print("=" * 70)
    print()
    
    while True:
        user_input = input("Query: ").strip()
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "demo":
            asyncio.run(demo_classification_workflow())
        elif user_input:
            result = asyncio.run(process_query(user_input))
            print(f"\n{result}\n")