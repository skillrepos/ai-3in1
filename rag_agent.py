#!/usr/bin/env python3
"""
Lab 5: RAG-Enhanced Agentic Weather Agent
────────────────────────────────────────────────────────────────────
A true agentic RAG workflow combining:
- Lab 2's agent pattern (TAO loop with LLM-driven tool selection)
- Lab 3's MCP server (weather and geocoding tools)
- Lab 4's vector database (ChromaDB with office PDF data)

The LLM controls the entire workflow, deciding which tools to call
and when to stop — just like the agents in Labs 2 and 3.

Tools Available to the Agent
----------------------------
1. search_offices(query) → text chunks from office vector DB (local RAG)
2. geocode_location(name) → lat/lon coordinates (MCP server)
3. get_weather(lat, lon) → current weather in Celsius (MCP server)
4. convert_c_to_f(c) → temperature in Fahrenheit (MCP server)

Prerequisites
-------------
- ChromaDB populated: python tools/index_pdf.py (Lab 4)
- MCP server running: python mcp_server.py (Lab 3)
"""

# ────────────────────────── standard libs ───────────────────────────
import asyncio
import json
import re
import textwrap
from pathlib import Path

# ────────────────────────── third-party libs ────────────────────────
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from fastmcp import Client
from fastmcp.exceptions import ToolError
from langchain_ollama import ChatOllama

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 1.  Configuration                                               ║
# ╚══════════════════════════════════════════════════════════════════╝
CHROMA_PATH      = Path("./chroma_db")          # Where Lab 4 stored the vector DB
COLLECTION_NAME  = "codebase"                   # Collection name from Lab 4
MCP_ENDPOINT     = "http://127.0.0.1:8000/mcp/" # MCP server from Lab 3
TOP_K            = 3                            # Number of RAG results to retrieve

# TODO: Set up vector DB path, collection name, embedding model,
#       MCP endpoint, and regex patterns for parsing LLM responses

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 2.  RAG search tool (local — queries the ChromaDB from Lab 4)   ║
# ╚══════════════════════════════════════════════════════════════════╝

# TODO: Initialize embedding model and ChromaDB collection
# TODO: Implement search_offices(query) that the agent can call
#       to search the office vector database from Lab 4

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 3.  MCP result unwrapper                                        ║
# ╚══════════════════════════════════════════════════════════════════╝
def unwrap(obj):
    """Extract plain Python values from FastMCP result wrappers."""
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

# Construct the system prompt
SYSTEM = textwrap.dedent("""
You are an office information agent. You answer questions about company
offices by searching a database and looking up live weather data.


Examples:

# Fill in examples

When you have gathered all the information, respond with:
Thought: I have all the information needed
Action: DONE
Args: {}

# Add Rules
""").strip()

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 5.  TAO agent loop — the LLM decides which tools to call        ║
# ╚══════════════════════════════════════════════════════════════════╝
async def run(prompt: str, max_steps: int = 10) -> None:
# Run the agentic RAG loop where the LLM drives teh workflow.   

    # Track gathered data for the final display
    context = {
        "office_info": None,
        "city": None,
        "conditions": None,
        "temp_f": None,
    }

    print("\n" + "="*60)
    print("RAG Agent — Thought / Action / Observation")
    print("="*60 + "\n")

    async with Client(MCP_ENDPOINT) as mcp:
        for step in range(1, max_steps + 1):
            print(f"[Step {step}]")

#  Get what to do next from the LLM

            # ── Check if the agent decided it is done ─────────────────

                return

            # ── Parse the Args ────────────────────────────────────────
            args_match = ARGS_RE.search(response)
            if not args_match:
                print("\nError: Could not parse Args from response\n")
                break

            try:
                args = json.loads(args_match.group(1))
            except json.JSONDecodeError as e:
                print(f"\nError: Invalid JSON: {e}\n")
                break

            # ── Call the tool — local (RAG) or remote (MCP) ──────────
            print(f"\n-> Calling: {action}({json.dumps(args)})")

            try:
# call apprpriate tool
            except ToolError as e:
                result = f"Error: {e}"
            except Exception as e:
                result = f"Error: {type(e).__name__}: {e}"

            # Store relevant context from MCP tool results
            if action == "geocode_location" and isinstance(result, dict):
                context["city"] = result.get("name")
            elif action == "get_weather" and isinstance(result, dict):
                context["conditions"] = result.get("conditions")
            elif action == "convert_c_to_f" and isinstance(result, (int, float)):
                context["temp_f"] = float(result)

            # Format the observation and show it
            if isinstance(result, dict):
                obs_text = json.dumps(result)
            else:
                obs_text = str(result)
            print(f"Observation: {obs_text}\n")

            # Feed the observation back to the LLM
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user",
                             "content": f"Observation: {obs_text}"})

        print(f"\nReached maximum steps ({max_steps}).\n")

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 6.  Interactive loop                                             ║
# ╚══════════════════════════════════════════════════════════════════╝
if __name__ == "__main__":
    print("="*60)
    print("RAG-Enhanced Office Weather Agent")
    print("="*60)
    print("\nAsk about any office (e.g. 'Tell me about HQ')")
    print("Type 'exit' to quit\n")

    while True:
        prompt = input("User: ").strip()
        if prompt.lower() == "exit":
            print("Goodbye!")
            break
        if prompt:
            asyncio.run(run(prompt))
            print()
