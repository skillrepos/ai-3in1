# RAG Agent with Canonical Queries - Minimized Diff Version

This is an optimized version of `rag-agent2-canonical.py` that minimizes differences from the original `rag-agent2.py` while preserving all canonical queries functionality.

## Optimizations Made

### 1. Reduced Line Count
- **Before**: 465 lines (180 line difference from original)
- **After**: 425 lines (140 line difference from original)
- **Improvement**: 40 fewer lines, 22% reduction in diff size

### 2. Structural Changes Minimized
- Kept original file structure and header comments
- Added canonical queries as compact extensions rather than rewrites
- Preserved original workflow as default behavior
- Made canonical mode an optional enhancement

### 3. Code Consolidation
- Combined LLM planner into a single compact function
- Removed redundant color coding and verbose output
- Eliminated separate weather_at_office function (uses original workflow)
- Simplified the main loop logic

### 4. Functionality Preserved
- **Original weather workflow**: Unchanged and works exactly as before
- **Canonical queries**: Full support for office data analysis
- **Auto-detection**: Automatically switches to canonical mode for data queries
- **Manual mode**: `--canonical` prefix for explicit canonical queries

## Usage

```bash
# Original weather queries (unchanged)
python3 rag-agent2-canonical.py
Prompt: paris marketing office

# Canonical data analysis (auto-detected)
Prompt: What's the average revenue?
Prompt: Which office has the most employees?

# Manual canonical mode
Prompt: --canonical compare chicago
```

## Canonical Queries Supported
- `average_revenue`
- `most_employees`  
- `opened_after_<year>`
- `highest_revenue_per_employee`
- `compare_<city>`

The agent automatically detects when to use canonical mode based on keywords in the query, maintaining backward compatibility while adding new structured analysis capabilities.