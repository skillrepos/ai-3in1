#!/usr/bin/env python3
"""
RAG Agent with MCP Classification & Prompt Templates
────────────────────────────────────────────────────
COMPLETED - Lab 7: Building the Classification RAG Agent

This agent uses a sophisticated 4-step process:
1. CLASSIFICATION: Ask MCP server to determine user intent → canonical query
2. TEMPLATE: Get structured prompt template from MCP server
3. DATA: Retrieve required data from MCP server
4. EXECUTION: Run LLM locally with template + data
"""

import asyncio
import json
import os
import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

import requests
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE
from sentence_transformers import SentenceTransformer
from fastmcp import Client
from fastmcp.exceptions import ToolError
from langchain_ollama import ChatOllama

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# ╔══════════════════════════════════════════════════════════════════╗
# 1. Configuration                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
CHROMA_PATH      = Path("./chroma_db")
COLLECTION_NAME  = "codebase"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
MCP_ENDPOINT     = "http://127.0.0.1:8000/mcp/"
TOP_K            = 5
MODEL            = os.getenv("OLLAMA_MODEL", "llama3.2")
PDF_DIR          = Path("./data")
LINE_RE          = re.compile(r"[^\S\r\n]*\r?\n[^\S\r\n]*")

# Regex patterns for location extraction
COORD_RE        = re.compile(r"\b(-?\d{1,2}(?:\.\d+)?)[,\s]+(-?\d{1,3}(?:\.\d+)?)\b")
CITY_STATE_RE   = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z]{2})\b")
CITY_COUNTRY_RE = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z][a-z]{2,})\b")
CITY_RE         = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b")
STOPWORDS = {"office", "hq", "center", "centre"}

# ╔══════════════════════════════════════════════════════════════════╗
# 2. Vector search helpers (from previous labs)                      ║
# ╚══════════════════════════════════════════════════════════════════╝
def open_collection() -> chromadb.Collection:
    """Return (or create) the Chroma collection."""
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )
    return client.get_or_create_collection(COLLECTION_NAME)

def rag_search(query: str, model: SentenceTransformer, coll: chromadb.Collection) -> List[str]:
    """Embed query and search vector DB."""
    q_emb = model.encode(query).tolist()
    res = coll.query(query_embeddings=[q_emb], n_results=TOP_K, include=["documents"])
    return res["documents"][0] if res["documents"] else []

