# Hugging Face Spaces Deployment Guide

This guide explains how to deploy the AI Office Assistant to Hugging Face Spaces with both MCP server and Streamlit app running together.

## 🚀 Quick Start

### Option 1: Use the Combined Startup Script
```bash
python start_huggingface_space.py
```

### Option 2: Use Docker (Recommended for HF Spaces)
```bash
docker build -t ai-office-assistant .
docker run -p 7860:7860 ai-office-assistant
```

## 📋 Files for Hugging Face Spaces

### Core Application Files
- `start_huggingface_space.py` - Main startup coordinator
- `mcp_server_canonical.py` - MCP server with canonical queries
- `streamlit_app.py` - Streamlit web interface
- `app.py` - Embedded fallback version (no MCP required)

### Configuration Files
- `Dockerfile` - Container configuration
- `requirements/requirements.txt` - Python dependencies
- `data/offices.csv` - Sample office data

## 🔧 How It Works

1. **Startup Process**:
   - `start_huggingface_space.py` starts the MCP server on port 8000
   - Waits for MCP server to be ready
   - Starts Streamlit app on port 7860 (HF Spaces default)
   - Monitors both processes and handles graceful shutdown

2. **Fallback Handling**:
   - If MCP server fails, the app falls back to embedded logic
   - No external dependencies required for basic functionality
   - Full feature parity between MCP and embedded modes

3. **Process Management**:
   - Health checks for both services
   - Automatic restart of failed MCP server
   - Proper cleanup on shutdown signals

## 🌐 Deployment on Hugging Face Spaces

### Method 1: Using the Space Interface

1. Create a new Space on Hugging Face
2. Choose "Streamlit" as the SDK
3. Upload all files from this directory
4. Set the main file to `start_huggingface_space.py`
5. The Space will automatically build and deploy

### Method 2: Using Git

1. Clone this repository to your local machine
2. Create a new Hugging Face Space repository
3. Push the contents to your Space repository
4. Ensure `start_huggingface_space.py` is set as the main entry point

### Required Space Configuration

In your Space settings:
- **SDK**: Streamlit
- **Python version**: 3.11
- **Hardware**: CPU Basic (sufficient for this app)

## 🔄 Fallback Modes

The application supports multiple modes:

1. **Full MCP Mode**: Both MCP server and Streamlit running
2. **Embedded Mode**: Streamlit with built-in logic (no MCP server)
3. **Hybrid Mode**: Attempts MCP, falls back to embedded

## 📊 Features

- **Natural Language Queries**: Ask questions in plain English
- **Real-time Processing**: Fast response times
- **Visual Interface**: Clean, modern Streamlit UI
- **Error Handling**: Graceful degradation with helpful messages
- **Status Monitoring**: Real-time system status indicators

## 🛠️ Development

### Local Testing
```bash
# Start just the MCP server
python mcp_server_canonical.py

# Start just the Streamlit app
streamlit run streamlit_app.py

# Start both together
python start_huggingface_space.py
```

### Environment Variables
- `PORT`: Streamlit port (default: 7860)
- `SPACE_ID`: Hugging Face Space ID (auto-set by HF)

## 📝 Example Queries

- "Which office has the highest revenue?"
- "Tell me about the Chicago office"
- "Show me employee distribution"
- "What's our most efficient office?"
- "What's the average revenue across all offices?"

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Won't Start**
   - Check if port 8000 is available
   - Verify all dependencies are installed
   - App will fall back to embedded mode

2. **Streamlit App Not Loading**
   - Ensure port 7860 is not blocked
   - Check Python version compatibility
   - Review error logs in startup script

3. **Queries Not Working**
   - Verify data files are present
   - Check system status in sidebar
   - Try example queries first

### Debug Mode
Add `--log-level debug` to the startup script for verbose logging.

## 📦 Dependencies

See `requirements/requirements.txt` for the complete list. Key dependencies:
- `streamlit` - Web interface
- `fastmcp` - MCP server framework
- `pandas` - Data processing
- `requests` - HTTP client

## 🤝 Contributing

1. Test locally using `start_huggingface_space.py`
2. Ensure both MCP and embedded modes work
3. Test on a Hugging Face Space before submitting changes
4. Update this README if adding new features