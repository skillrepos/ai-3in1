# Pseudo-Code: Streamlit Web Interface

## Streamlit UI Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (User)                           │
│              http://localhost:8501                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   main() runs        │
              │   - Setup page       │
              │   - Show header      │
              │   - Create input box │
              │   - Show sidebar     │
              └──────────┬───────────┘
                         │
              User types question &
              clicks "Ask Assistant"
                         │
                         ▼
         ┌───────────────────────────┐
         │ handle_query() called     │
         │                           │
         │ Step 1: Show progress     │
         │   📝 Analyzing...         │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │ Step 2: Detect route      │
         │   🌤️ Weather query?       │
         │   📊 Data query?          │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │ Step 3: Call agent        │
         │   ⚙️ Processing...        │
         │   await process_query()   │
         │   (30 sec timeout)        │
         └───────────┬───────────────┘
                     │
            ┌────────┴────────┐
            │                 │
            ▼                 ▼
        [SUCCESS]         [ERROR]
            │                 │
            ▼                 ▼
    ┌───────────────┐   ┌──────────────┐
    │ ✅ Complete!  │   │ ❌ Error     │
    │               │   │ - Timeout?   │
    │ Show green    │   │ - Exception? │
    │ result box    │   │              │
    │               │   │ Show red box │
    └───────────────┘   └──────────────┘
            │                 │
            └────────┬────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │ Display metrics           │
         │ - Query type              │
         │ - Processing time         │
         │ - Confidence              │
         └───────────────────────────┘
```

### UI Component Structure

```
STREAMLIT PAGE
│
├── HEADER
│   ├── Title: "🏢 AI Office Assistant"
│   └── Subtitle: Instructions
│
├── MAIN AREA
│   ├── Text Input Box
│   │   └─► User types question here
│   ├── Submit Button
│   │   └─► Triggers processing
│   ├── Progress Steps (4 boxes)
│   │   ├─► 📝 Analyzing question...
│   │   ├─► 🔍 Searching data...
│   │   ├─► ⚙️ Processing with AI...
│   │   └─► ✅ Complete!
│   └── Result Box (green or red)
│       └─► Final answer displayed
│
└── SIDEBAR
    ├── System Status
    │   └─► MCP Server: ✅/❌
    ├── Query Examples
    │   ├─► Revenue Analysis
    │   ├─► Employee Analysis
    │   └─► Weather Queries
    └── Available Data
        └─► Office stats
```

## What is Streamlit?

Streamlit is a Python framework for building web UIs quickly.
- Write Python → Get a web app
- No HTML/CSS/JavaScript needed
- Perfect for data science and AI demos

## App Structure

```
FUNCTION main()
    /*
    Main entry point for the Streamlit app.
    This function runs every time the user interacts with the page.
    */

    // Configure the page
    SET page_title = "AI Office Assistant"
    SET page_icon = "🏢"
    SET layout = "wide"

    // Display header
    SHOW title("🏢 AI Office Assistant")
    SHOW subtitle("Ask questions about office data or weather")

    // Create input area
    SET user_input = text_input_box(
        label="Your question:",
        placeholder="e.g., Which office has the highest revenue?"
    )

    // Handle submission
    IF user_clicked_submit_button() THEN
        CALL handle_query(user_input)
    END IF

    // Show example queries in sidebar
    SHOW sidebar_with_examples()
END FUNCTION
```

## Query Handling

```
ASYNC FUNCTION handle_query(user_question)
    /*
    Processes user query and displays results.
    Shows visual feedback during processing.
    */

    // STEP 1: Show visual feedback
    CREATE progress_indicator(
        steps=[
            "📝 Analyzing question...",
            "🔍 Searching data...",
            "⚙️ Processing with AI...",
            "✅ Complete!"
        ]
    )

    // STEP 2: Call the AI agent
    TRY
        // Import the agent function
        FROM rag_agent_canonical IMPORT process_query

        // Process with 30 second timeout
        SET result = AWAIT process_query(user_question, timeout=30)

        // STEP 3: Display result
        IF result IS NOT NULL THEN
            SHOW success_box(result)
        END IF

    CATCH timeout_error
        SHOW error_box("Query took too long. Please try a simpler question.")

    CATCH general_error
        SHOW error_box("An error occurred: " + error.message)
    END TRY
