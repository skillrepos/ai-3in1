# Lab 9 Architecture: Deploying to Hugging Face Spaces

## Overview
Lab 9 deploys the **complete Lab 8 architecture** to Hugging Face Spaces - including the Streamlit app, RAG agent, MCP server, and Ollama - all running in a single Docker container. This makes the full AI assistant publicly accessible with the same capabilities as local development.

## Detailed Architecture Diagram

```mermaid
graph TB
    subgraph "Hugging Face Cloud Infrastructure"
        subgraph "Docker Container (Single Space)"
            Startup["huggingface_space.py<br/>Process Manager"]

            subgraph "Running Services"
                Ollama["Ollama Server<br/>:11434<br/>llama3.2:1b model"]
                MCP["MCP Server<br/>:8000<br/>mcp_server_classification.py"]
                Streamlit["Streamlit App<br/>:7860<br/>streamlit_app.py"]
            end

            subgraph "Application Layer"
                Agent["RAG Agent<br/>rag_agent_classification.py"]
                Data["Data Files<br/>offices.csv<br/>offices.pdf"]
            end

            subgraph "Storage"
                ChromaDB["ChromaDB<br/>/tmp/mcp_chroma_db<br/>Vector Index"]
            end

            Startup -->|Starts| Ollama
            Startup -->|Starts| MCP
            Startup -->|Starts| Streamlit
            Streamlit -->|imports| Agent
            Agent <-->|MCP Protocol| MCP
            MCP --> Data
            MCP --> ChromaDB
            Agent -->|LLM calls| Ollama
        end

        subgraph "Hugging Face Services"
            Storage[Persistent Storage]
            CDN[CDN for Static Files]
            Logs[Application Logs]
        end

        ChromaDB -.->|Optional| Storage
        Streamlit --> Logs
    end

    Users[Public Users<br/>Internet] -->|HTTPS| Streamlit

    style Startup fill:#9C27B0,color:#fff
    style Streamlit fill:#4CAF50,color:#fff
    style Agent fill:#2196F3,color:#fff
    style MCP fill:#FF9800,color:#fff
    style Ollama fill:#e8f5e9
    style Users fill:#ffe8e8
```

## Simple Architecture Diagram

```mermaid
flowchart LR
    Users([Public Users]) -->|HTTPS| HF[Hugging Face Space]

    subgraph Container["Docker Container"]
        Startup[huggingface_space.py] -->|starts| Ollama[Ollama Server]
        Startup -->|starts| MCP[MCP Server]
        Startup -->|starts| Streamlit[Streamlit App]
        Streamlit -->|imports| Agent[RAG Agent<br/>Lab 7]
        Agent <-->|MCP Protocol| MCP
        Agent -->|LLM| Ollama
        MCP --> DB[(ChromaDB)]
    end

    HF --> Container

    style HF fill:#FF9800,color:#fff
    style Startup fill:#9C27B0,color:#fff
    style Streamlit fill:#4CAF50,color:#fff
    style Agent fill:#2196F3,color:#fff
    style MCP fill:#FF6F00,color:#fff
```

## Deployment Architecture Comparison

```mermaid
graph TB
    subgraph "Local Development (Lab 8)"
        L_Browser[Browser] <--> L_Streamlit[Streamlit :8501]
        L_Streamlit -->|imports| L_Agent[RAG Agent]
        L_Agent <--> L_MCP[MCP Server :8000]
        L_Agent --> L_Ollama[Ollama :11434]
        L_MCP --> L_DB[(ChromaDB)]

        Note1["Multiple Terminal Windows<br/>Manual Process Management"]
    end

    subgraph "Hugging Face Deployment (Lab 9)"
        H_Internet[Internet] -->|HTTPS| H_HF[HF Space]

        subgraph "Single Docker Container"
            H_Startup[huggingface_space.py] -->|manages| H_Processes[3 Processes]
            H_Processes --> H_Streamlit[Streamlit :7860]
            H_Processes --> H_MCP[MCP Server :8000]
            H_Processes --> H_Ollama[Ollama :11434]
            H_Streamlit -->|imports| H_Agent[RAG Agent]
            H_Agent <--> H_MCP
            H_Agent --> H_Ollama
            H_MCP --> H_DB[(ChromaDB)]
        end

        H_HF --> H_Startup

        Note2["Automated Process Management<br/>Same Architecture, Different Deployment"]
    end

    style L_Agent fill:#2196F3,color:#fff
    style L_MCP fill:#FF9800,color:#fff
    style H_Startup fill:#9C27B0,color:#fff
    style H_Agent fill:#2196F3,color:#fff
    style H_MCP fill:#FF9800,color:#fff
```

