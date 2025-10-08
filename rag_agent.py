#!/usr/bin/env python3
"""
Lab 5: RAG-Enhanced Weather Agent
────────────────────────────────────────────────────────────────────
A Retrieval-Augmented Generation (RAG) agent that combines vector search
with MCP tool calling to provide context-aware weather information.

Key Components
--------------
1. **Vector Search (ChromaDB)**

2. **Location Extraction (Pattern Matching + LLM)**
   - Extracts coordinates directly from text when available
   - Falls back to city name extraction (City, State | City, Country)
   - Uses MCP geocoding tool to convert city names to coordinates

3. **MCP Tool Integration**
   - get_weather(lat, lon) → temperature °C + weather conditions
   - convert_c_to_f(c) → temperature °F
   - geocode_location(name) → latitude/longitude coordinates

4. **Error Handling**
   - Gracefully handles MCP server errors
   - Validates tool responses before processing
   - Provides clear user feedback on failures


Prerequisites
-------------
- ChromaDB populated with office data
- MCP weather server running on localhost:8000
- pip install sentence-transformers chromadb fastmcp
"""

# ────────────────────────── standard libs ───────────────────────────
import asyncio
import json
import re
from pathlib import Path
from typing import List, Optional, Tuple

# ────────────────────────── third-party libs ────────────────────────
import requests
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE
from sentence_transformers import SentenceTransformer
from fastmcp import Client
from fastmcp.exceptions import ToolError

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 1.  Configuration and constants                                  ║
# ╚══════════════════════════════════════════════════════════════════╝
# Vector database settings
CHROMA_PATH      = Path("./chroma_db")          # Persistent storage location
COLLECTION_NAME  = "codebase"                   # Collection for office data
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"           # Sentence transformer model
MCP_ENDPOINT     = "http://127.0.0.1:8000/mcp/" # MCP server endpoint
TOP_K            = 5                            # Number of RAG results to retrieve

# Location extraction patterns - ordered by specificity
COORD_RE        = re.compile(r"\b(-?\d{1,2}(?:\.\d+)?)[,\s]+(-?\d{1,3}(?:\.\d+)?)\b")  # lat,lon pairs
CITY_STATE_RE   = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z]{2})\b")      # "Austin, TX"
CITY_COUNTRY_RE = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z][a-z]{2,})\b") # "Paris, France"
CITY_RE         = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b")                     # Any capitalized word

STOPWORDS = {"office", "hq", "center", "centre"}  # Words to exclude from city detection

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 2.  Vector search helpers (ChromaDB integration)                 ║
# ╚══════════════════════════════════════════════════════════════════╝
def open_collection() -> chromadb.Collection:

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )
    return client.get_or_create_collection(COLLECTION_NAME)


def rag_search(query: str,
               model: SentenceTransformer,
               coll: chromadb.Collection) -> List[str]:

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 3.  Location extraction helpers (pattern matching)               ║
# ╚══════════════════════════════════════════════════════════════════╝
# These functions extract location information using regex patterns,
# ordered from most specific (coordinates) to least specific (any city).

def find_coords(texts: List[str]) -> Optional[Tuple[float, float]]:
    """
    Extract explicit latitude/longitude coordinates from text.

    Returns:
        (latitude, longitude) tuple, or None if not found
    """
    for txt in texts:
        for m in COORD_RE.finditer(txt):
            lat, lon = map(float, m.groups())
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
    return None


def find_city_state(texts: List[str]) -> Optional[str]:
    """Return first “City, ST” (US/CA style) found."""
    for txt in texts:
        if (m := CITY_STATE_RE.search(txt)):
            return m.group(0)
    return None


def find_city_country(texts: List[str]) -> Optional[str]:
    """Return first “City, Country” found."""
    for txt in texts:
        if (m := CITY_COUNTRY_RE.search(txt)):
            return m.group(0)
    return None


