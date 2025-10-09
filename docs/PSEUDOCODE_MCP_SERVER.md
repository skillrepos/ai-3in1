# Pseudo-Code: MCP Server - Complete Tool Suite

## MCP Server Logic Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT REQUEST                         │
│          "I need weather for coordinates 47.6, -122.3"      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   MCP SERVER         │
              │   (Port 8000)        │
              │                      │
              │   8 Tools Available: │
              └──────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  [WEATHER TOOLS]  [DATA TOOLS]   [QUERY TOOLS]
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│get_weather() │ │get_office_   │ │list_canonical│
│convert_c_to_f│ │  dataset()   │ │  _queries()  │
└──────┬───────┘ │get_filtered_ │ │classify_     │
       │         │  office_data │ │ canonical_   │
       ▼         └──────┬───────┘ │  query()     │
[Call External]         │         │get_query_    │
[Weather API]           ▼         │ template()   │
       │         [Return CSV]     │validate_     │
       │         [Office Data]    │ query_params │
       │                │         └──────┬───────┘
       │                │                │
       └────────────────┴────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   JSON RESPONSE      │
              │   Back to Agent      │
              └──────────────────────┘
```

### Tool Categories

```
WEATHER TOOLS (2)
├── get_weather(lat, lon)
│   └─► Calls Open-Meteo API
│       └─► Returns: temp, conditions, code
└── convert_c_to_f(celsius)
    └─► Simple conversion
        └─► Returns: fahrenheit

BUSINESS INTELLIGENCE TOOLS (6)
├── list_canonical_queries()
│   └─► Returns catalog of available queries
├── classify_canonical_query(user_query)
│   └─► Smart routing: matches user query to canonical query
│       └─► Uses keyword scoring
├── get_query_template(query_name)
│   └─► Returns LLM prompt template for query
├── get_office_dataset()
│   └─► Returns complete CSV as JSON
├── get_filtered_office_data(filters)
│   └─► Returns filtered/selected data
└── validate_query_parameters(query, params)
    └─► Validates inputs before execution
```

## What is MCP?

**MCP (Model Context Protocol)** is a standard way for AI agents to call external tools and APIs.

Think of it like this:
- **Without MCP**: AI can only generate text
- **With MCP**: AI can call tools (get weather, search databases, analyze data, etc.)

## MCP Server Overview

```
The MCP Server provides TWO categories of tools:

CATEGORY 1: WEATHER TOOLS
1. get_weather(lat, lon) → Gets current weather
2. convert_c_to_f(celsius) → Converts temperature

CATEGORY 2: CANONICAL QUERY TOOLS (Business Intelligence)
3. list_canonical_queries() → Shows available data queries
4. classify_canonical_query(user_query) → Classifies best query for user's question
5. get_query_template(query_name) → Gets LLM prompt template
6. get_office_dataset() → Returns complete office data
7. get_filtered_office_data(filters) → Returns filtered data
8. validate_query_parameters(query, params) → Validates inputs
```

## Server Initialization

```
INITIALIZE FastMCP server("CanonicalQueryServer")

// Load canonical query definitions
SET CANONICAL_QUERIES = {
    "revenue_stats": {
        "description": "Calculate revenue statistics across all offices",
        "parameters": [],
        "example_queries": [
            "What's the average revenue?",
            "Which office has highest revenue?",
            "Show me revenue statistics"
        ]
    },
    "employee_analysis": {
        "description": "Analyze employee distribution",
        "parameters": [],
        "example_queries": [
            "Which office has most employees?",
            "How many employees total?"
        ]
    },
    "office_growth": {
        "description": "Analyze office growth over time",
        "parameters": ["year_threshold"],
        "example_queries": [
            "Which offices opened after 2015?",
            "Show recent office growth"
        ]
    },
    "efficiency_analysis": {
        "description": "Calculate revenue per employee",
        "parameters": [],
        "example_queries": [
            "Which office is most efficient?",
            "Revenue per employee comparison"
        ]
    }
}

