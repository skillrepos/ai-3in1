#!/usr/bin/env python3
"""
Model Warmup Script
───────────────────────────────────────────────────────────────────
Primes Ollama LLM and embedding models by loading them into memory.
This significantly reduces the first-run latency for labs 3, 5, 7, etc.

⏱️  WHY USE THIS SCRIPT?
   The first time you use an LLM or embedding model in a lab, there's a
   noticeable delay (30-60 seconds) as the model loads into memory. This
   script pre-loads the models so your labs start quickly.

📋 WHEN TO RUN:
   • After Lab 1, Step 4 (after `ollama pull llama3.2`)
   • Any time you restart Ollama (`ollama serve &`)
   • Before starting Labs 3, 5, 7, or any agent-based labs

⚡ WHAT IT DOES:
   1. Loads llama3.2 LLM into Ollama's memory
   2. Downloads and loads the sentence transformer embedding model
   3. Verifies ChromaDB is available for vector storage
   4. Pre-populates MCP server's vector database (for Labs 6-7)

💡 TIP: Run this once at the start of your session, then all labs will be fast!

Usage:
    python warmup_models.py
"""

import os
import sys
import time
from pathlib import Path

print("=" * 60)
print("Model Warmup Script")
print("=" * 60)
print("\nThis script will load models into memory to reduce first-run latency.")
print("Please wait while models are warmed up...\n")

# ═══════════════════════════════════════════════════════════════════
# 1. Warm up Ollama LLM (llama3.2)
# ═══════════════════════════════════════════════════════════════════
print("[1/3] Warming up Ollama LLM (llama3.2)...")
start = time.time()

try:
    from langchain_ollama import ChatOllama

    # Get model name from environment or use default
    model_name = os.getenv("OLLAMA_MODEL", "llama3.2")

    # Initialize the LLM (this loads the model into memory)
    llm = ChatOllama(model=model_name, temperature=0.0)

    # Make a simple test call to fully load the model
    print(f"   • Loading {model_name} into memory...")
    response = llm.invoke("Hello")

    elapsed = time.time() - start
    print(f"   ✓ Ollama LLM loaded successfully ({elapsed:.1f}s)")
    print(f"   • Model: {model_name}")

except ImportError as e:
    print(f"   ✗ Error: langchain_ollama not installed")
    print(f"   • Install with: pip install langchain-ollama")
    sys.exit(1)

except Exception as e:
    print(f"   ✗ Error loading Ollama LLM: {e}")
    print(f"\n   Troubleshooting:")
    print(f"   • Is Ollama running? Try: ollama serve &")
    print(f"   • Is llama3.2 downloaded? Try: ollama pull llama3.2")
    print(f"   • Check Ollama status: ollama list")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
# 2. Warm up Sentence Transformer (all-MiniLM-L6-v2)
# ═══════════════════════════════════════════════════════════════════
print("\n[2/3] Warming up Sentence Transformer (all-MiniLM-L6-v2)...")
start = time.time()