END FUNCTION
```

## Visual Components

```
FUNCTION show_sidebar_with_examples()
    /*
    Displays helpful examples in the sidebar
    */

    SHOW sidebar_header("📚 Example Questions")

    // Office data examples
    SHOW section_header("Office Data:")
    SHOW bullet_list([
        "Which office has the highest revenue?",
        "What's the average revenue?",
        "Which office has the most employees?",
        "How many offices do we have?"
    ])

    // Weather examples
    SHOW section_header("Weather:")
    SHOW bullet_list([
        "What's the weather in Seattle?",
        "Current weather in Tokyo office"
    ])
END FUNCTION
```

## Progress Indicator

```
FUNCTION show_processing_steps(steps)
    /*
    Creates visual feedback during processing.
    Shows users that work is happening.
    */

    // Create columns for each step
    SET columns = create_columns(count=4)

    FOR EACH step, column IN zip(steps, columns) DO
        WITH column DO
            SHOW markdown_box(
                text=step,
                style="processing-step"
            )
        END FOR

        // Small delay so users can see progression
        SLEEP(0.5 seconds)
    END FOR
END FUNCTION
```

## Error Handling UI

```
FUNCTION show_error_box(message)
    /*
    User-friendly error display
    */

    SHOW colored_box(
        color="red",
        icon="❌",
        title="Error",
        message=message
    )
END FUNCTION


FUNCTION show_success_box(result)
    /*
    Display successful result
    */

    SHOW colored_box(
        color="green",
        icon="✅",
        title="Result",
        message=result
    )
END FUNCTION
```

## CSS Styling

```
FUNCTION apply_custom_styles()
    /*
    Makes the app look professional
    */

    SET custom_css = "
        .processing-step {
            padding: 20px;
            border-radius: 10px;
            background: #f0f2f6;
            text-align: center;
        }

        .result-box {
            padding: 20px;
            border-left: 4px solid #00cc66;
            background: #f0fff4;
            margin: 20px 0;
        }

        .error-box {
            padding: 20px;
            border-left: 4px solid #ff4444;
            background: #fff0f0;
            margin: 20px 0;
        }
    "

    APPLY styles(custom_css)
END FUNCTION
```

## Complete Flow

```
User visits page
    ↓
Streamlit runs main()
    ↓
User types question: "Which office has highest revenue?"
    ↓
User clicks Submit
    ↓
handle_query() is called
    ↓
Show progress: "📝 Analyzing question..."
    ↓
Call process_query() from agent
    ↓
Show progress: "🔍 Searching data..."
    ↓
Agent processes query
    ↓
Show progress: "⚙️ Processing with AI..."
    ↓
Agent returns: "New York office has the highest revenue: $62.10M"
    ↓
Show progress: "✅ Complete!"
    ↓
Display result in green success box
    ↓
User sees friendly formatted answer
```

## Streamlit Session State

```
PSEUDOCODE for maintaining state:

// Streamlit reruns the entire script on each interaction
// Use session_state to remember values

IF "query_history" NOT IN session_state THEN
    session_state.query_history = []
END IF

// When user submits
IF submit_button_clicked THEN
    session_state.query_history.append({
        "question": user_input,
        "answer": result,
        "timestamp": current_time()
    })
END IF

// Display history
FOR EACH entry IN session_state.query_history DO
    SHOW question_answer_pair(entry)
END FOR
```

## Key Streamlit Concepts

1. **Reactive Updates**
   - Script reruns on any user interaction
   - UI automatically updates

2. **Widgets**
   - `text_input()` - Text box
   - `button()` - Clickable button
   - `columns()` - Layout columns
   - `markdown()` - Formatted text

3. **Session State**
   - Preserves data across reruns
   - Like browser cookies for the app

4. **Async Support**
   - Can await async functions
   - Good for long-running AI calls

5. **Simplicity**
   - No HTML/JavaScript needed
   - Pure Python for web UIs

---

For educational use only by the attendees of our workshops.

**For training purposes only. (C) 2025 Tech Skills Transformations and Brent C. Laster - all rights reserved.**
