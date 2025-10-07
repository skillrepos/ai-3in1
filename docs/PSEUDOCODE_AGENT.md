# Pseudo-Code: RAG Agent Core Logic

## Logic Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER ASKS QUESTION                       │
│              "Which office has highest revenue?"            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  CLASSIFY QUERY TYPE │
              │  (keyword matching)  │
              └──────────┬───────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
           ▼                           ▼
    [DATA KEYWORDS]             [WEATHER KEYWORDS]
    revenue, employees          weather, temperature
           │                           │
           ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│  CANONICAL WORKFLOW  │    │   WEATHER WORKFLOW   │
│                      │    │                      │
│ 1. Load CSV data     │    │ 1. RAG vector search │
│ 2. LLM picks query   │    │ 2. Extract location  │
│ 3. Execute analysis  │    │ 3. Call MCP weather  │
│ 4. LLM formats result│    │ 4. LLM formats result│
└──────────┬───────────┘    └──────────┬───────────┘
           │                           │
           └─────────────┬─────────────┘
                         ▼
              ┌──────────────────────┐
              │   NATURAL LANGUAGE   │
              │       RESPONSE       │
              └──────────────────────┘
```

## Main Entry Point: `process_query()`

```
FUNCTION process_query(user_question)
    /*
    This is the main entry point from the Streamlit UI.
    It routes queries to either data analysis or weather workflows.
    */

    PRINT "Starting query processing"

    // STEP 1: Classify the query type
    SET canonical_keywords = ["revenue", "employees", "office", "highest", "average", etc.]
    SET weather_keywords = ["weather", "temperature", "forecast", "rain"]

    IF user_question contains canonical_keywords AND NOT weather_keywords THEN
        SET query_type = "data_analysis"
    ELSE IF user_question contains weather_keywords THEN
        SET query_type = "weather"
    ELSE
        SET query_type = "data_analysis"  // default
    END IF

    PRINT "Query type detected:", query_type

    // STEP 2: Route to appropriate workflow
    IF query_type == "data_analysis" THEN
        CALL run_canonical_mode(user_question)
    ELSE
        CALL run_weather_mode(user_question)
    END IF

    RETURN formatted_response
END FUNCTION
```

## Data Analysis Workflow: `run_canonical_mode()`

### Canonical Mode Flow Diagram

```
User: "Which office has highest revenue?"
           │
           ▼
┌──────────────────────┐
│  Iteration Loop      │  Max 3 iterations
│  (allows multi-step) │
└──────────┬───────────┘
           │
           ▼
    ┌──────────────┐
    │ Data Loaded? │
    └──────┬───────┘
           │
     ┌─────┴─────┐
     NO          YES
     │            │
     ▼            ▼
