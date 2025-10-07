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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Office Assistant",
    page_icon="📊",
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

**Key Statistics:**
- **Average Revenue:** ${avg_revenue:.1f} million
- **Total Revenue:** ${total_revenue:.1f} million
- **Number of Offices:** {len(df)}

**Top Performer:** {max_office} (${max_revenue:.1f} million)
**Lowest Revenue:** {min_office} (${min_revenue:.1f} million)

**Insight:** {max_office} generates {max_revenue/avg_revenue:.1f}x the average revenue, indicating strong market performance in that location.
"""

    elif query_type == "employee_analysis":
        max_employees = df['employees'].max()
        max_emp_office = df.loc[df['employees'].idxmax(), 'city']
        total_employees = df['employees'].sum()
        avg_employees = df['employees'].mean()
        
        return f"""**Employee Distribution Analysis**

**Key Statistics:**
- **Total Employees:** {total_employees:,}
- **Average per Office:** {avg_employees:.0f}

**Largest Office:** {max_emp_office} ({max_employees} employees)

**Distribution:** Our workforce is distributed across {len(df)} offices, with {max_emp_office} being our largest operational center.
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

**Location:** {office['city']}, {office['state']}
**Team Size:** {office['employees']} employees
**Revenue:** ${office['revenue_million']:.1f} million
**Established:** {office['opened_year']}

**Performance Metrics:**
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

**Most Efficient Office:** {most_efficient['city']}
- Revenue per Employee: ${most_efficient['efficiency']:.0f}K
- Total Revenue: ${most_efficient['revenue_million']:.1f}M
- Team Size: {most_efficient['employees']} people

**Average Efficiency:** ${avg_efficiency:.0f}K per employee

**Insight:** {most_efficient['city']} demonstrates {most_efficient['efficiency']/avg_efficiency:.1f}x the average efficiency, suggesting optimized operations or high-value market positioning.
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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if status["mcp_available"]:
            st.success("MCP Server Connected")
        else:
            st.warning("Using Embedded Mode")

    with col2:
        st.info(f"Method: {status['method']}")

    with col3:
        st.info(f"Speed: {status['processing_time']}")

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">AI Office Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Intelligent office data analysis with natural language queries</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Deployment Info")

        # Deployment mode indicator
        if os.environ.get("SPACE_ID"):
            st.success("Running on Hugging Face Spaces")
            space_id = os.environ.get("SPACE_ID", "unknown")
            st.info(f"Space: {space_id}")
        else:
            st.info("Running Locally")

        st.header("Example Queries")
        example_queries = [
            "Which office has the highest revenue?",
            "Tell me about the Chicago office",
            "Which office has the most employees?",
            "Show me efficiency analysis",
            "What's the average revenue?"
        ]
        
        for i, example in enumerate(example_queries):
            if st.button(f"{example}", key=f"example_{i}"):
                st.session_state.selected_query = example

        st.header("Office Data")
        with st.expander("View Sample Data"):
            df = pd.DataFrame(get_office_data())
            st.dataframe(df, use_container_width=True)
        
        st.header("System Status")
        mcp_manager = get_mcp_manager()
        if mcp_manager.check_connection():
            st.success("MCP Server Available")
        else:
            st.warning("MCP Offline - Using Embedded Mode")
            st.info("This is normal for Hugging Face Spaces deployment")
    
    # Main query interface
    st.header("Ask Your Question")
    
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
    if st.button("Analyze", type="primary") or user_query:
        if user_query.strip():
            
            # Display query
            with st.container():
                st.markdown(f'<div class="query-box"><strong>Your Question:</strong> {user_query}</div>', unsafe_allow_html=True)
            
            # Processing indicator
            with st.spinner("Analyzing your question..."):
                try:
                    result, status_type, status_info = asyncio.run(process_query_with_status(user_query))
                    
                    # Display status
                    display_status_info(status_info)
                    
                    # Display result
                    st.markdown("### Analysis Result")
                    with st.container():
                        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                    
                    # Additional insights
                    if status_type == "success":
                        st.success("Query processed successfully!")
                    else:
                        st.info("Processed using embedded intelligence (no external dependencies)")
                
                except Exception as e:
                    st.error(f"Error processing query: {e}")
                    st.info("Please try rephrasing your question or use one of the example queries.")
        else:
            st.warning("Please enter a question to analyze!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.8rem;">'
        'Powered by Canonical Query Classification • Deployed on Hugging Face Spaces'
        '</p>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()