def extract_lines_from_pdf(path: Path) -> List[str]:
    """Extract all non-blank lines from a PDF file."""
    if not pdfplumber:
        raise ImportError("pdfplumber is required for PDF ingestion. Install it with: pip install pdfplumber")

    lines: List[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for raw_line in LINE_RE.split(text):
                line = raw_line.strip()
                if line:
                    lines.append(line)
    return lines

def ensure_chromadb_populated(embed_model: SentenceTransformer, coll: chromadb.Collection) -> None:
    """
    Ensure ChromaDB is populated with office data from PDF.
    If the collection is empty, populate it from data/offices.pdf.
    """
    # Check if collection already has data
    try:
        count = coll.count()
        if count > 0:
            print(f"ChromaDB already populated with {count} documents")
            return
    except Exception:
        pass

    # Collection is empty, populate it
    print("ChromaDB is empty, populating from offices.pdf...")

    pdf_path = PDF_DIR / "offices.pdf"
    if not pdf_path.exists():
        print(f"WARNING: {pdf_path} not found. RAG queries for office locations may not work.")
        return

    try:
        lines = extract_lines_from_pdf(pdf_path)
        print(f"Extracted {len(lines)} lines from {pdf_path.name}")

        # Embed and store each line
        for idx, line in enumerate(lines):
            vector = embed_model.encode(line).tolist()
            coll.add(
                ids=[f"{pdf_path.name}-{idx}"],
                embeddings=[vector],
                documents=[line],
                metadatas=[{"path": str(pdf_path), "chunk_index": idx}],
            )

        print(f"✅ ChromaDB populated with {len(lines)} documents from {pdf_path.name}")
    except Exception as e:
        print(f"ERROR: Failed to populate ChromaDB: {e}")

# ╔══════════════════════════════════════════════════════════════════╗
# 3. Location extraction helpers (from previous labs)                ║
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

def geocode(name: str) -> Optional[Tuple[float, float]]:
    """Geocode city name to coordinates."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    
    def _lookup(n: str):
        try:
            r = requests.get(url, params={"name": n, "count": 1}, timeout=10)
            r.raise_for_status()
            data = r.json()
            if data.get("results"):
                hit = data["results"][0]
                return hit["latitude"], hit["longitude"]
        except Exception:
            pass
        return None

    coords = _lookup(name)
    if coords:
        return coords
    if "," in name:
        return _lookup(name.split(",", 1)[0].strip())
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
# 4. Classification-Based Canonical Query Handler                    ║
# ╚══════════════════════════════════════════════════════════════════╝
async def handle_canonical_query_with_classification(user_query: str) -> str:
    """
    
    """
    async with Client(MCP_ENDPOINT) as mcp:
        try:
            # Step 1: Classify canonical query from user input
            print("[1/4] Classifying canonical query...")
       

            # Debug: Check what we got back
            if not isinstance(classification, dict):
                return f"Classification error: Expected dict, got {type(classification)}: {classification}"

            if not classification.get("suggested_query"):
                return f"Sorry, I couldn't determine how to analyze: '{user_query}'"

       
            
            print(f"[Result] Suggested query: {suggested_query} (confidence: {confidence:.2f})")
            
            # Step 2: Extract parameters if needed
            parameters = {}
            
            # Handle parameterized queries
            if suggested_query == "growth_analysis":
            
            
            elif suggested_query == "office_profile":
               
                if "city" not in parameters:
                    return "Please specify which office you'd like to know about (e.g., 'Tell me about the Chicago office')."
            
            # Step 3: Validate parameters
            if parameters:
                print(f"Using parameters: {parameters}")
 
                })
                validation = unwrap(validation_result)
                
                if not validation.get("valid"):
                    missing = validation.get("missing", [])
                    if missing:
                        return f"Missing required parameters: {', '.join(missing)}"
            
            # Step 4: Get prompt template
            print("[2/4] Getting prompt template...")
            template_args = {"query_name": suggested_query}
            if "city" in parameters:
                template_args["city"] = parameters["city"]
            if "year_threshold" in parameters:
                template_args["year_threshold"] = parameters["year_threshold"]
                
 
            
            if "error" in template_info:
                return f"Template error: {template_info['error']}"
            
 
            
            # Step 5: Get required data
            print(f"[3/4] Fetching data: {data_requirements}")
 
            data_info = unwrap(data_result)
            
            if "error" in data_info:
                return f"Data error: {data_info['error']}"
            
            office_data = data_info["data"]
            
            # Step 6: Execute LLM with template and data
            print("[4/4] Executing LLM with template...")
            
            # Format template with data
 
            print(f"📄 Data count: {len(office_data)} records")
            print(f"📄 Prompt length: {len(formatted_prompt)} characters")
            
            try:
                # Use more specific LLM settings with fallback

                print(f"✅ LLM response received ({len(result)} chars)")
                return result
                
            except Exception as llm_error:
                print(f"❌ LLM error: {llm_error}")
                print("🔄 Using calculated fallback...")
                # Fallback: provide a simple calculation-based response
                if suggested_query == "employee_analysis":
                    max_emp = max(office_data, key=lambda x: x['employees'])
                    total_emp = sum(x['employees'] for x in office_data)
                    avg_emp = total_emp / len(office_data)
                    return (f"**Employee Analysis (Calculated)**\n\n"
                           f"1. Office with most employees: {max_emp['city']} ({max_emp['employees']} employees)\n"
                           f"2. Total employees: {total_emp}\n"
                           f"3. Average per office: {avg_emp:.1f}\n"
                           f"4. Distribution: {len(office_data)} offices analyzed")
                elif suggested_query == "revenue_stats":
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
# 5. Weather workflow (from previous labs)                           ║
# ╚══════════════════════════════════════════════════════════════════╝
async def handle_weather_query(prompt: str) -> str:
    """Original weather workflow using RAG + MCP."""
    embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    coll = open_collection()

    # Ensure ChromaDB is populated with office data
    ensure_chromadb_populated(embed_model, coll)

    # Vector search
    rag_hits = rag_search(prompt, embed_model, coll)
    top_hit = rag_hits[0] if rag_hits else ""
    if top_hit:
        print(f"\nTop RAG hit: {top_hit[:100]}...\n")

    # Extract coordinates
    coords = find_coords([top_hit, prompt])
    if not coords:
        city_str = (
            find_city_state([top_hit, prompt])
            or find_city_country([top_hit, prompt])
            or guess_city([top_hit, prompt])
        )
        if city_str:
            print(f"Geocoding '{city_str}'...")
            coords = geocode(city_str)

    if not coords:
        return "Could not determine location for weather lookup."

    lat, lon = coords
    print(f"Using coordinates: {lat:.4f}, {lon:.4f}")

    # Get weather via MCP
    async with Client(MCP_ENDPOINT) as mcp:
        try:
            w_raw = await mcp.call_tool("get_weather", {"lat": lat, "lon": lon})
            weather = unwrap(w_raw)
            
            # Handle case where weather might be unwrapped too much
            if isinstance(weather, (int, float)):
                return f"Invalid weather data format received: {weather}"
            
            if not isinstance(weather, dict):
                return f"Weather data is not in expected format: {type(weather)}"
            
            temp_c = weather.get("temperature")
            cond = weather.get("conditions", "Unknown")
            
            if temp_c is None:
                return "Temperature data not available from weather service."
            
            tf_raw = await mcp.call_tool("convert_c_to_f", {"c": temp_c})
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
    Route query to appropriate handler based on content.
    
    Uses simple heuristics to determine if query is:
    - Weather-related (use RAG workflow)
    - Data analysis (use classification workflow)
    """
    user_lower = user_query.lower()
    
    # Weather-related keywords
    weather_keywords = ["weather", "temperature", "forecast", "conditions", "climate"]
   
    
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
    print("RAG Agent with MCP Classification & Prompt Templates")
    print("Make sure mcp_server_classification.py is running first!")
    print("Type 'exit' to quit, 'demo' for sample queries.\n")
    
    while True:
        user_input = input("Query: ").strip()
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "demo":
            asyncio.run(demo_classification_workflow())
        elif user_input:
            result = asyncio.run(process_query(user_input))
            print(f"\n{result}\n")