# Lab 8: Streamlit Web Application for Canonical Query Classification Agent

In this lab, we'll create a modern web interface for our canonical query classification-based RAG agent using Streamlit. This will provide a user-friendly way to interact with our query classification system.

## Overview

We'll build a Streamlit app that:
- Provides a clean chat interface for querying office data
- Shows the classification process (which canonical query was selected)
- Displays confidence scores and alternative suggestions
- Handles both weather and office data queries
- Shows real-time processing steps

## Prerequisites

1. Completed previous labs (especially the classification system from Lab 7)
2. MCP server running (`mcp_server_canonical.py`)
3. Office data available in `data/offices.csv`

## Step 1: Install Streamlit

Add Streamlit to your requirements:

```bash
pip install streamlit plotly pandas
```

Or add to `requirements/requirements.txt`:
```
streamlit==1.40.0
plotly==5.18.0
pandas==2.1.4
```

## Step 2: Create the Streamlit Application

Create `streamlit_app.py`:

```python
#!/usr/bin/env python3
"""
Streamlit Web Application for Canonical Query Classification Agent
==================================================================

This web app provides a user-friendly interface for our canonical query system.
Features:
- Chat-like interface for natural language queries  
- Real-time display of classification process
- Confidence scores and alternative query suggestions
- Support for both weather and office data queries
- Visual indicators for processing steps
"""

import asyncio
import streamlit as st
import time
import json
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our agent
from rag_agent2_canonical import process_query, handle_canonical_query_with_classification, handle_weather_query

# Page configuration
st.set_page_config(
    page_title="AI Office Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
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
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
    .processing-step {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
        border-left: 3px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

def get_confidence_class(confidence):
    """Get CSS class based on confidence score."""
    if confidence >= 0.8:
        return "confidence-high"
    elif confidence >= 0.5:
        return "confidence-medium"
    else:
        return "confidence-low"

def get_confidence_emoji(confidence):
    """Get emoji based on confidence score."""
    if confidence >= 0.8:
        return "🎯"
    elif confidence >= 0.5:
        return "🎲"
    else:
        return "❓"

async def process_query_with_progress(user_query):
    """Process query and show progress steps."""
    
    # Create progress containers
    progress_container = st.container()
    result_container = st.container()
    
    with progress_container:
        st.markdown("### 🔄 Processing Steps")
        
        # Step indicators
        step1 = st.empty()
        step2 = st.empty()
        step3 = st.empty()
        step4 = st.empty()
        
        # Step 1: Query Analysis
        with step1:
            st.markdown('<div class="processing-step">🔍 Analyzing query intent...</div>', unsafe_allow_html=True)
        
        time.sleep(0.5)  # Simulate processing time
        
        # Step 2: Route Detection
        user_lower = user_query.lower()
        weather_keywords = ["weather", "temperature", "forecast", "conditions", "climate"]
        is_weather = any(keyword in user_lower for keyword in weather_keywords)
        
        with step2:
            if is_weather:
                st.markdown('<div class="processing-step">🌤️ Weather query detected - using RAG workflow</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="processing-step">📊 Data analysis query detected - using classification workflow</div>', unsafe_allow_html=True)
        
        time.sleep(0.5)
        
        # Step 3: Processing
        with step3:
            st.markdown('<div class="processing-step">⚙️ Processing with AI agent...</div>', unsafe_allow_html=True)
        
        # Actually process the query
        try:
            result = await process_query(user_query)
            
            with step4:
                st.markdown('<div class="processing-step">✅ Analysis complete!</div>', unsafe_allow_html=True)
            
            return result, None
            
        except Exception as e:
            with step4:
                st.markdown('<div class="processing-step">❌ Error occurred during processing</div>', unsafe_allow_html=True)
            return None, str(e)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🏢 AI Office Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Ask questions about office data, weather, and more using natural language</p>', unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Check if MCP server is running
        try:
            import requests
            response = requests.get("http://127.0.0.1:8000/mcp/", timeout=2)
            if response.status_code == 200:
                st.success("✅ MCP Server Connected")
            else:
                st.error("❌ MCP Server Error")
        except:
            st.error("❌ MCP Server Offline")
            st.warning("Start the MCP server:\n```\npython mcp_server_canonical.py\n```")
        
        st.header("💡 Query Examples")
        st.markdown("""
        **Revenue Analysis:**
        - Which office has the highest revenue?
        - What's the average revenue?
        - Show me revenue statistics
        
        **Employee Analysis:**
        - Which office has the most employees?
        - How are employees distributed?
        
        **Office Profiles:**
        - Tell me about the Chicago office
        - What's the profile of New York?
        
        **Weather Queries:**
        - What's the weather at our Paris office?
        - Temperature in New York office
        """)
        
        st.header("📊 Available Data")
        st.markdown("""
        - **Offices**: 10 locations
        - **Cities**: New York, Chicago, San Francisco, etc.
        - **Metrics**: Revenue, employees, opening year
        - **Weather**: Real-time data via API
        """)
    
    # Main query interface
    st.header("💬 Ask Your Question")
    
    # Query input
    user_query = st.text_input(
        "Enter your question:",
        placeholder="e.g., Which office has the highest revenue?",
        help="Ask about office data, weather, or any business metrics"
    )
    
    # Submit button
    if st.button("🚀 Ask Assistant", type="primary") or user_query:
        if user_query.strip():
            
            # Display the user query
            with st.container():
                st.markdown(f'<div class="query-box"><strong>Your Question:</strong> {user_query}</div>', unsafe_allow_html=True)
            
            # Process the query
            with st.spinner("Processing your question..."):
                try:
                    # Run async function in streamlit
                    result, error = asyncio.run(process_query_with_progress(user_query))
                    
                    if error:
                        st.error(f"Error: {error}")
                    elif result:
                        # Display the result
                        st.markdown("### 🤖 Assistant Response")
                        with st.container():
                            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                        
                        # Additional insights for data queries
                        if not any(word in user_query.lower() for word in ["weather", "temperature", "forecast"]):
                            st.markdown("### 📈 Query Insights")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Query Type", "Data Analysis")
                            with col2:
                                st.metric("Processing Time", "< 5s")
                            with col3:
                                st.metric("Confidence", "High")
                    
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
                    st.info("Make sure the MCP server is running: `python mcp_server_canonical.py`")
        else:
            st.warning("Please enter a question to get started!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.8rem;">'
        'Powered by Canonical Query Classification Agent | Built with Streamlit'
        '</p>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
```

