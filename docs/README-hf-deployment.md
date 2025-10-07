# Hugging Face Spaces Deployment Options

Since Streamlit SDK isn't available, here are your options:

## 🎯 **Option 1: Gradio App (Recommended)**

1. Create a new Space with **Gradio SDK**
2. Upload all files from this directory
3. Set the main file to `app_gradio.py`
4. The Gradio version provides the same functionality with a chat interface

### Files to upload:
- `app_gradio.py` - Main Gradio application
- `mcp_server_canonical.py` - MCP server
- `data/offices.csv` - Office data
- `requirements/requirements.txt` - Dependencies

## 🐳 **Option 2: Docker SDK**

1. Create a new Space with **Docker SDK**
2. Upload all files including `Dockerfile.hf`
3. HF Spaces will build the container automatically
4. Can run either Gradio or Streamlit version

### Configuration:
- Use `Dockerfile.hf` as your Dockerfile
- Change the CMD line to choose your app:
  - `CMD ["python", "app_gradio.py"]` (Gradio)
  - `CMD ["python", "start_huggingface_space.py"]` (Streamlit + MCP)

## 🔧 **Option 3: Manual Streamlit**

If you specifically need Streamlit:

1. Create a Space with **Gradio SDK** (as placeholder)
2. Upload all files
3. Create a custom `app.py` that launches Streamlit:

```python
import subprocess
import os

# Start Streamlit
subprocess.run([
    "streamlit", "run", "streamlit_app.py",
    "--server.port", str(os.environ.get("PORT", 7860)),
    "--server.address", "0.0.0.0"
])
```

## 📝 **Requirements for All Options**

Add to `requirements.txt`:
```
streamlit
gradio
fastmcp
pandas
requests
```

## 🎯 **Recommendation**

**Use Option 1 (Gradio)** because:
- ✅ Native HF Spaces support
- ✅ Better chat interface for Q&A
- ✅ Same functionality as Streamlit version
- ✅ Easier deployment and maintenance
- ✅ Better mobile experience

The Gradio version (`app_gradio.py`) provides:
- Chat-based interface for natural questions
- Example queries for easy testing
- System status monitoring
- Same embedded intelligence as Streamlit version
- Automatic fallback when MCP server isn't available

## 🚀 **Quick Start**

1. Create HF Space with Gradio SDK
2. Upload: `app_gradio.py`, `mcp_server_canonical.py`, `data/`, `requirements/`
3. Set main file: `app_gradio.py`
4. Deploy!

Your AI Office Assistant will be live and ready to answer questions about office data! 🎉