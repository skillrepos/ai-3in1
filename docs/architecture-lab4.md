# Lab 4 Architecture: Working with Vector Databases

## Overview
Lab 4 introduces vector databases (ChromaDB) for semantic search and similarity matching, enabling RAG capabilities.

## Detailed Architecture Diagram

```mermaid
graph TB
    subgraph "Indexing Phase"
        Source1["Source - offices.pdf"]
        Source2["Source - *.py files"]

        Chunker[Text Chunker Split into chunks]

        Embedder[Embedding Model all-MiniLM-L6-v2]

        ChromaDB[(ChromaDB Vector Database)]

        Source1 --> Chunker
        Source2 --> Chunker
        Chunker --> Embedder
        Embedder -->|Store vectors| ChromaDB
    end

    subgraph "Search Phase"
        Query["User Query - High revenue branch"]

        QueryEmbed[Embed Query all-MiniLM-L6-v2]

        VectorSearch[Cosine Similarity Search]

        Results[Top-K Results with scores]

        Query --> QueryEmbed
        QueryEmbed --> VectorSearch
        ChromaDB --> VectorSearch
        VectorSearch --> Results
    end

    style Embedder fill:#e1f5ff
    style ChromaDB fill:#fff4e1
    style VectorSearch fill:#e8f5e9
```

## Presentation Slide Diagram (Simple)

```mermaid
flowchart TD
    Docs([Documents]) -->|1. Chunk & Embed| Index[Embedding Model]
    Index -->|2. Store| DB[(Vector DB ChromaDB)]
    Query([Query]) -->|3. Embed| Index
    Index -->|4. Search| DB
    DB -->|5. Top Matches| Results([Results])

    style Index fill:#4CAF50,color:#fff
    style DB fill:#2196F3,color:#fff
    style Results fill:#FF9800,color:#fff
```

## Vector Embedding Process

```mermaid
sequenceDiagram
    participant Doc as Document
    participant Chunker
    participant Embedder as Embedding Model
    participant DB as ChromaDB

    Note over Doc,DB: Indexing Phase
    Doc->>Chunker: "New York Office, 120 employees, $85.5M revenue"
    Chunker->>Embedder: Chunk 1
    Embedder->>Embedder: Generate 384-dim vector
    Embedder->>DB: store(chunk, [0.12, -0.45, ..., 0.88])

    Note over Doc,DB: Search Phase
    Doc->>Embedder: "High revenue branch"
    Embedder->>Embedder: Generate query vector
    Embedder->>DB: search([0.15, -0.42, ..., 0.82])
    DB->>DB: Cosine similarity
    DB->>Doc: Top-5 matches with scores
```

## Component Details

### 1. Embedding Model (SentenceTransformer)
```python
model = SentenceTransformer("all-MiniLM-L6-v2")
embedding = model.encode(text)  # Returns 384-dim vector
```

**Specifications:**
- Model: all-MiniLM-L6-v2
- Dimensions: 384
- Size: ~80MB
- Speed: ~1000 sentences/sec on CPU

### 2. ChromaDB
```python
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("codebase")

# Add documents
collection.add(
    documents=["text chunk"],
    embeddings=[[0.12, -0.45, ...]],
    ids=["chunk_1"]
)

# Search
results = collection.query(
    query_embeddings=[[0.15, -0.42, ...]],
    n_results=5
)
```

**Features:**
- Persistent storage on disk
- Cosine similarity search
- Metadata filtering
- Efficient indexing (HNSW)

### 3. Indexing Tools

**index_code.py**: Index Python files
```python
for file in glob("**/*.py"):
    chunks = chunk_text(file.read_text())
    embeddings = model.encode(chunks)
    collection.add(documents=chunks, embeddings=embeddings)
```

**index_pdf.py**: Index PDF documents
```python
pdf_text = extract_text_from_pdf("offices.pdf")
chunks = chunk_text(pdf_text)
embeddings = model.encode(chunks)
collection.add(documents=chunks, embeddings=embeddings)
```