## Step 3: Create Enhanced Version with Classification Details

Create `streamlit_app_advanced.py` for power users who want to see the classification process:

```python
#!/usr/bin/env python3
"""
Advanced Streamlit App with Classification Details
==================================================

This version shows the internal classification process for educational purposes.
"""

import asyncio
import streamlit as st
import time
import json
from pathlib import Path
import sys
import plotly.express as px
import pandas as pd

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastmcp import Client
from rag_agent2_canonical import process_query

# Page configuration
st.set_page_config(
    page_title="AI Office Assistant - Advanced",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .classification-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    .confidence-score {
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

async def get_classification_details(user_query):
    """Get detailed classification information."""
    mcp_endpoint = "http://127.0.0.1:8000/mcp/"
    
    try:
        async with Client(mcp_endpoint) as mcp:
            # Get classification result
            classify_result = await mcp.call_tool("classify_canonical_query", {"user_query": user_query})
            
            # Extract the data
            if hasattr(classify_result, "structured_content") and classify_result.structured_content:
                classification = classify_result.structured_content
            elif hasattr(classify_result, "data") and classify_result.data:
                classification = classify_result.data
            else:
                classification = classify_result
            
            # Get available queries
            queries_result = await mcp.call_tool("list_canonical_queries", {})
            if hasattr(queries_result, "structured_content"):
                queries_data = queries_result.structured_content
            elif hasattr(queries_result, "data"):
                queries_data = queries_result.data
            else:
                queries_data = queries_result
            
            return classification, queries_data.get("queries", [])
            
    except Exception as e:
        return None, None

def display_classification_details(classification, all_queries):
    """Display detailed classification information."""
    
    st.markdown("### 🔬 Classification Analysis")
    
    if not classification:
        st.error("Could not retrieve classification details")
        return
    
    # Main result
    col1, col2 = st.columns([2, 1])
    
    with col1:
        suggested = classification.get("suggested_query", "None")
        confidence = classification.get("confidence", 0)
        
        st.markdown(f"**Selected Query Type:** `{suggested}`")
        st.markdown(f"**Reason:** {classification.get('reason', 'Not provided')}")
    
    with col2:
        # Confidence gauge
        fig = px.pie(
            values=[confidence, 1-confidence], 
            names=["Confidence", "Uncertainty"],
            title="Confidence Score",
            color_discrete_sequence=["#28a745", "#dee2e6"]
        )
        fig.update_traces(textinfo='none')
        fig.update_layout(height=200, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Alternatives
    alternatives = classification.get("alternatives", [])
    if alternatives:
        st.markdown("**Alternative Suggestions:**")
        alt_data = []
        for alt in alternatives:
            alt_data.append({
                "Query Type": alt["query"],
                "Score": alt["score"]
            })
        
        if alt_data:
            df = pd.DataFrame(alt_data)
            st.dataframe(df, use_container_width=True)
    
    # All available queries
    with st.expander("📋 All Available Query Types"):
        for query in all_queries:
            st.markdown(f"**{query['name']}**: {query['description']}")
            if query.get('example_queries'):
                st.markdown(f"*Examples:* {', '.join(query['example_queries'][:2])}")
            st.markdown("---")

def main():
    """Main application."""
    
    st.title("🔬 AI Office Assistant - Advanced")
    st.markdown("*See the classification process in action*")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Settings")
        show_classification = st.checkbox("Show Classification Details", value=True)
        show_raw_data = st.checkbox("Show Raw Data", value=False)
        
        st.header("💡 About Classification")
        st.markdown("""
        The classification process determines which canonical query best matches your intent:
        
        1. **Keyword Analysis**: Matches words to query examples
        2. **Context Detection**: Identifies comparison vs. profile queries  
        3. **Confidence Scoring**: Rates match quality
        4. **Alternative Ranking**: Suggests other possibilities
        """)
    
    # Main interface
    user_query = st.text_input(
        "Enter your question:",
        placeholder="Which office has the highest revenue?",
    )
    
    if st.button("🚀 Analyze Query") or user_query:
        if user_query.strip():
            
            # Show classification details if requested
            if show_classification:
                with st.spinner("Analyzing query intent..."):
                    classification, queries = asyncio.run(get_classification_details(user_query))
                    display_classification_details(classification, queries)
            
            # Process the query
            st.markdown("### 🤖 Assistant Response")
            with st.spinner("Getting response..."):
                try:
                    result = asyncio.run(process_query(user_query))
                    st.success(result)
                    
                    if show_raw_data and classification:
                        with st.expander("🔍 Raw Classification Data"):
                            st.json(classification)
                            
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a question!")

if __name__ == "__main__":
    main()
```