[Load CSV]   [Ask LLM: What query?]
     │            │
     │            ▼
     │    ┌──────────────────┐
     │    │ LLM Returns JSON │
     │    │ {"action":       │
     │    │  "analyze_      │
     │    │   offices"}      │
     │    └────────┬─────────┘
     │             │
     │             ▼
     │    ┌──────────────────┐
     │    │ Execute Query    │
     │    │ (analyze_offices)│
     │    └────────┬─────────┘
     │             │
     │             ▼
     │    ┌──────────────────┐
     │    │ Raw Result:      │
     │    │ "New York: $62M" │
     │    └────────┬─────────┘
     │             │
     │             ▼
     │    ┌──────────────────┐
     │    │ LLM Formats      │
     │    │ Natural Response │
     │    └────────┬─────────┘
     │             │
     └─────────────┴─────► DONE!
```

### Pseudo-Code

```
ASYNC FUNCTION run_canonical_mode(user_question)
    /*
    Handles queries about office data (revenue, employees, etc.)
    Uses a 2-step process: Load data → Analyze with LLM
    */

    SET data_loaded = FALSE
    SET office_data = NULL
    SET max_iterations = 3

    // Loop allows for multi-step reasoning
    FOR iteration FROM 1 TO max_iterations DO

        PRINT "Iteration", iteration

        // STEP 1: Ask LLM what to do next
        SET llm_plan = llm_decide_next_action(user_question, data_loaded)

        /*
        LLM returns JSON like:
        {"action": "load_data"} OR
        {"action": "analyze_offices", "args": {"query": "highest_revenue"}}
        */

        SET action = parse_json(llm_plan)["action"]

        // STEP 2: Execute the action
        IF action == "load_data" THEN
            office_data = LOAD CSV("data/offices.csv")
            data_loaded = TRUE
            CONTINUE  // Go to next iteration

        ELSE IF action == "analyze_offices" THEN
            SET canonical_query = parse_json(llm_plan)["args"]["query"]

            // Execute the structured query
            SET raw_result = analyze_offices(office_data, canonical_query)

            // Example raw_result: "New York office has highest revenue: $62.10M"

            // STEP 3: Use LLM to make response conversational
            SET natural_response = llm_generate_response(
                user_question,
                raw_result
            )

            PRINT natural_response
            BREAK  // Done!
        END IF
    END FOR
END FUNCTION
```

## LLM Decision Making: `llm_decide_next_action()`

```
FUNCTION llm_decide_next_action(user_question, data_loaded)
    /*
    Uses LLM to convert natural language into structured actions.
    This is the "intelligence" layer.
    */

    // If data not loaded yet, must load first
    IF NOT data_loaded THEN
        RETURN {"action": "load_data"}
    END IF

    // Use LLM to map question to canonical query
    SET system_prompt = "
        You convert natural language questions into structured queries.
        Available queries:
        - 'highest_revenue': Which office has most revenue
        - 'average_revenue': Average revenue across offices
        - 'most_employees': Which office has most employees
        - 'office_count': How many offices exist

        Respond with JSON only:
        {\"action\": \"analyze_offices\", \"args\": {\"query\": \"QUERY_NAME\"}}
    "

    SET user_prompt = "User question: " + user_question

    // Call Ollama LLM
    SET llm_response = CALL ollama_llm(
        model="llama3.2:1b",
        system=system_prompt,
        user=user_prompt,
        format="json"
    )

    RETURN llm_response
END FUNCTION
```

## Data Analysis: `analyze_offices()`

```
FUNCTION analyze_offices(office_data, canonical_query)
    /*
    Executes predefined queries on the office dataset.
    This is deterministic - no AI randomness here.
    */

    // Convert dict to DataFrame for easy analysis
    SET df = create_dataframe(office_data)

    // Pattern matching on canonical query
    IF canonical_query == "highest_revenue" THEN
        SET max_index = find_max_index(df["revenue_million"])
        SET city = df[max_index]["city"]
        SET revenue = df[max_index]["revenue_million"]
        RETURN city + " office has highest revenue: $" + revenue + "M"

    ELSE IF canonical_query == "average_revenue" THEN
        SET avg = calculate_mean(df["revenue_million"])
        RETURN "Average revenue is $" + avg + "M"

    ELSE IF canonical_query == "most_employees" THEN
        SET max_index = find_max_index(df["employees"])
        SET city = df[max_index]["city"]
        SET employees = df[max_index]["employees"]
        RETURN city + " office has most employees: " + employees

    ELSE IF canonical_query == "office_count" THEN
        RETURN "Total offices: " + count_rows(df)
    END IF
END FUNCTION
```

## Weather Workflow: `run_weather_mode()`

```
ASYNC FUNCTION run_weather_mode(user_question)
    /*
    Handles weather queries using RAG + MCP
    */

    // STEP 1: RAG Vector Search
    SET embedding_model = load_sentence_transformer("all-MiniLM-L6-v2")
    SET chroma_db = open_chromadb_collection()

    // Search for similar documents
    SET query_embedding = embedding_model.encode(user_question)
    SET search_results = chroma_db.search(query_embedding, top_k=5)
    SET top_document = search_results[0]

    // STEP 2: Extract location from document
    SET coordinates = extract_coordinates(top_document)

    IF coordinates == NULL THEN
        SET city_name = extract_city_name(top_document)
        coordinates = geocode_city(city_name)
    END IF

    // STEP 3: Call MCP Weather API
    SET mcp_client = connect_to_mcp("http://127.0.0.1:8000/mcp/")

    SET weather_data = AWAIT mcp_client.call_tool(
        "get_weather",
        {"lat": coordinates.latitude, "lon": coordinates.longitude}
    )

    SET temperature_f = AWAIT mcp_client.call_tool(
        "convert_c_to_f",
        {"c": weather_data.temperature}
    )

    // STEP 4: Generate natural summary with LLM
    SET summary = llm_generate_weather_summary(
        location=top_document,
        temperature=temperature_f,
        conditions=weather_data.conditions
    )

    RETURN summary
END FUNCTION
```

## RAG Helper Functions (Location Extraction)

```
FUNCTION extract_coordinates(document_text)
    /*
    The weather workflow needs to extract location from RAG results.
    This section shows the multi-step extraction strategy.
    */

    // STEP 1: Try to find explicit coordinates
    SET coords = find_coords([document_text])

    IF coords IS NOT NULL THEN
        RETURN coords  // Found "40.7128, -74.0060" format
    END IF

    // STEP 2: Try structured formats
    SET city_state = find_city_state([document_text])  // "Seattle, WA"
    IF city_state IS NOT NULL THEN
        RETURN geocode(city_state)
    END IF

    SET city_country = find_city_country([document_text])  // "Tokyo, Japan"
    IF city_country IS NOT NULL THEN
        RETURN geocode(city_country)
    END IF

    // STEP 3: Fallback - guess city name
    SET city_guess = guess_city([document_text])
    IF city_guess IS NOT NULL THEN
        RETURN geocode(city_guess)
    END IF

    RETURN NULL  // Could not extract location
END FUNCTION


FUNCTION find_coords(texts)
    /*
    Search for explicit latitude/longitude coordinates.
    Pattern: "40.7128, -74.0060" or "40.7128 -74.0060"
    */

    SET coord_pattern = REGEX("\b(-?\d{1,2}(?:\.\d+)?)[,\s]+(-?\d{1,3}(?:\.\d+)?)\b")

    FOR EACH text IN texts DO
        FOR EACH match IN coord_pattern.find_all(text) DO
            SET lat = parse_float(match.group(1))
            SET lon = parse_float(match.group(2))

            // Validate ranges
            IF -90 <= lat <= 90 AND -180 <= lon <= 180 THEN
                RETURN (lat, lon)
            END IF
        END FOR
    END FOR

    RETURN NULL
END FUNCTION


FUNCTION find_city_state(texts)
    /*
    Extract US/Canada style "City, ST" format.
    Example: "Seattle, WA" or "Toronto, ON"
    */

    SET pattern = REGEX("\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z]{2})\b")

    FOR EACH text IN texts DO
        SET match = pattern.search(text)
        IF match EXISTS THEN
            RETURN match.group(0)  // Returns "Seattle, WA"
        END IF
    END FOR

    RETURN NULL
END FUNCTION


FUNCTION find_city_country(texts)
    /*
    Extract international "City, Country" format.
    Example: "Tokyo, Japan" or "London, England"
    */

    SET pattern = REGEX("\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z][a-z]{2,})\b")

    FOR EACH text IN texts DO
        SET match = pattern.search(text)
        IF match EXISTS THEN
            RETURN match.group(0)  // Returns "Tokyo, Japan"
        END IF
    END FOR

    RETURN NULL
END FUNCTION


FUNCTION guess_city(texts)
    /*
    Fallback: Find any capitalized word that might be a city.
    Uses stopwords to filter out common words like "Office", "HQ".
    */

    SET stopwords = ["Office", "HQ", "Center", "Centre", "Building"]
    SET pattern = REGEX("\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b")

    FOR EACH text IN texts DO
        FOR EACH match IN pattern.find_all(text) DO
            SET token = match.group(1).strip()

            // Filter out stopwords and short words
            IF length(token) > 2 AND token NOT IN stopwords THEN
                RETURN token
            END IF
        END FOR
    END FOR

    RETURN NULL
END FUNCTION


FUNCTION geocode(city_name)
    /*
    Convert city name to coordinates using Open-Meteo geocoding API.
    Implements retry logic for "City, State" → "City" fallback.
    */

    SET url = "https://geocoding-api.open-meteo.com/v1/search"

    // Helper function for API lookup
    FUNCTION lookup_coords(name)
        TRY
            SET response = HTTP_GET(url, params={"name": name, "count": 1}, timeout=10)
            SET data = parse_json(response.body)

            IF data.has("results") AND length(data["results"]) > 0 THEN
                SET result = data["results"][0]
                RETURN (result["latitude"], result["longitude"])
            END IF
        CATCH network_error
            RETURN NULL
        END TRY

        RETURN NULL
    END FUNCTION

    // Try full name first
    SET coords = lookup_coords(city_name)
    IF coords IS NOT NULL THEN
        RETURN coords
    END IF

    // Retry with simplified name if comma present
    IF "," IN city_name THEN
        SET simple_name = split(city_name, ",")[0].strip()
        RETURN lookup_coords(simple_name)
    END IF

    RETURN NULL
END FUNCTION


FUNCTION rag_search(query, embedding_model, chromadb_collection)
    /*
    Semantic search using vector embeddings.
    This is the "Retrieval" part of RAG.
    */

    // Convert query to vector embedding
    SET query_embedding = embedding_model.encode(query)
    // Example: "weather in Seattle" → [0.234, -0.112, 0.789, ...]

    // Search ChromaDB for similar documents
    SET results = chromadb_collection.query(
        query_embeddings=[query_embedding],
        n_results=5,  // Top 5 matches
        include=["documents"]
    )

    // Return the text of matching documents
    IF results.has("documents") AND length(results["documents"]) > 0 THEN
        RETURN results["documents"][0]  // List of top 5 document texts
    ELSE
        RETURN []  // No matches found
    END IF
END FUNCTION


FUNCTION open_collection()
    /*
    Initialize ChromaDB collection for vector storage.
    Creates directory if needed.
    */

    // Ensure storage directory exists
    CREATE_DIRECTORY("./chroma_db")

    // Create persistent ChromaDB client
    SET client = ChromaDBPersistentClient(path="./chroma_db")

    // Get or create collection
    SET collection = client.get_or_create_collection("codebase")

    RETURN collection
END FUNCTION
```

## Key Takeaways

1. **Query Classification** - First decision: what kind of query is this?
2. **LLM as Router** - AI decides which tool/query to use
3. **Structured Queries** - Predefined queries ensure consistent results
4. **LLM as Presenter** - AI converts raw data into natural language
5. **Async Operations** - Weather API calls happen asynchronously
6. **Error Handling** - Multiple fallbacks ensure robustness
