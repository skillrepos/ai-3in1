# Lab 9 Architecture: Deploying to Hugging Face Spaces

## Overview
Lab 9 focuses on deploying the Streamlit app to Hugging Face Spaces, making the AI assistant publicly accessible with cloud-based inference.

## Detailed Architecture Diagram

```mermaid
graph TB
    subgraph "Hugging Face Cloud Infrastructure"
        subgraph "Space Container"
            App[Streamlit App app.py]

            subgraph "Embedded Components"
                Agent[RAG Agent Embedded Logic]
                Fallback[Fallback Mode No MCP Server]
                Data[(Embedded offices.csv)]
            end

            subgraph "Local Resources"
                Ollama[Ollama Server llama3.2:1b]
                ChromaDB[(ChromaDB Vector Index)]
            end

            App --> Agent
            Agent --> Fallback
            Agent --> Data
            Agent --> Ollama
            Agent --> ChromaDB
        end

        subgraph "Hugging Face Services"
            Inference[Inference API Optional]
            Storage[Persistent Storage Vector DB]
            CDN[CDN for Static Files]
        end

        App --> Inference
        ChromaDB --> Storage
    end

    Users[Public Users Internet] -->|HTTPS| App

    style App fill:#e1f5ff
    style Fallback fill:#fff4e1
    style Ollama fill:#e8f5e9
    style Users fill:#ffe8e8
```

## Presentation Slide Diagram (Simple)

```mermaid
flowchart LR
    Users([Public Users]) -->|HTTPS| HF[Hugging Face Space]
    HF -->|Runs| Streamlit[Streamlit App]
    Streamlit -->|Embedded| Agent[RAG Agent]
    Agent -->|Local| Ollama[Ollama llama3.2:1b]
    Agent -->|Local| DB[(ChromaDB)]

    style HF fill:#FF9800,color:#fff
    style Streamlit fill:#4CAF50,color:#fff
    style Agent fill:#2196F3,color:#fff
```

## Deployment Architecture Comparison

```mermaid
graph TB
    subgraph "Local Development (Lab 8)"
        L_Browser[Browser] <--> L_Streamlit[Streamlit :8501]
        L_Streamlit <--> L_MCP[MCP Server :8000]
        L_Streamlit <--> L_Ollama[Ollama :11434]
        L_Streamlit <--> L_DB[(ChromaDB)]

        Note1[Multiple Processes Separate Services]
    end

    subgraph "Hugging Face Deployment (Lab 9)"
        H_Internet[Internet] -->|HTTPS| H_HF[HF Space]
        H_HF --> H_App[Streamlit App]

        subgraph "Single Container"
            H_App --> H_Agent[Embedded Agent]
            H_Agent --> H_Ollama[Ollama Downloaded]
            H_Agent --> H_DB[(ChromaDB Built-in)]
            H_Agent --> H_CSV[(offices.csv Included)]
        end

        Note2[Single Container All-in-One]
    end

    style L_MCP fill:#f44336,color:#fff
    style H_App fill:#4caf50,color:#fff
```

## Component Details

### 1. Hugging Face Space Configuration

**README.md Header:**
```yaml
---
title: AI Office Assistant
emoji: 📊
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.28.0"
app_file: app.py
pinned: false
python_version: "3.10"
---
```

### 2. Dockerfile for Hugging Face

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download Ollama
RUN curl -L https://ollama.ai/install.sh | sh

# Pull llama3.2:1b model
RUN ollama pull llama3.2:1b

# Expose Streamlit port
EXPOSE 7860

# Start script
CMD ["sh", "start_huggingface_space.py"]
```

### 3. Embedded Agent (app.py)

```python
# app.py - Optimized for Hugging Face Spaces

# Embedded logic - no MCP server needed
def analyze_offices_embedded(canonical_query: str, df) -> str:
    """Direct execution without MCP"""
    if canonical_query == "highest_revenue":
        idx = df["revenue_million"].idxmax()
        return f"{df.loc[idx, 'city']}: ${df.loc[idx, 'revenue_million']}M"
    # ... more queries

