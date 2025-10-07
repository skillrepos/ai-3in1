#!/usr/bin/env python3
"""
Quick local test to verify the canonical query workflow works
"""
import asyncio
from pathlib import Path
import pandas as pd

# Test data loading
def test_data_loading():
    print("=" * 60)
    print("TEST 1: Data Loading")
    print("=" * 60)

    csv_path = Path("data/offices.csv")
    print(f"CSV path: {csv_path.absolute()}")
    print(f"Exists: {csv_path.exists()}")

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} offices")
        print(f"Columns: {list(df.columns)}")
        print(f"\nSample data:")
        print(df.head())
        return df
    else:
        print("❌ CSV file not found!")
        return None

# Test analysis
def test_analysis(df):
    print("\n" + "=" * 60)
    print("TEST 2: Data Analysis")
    print("=" * 60)

    if df is None:
        print("❌ No data to analyze")
        return

    # Test highest revenue
    idx = df["revenue_million"].idxmax()
    result = f"{df.loc[idx, 'city']} office has the highest revenue: ${df.loc[idx, 'revenue_million']:.2f} million."
    print(f"✅ Highest revenue: {result}")

    # Test average revenue
    avg = df["revenue_million"].mean()
    print(f"✅ Average revenue: ${avg:.2f} million")

    # Test most employees
    idx = df["employees"].idxmax()
    print(f"✅ Most employees: {df.loc[idx, 'city']} office with {df.loc[idx, 'employees']} employees")

# Test Ollama connection
async def test_ollama():
    print("\n" + "=" * 60)
    print("TEST 3: Ollama Connection")
    print("=" * 60)

    try:
        from langchain_ollama import ChatOllama

        print("Attempting to connect to Ollama...")
        llm = ChatOllama(model="llama3.2:1b", temperature=0)

        response = llm.invoke([
            {"role": "user", "content": "Say 'hello' in exactly one word"}
        ])

        print(f"✅ Ollama responded: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return False

# Test MCP server
async def test_mcp():
    print("\n" + "=" * 60)
    print("TEST 4: MCP Server Connection")
    print("=" * 60)

    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()

        if result == 0:
            print("✅ MCP server is running on port 8000")
            return True
        else:
            print("❌ MCP server not accessible")
            return False
    except Exception as e:
        print(f"❌ MCP connection error: {e}")
        return False

async def main():
    print("\n🧪 LOCAL COMPONENT TEST\n")

    # Test data
    df = test_data_loading()
    if df is not None:
        test_analysis(df)

    # Test Ollama (optional - only if running)
    print("\nNote: Ollama test will fail if not running locally - that's OK")
    await test_ollama()

    # Test MCP (optional)
    print("\nNote: MCP test will fail if not running locally - that's OK")
    await test_mcp()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("If data loading and analysis passed, the core logic works!")
    print("Deploy to HuggingFace and check if Ollama starts properly.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
