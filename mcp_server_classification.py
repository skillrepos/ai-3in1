#!/usr/bin/env python3
"""
MCP Server with Canonical Query Classification & Prompt Templates
─────────────────────────────────────────────────────────────────
Lab 6: Building the Classification MCP Server

This server provides a sophisticated approach to canonical queries:
"""

from __future__ import annotations

import time
from typing import Final
from pathlib import Path
import json

import requests
from requests.adapters import HTTPAdapter

import pandas as pd
from fastmcp import FastMCP

# ╔══════════════════════════════════════════════════════════════════╗
# 1. Configuration and Constants                                     ║
# ╚══════════════════════════════════════════════════════════════════╝
WEATHER_CODES: Final[dict[int, str]] = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 
    53: "Moderate drizzle", 55: "Dense drizzle", 61: "Slight rain",
    63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow fall",
    73: "Moderate snow fall", 75: "Heavy snow fall", 95: "Thunderstorm",
}

MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5
TRANSIENT_CODES = {429, 500, 502, 503, 504}

OFFICE_DATA_PATH = Path("data/offices.csv")
_office_data_cache = None

def _get_office_data() -> pd.DataFrame:

    global _office_data_cache
    if _office_data_cache is None:
        if not OFFICE_DATA_PATH.exists():
            raise FileNotFoundError(f"Office data not found at {OFFICE_DATA_PATH}")
        _office_data_cache = pd.read_csv(OFFICE_DATA_PATH)
    return _office_data_cache

CANONICAL_QUERIES = {
    "revenue_stats": {
        "description": "Calculate revenue statistics across all offices",
        "parameters": [],
        "data_requirements": ["revenue_million", "city"],
        "example_queries": [
        ]
    },
    
    "employee_analysis": {
        "description": "Analyze employee distribution across offices", 
        "parameters": [],
        "data_requirements": ["employees", "city"],
        "example_queries": [
        ]
    },
    
    "growth_analysis": {
        "description": "Analyze office growth patterns by opening year",
        "parameters": [
            {"name": "year_threshold", "type": "int", "description": "Year to filter by", "required": True}
        ],
        "data_requirements": ["opened_year", "city", "state"],
        "example_queries": [
        ]
    },
    
    "efficiency_analysis": {
        "description": "Calculate revenue efficiency (revenue per employee)",
        "parameters": [],
        "data_requirements": ["revenue_million", "employees", "city"],
        "example_queries": [
        ]
    },
    
    "office_profile": {
        "description": "Detailed profile of a specific office",
        "parameters": [
            {"name": "city", "type": "str", "description": "City name to profile", "required": True}
        ],
        "data_requirements": ["city", "state", "employees", "revenue_million", "opened_year"],
        "example_queries": [
        ]
    }
}

# ╔══════════════════════════════════════════════════════════════════╗
# 3. FastMCP Server and Tools                                        ║
# ╚══════════════════════════════════════════════════════════════════╝
mcp = FastMCP("CanonicalQueryServer")

# ─── Weather Tools (from previous labs) ──────────────────────────────────────