def classify_query_embedded(query: str) -> str:
    """LLM classification without MCP"""
    llm = ChatOllama(model="llama3.2:1b", temperature=0)
    # Direct classification logic
    return canonical_query

# Use embedded functions instead of MCP calls
result = analyze_offices_embedded(canonical, df)
```

### 4. Startup Script

```python
# start_huggingface_space.py

import subprocess
import time
import os

# Start Ollama in background
ollama_process = subprocess.Popen(["ollama", "serve"])
time.sleep(5)  # Wait for Ollama to start

# Ensure model is available
subprocess.run(["ollama", "pull", "llama3.2:1b"])

# Index data if needed
if not os.path.exists("chroma_db"):
    subprocess.run(["python", "tools/index_pdf.py"])

# Start Streamlit
subprocess.run(["streamlit", "run", "app.py", "--server.port=7860"])
```

## Data Flow in Cloud Environment

```mermaid
sequenceDiagram
    participant User
    participant HF as Hugging Face
    participant Container
    participant Streamlit
    participant Agent
    participant Ollama
    participant DB as ChromaDB

    Note over User,HF: Initial Access
    User->>HF: HTTPS request
    HF->>Container: Route to Space
    Container->>Streamlit: Start if not running

    Note over Streamlit,DB: Initialization
    Streamlit->>Ollama: Start server
    Streamlit->>DB: Load/create vector index
    Streamlit->>User: Render UI

    Note over User,DB: Query Processing
    User->>Streamlit: Submit query
    Streamlit->>Agent: Process (embedded)
    Agent->>DB: RAG search (if weather)
    Agent->>Ollama: LLM call (local)
    Agent->>Agent: Data analysis (if data query)
    Agent->>Streamlit: Response
    Streamlit->>User: Display result
```

## Key Modifications for Cloud Deployment

### 1. Remove MCP Server Dependency
```python
# Local (Lab 8):
async with Client(MCP_ENDPOINT) as mcp:
    result = await mcp.call_tool("analyze_offices", args)

# Cloud (Lab 9):
result = analyze_offices_embedded(canonical_query, df)
```

### 2. Lightweight Model
```python
# Local: Can use larger models
OLLAMA_MODEL = "llama3.2"  # 3B parameters

# Cloud: Use smaller model
OLLAMA_MODEL = "llama3.2:1b"  # 1B parameters - faster, less memory
```

### 3. Included Data Files
```
/app/
  ├── app.py
  ├── data/
  │   └── offices.csv        # Included in deployment
  ├── chroma_db/             # Pre-built or built on startup
  └── requirements.txt
```

### 4. Environment Detection
```python
def is_huggingface_space():
    return os.environ.get("SPACE_ID") is not None

if is_huggingface_space():
    # Use embedded logic
    use_mcp = False
else:
    # Try to connect to MCP server
    use_mcp = check_mcp_available()
```

## Resource Optimization

```mermaid
graph TB
    subgraph "Resource Constraints"
        CPU[CPU: 2 cores]
        RAM[RAM: 16GB]
        Storage[Storage: 50GB]
        Time[Cold Start: ~30s]
    end

    subgraph "Optimizations"
        O1[Lightweight Model llama3.2:1b]
        O2[Pre-built Vector Index]
        O3[Embedded Logic No MCP]
        O4[Minimal Dependencies]
    end

    CPU --> O1
    RAM --> O1
    Storage --> O2
    Time --> O3
    Time --> O4

    style CPU fill:#ffe8e8
    style O1 fill:#e8f5e9
    style O2 fill:#e8f5e9
    style O3 fill:#e8f5e9
```

## Deployment Process

```mermaid
flowchart TD
    Start([Start]) --> Create[Create HF Space]
    Create --> Clone[Clone Repo Locally]
    Clone --> Modify[Modify app.py for Cloud]
    Modify --> Add[Add Dockerfile + requirements.txt]
    Add --> Test[Test Locally]
    Test --> Push[Push to HF Space]
    Push --> Build[HF Builds Container]
    Build --> Deploy[Deploy to Cloud]
    Deploy --> Monitor[Monitor Logs]
    Monitor --> Live[Space Live!]

    Test -->|Issues| Modify

    style Create fill:#e1f5ff
    style Build fill:#fff4e1
    style Live fill:#e8f5e9
