#!/usr/bin/env python3
"""
Lab 3: TAO Agent with FastMCP Weather Server
────────────────────────────────────────────────────────────────────
A TRUE agentic implementation where the LLM dynamically selects which
tools to call and when to stop. This demonstrates:


Prerequisites: FastMCP weather server must be running on localhost:8000
"""

import asyncio
import json
import re
import textwrap
from typing import Optional, Dict, Any

from fastmcp import Client
from fastmcp.exceptions import ToolError
from langchain_ollama import ChatOllama

SYSTEM = textwrap.dedent("""
You are a weather information agent with access to these tools:

""").strip()

# Regex patterns for parsing LLM responses
ACTION_RE = re.compile(r"Action:\s*(\w+)", re.IGNORECASE)
ARGS_RE = re.compile(r"Args:\s*(\{.*?\})(?:\s|$)", re.S | re.IGNORECASE)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 2.  Robust unwrap helper                                         ║
# ╚══════════════════════════════════════════════════════════════════╝
# FastMCP wraps tool results in various formats depending on version.
# This helper extracts the actual Python value from any wrapper format.
def unwrap(obj):
    """Extract plain Python value from FastMCP wrapper objects."""
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
# ║ 3.  Simple regex-based city extractor (no LLM call)             ║
# ╚══════════════════════════════════════════════════════════════════╝
# Parses city names from natural language without requiring an LLM call.
# Handles inputs like "What's the weather in Paris?" → "Paris"

def extract_city(prompt: str) -> Optional[str]:
    """Extract city name from natural language using regex patterns."""
    # Pattern 1: "in <City>", "at <City>", "for <City>"
    patterns = [
        r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in New York"
        r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "at San Francisco"
        r'\bfor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', # "for Los Angeles"
    ]

    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return match.group(1)

    # Pattern 2: Find capitalized words (fallback)
    # Look for capitalized words that might be city names
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', prompt)
    if capitalized:
        # Return the longest match (likely to be the full city name)
        return max(capitalized, key=len)

    # Pattern 3: If no capitalized words, assume entire input is city name
    # This handles lowercase inputs like "paris" or "new york"
    cleaned = re.sub(r'\b(what|is|the|weather|in|at|for|tell|me|about)\b', '',
                     prompt, flags=re.IGNORECASE).strip()
    if cleaned:
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in cleaned.split())

    return None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 4.  Dynamic TAO loop with LLM-controlled tool selection          ║
# ╚══════════════════════════════════════════════════════════════════╝

    async with Client("http://127.0.0.1:8000/mcp/") as mcp:
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"What is the current weather in {city}?"},
        ]

        print("\n" + "="*60)
        print("Dynamic TAO Agent - LLM Controls Tool Selection")
        print("="*60 + "\n")

        # Store context for final answer
        context = {
            "city": city,
            "latitude": None,
            "longitude": None,
            "temperature_c": None,
            "temperature_f": None,
            "conditions": None,
        }

        for step in range(1, max_steps + 1):
            print(f"[Step {step}]")
                        

            action = action_match.group(1).lower()

            # Check if LLM says we're done
            if action == "done":
                print("\n" + "="*60)
                print("Agent has gathered sufficient information!")
                print("="*60)

                # Generate final summary
                if context["temperature_f"] is not None:
                    temp_display = f"{context['temperature_f']:.1f}°F"
                elif context["temperature_c"] is not None:
                    temp_display = f"{context['temperature_c']:.1f}°C"
                else:
                    temp_display = "Unknown"

                print(f"\nFinal Answer:")
                print(f"  Location: {context.get('location_name', city)}")
                print(f"  Conditions: {context['conditions'] or 'Unknown'}")
                print(f"  Temperature: {temp_display}")
                return

            # Parse arguments
            args_match = ARGS_RE.search(response)
            if not args_match:
                print(f"\n❌ Error: Could not parse Args from LLM response")
                return

            try:
                args = json.loads(args_match.group(1))
            except json.JSONDecodeError as e:
                print(f"\n❌ Error: Invalid JSON in Args: {e}")
                return


            except ToolError as e:
                print(f"❌ MCP Error: {e}\n")
                # Add error to conversation and let LLM try to recover
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Observation: Error calling {action} - {e}"})
                continue
            except Exception as e:
                print(f"❌ Unexpected Error: {type(e).__name__}: {e}\n")
                return

            # Handle tool-specific errors (e.g., geocoding failures)
            if isinstance(result, dict) and "error" in result:
                print(f"⚠️  Tool returned error: {result['error']}\n")
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Observation: {result}"})
                continue

            # Store relevant data in context
            if action == "geocode_location" and isinstance(result, dict):
                context["latitude"] = result.get("latitude")
                context["longitude"] = result.get("longitude")
                context["location_name"] = result.get("name", city)
            elif action == "get_weather" and isinstance(result, dict):
                context["temperature_c"] = result.get("temperature")
                context["conditions"] = result.get("conditions")
            elif action == "convert_c_to_f":
                context["temperature_f"] = float(result)           
        # Max steps reached
        print(f"\n⚠️  Reached maximum steps ({max_steps}) without completion")
        print("Partial information gathered:")
        for key, value in context.items():
            if value is not None:
                print(f"  {key}: {value}")

# ╔══════════════════════════════════════════════════════════════════╗
# ║ 5.  Interactive REPL                                             ║
# ╚══════════════════════════════════════════════════════════════════╝
if __name__ == "__main__":
    print("="*60)
    print("Dynamic Weather TAO Agent")
    print("="*60)
    print("\nThis agent uses LLM-controlled tool selection.")
    print("The LLM decides which tools to call and when to stop.\n")
    print("Type 'exit' to quit\n")

    while True:
        raw_prompt = input("Ask about the weather: ").strip()
        if raw_prompt.lower() == "exit":
            break

        city = extract_city(raw_prompt)
        if not city or len(city) < 3:
            print("❌ No city detected; please try again.\n")
            continue

        print(f"\n🔍 Detected city: {city}")
        asyncio.run(run_dynamic(city))
        print()