@mcp.tool
def get_weather(lat: float, lon: float) -> dict:
    """
    Fetch current weather from Open-Meteo API with retry logic.

    Returns dict with temperature, code, and conditions, or error key on failure.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            # Create a fresh session for each retry to avoid connection pool issues
            session = requests.Session()
            resp = session.get(url, timeout=15)
            session.close()  # Explicitly close the session

            # Check for transient errors that should trigger retry
            if resp.status_code in TRANSIENT_CODES:
                last_error = f"HTTP {resp.status_code}"
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_FACTOR ** attempt)
                    continue

            resp.raise_for_status()

            cw = resp.json()["current_weather"]
            code = cw["weathercode"]
            return {
                "temperature": cw["temperature"],
                "code": code,
                "conditions": WEATHER_CODES.get(code, "Unknown"),
            }

        except requests.HTTPError as e:
            last_error = f"HTTP {e.response.status_code}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue

        except requests.RequestException as e:
            last_error = f"{type(e).__name__}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue

        except (KeyError, ValueError) as e:
            # Data format errors shouldn't be retried
            return {
                "error": f"Received invalid data from weather service: {type(e).__name__}. Please try again later."
            }

    # All retries exhausted
    return {
        "error": f"Weather service failed after {MAX_RETRIES} attempts (last error: {last_error}). Please try again later."
    }

@mcp.tool
def convert_c_to_f(c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return c * 9 / 5 + 32

@mcp.tool
def geocode_location(name: str) -> dict:
    """
    Geocode a location name to latitude/longitude coordinates using Open-Meteo's geocoding API.

    Retry policy
    ------------
    * Up to MAX_RETRIES total attempts with fresh connections.
    * Retries on network errors **or** HTTP 429/5xx.
    * Exponential back-off (1.5 s, 2.25 s, …).
    * Each retry uses a new session to avoid connection pool issues.

    Parameters
    ----------
    name : str
        Location name (e.g., "San Francisco", "Paris, France", "London, UK")

    Returns
    -------
    dict
        {
            "latitude": <float>,
            "longitude": <float>,
            "name": <matched location name>,
            "error": <error message if request failed>
        }
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            # Create a fresh session for each retry to avoid connection pool issues
            session = requests.Session()
            resp = session.get(url, params={"name": name, "count": 1}, timeout=15)
            session.close()  # Explicitly close the session

            # Check for transient errors that should trigger retry
            if resp.status_code in TRANSIENT_CODES:
                last_error = f"HTTP {resp.status_code}"
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_FACTOR ** attempt)
                    continue

            resp.raise_for_status()

            data = resp.json()
            if data.get("results"):
                hit = data["results"][0]
                return {
                    "latitude": hit["latitude"],
                    "longitude": hit["longitude"],
                    "name": hit.get("name", name),
                }
            else:
                return {
                    "error": f"No location found for '{name}'. Try a different search term."
                }

        except requests.HTTPError as e:
            last_error = f"HTTP {e.response.status_code}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue

        except requests.RequestException as e:
            last_error = f"{type(e).__name__}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue

        except (KeyError, ValueError) as e:
            # Data format errors shouldn't be retried
            return {
                "error": f"Received invalid data from geocoding service: {type(e).__name__}. Please try again later."
            }

    # All retries exhausted
    return {
        "error": f"Geocoding service failed after {MAX_RETRIES} attempts (last error: {last_error}). Please try again later."
    }

# ─── Query Classification Tools ───────────────────────────────────

@mcp.tool
def list_canonical_queries() -> dict:
    """
  
    
    Returns
    -------
    dict
        {"queries": [{"name": str, "description": str, "parameters": list}]}
    """
    queries = []
    for name, config in CANONICAL_QUERIES.items():
        queries.append({
  
        })
    
    return {"queries": queries}

@mcp.tool

    """
    Classify which canonical query best matches user intent.
    
    Parameters
    ----------
    user_query : str
        Natural language query from user
        
    Returns
    -------
    dict
        {"suggested_query": str, "confidence": float, "alternatives": list, "reason": str}
    """
    user_lower = user_query.lower()
    scores = {}
    
   
    for query_name, config in CANONICAL_QUERIES.items():
        score = 0
        examples = config["example_queries"]
        

        for example in examples:
            example_words = set(example.lower().split())
            user_words = set(user_lower.split())
            overlap = len(example_words.intersection(user_words))
            if overlap > 0:
                score += overlap / len(example_words)
        
     
        if "revenue" in user_lower and "revenue" in query_name:
            score += 0.5
        if "employee" in user_lower and "employee" in query_name:
            score += 0.5
        if "efficiency" in user_lower and "efficiency" in query_name:
            score += 0.5
        if any(word in user_lower for word in ["opened", "growth", "new"]) and "growth" in query_name:
            score += 0.4
            

        if any(phrase in user_lower for phrase in ["highest revenue", "most revenue", "which office", "what office"]) and "revenue" in query_name:
            score += 0.8
            
   
        if query_name == "office_profile":
            # Look for specific city names, not question words
            city_indicators = ["tell me about", "profile", "details", "information about"]
            if any(indicator in user_lower for indicator in city_indicators):
                score += 0.3
            # Penalize if it's a "which/what" question about revenue/employees
            if any(word in user_lower for word in ["which", "what"]) and any(word in user_lower for word in ["revenue", "employees", "most", "highest"]):
                score -= 0.5
            
        scores[query_name] = score
    

    if not scores or max(scores.values()) == 0:
        return {
            "suggested_query": None,
            "confidence": 0.0,
            "alternatives": [],
            "reason": "No matching canonical query found"
        }
    

    
    # Get alternatives (other queries with score > 0)
    alternatives = [
        {"query": name, "score": score} 
        for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if score > 0 and name != best_query
    ][:3]
    
    return {
        "suggested_query": best_query,
        "confidence": confidence,
        "alternatives": alternatives,
        "reason": f"Best keyword match with confidence {confidence:.2f}"
    }