```

## File Structure for Deployment

```
huggingface-space/
├── README.md                 # HF Space config
├── Dockerfile               # Container definition
├── requirements.txt         # Python dependencies
├── app.py                   # Main Streamlit app (embedded logic)
├── start_huggingface_space.py  # Startup script
├── data/
│   └── offices.csv         # Office data
├── tools/
│   └── index_pdf.py        # Vector indexing
└── docs/
    └── offices.pdf         # Source document
```

## Requirements.txt Optimization

```txt
# Minimal dependencies for cloud deployment
streamlit==1.28.0
pandas==2.0.3
langchain-ollama==0.1.0
chromadb==0.4.15
sentence-transformers==2.2.2
requests==2.31.0

# Note: Reduced from full local requirements
# Removed: fastmcp (embedded logic instead)
```

## Monitoring and Logs

```mermaid
graph LR
    subgraph "Hugging Face Dashboard"
        Logs[Application Logs stdout/stderr]
        Metrics[Usage Metrics Requests/Min]
        Status[Health Status Running/Stopped]
    end

    subgraph "Application"
        App[Streamlit App]
        Print[print statements]
        Errors[Error handling]
    end

    App --> Print
    App --> Errors
    Print --> Logs
    Errors --> Logs
    App --> Metrics
    App --> Status

    style Logs fill:#e1f5ff
    style Metrics fill:#fff4e1
    style Status fill:#e8f5e9
```

## Key Differences from Lab 8

| Aspect | Lab 8 (Local) | Lab 9 (Cloud) |
|--------|---------------|---------------|
| Deployment | Local machine | Hugging Face Cloud |
| MCP Server | Required (:8000) | Embedded in app |
| Model | llama3.2 (3B) | llama3.2:1b (1B) |
| Access | localhost:8501 | Public URL |
| Persistence | Local disk | HF persistent storage |
| Scalability | Single user | Multiple users |
| Resources | Your hardware | HF allocated resources |
| Cold Start | Instant | ~30 seconds |

## Key Learning Points
- **Cloud Deployment**: Moving from local to cloud
- **Container Packaging**: Docker for reproducible environments
- **Resource Optimization**: Smaller models, embedded logic
- **Public Access**: Sharing apps with the world
- **Serverless Considerations**: Cold starts, resource limits
- **Embedded vs Distributed**: When to embed vs separate services
- **Configuration Management**: Environment-specific settings

## Architecture Characteristics
- **Type**: Cloud-hosted web application
- **Platform**: Hugging Face Spaces
- **Container**: Docker-based
- **Model**: Ollama llama3.2:1b (local to container)
- **Public**: Yes (shareable URL)
- **Persistence**: HF storage for vector DB
- **Scalability**: HF handles multiple concurrent users
- **Cost**: Free tier available

## Benefits

1. **Public Access**: Anyone can use the app
2. **No Setup**: Users don't need to install anything
3. **Shareable**: Easy to share URL
4. **Persistent**: App stays running
5. **Professional**: Custom domain possible
6. **Free Hosting**: HF provides free tier
7. **CI/CD**: Auto-deploy on git push
8. **Monitoring**: Built-in logs and metrics

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Resource limits | Use smaller model (1B params) |
| Cold starts | Optimize startup script |
| No MCP server | Embed logic directly |
| Network latency | Cache vector index |
| Cost concerns | Use free tier, optimize queries |
| Debugging | Comprehensive logging |

## Production Considerations

1. **Error Handling**: Robust fallbacks for API failures
2. **Rate Limiting**: Prevent abuse
3. **Caching**: Cache embeddings, reduce computation
4. **Monitoring**: Track errors and usage
5. **Security**: No sensitive data in public space
6. **Performance**: Optimize for cold starts
7. **Documentation**: Clear README for users