### 4. Search Tool (search.py)
```python
query_embedding = model.encode(user_query)
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)
# Returns: documents + cosine similarity scores
```

## Vector Space Visualization

```mermaid
graph TD
    subgraph "384-Dimensional Vector Space"
        V1[["Paris Office [0.12, -0.45, ...]"]]
        V2[["New York Office [0.15, -0.42, ...]"]]
        V3[["Chicago Office [0.18, -0.48, ...]"]]
        Q[["Query - High revenue [0.16, -0.44, ...]"]]

        Q -.->|Distance: 0.02| V2
        Q -.->|Distance: 0.15| V1
        Q -.->|Distance: 0.25| V3
    end

    Note["Cosine Similarity - Closer = More Similar"]

    style Q fill:#ffeb3b
    style V2 fill:#4caf50
    style V1 fill:#9e9e9e
    style V3 fill:#9e9e9e
```

## Data Flow

### Indexing Flow
```
Source Files → Read Text → Chunk (512 chars) → Embed → Store in ChromaDB
```

**Example:**
```
offices.pdf (10 offices) → 50 chunks → 50 embeddings → ChromaDB collection
```

### Search Flow
```
User Query → Embed → Cosine Similarity Search → Top-K Results → Display
```

**Example:**
```
"High revenue" → [0.16, -0.44, ...] → Search → Top 5 matches → Print scores
```

## Cosine Similarity Calculation

```mermaid
graph LR
    A[Query Vector q = [0.16, -0.44, ...]] --> CS[Cosine Similarity]
    B[Document Vector d = [0.15, -0.42, ...]] --> CS
    CS --> Score["Score - 0.98 Very Similar"]

    style CS fill:#e1f5ff
    style Score fill:#e8f5e9
```

**Formula:**
```
similarity = (q · d) / (||q|| * ||d||)
Range: [-1, 1], typically [0, 1] for semantic search
```

## Comparison: Keyword vs. Semantic Search

```mermaid
graph TB
    subgraph "Keyword Search"
        KQ["Query - high revenue"]
        KM[Exact Match Only]
        KR["Finds - 'high revenue'"]
        KQ --> KM --> KR
    end

    subgraph "Semantic/Vector Search"
        SQ["Query - high revenue"]
        SE[Embedding]
        SS[Similarity Search]
        SR["Finds - 'high revenue' 'top earning' 'most profitable' '$85.5M'"]
        SQ --> SE --> SS --> SR
    end

    style SR fill:#e8f5e9
    style KR fill:#ffe8e8
```

## Key Learning Points
- **Vector Embeddings**: Text → Numeric representation
- **Semantic Search**: Find similar meaning, not just keywords
- **Cosine Similarity**: Measure distance in vector space
- **Chunking Strategy**: Split long documents for better matching
- **Persistence**: ChromaDB stores vectors on disk
- **Embedding Models**: Pre-trained models encode semantic meaning

## Architecture Characteristics
- **Type**: Offline indexing + Online search
- **Complexity**: Medium
- **Dependencies**: SentenceTransformers, ChromaDB
- **Storage**: Disk-based (./chroma_db/)
- **Search Speed**: ~100ms for 1000 vectors (local)
- **Scalability**: Handles millions of vectors

## Performance Metrics

| Metric | Value |
|--------|-------|
| Embedding Speed | ~1000 sentences/sec |
| Index Size (10 offices) | ~50 chunks, ~20KB |
| Search Latency | 10-100ms |
| Vector Dimensions | 384 |
| Top-K Results | 5 (configurable) |

## Use Cases Enabled
1. **Document Search**: Find relevant content semantically
2. **Code Search**: Find similar code patterns
3. **Question Answering**: Retrieve context for answers
4. **Recommendation**: Find similar items
5. **RAG Foundation**: Retrieval for generation (Lab 5)