try:
    from sentence_transformers import SentenceTransformer

    # Initialize the embedding model (this downloads and loads it)
    print("   • Loading embedding model into memory...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Make a test encoding to fully load the model
    test_embedding = embed_model.encode("test")

    elapsed = time.time() - start
    print(f"   ✓ Sentence Transformer loaded successfully ({elapsed:.1f}s)")
    print(f"   • Model: all-MiniLM-L6-v2")
    print(f"   • Embedding dimension: {len(test_embedding)}")

except ImportError:
    print(f"   ✗ Error: sentence-transformers not installed")
    print(f"   • Install with: pip install sentence-transformers")
    sys.exit(1)

except Exception as e:
    print(f"   ✗ Error loading Sentence Transformer: {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
# 3. Verify ChromaDB (optional - doesn't need warmup)
# ═══════════════════════════════════════════════════════════════════
print("\n[3/4] Verifying ChromaDB installation...")
start = time.time()

try:
    import chromadb
    from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE

    # Just verify import works - no need to create a client
    elapsed = time.time() - start
    print(f"   ✓ ChromaDB available ({elapsed:.3f}s)")

    # Check if chroma_db directory exists
    chroma_path = Path("./chroma_db")
    if chroma_path.exists():
        print(f"   • Found existing ChromaDB at {chroma_path}")
    else:
        print(f"   • ChromaDB will be created when first used")

except ImportError:
    print(f"   ✗ Warning: chromadb not installed (needed for Labs 5, 7)")
    print(f"   • Install with: pip install chromadb")

# ═══════════════════════════════════════════════════════════════════
# 4. Pre-populate MCP Server Vector Database (for Labs 6-7)
# ═══════════════════════════════════════════════════════════════════
print("\n[4/4] Pre-populating MCP server vector database...")
start = time.time()

try:
    import pandas as pd
    import chromadb
    from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE
    from sentence_transformers import SentenceTransformer

    try:
        import pdfplumber
        pdf_available = True
    except ImportError:
        pdf_available = False
        print("   ⚠️  pdfplumber not installed - skipping PDF data")

    # Paths
    MCP_CHROMA_PATH = Path("./mcp_chroma_db")
    OFFICE_CSV = Path("./data/offices.csv")
    OFFICE_PDF = Path("./data/offices.pdf")

    # Check if vector DB already populated
    if MCP_CHROMA_PATH.exists():
        client = chromadb.PersistentClient(
            path=str(MCP_CHROMA_PATH),
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )

        try:
            locations = client.get_collection("office_locations")
            analytics = client.get_collection("office_analytics")

            if locations.count() > 0 and analytics.count() > 0:
                print(f"   ✓ MCP vector DB already populated ({elapsed:.3f}s)")
                print(f"   • Locations: {locations.count()} documents")
                print(f"   • Analytics: {analytics.count()} documents")
                print(f"   • Path: {MCP_CHROMA_PATH}")
            else:
                raise ValueError("Collections exist but are empty")

        except Exception:
            # Collections don't exist or are empty, populate them
            print(f"   • Creating MCP vector database...")
            populate_needed = True
    else:
        print(f"   • Creating MCP vector database...")
        populate_needed = True

    # Populate if needed
    if 'populate_needed' in locals() and populate_needed:
        # Initialize
        client = chromadb.PersistentClient(
            path=str(MCP_CHROMA_PATH),
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )
        locations_coll = client.get_or_create_collection("office_locations")
        analytics_coll = client.get_or_create_collection("office_analytics")

        # Use already-loaded embedding model
        print(f"   • Using pre-loaded embedding model...")

        # Populate locations from PDF
        if pdf_available and OFFICE_PDF.exists():
            print(f"   • Reading {OFFICE_PDF.name}...")
            with pdfplumber.open(OFFICE_PDF) as pdf:
                lines = []
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    for line in text.split('\n'):
                        line = line.strip()
                        if line:
                            lines.append(line)

            print(f"   • Embedding {len(lines)} location documents...")
            for idx, line in enumerate(lines):
                vector = embed_model.encode(line).tolist()
                locations_coll.add(
                    ids=[f"pdf-{idx}"],
                    embeddings=[vector],
                    documents=[line],
                    metadatas=[{"source": "offices.pdf", "line": idx}],
                )
            print(f"   ✓ Populated {len(lines)} location documents")
        else:
            if not pdf_available:
                print(f"   ⚠️  Skipping PDF (pdfplumber not installed)")
            elif not OFFICE_PDF.exists():
                print(f"   ⚠️  Skipping PDF ({OFFICE_PDF} not found)")

        # Populate analytics from CSV
        if OFFICE_CSV.exists():
            print(f"   • Reading {OFFICE_CSV.name}...")
            df = pd.read_csv(OFFICE_CSV)

            print(f"   • Embedding {len(df)} analytics documents...")
            for idx, row in df.iterrows():
                text = (f"{row['city']} office with {row['employees']} employees "
                       f"and ${row['revenue_million']}M revenue, opened in {row['opened_year']}")
                vector = embed_model.encode(text).tolist()
                analytics_coll.add(
                    ids=[f"csv-{idx}"],
                    embeddings=[vector],
                    documents=[text],
                    metadatas={
                        "source": "offices.csv",
                        "city": row['city'],
                        "employees": int(row['employees']),
                        "revenue_million": float(row['revenue_million']),
                        "opened_year": int(row['opened_year'])
                    },
                )
            print(f"   ✓ Populated {len(df)} analytics documents")
        else:
            print(f"   ⚠️  Skipping CSV ({OFFICE_CSV} not found)")

        elapsed = time.time() - start
        print(f"   ✓ MCP vector DB populated successfully ({elapsed:.1f}s)")
        print(f"   • Path: {MCP_CHROMA_PATH}")

except ImportError as e:
    print(f"   ⚠️  Skipping MCP vector DB (missing dependencies)")
    print(f"   • This is OK for Labs 3-5, needed for Labs 6-7")

except Exception as e:
    print(f"   ⚠️  Could not populate MCP vector DB: {e}")
    print(f"   • MCP server will populate it on first startup")

# ═══════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("✓ Warmup Complete!")
print("=" * 60)
print("\nModels are now loaded in memory. Your labs should start faster!")
print("\nReady to run:")
print("  • Lab 3: python mcp_agent.py")
print("  • Lab 5: python rag_agent.py")
print("  • Lab 7: python rag_agent_classification.py")
print("\nNote: Models will remain in memory until Ollama is restarted.")
print("=" * 60)