LOAD office_data FROM "data/offices.csv"
```

---

## CATEGORY 1: Weather Tools

### Tool 1: Get Weather Data

```
DEFINE TOOL get_weather(latitude, longitude)
    /*
    Fetches real-time weather from Open-Meteo API.
    Uses retry logic for reliability.
    */

    SET url = "https://api.open-meteo.com/v1/forecast"
    SET params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": true
    }

    PRINT "[MCP get_weather] Called with lat=", latitude, "lon=", longitude

    // Retry logic for reliability
    FOR attempt FROM 1 TO 3 DO
        TRY
            SET response = HTTP_GET(url, params, timeout=15)
            PRINT "[MCP get_weather] Response status:", response.status

            IF response.status IN [429, 500, 502, 503, 504] THEN
                THROW transient_error
            END IF

            SET weather_data = parse_json(response.body)
            SET current = weather_data["current_weather"]

            SET result = {
                "temperature": current["temperature"],
                "code": current["weathercode"],
                "conditions": weather_code_to_text(current["weathercode"])
            }

            PRINT "[MCP get_weather] Returning:", result
            RETURN result

        CATCH (network_error, json_error, key_error)
            PRINT "[MCP get_weather] Error on attempt", attempt, ":", error

            IF attempt == 3 THEN
                PRINT "[MCP get_weather] FAILED after 3 attempts"
                THROW error
            END IF

            SET wait_time = 1.5 ^ (attempt - 1)  // Exponential backoff
            PRINT "[MCP get_weather] Retrying after", wait_time, "seconds..."
            SLEEP(wait_time)
        END TRY
    END FOR
END TOOL


FUNCTION weather_code_to_text(code)
    /*
    Maps WMO weather codes to human descriptions
    */
    SET codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
        3: "Overcast", 45: "Fog", 61: "Slight rain",
        63: "Moderate rain", 95: "Thunderstorm"
    }

    IF code IN codes THEN
        RETURN codes[code]
    ELSE
        RETURN "Unknown"
    END IF
END FUNCTION
```

### Tool 2: Temperature Conversion

```
DEFINE TOOL convert_c_to_f(celsius)
    /*
    Simple utility for temperature conversion
    */
    PRINT "[MCP convert_c_to_f] Called with c=", celsius

    SET fahrenheit = (celsius * 9/5) + 32

    PRINT "[MCP convert_c_to_f] Returning:", fahrenheit
    RETURN fahrenheit
END TOOL
```

---

## CATEGORY 2: Business Intelligence Tools

### Tool 3: List Available Queries

```
DEFINE TOOL list_canonical_queries()
    /*
    Returns catalog of all available data analysis queries.
    Helps AI agent discover what questions it can answer.
    */

    SET query_list = []

    FOR EACH query_name, config IN CANONICAL_QUERIES DO
        query_list.append({
            "name": query_name,
            "description": config["description"],
            "parameters": config["parameters"],
            "example_queries": config["example_queries"]
        })
    END FOR

    RETURN {"queries": query_list}
END TOOL

/*
Example return:
{
    "queries": [
        {
            "name": "revenue_stats",
            "description": "Calculate revenue statistics",
            "parameters": [],
            "example_queries": ["What's the average revenue?", ...]
        },
        ...
    ]
}
*/
```

### Tool 4: Query Classification (Intent Recognition)

```
DEFINE TOOL classify_canonical_query(user_query)
    /*
    IMPORTANT: This is the "smart routing" tool.
    Analyzes natural language to suggest which canonical query to use.

    Uses keyword matching and scoring to find best match.
    */

    PRINT "Analyzing user query:", user_query
    SET user_lower = lowercase(user_query)
    SET scores = {}

    // Score each canonical query
    FOR EACH query_name, config IN CANONICAL_QUERIES DO
        SET score = 0

        // Match against example queries
        FOR EACH example IN config["example_queries"] DO
            SET example_words = split_into_words(example)
            SET user_words = split_into_words(user_lower)
            SET overlap = count_common_words(example_words, user_words)

            IF overlap > 0 THEN
                score += overlap / length(example_words)
            END IF
        END FOR

        // Keyword boosting
        IF "revenue" IN user_lower AND "revenue" IN query_name THEN
            score += 0.5
        END IF

        IF "employee" IN user_lower AND "employee" IN query_name THEN
            score += 0.5
        END IF

        IF "efficiency" IN user_lower AND "efficiency" IN query_name THEN
            score += 0.5
        END IF

        // Special handling for comparative queries
        IF query_name == "revenue_stats" THEN
            IF ("highest" IN user_lower OR "lowest" IN user_lower) AND "revenue" IN user_lower THEN
                score += 0.7  // Strong match
            END IF
        END IF

        scores[query_name] = score
    END FOR

    // Find best match
    SET best_query = find_max_score(scores)
    SET best_score = scores[best_query]

    // Get alternatives (other high-scoring queries)
    SET alternatives = find_top_n_scores(scores, n=3, exclude=best_query)

    // Determine confidence
    IF best_score > 1.0 THEN
        SET confidence = "high"
    ELSE IF best_score > 0.5 THEN
        SET confidence = "medium"
    ELSE
        SET confidence = "low"
    END IF

    RETURN {
        "suggested_query": best_query,
        "confidence": confidence,
        "score": best_score,
        "alternatives": alternatives,
        "reason": "Matched keywords: revenue, highest"
    }