def guess_city(texts: List[str]) -> Optional[str]:
    """
    Fallback: first capitalised token not in STOPWORDS and >2 chars.
    """
    for txt in texts:
        for m in CITY_RE.finditer(txt):
            token = m.group(1).strip()
            if len(token) > 2 and token.split()[-1].lower() not in STOPWORDS:
                return token
    return None


async def geocode_via_mcp(name: str, mcp_client: Client) -> Optional[Tuple[float, float]]:
    """

    Args:
        name: Location name to geocode (e.g., "Paris" or "Austin, TX")
        mcp_client: Active MCP client connection

    Returns:
        (latitude, longitude) tuple, or None if geocoding fails
    """
    async def _lookup(n: str):
        try:
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

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 4.  MCP result unwrapper (handles version differences)           ║
# ╚══════════════════════════════════════════════════════════════════╝
def unwrap(obj):
    """
    Extract plain Python values from FastMCP result wrappers.

    FastMCP returns CallToolResult objects in various formats depending on
    version. This helper normalizes them to plain Python types (dict/number/string).

    Args:
        obj: FastMCP result object

    Returns:
        Plain Python value (dict, number, string, list, etc.)
    """
    if hasattr(obj, "structured_content") and obj.structured_content:
        return unwrap(obj.structured_content)
    if hasattr(obj, "data") and obj.data:
        return unwrap(obj.data)
    if isinstance(obj, list) and len(obj) == 1:
        return unwrap(obj[0])              # unwrap single-element list
    if isinstance(obj, dict):
        numeric_vals = [v for v in obj.values() if isinstance(v, (int, float))]
        if len(numeric_vals) == 1:         # {'value': 78.8}
            return numeric_vals[0]
    return obj

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 5.  Main workflow orchestration (async)                          ║
# ╚══════════════════════════════════════════════════════════════════╝
async def run(prompt: str) -> None:
    """
    Execute the complete RAG + MCP workflow.

    Args:
        prompt: Natural language user query about weather
    """
    embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    coll        = open_collection()

    rag_hits = rag_search(prompt, embed_model, coll)
    top_hit  = rag_hits[0] if rag_hits else ""
    if top_hit:
        print("\nTop RAG hit:\n", top_hit, "\n")

    coords = find_coords([top_hit, prompt])

    async with Client(MCP_ENDPOINT) as mcp:
        if not coords:
            city_str = (
                find_city_state([top_hit, prompt])
                or find_city_country([top_hit, prompt])
                or guess_city([top_hit, prompt])
            )
            if city_str:
                print(f"No coords found; geocoding '{city_str}'.")
                coords = await geocode_via_mcp(city_str, mcp)

        if not coords:
            print("Could not determine latitude/longitude.\n")
            return

        lat, lon = coords
        print(f"Using coordinates: {lat:.4f}, {lon:.4f}\n")

        try:
        except ToolError as e:
            print(f"Error calling get_weather: {e}")
            return

        weather = unwrap(w_raw)
        if not isinstance(weather, dict):
            print(f"Unexpected get_weather result: {weather}")
            return

        # Check for error response from the weather service
        if "error" in weather:
            print(f"Weather service error: {weather['error']}")
            return

        temp_c = weather.get("temperature")
        cond   = weather.get("conditions", "Unknown")

        if temp_c is None:
            print("Weather service did not return temperature data.")
            return

        try:
            temp_f = float(unwrap(tf_raw))
        except (ToolError, ValueError) as e:
            print(f"Temperature conversion failed: {e}")
            return

        print(f"Weather: {cond}, {temp_f:.1f} °F\n")

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 6.  Interactive command-line interface                           ║
# ╚══════════════════════════════════════════════════════════════════╝
if __name__ == "__main__":
    print("Office-aware weather agent. Type 'exit' to quit.\n")
    while True:
        prompt = input("Prompt: ").strip()
        if prompt.lower() == "exit":
            break
        if prompt:
            asyncio.run(run(prompt))