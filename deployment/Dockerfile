FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl and other dependencies needed for Ollama
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory and ChromaDB directory with proper permissions
RUN mkdir -p data && \
    mkdir -p mcp_chroma_db && \
    chmod -R 777 mcp_chroma_db && \
    chmod -R 755 data
    
# Create data and chroma_db directories with proper permissions
RUN mkdir -p data chroma_db && chmod -R 777 data chroma_db

# Create cache directories for HuggingFace and set permissions
RUN mkdir -p /app/.cache && chmod -R 777 /app/.cache

# Create Ollama directory with proper permissions
RUN mkdir -p /app/.ollama && chmod -R 777 /app/.ollama

# Expose the port that Streamlit will run on
EXPOSE 7860

# Make the startup script executable
RUN chmod +x deployment/huggingface_space.py

# Set environment variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV HOME=/app
ENV HF_HOME=/app/.cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers
ENV OLLAMA_HOME=/app/.ollama
ENV OLLAMA_MODELS=/app/.ollama/models
ENV OLLAMA_MODEL=llama3.2:1b

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

# Start the application
CMD ["python", "deployment/huggingface_space.py"]