## Component Details

### 1. Hugging Face Space Configuration

**README.md Header:**
```yaml
---
title: AI Office Assistant
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: 1.40.0
app_file: streamlit_app.py
pinned: false
license: mit
---
```

### 2. Dockerfile for Hugging Face

```dockerfile
FROM python:3.11-slim

# Install system dependencies (Ollama, build tools)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Create writable directories for ChromaDB
RUN mkdir -p /tmp/mcp_chroma_db && \
    chmod -R 777 /tmp/mcp_chroma_db

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port (HF Spaces uses 7860)
EXPOSE 7860

# Start script runs Ollama, MCP server, and Streamlit
CMD ["python3", "huggingface_space.py"]
```

### 3. Process Manager (huggingface_space.py)

```python
# huggingface_space.py - Manages all services

class ProcessManager:
    def start_ollama(self):
        """Start Ollama and pull llama3.2:1b model"""
        self.ollama_process = subprocess.Popen(["ollama", "serve"])
        time.sleep(5)
        subprocess.run(["ollama", "pull", "llama3.2:1b"])

    def start_mcp_server(self):
        """Start MCP classification server on :8000"""
        self.mcp_process = subprocess.Popen(
            ["python3", "mcp_server_classification.py"]
        )
        self.wait_for_mcp_server()

    def start_streamlit_app(self):
        """Start Streamlit app on :7860"""
        cmd = [
            "python3", "-m", "streamlit", "run",
            "streamlit_app.py",
            "--server.port", "7860",
            "--server.address", "0.0.0.0"
        ]
        self.streamlit_process = subprocess.Popen(cmd)

# Main startup
manager = ProcessManager()
manager.start_ollama()      # 1. Start Ollama
manager.start_mcp_server()  # 2. Start MCP Server
manager.start_streamlit_app()  # 3. Start Streamlit
```

### 4. Application Stack

The deployment uses the **same code as Lab 8**:
- **streamlit_app.py**: Web UI (unchanged)
- **rag_agent_classification.py**: RAG agent with classification (unchanged)
- **mcp_server_classification.py**: MCP server with tools (unchanged)

**Key Point**: The architecture is identical to local development - we just containerized it!

## Data Flow in Cloud Environment

```mermaid
sequenceDiagram
    participant User
    participant HF as Hugging Face
    participant Startup as huggingface_space.py
    participant Ollama
    participant MCP as MCP Server
    participant Streamlit
    participant Agent as RAG Agent

    Note over User,Startup: Container Startup
    HF->>Startup: Launch container
    Startup->>Ollama: Start Ollama server
    Ollama->>Ollama: Pull llama3.2:1b model
    Startup->>MCP: Start MCP server :8000
    MCP->>MCP: Initialize ChromaDB
    MCP->>MCP: Populate vector DB
    Startup->>Streamlit: Start Streamlit :7860

    Note over User,Agent: User Request
    User->>HF: HTTPS request
    HF->>Streamlit: Route to app
    Streamlit->>User: Render UI

    Note over User,Agent: Query Processing
    User->>Streamlit: Submit query
    Streamlit->>Agent: process_query()
    Agent->>MCP: classify_canonical_query()
    MCP->>Agent: Suggested query
    Agent->>MCP: get_query_template()
    MCP->>Agent: Template
    Agent->>MCP: get_filtered_office_data()
    MCP->>Agent: Data
    Agent->>Ollama: LLM inference
    Ollama->>Agent: Response
    Agent->>Streamlit: Result
    Streamlit->>User: Display answer
```

## Key Modifications for Cloud Deployment

