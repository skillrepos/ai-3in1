#!/usr/bin/env python3
"""
────────────────────────────────────────────────────────────────────
Interactive Thought-Action-Observation (TAO) agent that queries a local
FastMCP weather server.  The user can ask *any* question; the Llama-3.2
model first extracts a city name from that raw prompt, then plans the
two tool calls:

    get_weather(lat, lon)   → current temp in °C + conditions
    convert_c_to_f(c)       → °F

The script prints the complete TAO trace on every run.
"""

import asyncio
import json
import re
import textwrap
from typing import Optional

from fastmcp import Client
from fastmcp.exceptions import ToolError
from langchain_ollama import ChatOllama   # local Llama-3.2 wrapper

# ──────────────────────────────────────────────────────────────────
# 1.  System prompt that defines the TAO protocol
# ──────────────────────────────────────────────────────────────────
SYSTEM = textwrap.dedent("""
You are an agent with two tools:

get_weather(lat:float, lon:float)
    → {"temperature": float, "code": int, "conditions": str}

convert_c_to_f(c:float)
    → float

When you plan, emit exactly three lines:

Thought: <your thought>
Action: <tool name>
Args: {"lat":X,"lon":Y}   or   {"c":Z}

Do NOT output anything else.
""").strip()

ARGS_RE = re.compile(r"Args:\s*(\{.*?\})(?:\s|$)", re.S)

# ──────────────────────────────────────────────────────────────────
# 2.  Robust unwrap helper (works with all FastMCP versions)
# ──────────────────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────────────────
# 3.  LLM-only city extractor
# ──────────────────────────────────────────────────────────────────
extract_llm = ChatOllama(model="llama3.2", temperature=0.0)

def extract_city(prompt: str) -> Optional[str]:
    """
    Ask the LLM to pull a city name from a prompt.
    Returns None if it replies 'NONE'.
    """
    ask = (
        "Return ONLY the city name mentioned here (no country or state). "
        "If none, reply exactly 'NONE'.\n\n"
        + prompt
    )
    reply = extract_llm.invoke(ask).content.strip()
    return None if reply.upper() == "NONE" else reply

# ──────────────────────────────────────────────────────────────────
# 4.  One TAO episode (async because MCP calls are async)
# ──────────────────────────────────────────────────────────────────
async def run(question: str) -> None:
    llm = ChatOllama(model="llama3.2", temperature=0.0)

    async with Client("http://127.0.0.1:8000/mcp/") as mcp:
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": question},
        ]

        print("\n--- Thought → Action → Observation → Final ---\n")

        # 1. Planning step → get_weather
        plan1 = llm.invoke(messages).content.strip()
        print(plan1 + "\n")
        args1 = json.loads(ARGS_RE.search(plan1).group(1))

        try:
            res1 = unwrap(await mcp.call_tool("get_weather", args1))
        except ToolError as e:
            print(f"Error: get_weather failed ({e})\n")
            return

        temp_c = res1.get("temperature")
        cond   = res1.get("conditions", "Unknown")
        print(f"Observation: {{'temperature': {temp_c}, 'conditions': '{cond}'}}\n")

        # 2. Planning step → convert_c_to_f
        messages += [
            {"role": "assistant", "content": plan1},
            {"role": "user",      "content": f"Observation: {temp_c}"},
        ]
        plan2 = llm.invoke(messages).content.strip()
        print(plan2 + "\n")

        try:
            raw = await mcp.call_tool("convert_c_to_f", {"c": temp_c})
            temp_f = float(unwrap(raw))
        except (ToolError, ValueError) as e:
            print(f"Error: convert_c_to_f failed ({e})\n")
            return

        print(f"Observation: {{'temperature_f': {temp_f}}}\n")
        print(f"Final: {cond} ({temp_f:.1f} °F)\n")

# ──────────────────────────────────────────────────────────────────
# 5.  Simple REPL
# ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Weather TAO agent (LLM extraction, 'exit' to quit)\n")
    while True:
        raw_prompt = input("Ask about the weather: ").strip()
        if raw_prompt.lower() == "exit":
            break

        city = extract_city(raw_prompt)
        if not city or len(city) < 3:
            print("No city detected; please try again.\n")
            continue

        asyncio.run(run(f"What is the current weather in {city}?"))