END TOOL

/*
Example:
Input: "Which office has the highest revenue?"
Output: {
    "suggested_query": "revenue_stats",
    "confidence": "high",
    "score": 1.7,
    "alternatives": ["employee_analysis", "efficiency_analysis"]
}
*/
```

### Tool 5: Get Query Template

```
DEFINE TOOL get_query_template(query_name, city=NULL, year_threshold=NULL)
    /*
    Returns LLM prompt template for a canonical query.
    This separates query logic from execution.
    */

    IF query_name NOT IN CANONICAL_QUERIES THEN
        RETURN error("Unknown query: " + query_name)
    END IF

    SET config = CANONICAL_QUERIES[query_name]
    SET template = config["prompt_template"]

    // Fill in template variables
    IF city IS NOT NULL THEN
        template = replace(template, "{city}", city)
    END IF

    IF year_threshold IS NOT NULL THEN
        template = replace(template, "{year}", year_threshold)
    END IF

    RETURN {
        "query_name": query_name,
        "template": template,
        "description": config["description"],
        "parameters": config["parameters"]
    }
END TOOL

/*
Example template:
"Analyze the office revenue data and provide a summary.

Data: {data}

Calculate and present:
1. Average revenue across all offices
2. Minimum and maximum revenue (include office names)
3. Total revenue

Format as a clear, business-friendly summary."
*/
```

### Tool 6: Get Office Dataset

```
DEFINE TOOL get_office_dataset()
    /*
    Returns complete office dataset as JSON.
    Allows agent to work with raw data.
    */

    SET csv_path = "data/offices.csv"

    IF NOT file_exists(csv_path) THEN
        RETURN error("Office data not found")
    END IF

    SET dataframe = read_csv(csv_path)

    RETURN {
        "offices": convert_to_list_of_dicts(dataframe),
        "count": row_count(dataframe),
        "columns": list_columns(dataframe)
    }
END TOOL

/*
Example return:
{
    "offices": [
        {"city": "San Francisco", "employees": 250, "revenue_million": 45.3, "opened_year": 2015},
        {"city": "New York", "employees": 380, "revenue_million": 62.1, "opened_year": 2012},
        ...
    ],
    "count": 10,
    "columns": ["city", "employees", "revenue_million", "opened_year"]
}
*/
```

### Tool 7: Get Filtered Office Data

```
DEFINE TOOL get_filtered_office_data(columns=NULL, filters=NULL)
    /*
    Returns filtered subset of office data.
    Supports column selection and row filtering.
    */

    SET dataframe = read_csv("data/offices.csv")

    // Apply column filtering
    IF columns IS NOT NULL THEN
        IF NOT validate_columns(columns, dataframe) THEN
            RETURN error("Invalid columns: " + columns)
        END IF
        dataframe = select_columns(dataframe, columns)
    END IF

    // Apply row filters
    IF filters IS NOT NULL THEN
        /*
        filters format:
        {
            "revenue_million": {"operator": ">", "value": 40},
            "opened_year": {"operator": ">=", "value": 2015}
        }
        */
        FOR EACH column, filter IN filters DO
            SET operator = filter["operator"]
            SET value = filter["value"]

            IF operator == ">" THEN
                dataframe = filter_rows(dataframe, column > value)
            ELSE IF operator == ">=" THEN
                dataframe = filter_rows(dataframe, column >= value)
            ELSE IF operator == "==" THEN
                dataframe = filter_rows(dataframe, column == value)
            END IF
        END FOR
    END IF

    RETURN {
        "data": convert_to_list_of_dicts(dataframe),
        "count": row_count(dataframe)
    }
