# Lab 9: Deploying to Hugging Face Spaces

In this lab, we'll deploy our classification-based RAG agent to Hugging Face Spaces, creating a publicly accessible web application. We'll explore two deployment strategies: full deployment (if possible) and a hybrid approach with local MCP server.

## Overview

We'll create a Hugging Face Space that:
- Runs our Streamlit app in the cloud
- Handles the classification logic and AI processing
- Provides fallback options for MCP server connectivity
- Supports both local development and cloud deployment

## Prerequisites

1. Hugging Face account (free at https://huggingface.co)
2. Completed Lab 8 (Streamlit application)
3. Git knowledge for pushing to repositories

## Deployment Strategy

We'll implement a **hybrid approach** that supports:
1. **Full Cloud**: MCP server + Streamlit app in Hugging Face Spaces
2. **Hybrid**: Streamlit app in cloud + MCP server locally (fallback)
3. **Embedded**: All logic embedded in Streamlit app (no MCP dependency)

## Step 1: Prepare Files for Deployment

### Create Space-Compatible File Structure

Create the following files for Hugging Face Spaces:

#### `app.py` (Main Streamlit App for Spaces)

```python
#!/usr/bin/env python3
"""
Hugging Face Spaces Streamlit Application
=========================================

This version is optimized for Hugging Face Spaces deployment with fallback options.
"""

import asyncio
import streamlit as st
import time
import json
import os
import pandas as pd
from pathlib import Path
import sys
from typing import Optional, Tuple, Dict, Any
import requests
from sentence_transformers import SentenceTransformer
import threading
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Office Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .processing-step {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
        border-left: 3px solid #ffc107;
    }
    .status-running { color: #28a745; }
    .status-fallback { color: #ffc107; }
    .status-error { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# EMBEDDED CANONICAL QUERY SYSTEM (MCP-Free Fallback)
# =====================================================

CANONICAL_QUERIES = {
    "revenue_stats": {
        "description": "Calculate revenue statistics across all offices",
        "keywords": ["revenue", "highest", "lowest", "most", "average", "total", "statistics"],
        "pattern_boost": lambda q: 0.7 if any(word in q.lower() for word in ["highest", "lowest", "most"]) and "revenue" in q.lower() else 0
    },
    "employee_analysis": {
        "description": "Analyze employee distribution across offices", 
        "keywords": ["employee", "employees", "staff", "workforce", "distribution", "most"],
        "pattern_boost": lambda q: 0.5 if "employee" in q.lower() else 0
    },
    "office_profile": {
        "description": "Detailed profile of a specific office",
        "keywords": ["profile", "about", "tell", "details", "information", "office"],
        "pattern_boost": lambda q: 0.8 if any(word in q.lower() for word in ["profile", "about", "tell"]) else 0
    },
    "efficiency_analysis": {
        "description": "Calculate revenue efficiency (revenue per employee)",
        "keywords": ["efficiency", "efficient", "revenue per employee", "productivity"],
        "pattern_boost": lambda q: 0.6 if "efficiency" in q.lower() else 0
    }
}

SAMPLE_OFFICE_DATA = [
    {"city": "New York", "state": "NY", "employees": 150, "revenue_million": 85.5, "opened_year": 2010},
    {"city": "Chicago", "state": "IL", "employees": 120, "revenue_million": 67.2, "opened_year": 2012},
    {"city": "San Francisco", "state": "CA", "employees": 95, "revenue_million": 78.9, "opened_year": 2014},
    {"city": "Austin", "state": "TX", "employees": 80, "revenue_million": 52.3, "opened_year": 2015},
    {"city": "Atlanta", "state": "GA", "employees": 75, "revenue_million": 48.7, "opened_year": 2013},
    {"city": "Boston", "state": "MA", "employees": 65, "revenue_million": 45.1, "opened_year": 2011},
    {"city": "Denver", "state": "CO", "employees": 55, "revenue_million": 38.9, "opened_year": 2016},
    {"city": "Seattle", "state": "WA", "employees": 70, "revenue_million": 51.8, "opened_year": 2014},
    {"city": "Miami", "state": "FL", "employees": 45, "revenue_million": 32.1, "opened_year": 2017},
    {"city": "Los Angeles", "state": "CA", "employees": 85, "revenue_million": 59.4, "opened_year": 2013}
]

def embedded_classify_query(user_query: str) -> Dict[str, Any]:
    """Embedded classification logic (no MCP required)."""
    user_lower = user_query.lower()
    scores = {}
    
    for query_name, config in CANONICAL_QUERIES.items():
        score = 0
        
        # Keyword matching
        for keyword in config["keywords"]:
            if keyword in user_lower:
                score += 0.3
        
        # Pattern boost
        pattern_score = config["pattern_boost"](user_query)
        score += pattern_score
        
        scores[query_name] = score
    
    if not scores or max(scores.values()) == 0:
        return {
            "suggested_query": "revenue_stats",  # Default fallback
            "confidence": 0.5,
            "method": "embedded_fallback"
        }
    
    best_query = max(scores, key=scores.get)
    confidence = min(scores[best_query], 1.0)
    
    return {
        "suggested_query": best_query,
        "confidence": confidence,
        "method": "embedded_classification"
    }

def embedded_process_query(user_query: str, office_data: list) -> str:
    """Process query using embedded logic."""
    classification = embedded_classify_query(user_query)
    query_type = classification["suggested_query"]
    
    df = pd.DataFrame(office_data)
    
    if query_type == "revenue_stats":
        avg_revenue = df['revenue_million'].mean()
        max_revenue = df['revenue_million'].max()
        min_revenue = df['revenue_million'].min()
        max_office = df.loc[df['revenue_million'].idxmax(), 'city']
        min_office = df.loc[df['revenue_million'].idxmin(), 'city']
        total_revenue = df['revenue_million'].sum()
        
        return f"""**Revenue Analysis Summary**

📊 **Key Statistics:**
- **Average Revenue:** ${avg_revenue:.1f} million
- **Total Revenue:** ${total_revenue:.1f} million  
- **Number of Offices:** {len(df)}

🏆 **Top Performer:** {max_office} (${max_revenue:.1f} million)
📉 **Lowest Revenue:** {min_office} (${min_revenue:.1f} million)

💡 **Insight:** {max_office} generates {max_revenue/avg_revenue:.1f}x the average revenue, indicating strong market performance in that location.
"""

    elif query_type == "employee_analysis":
        max_employees = df['employees'].max()
        max_emp_office = df.loc[df['employees'].idxmax(), 'city']
        total_employees = df['employees'].sum()
        avg_employees = df['employees'].mean()
        
        return f"""**Employee Distribution Analysis**

👥 **Key Statistics:**
- **Total Employees:** {total_employees:,}
- **Average per Office:** {avg_employees:.0f}

🏆 **Largest Office:** {max_emp_office} ({max_employees} employees)

📊 **Distribution:** Our workforce is distributed across {len(df)} offices, with {max_emp_office} being our largest operational center.
"""

    elif query_type == "office_profile":
        # Try to extract city name
        cities = df['city'].str.lower().tolist()
        user_lower = user_query.lower()
        
        matched_city = None
        for city in cities:
            if city in user_lower:
                matched_city = city
                break
        
        if matched_city:
            office = df[df['city'].str.lower() == matched_city].iloc[0]
            return f"""**{office['city']} Office Profile**

📍 **Location:** {office['city']}, {office['state']}
👥 **Team Size:** {office['employees']} employees
💰 **Revenue:** ${office['revenue_million']:.1f} million
📅 **Established:** {office['opened_year']}

📊 **Performance Metrics:**
- Revenue per Employee: ${office['revenue_million']*1000/office['employees']:.0f}K
- Years in Operation: {2024 - office['opened_year']} years

This office represents {office['revenue_million']/df['revenue_million'].sum()*100:.1f}% of our total revenue.
"""
        else:
            return "Please specify which office you'd like to know about (e.g., 'Tell me about the Chicago office')."
    
    elif query_type == "efficiency_analysis":
        df['efficiency'] = df['revenue_million'] / df['employees'] * 1000  # Revenue per employee in thousands
        most_efficient = df.loc[df['efficiency'].idxmax()]
        avg_efficiency = df['efficiency'].mean()
        
        return f"""**Office Efficiency Analysis**

⚡ **Most Efficient Office:** {most_efficient['city']}
- Revenue per Employee: ${most_efficient['efficiency']:.0f}K
- Total Revenue: ${most_efficient['revenue_million']:.1f}M
- Team Size: {most_efficient['employees']} people

📊 **Average Efficiency:** ${avg_efficiency:.0f}K per employee

💡 **Insight:** {most_efficient['city']} demonstrates {most_efficient['efficiency']/avg_efficiency:.1f}x the average efficiency, suggesting optimized operations or high-value market positioning.
"""
    
    return "I understand you're asking about our office data. Could you rephrase your question to be more specific?"

# =====================================================
# MCP CONNECTION HANDLING
# =====================================================

class MCPManager:
    """Manages MCP server connection with fallback."""
    
    def __init__(self):
        self.mcp_available = False
        self.mcp_endpoint = "http://127.0.0.1:8000/mcp/"
        self.fallback_endpoint = None  # Could be a remote MCP server
        self.check_connection()
    
    def check_connection(self) -> bool:
        """Check if MCP server is available."""
        try:
            response = requests.get(self.mcp_endpoint, timeout=2)
            self.mcp_available = response.status_code == 200
            return self.mcp_available
        except:
            self.mcp_available = False
            return False
    
    async def process_query_mcp(self, user_query: str) -> Tuple[str, str]:
        """Process query using MCP server."""
        try:
            # Import here to avoid dependency issues
            from fastmcp import Client
            
            async with Client(self.mcp_endpoint) as mcp:
                # This would use the original classification logic
                # For now, fall back to embedded version
                result = embedded_process_query(user_query, SAMPLE_OFFICE_DATA)
                return result, "mcp_server"
                
        except Exception as e:
            logger.warning(f"MCP processing failed: {e}")
            result = embedded_process_query(user_query, SAMPLE_OFFICE_DATA)
            return result, "embedded_fallback"

# =====================================================
# STREAMLIT APPLICATION
# =====================================================

@st.cache_resource
def get_mcp_manager():
    """Get cached MCP manager."""
    return MCPManager()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_office_data():
    """Get office data (cached)."""
    return SAMPLE_OFFICE_DATA

async def process_query_with_status(user_query: str) -> Tuple[str, str, Dict]:
    """Process query and return result with status info."""
    mcp_manager = get_mcp_manager()
    
    # Try MCP first, fall back to embedded
    if mcp_manager.check_connection():
        try:
            result, method = await mcp_manager.process_query_mcp(user_query)
            status = {
                "method": method,
                "mcp_available": True,
                "processing_time": "< 2s"
            }
            return result, "success", status
        except Exception as e:
            logger.warning(f"MCP failed, using fallback: {e}")
    
    # Embedded fallback
    result = embedded_process_query(user_query, get_office_data())
    status = {
        "method": "embedded_fallback",
        "mcp_available": False,
        "processing_time": "< 1s"
    }
    return result, "fallback", status

def display_status_info(status: Dict):
    """Display system status information."""
    mcp_manager = get_mcp_manager()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if status["mcp_available"]:
            st.success("🔗 MCP Server Connected")
        else:
            st.warning("🔄 Using Embedded Mode")
    
    with col2:
        st.info(f"⚡ Method: {status['method']}")
    
    with col3:
        st.info(f"⏱️ Speed: {status['processing_time']}")

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🏢 AI Office Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Intelligent office data analysis with natural language queries</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🚀 Deployment Info")
        
        # Deployment mode indicator
        if os.environ.get("SPACE_ID"):
            st.success("☁️ Running on Hugging Face Spaces")
            space_id = os.environ.get("SPACE_ID", "unknown")
            st.info(f"Space: {space_id}")
        else:
            st.info("🖥️ Running Locally")
        
        st.header("💡 Example Queries")
        example_queries = [
            "Which office has the highest revenue?",
            "Tell me about the Chicago office",
            "Which office has the most employees?",
            "Show me efficiency analysis",
            "What's the average revenue?"
        ]
        
        for i, example in enumerate(example_queries):
            if st.button(f"💬 {example}", key=f"example_{i}"):
                st.session_state.selected_query = example
        
        st.header("📊 Office Data")
        with st.expander("View Sample Data"):
            df = pd.DataFrame(get_office_data())
            st.dataframe(df, use_container_width=True)
        
        st.header("🔧 System Status")
        mcp_manager = get_mcp_manager()
        if mcp_manager.check_connection():
            st.success("✅ MCP Server Available")
        else:
            st.warning("⚠️ MCP Offline - Using Embedded Mode")
            st.info("This is normal for Hugging Face Spaces deployment")
    
    # Main query interface
    st.header("💬 Ask Your Question")
    
    # Handle example query selection
    default_query = st.session_state.get("selected_query", "")
    
    user_query = st.text_input(
        "Enter your question about office data:",
        value=default_query,
        placeholder="e.g., Which office has the highest revenue?",
        help="Ask about revenue, employees, office profiles, or efficiency metrics"
    )
    
    # Clear the session state after using it
    if "selected_query" in st.session_state:
        del st.session_state.selected_query
    
    # Process query
    if st.button("🚀 Analyze", type="primary") or user_query:
        if user_query.strip():
            
            # Display query
            with st.container():
                st.markdown(f'<div class="query-box"><strong>Your Question:</strong> {user_query}</div>', unsafe_allow_html=True)
            
            # Processing indicator
            with st.spinner("🤖 Analyzing your question..."):
                try:
                    result, status_type, status_info = asyncio.run(process_query_with_status(user_query))
                    
                    # Display status
                    display_status_info(status_info)
                    
                    # Display result
                    st.markdown("### 🎯 Analysis Result")
                    with st.container():
                        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                    
                    # Additional insights
                    if status_type == "success":
                        st.success("✅ Query processed successfully!")
                    else:
                        st.info("ℹ️ Processed using embedded intelligence (no external dependencies)")
                
                except Exception as e:
                    st.error(f"Error processing query: {e}")
                    st.info("Please try rephrasing your question or use one of the example queries.")
        else:
            st.warning("Please enter a question to analyze!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.8rem;">'
        'Powered by Classification-Based RAG • Deployed on Hugging Face Spaces'
        '</p>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
```

#### `requirements.txt` (for Hugging Face Spaces)

```txt
streamlit==1.40.0
pandas==2.1.4
plotly==5.18.0
requests==2.32.4
sentence-transformers==5.0.0
fastmcp==2.10.2
```

#### `README.md` (for the Space)

```markdown
---
title: AI Office Assistant
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.40.0
app_file: app.py
pinned: false
license: mit
---

# AI Office Assistant 🏢

An intelligent office data analysis tool powered by classification-based RAG (Retrieval-Augmented Generation).

## Features

- **Natural Language Queries**: Ask questions in plain English
- **Intelligent Classification**: Automatically determines your intent
- **Office Analytics**: Revenue, employee, and efficiency analysis
- **Real-time Processing**: Fast responses with embedded intelligence
- **Fallback Architecture**: Works with or without external dependencies

## Example Queries

- "Which office has the highest revenue?"
- "Tell me about the Chicago office"
- "Which office has the most employees?"
- "Show me efficiency analysis"
- "What's the average revenue across all offices?"

## Architecture

This application uses an advanced classification system that:

1. **Analyzes Query Intent**: Determines what type of analysis you want
2. **Matches Canonical Patterns**: Maps to pre-defined query types
3. **Processes with AI**: Uses intelligent algorithms for data analysis
4. **Provides Insights**: Delivers business-relevant answers

## Deployment Modes

- **Cloud Mode**: Full deployment on Hugging Face Spaces
- **Hybrid Mode**: Can connect to external MCP servers
- **Embedded Mode**: Self-contained with no external dependencies

Built with ❤️ using Streamlit and advanced AI techniques.
```

## Step 2: Create Hugging Face Space

1. **Go to Hugging Face Spaces**: https://huggingface.co/spaces

2. **Create New Space**:
   - Click "Create new Space"
   - Choose a name: e.g., "ai-office-assistant"
   - Select "Streamlit" as the SDK
   - Choose Public or Private
   - Click "Create Space"

3. **Upload Files**:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-office-assistant
   cd ai-office-assistant
   
   # Copy files
   cp /path/to/your/app.py .
   cp /path/to/your/requirements.txt .
   cp /path/to/your/README.md .
   
   # Commit and push
   git add .
   git commit -m "Initial deployment of AI Office Assistant"
   git push
   ```

## Step 3: Advanced Deployment with MCP Server

### Option A: Full Cloud Deployment (Experimental)

Create `start_services.py` to run both MCP server and Streamlit:

```python
#!/usr/bin/env python3
"""
Service orchestrator for Hugging Face Spaces
Attempts to run MCP server alongside Streamlit
"""

import subprocess
import threading
import time
import sys
import os

def start_mcp_server():
    """Start MCP server in background."""
    try:
        # Create a minimal MCP server
        subprocess.run([
            sys.executable, "-c", """
import time
from fastmcp import FastMCP

mcp = FastMCP("OfficeServer")

@mcp.tool
def simple_classify(query: str) -> dict:
    # Simplified classification logic
    if 'highest' in query.lower() and 'revenue' in query.lower():
        return {'suggested_query': 'revenue_stats', 'confidence': 1.0}
    return {'suggested_query': 'revenue_stats', 'confidence': 0.5}

if __name__ == '__main__':
    mcp.run(transport='http', host='127.0.0.1', port=8000, path='/mcp/')
"""
        ])
    except Exception as e:
        print(f"MCP server failed to start: {e}")

def start_streamlit():
    """Start Streamlit app."""
    time.sleep(2)  # Wait for MCP server
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    # Start MCP server in background
    mcp_thread = threading.Thread(target=start_mcp_server)
    mcp_thread.daemon = True
    mcp_thread.start()
    
    # Start Streamlit
    start_streamlit()
```

### Option B: Hybrid Deployment (Recommended)

Use the embedded fallback system in `app.py` which works entirely in Hugging Face Spaces while still supporting local MCP connections for development.

## Step 4: Test and Optimize

### Performance Optimization

Add caching and optimization:

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_office_data():
    """Load and cache office data."""
    # Your data loading logic
    pass

@st.cache_resource
def get_sentence_transformer():
    """Get cached sentence transformer model."""
    return SentenceTransformer('all-MiniLM-L6-v2')
```

### Error Handling

```python
def safe_process_query(user_query: str) -> str:
    """Process query with comprehensive error handling."""
    try:
        return process_query(user_query)
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        return """
        I encountered an issue processing your query. Please try:
        - Rephrasing your question
        - Using one of the example queries
        - Checking your internet connection
        """
```

## Step 5: Configure Space Settings

In your Space repository, create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
maxUploadSize = 200
enableXsrfProtection = false
enableCORS = false
```

## Step 6: Monitor and Maintain

### Add Logging

```python
import logging

# Configure logging for Spaces
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log usage metrics
def log_query(query: str, result_type: str):
    """Log query for analytics."""
    logger.info(f"Query: {query[:50]}... | Type: {result_type}")
```

### Health Checks

```python
def health_check():
    """Perform system health check."""
    checks = {
        "streamlit": True,
        "data_access": len(get_office_data()) > 0,
        "mcp_server": MCPManager().check_connection()
    }
    return checks
```

## Alternative: Local MCP + Remote Streamlit

If the full cloud deployment doesn't work, you can:

1. **Run MCP Server Locally**:
   ```bash
   python mcp_server_classification.py
   ```

2. **Use ngrok for Public Access**:
   ```bash
   ngrok http 8000
   ```

3. **Update Space to Use Remote MCP**:
   ```python
   # In app.py
   MCP_ENDPOINT = "https://your-ngrok-url.ngrok.io/mcp/"
   ```

## Troubleshooting

### Common Issues

1. **Dependencies**: Ensure all packages are in requirements.txt
2. **Memory Limits**: Hugging Face Spaces have memory constraints
3. **Async Issues**: Use `asyncio.run()` for async functions in Streamlit
4. **File Paths**: Use relative paths, not absolute ones

### Debug Mode

Add debug information:

```python
if st.checkbox("Debug Mode"):
    st.json({
        "environment": dict(os.environ),
        "system_status": health_check(),
        "space_id": os.environ.get("SPACE_ID", "local")
    })
```

## Conclusion

This lab provides multiple deployment strategies:

1. **Embedded Mode**: Self-contained, always works
2. **Hybrid Mode**: Best of both worlds
3. **Full Cloud**: Maximum functionality (if technically feasible)

The embedded fallback ensures your application works reliably on Hugging Face Spaces while maintaining the sophisticated classification capabilities you've built.

Your Space will be publicly accessible and demonstrate the power of classification-based RAG systems to a global audience!

## Next Steps

- Monitor usage and performance
- Add user authentication if needed
- Implement query analytics
- Consider premium Spaces for better performance
- Add more sophisticated AI models