### 1. Process Management
```python
# Local (Lab 8): Manual process management
# Terminal 1: python mcp_server_classification.py
# Terminal 2: streamlit run streamlit_app.py

# Cloud (Lab 9): Automated process management
# huggingface_space.py manages all three:
manager.start_ollama()      # Background process
manager.start_mcp_server()  # Background process
manager.start_streamlit_app()  # Foreground process
```

### 2. Lightweight Model
```python
# Local: Can use larger models
OLLAMA_MODEL = "llama3.2"  # 3B parameters

# Cloud: Use smaller model for faster startup
OLLAMA_MODEL = "llama3.2:1b"  # 1B parameters
```

### 3. ChromaDB Path
```python
# Local (Lab 8): Current directory
CHROMA_PATH = Path("./mcp_chroma_db")

# Cloud (Lab 9): Temp directory (writable in container)
CHROMA_PATH = Path("/tmp/mcp_chroma_db")
```

### 4. Port Configuration
```python
# Local (Lab 8):
# - Streamlit: 8501 (default)
# - MCP Server: 8000
# - Ollama: 11434 (default)

# Cloud (Lab 9):
# - Streamlit: 7860 (HF Spaces requirement)
# - MCP Server: 8000 (same)
# - Ollama: 11434 (same)
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
├── README.md                        # HF Space config (sdk: docker)
├── Dockerfile                       # Container definition
├── Dockerfile.hf                    # HF-specific Dockerfile
├── requirements.txt                 # Python dependencies
├── huggingface_space.py            # Process manager (starts all services)
├── streamlit_app.py                # Streamlit UI (from Lab 8)
├── rag_agent_classification.py     # RAG agent (from Lab 7)
├── mcp_server_classification.py    # MCP server (from Lab 6)
├── data/
│   ├── offices.csv                 # Office analytics data
│   └── offices.pdf                 # Office locations data
└── scripts/
    └── copyfiles.sh                # Deployment prep script
```

**Key Point**: All the application code (streamlit_app.py, rag_agent_classification.py, mcp_server_classification.py) is identical to Labs 6-8. Only the startup/orchestration changes!

## Requirements.txt

```txt
# Same dependencies as local development
streamlit>=1.28.0
pandas>=2.0.0
langchain-ollama>=0.1.0
fastmcp>=0.1.0              # Required for MCP server
chromadb>=0.4.0
sentence-transformers>=2.2.0
pdfplumber>=0.10.0          # For PDF processing
requests>=2.31.0

# Note: Identical to local requirements
# Full MCP architecture deployed to cloud
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
| **Deployment** | Local machine | Hugging Face Cloud (Docker) |
| **Process Management** | Manual (multiple terminals) | Automated (huggingface_space.py) |
| **MCP Server** | Manual start on :8000 | Auto-started in container |
| **Ollama** | Manual start | Auto-started + model pulled |
| **Model** | llama3.2 (3B) | llama3.2:1b (1B) |
| **Streamlit Port** | 8501 (default) | 7860 (HF requirement) |
| **ChromaDB Path** | ./mcp_chroma_db | /tmp/mcp_chroma_db |
| **Architecture** | Same 3-tier (UI→Agent→MCP) | Same 3-tier (UI→Agent→MCP) |
| **Access** | localhost:8501 | Public HTTPS URL |
| **Persistence** | Local disk | Container ephemeral |
| **Scalability** | Single user | Multiple concurrent users |
| **Resources** | Your hardware | HF allocated resources |
| **Cold Start** | Instant (if running) | ~60-90 seconds |

## Key Learning Points
- **Cloud Deployment**: Moving from local to cloud-based hosting
- **Container Packaging**: Docker for reproducible multi-service environments
- **Process Orchestration**: Managing multiple services in one container
- **Resource Optimization**: Using smaller models (1B vs 3B) for faster startup
- **Public Access**: Making AI apps shareable via HTTPS
- **Path Configuration**: Adapting file paths for container environments
- **Same Architecture**: Proof that good local architecture scales to cloud
- **Automated Management**: Single startup script replaces manual terminal management

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

---

<p align="center">
**For educational use only by the attendees of our workshops.**
</p>

**(C) 2025 Tech Skills Transformations and Brent C. Laster - all rights reserved.**