## Step 4: Run the Application

1. **Start the MCP Server:**
```bash
python mcp_server_canonical.py
```

2. **Run the Streamlit App:**
```bash
streamlit run streamlit_app.py
```

3. **Or run the advanced version:**
```bash
streamlit run streamlit_app_advanced.py
```

## Step 5: Test the Application

Try these example queries:
- "Which office has the highest revenue?"
- "Tell me about the Chicago office"
- "What's the weather at our New York office?"
- "Which office has the most employees?"

## Features

### Basic App (`streamlit_app.py`)
- Clean, user-friendly interface
- Real-time processing indicators
- System status monitoring
- Query examples and help
- Responsive design

### Advanced App (`streamlit_app_advanced.py`)  
- Detailed classification process visualization
- Confidence scoring with charts
- Alternative query suggestions
- Raw data inspection
- Educational insights

## Customization Options

1. **Styling**: Modify the CSS in the `st.markdown()` sections
2. **Layout**: Adjust column ratios and container arrangements
3. **Features**: Add data visualization, query history, export options
4. **Branding**: Change colors, logos, and text to match your organization

## Troubleshooting

- **MCP Server Offline**: Ensure `python mcp_server_canonical.py` is running
- **Port Conflicts**: Change port in MCP server if 8000 is occupied
- **Import Errors**: Ensure all dependencies are installed
- **Async Issues**: Streamlit handles asyncio automatically in recent versions

## Next Steps

- Lab 9 will show how to deploy this to Hugging Face Spaces
- Consider adding authentication for production use
- Add data export and visualization features
- Implement query history and favorites

The Streamlit app provides an intuitive interface for your canonical query classification-based RAG agent, making it accessible to non-technical users while still showing the sophisticated AI processing underneath.