END TOOL

/*
Example call:
get_filtered_office_data(
    columns=["city", "revenue_million"],
    filters={"revenue_million": {"operator": ">", "value": 40}}
)

Returns:
{
    "data": [
        {"city": "San Francisco", "revenue_million": 45.3},
        {"city": "New York", "revenue_million": 62.1},
        {"city": "Tokyo", "revenue_million": 51.2}
    ],
    "count": 3
}
*/
```

### Tool 8: Validate Query Parameters

```
DEFINE TOOL validate_query_parameters(query_name, parameters)
    /*
    Validates that parameters are correct for a query.
    Prevents errors before execution.
    */

    IF query_name NOT IN CANONICAL_QUERIES THEN
        RETURN {"valid": FALSE, "error": "Unknown query"}
    END IF

    SET config = CANONICAL_QUERIES[query_name]
    SET required_params = filter(config["parameters"], is_required=TRUE)

    SET missing = []
    SET invalid = []
    SET suggestions = []

    // Check required parameters present
    FOR EACH param IN required_params DO
        IF param["name"] NOT IN parameters THEN
            missing.append(param["name"])
            suggestions.append("Add " + param["name"] + ": " + param["description"])
        END IF
    END FOR

    // Validate parameter types
    FOR EACH param_name, value IN parameters DO
        SET param_config = find_param_config(config, param_name)

        IF param_config EXISTS THEN
            SET expected_type = param_config["type"]

            IF expected_type == "int" AND NOT is_integer(value) THEN
                invalid.append(param_name + " must be an integer")
            END IF
        END IF
    END FOR

    RETURN {
        "valid": (length(missing) == 0 AND length(invalid) == 0),
        "missing": missing,
        "invalid": invalid,
        "suggestions": suggestions
    }
END TOOL
```

---

## Complete MCP Server Workflow

```
Agent connects to MCP server
    ↓
Agent: "I have user query: 'Which office has highest revenue?'"
    ↓
[STEP 1] Agent calls: list_canonical_queries()
    → Gets catalog of available queries
    ↓
[STEP 2] Agent calls: classify_canonical_query("Which office has highest revenue?")
    → Server suggests: "revenue_stats" with high confidence
    ↓
[STEP 3] Agent calls: get_query_template("revenue_stats")
    → Gets LLM prompt template for analysis
    ↓
[STEP 4] Agent calls: get_office_dataset()
    → Gets complete office data
    ↓
[STEP 5] Agent executes analysis locally
    → "New York office has highest revenue: $62.10M"
    ↓
[STEP 6] Agent uses LLM to format response
    → "Based on our data, the New York office leads..."
```

## Key Design Principles

### 1. **Separation of Concerns**
- **Server**: Provides data and query catalog
- **Agent**: Handles reasoning and presentation

### 2. **Discoverability**
- Agent can list all available queries
- Each query has examples and descriptions

### 3. **Smart Routing**
- `classify_canonical_query()` helps agent choose right query
- Keyword matching + scoring algorithm

### 4. **Template-Based**
- Query templates separate structure from execution
- Easy to add new queries without code changes

### 5. **Validation**
- Parameter validation before execution
- Prevents errors and provides helpful suggestions

### 6. **Dual Purpose**
- Weather tools: External API integration
- Business tools: Internal data analysis
- Shows versatility of MCP protocol

## Why This Architecture?

```
TRADITIONAL APPROACH:
User → AI generates SQL → Database
Problem: AI might generate bad SQL, security issues

MCP APPROACH:
User → AI picks canonical query → MCP tool → Safe execution
Benefits:
- Predefined queries (safe)
- AI does routing, not generation
- Separation of concerns
- Easy to audit and control
```

This MCP server demonstrates a **production-ready pattern** for building AI agents with business intelligence capabilities!

---

<p align="center">
**For educational use only by the attendees of our workshops.**
</p>

**(C) 2025 Tech Skills Transformations and Brent C. Laster - all rights reserved.**
