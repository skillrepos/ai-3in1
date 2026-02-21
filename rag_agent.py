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
from sentence_transformers import SentenceTransformer
from fastmcp import Client
from fastmcp.exceptions import ToolError
from langchain_ollama import ChatOllama

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 1.  Configuration                                               ║
# ╚══════════════════════════════════════════════════════════════════╝

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

# TODO: Implement unwrap() to extract values from FastMCP wrappers
#       (same helper used in Lab 3's mcp_agent.py)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 4.  System prompt — tells the LLM about all available tools     ║
# ╚══════════════════════════════════════════════════════════════════╝

# TODO: Create system prompt listing all four tools and the
#       Thought/Action/Args format (similar to Labs 2 and 3)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 5.  TAO agent loop — the LLM decides which tools to call        ║
# ╚══════════════════════════════════════════════════════════════════╝

# TODO: Implement run(prompt) with an async agent loop that:
#       - Sends messages to the LLM and parses Thought/Action/Args
#       - Dispatches to search_offices (local) or MCP tools (remote)
#       - Feeds observations back to the LLM
#       - Stops when the LLM says DONE

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
