#!/usr/bin/env python3

import asyncio
import json
import re
import textwrap
from typing import Optional

from fastmcp import Client
from fastmcp.exceptions import ToolError
from langchain_ollama import ChatOllama   # local Llama-3.2 wrapper

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 1.  System prompt that defines the TAO protocol                  ║
# ╚══════════════════════════════════════════════════════════════════╝
# This prompt teaches the LLM how to format its tool-calling responses.
# The agent expects exactly 3 lines: Thought, Action, and Args.
SYSTEM = textwrap.dedent("""
""").strip()

ARGS_RE = re.compile(r"Args:\s*(\{.*?\})(?:\s|$)", re.S)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 2.  Robust unwrap helper (works with all FastMCP versions)       ║
# ╚══════════════════════════════════════════════════════════════════╝
# FastMCP wraps tool results in various formats depending on version.
# This helper extracts the actual Python value from any wrapper format.
def unwrap(obj):
    """Return plain Python value from any CallToolResult variant."""
    if hasattr(obj, "structured_content") and obj.structured_content:
        return unwrap(obj.structured_content)
    if hasattr(obj, "data") and obj.data:
        return unwrap(obj.data)
    if hasattr(obj, "text"):
        try:
            return json.loads(obj.text)
        except Exception:
            return obj.text
    if hasattr(obj, "value"):
        return obj.value
    if isinstance(obj, list) and len(obj) == 1:
        return unwrap(obj[0])
    if isinstance(obj, dict):
        numeric_vals = [v for v in obj.values() if isinstance(v, (int, float))]
        if len(numeric_vals) == 1:
            return numeric_vals[0]
    return obj

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 3.  LLM-based city extractor                                     ║
# ╚══════════════════════════════════════════════════════════════════╝
# Uses a separate LLM call to extract city names from natural language.
# This handles inputs like "What's the weather in Paris?" → "Paris"
extract_llm = ChatOllama(model="llama3.2", temperature=0.0)

def extract_city(prompt: str) -> Optional[str]:
    """
    Ask the LLM to extract a city name from natural language input.

    Returns:
        City name string, or None if no city is mentioned
    """
    ask = (
        "Return ONLY the city name mentioned here (no country or state). "
        "If none, reply exactly 'NONE'.\n\n"
        + prompt
    )
    reply = extract_llm.invoke(ask).content.strip()
    return None if reply.upper() == "NONE" else reply

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 4.  TAO episode execution (async for MCP client)                 ║
# ╚══════════════════════════════════════════════════════════════════╝

async def run(city: str) -> None:
    llm = ChatOllama(model="llama3.2", temperature=0.0)


        print("\n--- Thought → Action → Observation → Final ---\n")

        # ── Step 1: LLM plans geocoding to get coordinates ──────────────
        plan1 = llm.invoke(messages).content.strip()
        print(plan1 + "\n")
        args1 = json.loads(ARGS_RE.search(plan1).group(1))

        # Call MCP server's geocode_location tool
        try:

        except ToolError as e:
            print(f"Error: geocode_location failed ({e})\n")
            return

        # Handle geocoding errors
        if isinstance(geo_result, dict) and "error" in geo_result:
            print(f"Error: {geo_result['error']}\n")
            return

        lat = geo_result.get("latitude")
        lon = geo_result.get("longitude")
        location_name = geo_result.get("name", city)
        print(f"Observation: {{'latitude': {lat}, 'longitude': {lon}, 'name': '{location_name}'}}\n")

        # ── Step 2: LLM plans weather lookup with coordinates ───────────
        
        print(plan2 + "\n")
        args2 = json.loads(ARGS_RE.search(plan2).group(1))

        # Call MCP server's get_weather tool
        try:
     
            print(f"Error: get_weather failed ({e})\n")
            return

        # Handle weather errors
        if isinstance(weather_result, dict) and "error" in weather_result:
            print(f"Error: {weather_result['error']}\n")
            return

        temp_c = weather_result.get("temperature")
        cond   = weather_result.get("conditions", "Unknown")
        print(f"Observation: {{'temperature': {temp_c}, 'conditions': '{cond}'}}\n")

        # ── Step 3: LLM plans temperature unit conversion ───────────────
        messages += [
            {"role": "assistant", "content": plan2},
            {"role": "user",      "content": f"Observation: {{'temperature': {temp_c}, 'conditions': '{cond}'}}"},
        ]
        plan3 = llm.invoke(messages).content.strip()
        print(plan3 + "\n")

        # Call MCP server's convert_c_to_f tool
        try:

            temp_f = float(unwrap(raw))
        except (ToolError, ValueError) as e:
            print(f"Error: convert_c_to_f failed ({e})\n")
            return

        print(f"Observation: {{'temperature_f': {temp_f}}}\n")
        print(f"Final: {location_name} - {cond} ({temp_f:.1f} °F)\n")

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 5.  Interactive REPL for user queries                            ║
# ╚══════════════════════════════════════════════════════════════════╝
if __name__ == "__main__":
    print("Weather TAO agent with geocoding (LLM extraction, 'exit' to quit)\n")
    while True:
        raw_prompt = input("Ask about the weather: ").strip()
        if raw_prompt.lower() == "exit":
            break

        city = extract_city(raw_prompt)
        if not city or len(city) < 3:
            print("No city detected; please try again.\n")
            continue

        asyncio.run(run(city))