@mcp.tool

    """
    Get the prompt template for a canonical query.
    
    Parameters
    ----------
    query_name : str
        Name of the canonical query
    city : str, optional
        City parameter for office_profile queries
    year_threshold : int, optional
        Year parameter for growth_analysis queries
        
    Returns
    -------
    dict
        {"template": str, "data_requirements": list, "parameters_used": dict}
    """
    if query_name not in CANONICAL_QUERIES:
        return {"error": f"Unknown canonical query: {query_name}"}
    
    
    # Build parameters dict from provided arguments
    parameters = {}
    if city is not None:
        parameters["city"] = city
    if year_threshold is not None:
        parameters["year_threshold"] = year_threshold
    
    # Only substitute non-data parameters in template
    # Leave {data} placeholder for later substitution by the client
    try:
        if parameters:          
    except KeyError as e:
        return {"error": f"Missing required parameter: {e}"}
    
    return {
    }

# ─── Data Access Tools ──────────────────────────────────────────────

@mcp.tool  
def get_office_dataset() -> dict:
    """
    Get the complete office dataset.
    
    Returns
    -------
    dict
        {"data": list, "columns": list, "count": int}
    """
    try:
        return {
            "data": df.to_dict(orient="records"),
            "columns": list(df.columns),
            "count": len(df)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def get_filtered_office_data(columns: list = None, filters: dict = None) -> dict:
    """

    
    Parameters
    ----------
    columns : list, optional
        Specific columns to return
    filters : dict, optional
        Filters to apply (e.g., {"opened_year": {"gt": 2014}})
        
    Returns
    -------
    dict
        {"data": list, "count": int, "filters_applied": dict}
    """
    try:
        df = _get_office_data()
        
        # Apply filters
        if filters:
            for col, condition in filters.items():
                if col in df.columns:
                    if isinstance(condition, dict):
                        if "gt" in condition:
                            df = df[df[col] > condition["gt"]]
                        if "lt" in condition:
                            df = df[df[col] < condition["lt"]]
                        if "eq" in condition:
                            df = df[df[col] == condition["eq"]]
                    else:
                        df = df[df[col] == condition]
        
        # Select columns
        if columns:
            available_cols = [col for col in columns if col in df.columns]
            df = df[available_cols]
        
        return {
            "data": df.to_dict(orient="records"),
            "count": len(df),
            "filters_applied": filters or {},
            "columns": list(df.columns)
        }
    except Exception as e:
        return {"error": str(e)}

# ─── Validation Tools ──────────────────────────────────────────────

@mcp.tool
def validate_query_parameters(query_name: str, parameters: dict) -> dict:
    """
    Validate parameters for a canonical query.
    
    Parameters
    ----------
    query_name : str
        Name of canonical query
    parameters : dict
        Parameters to validate
        
    Returns
    -------
    dict
        {"valid": bool, "missing": list, "invalid": list, "suggestions": list}
    """
    if query_name not in CANONICAL_QUERIES:
        return {"error": f"Unknown canonical query: {query_name}"}
    
    config = CANONICAL_QUERIES[query_name]
    required_params = [p for p in config["parameters"] if p.get("required", False)]
    
    missing = []
    invalid = []
    suggestions = []
    
 
    for param in required_params:
        param_name = param["name"]
        if param_name not in parameters:
            missing.append(param_name)
            suggestions.append(f"Add {param_name}: {param['description']}")
    
 
    for param_name, value in parameters.items():
        param_config = next((p for p in config["parameters"] if p["name"] == param_name), None)
        if param_config:
            expected_type = param_config["type"]
            if expected_type == "int" and not isinstance(value, int):
                try:
                    int(value)
                except (ValueError, TypeError):
                    invalid.append(f"{param_name} must be an integer")
    
    return {
        "valid": len(missing) == 0 and len(invalid) == 0,
        "missing": missing,
        "invalid": invalid,
        "suggestions": suggestions
    }

# ╔══════════════════════════════════════════════════════════════════╗
# 4. Server Startup                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝
if __name__ == "__main__":
    print("Starting Canonical Query Classification MCP Server...")
    print("\nAvailable tool categories:")
    print("  [Weather]: get_weather, convert_c_to_f")
    print("  [Classification]: list_canonical_queries, classify_canonical_query")
    print("  [Templates]: get_query_template, validate_query_parameters")
    print("  [Data]: get_office_dataset, get_filtered_office_data")
    print("\nWorkflow:")
    print("  1. Client sends natural language query")
    print("  2. Use classify_canonical_query to determine intent")
    print("  3. Use get_query_template to get LLM prompt")
    print("  4. Use data tools to get required data")
    print("  5. Client executes LLM with template + data")
    print("\nServer endpoint: POST http://127.0.0.1:8000/mcp/")
    
    mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp/")