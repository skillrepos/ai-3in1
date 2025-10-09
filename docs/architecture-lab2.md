# Lab 2 Architecture: Creating a Simple Agent

## Overview
Lab 2 introduces the TAO (Thought-Action-Observation) agent pattern with tool calling capabilities.

## Detailed Architecture Diagram

```mermaid
graph TB
    subgraph "Agent Workflow (TAO Loop)"
        User[User Query: Weather in Paris?]

        subgraph "Thought Phase"
            LLM1[LLM llama3.2]
            Parse1[Parse: Extract lat/lon]
        end

        subgraph "Action Phase"
            Tool1[Tool: get_weather Open-Meteo API]
            Tool2[Tool: convert_c_to_f Math Function]
        end

        subgraph "Observation Phase"
            Result[Observation: Weather Data]
            LLM2[LLM Format Response]
        end

        User --> LLM1
        LLM1 --> Parse1
        Parse1 --> Tool1
        Tool1 --> Result
        Result --> LLM2
        LLM2 --> Tool2
        Tool2 --> Response[Final Answer]
    end

    Internet[Open-Meteo API] --> Tool1

    style LLM1 fill:#e1f5ff
    style LLM2 fill:#e1f5ff
    style Tool1 fill:#fff4e1
    style Tool2 fill:#fff4e1
    style Result fill:#e8f5e9
```

## Simple Architecture Diagram

```mermaid
flowchart TD
    Query([User Query]) -->|1. Thought| LLM[LLM Planning]
    LLM -->|2. Action| Tools[Tools get_weather convert_c_to_f]
    Tools -->|3. Observation| Data[Weather Data]
    Data -->|4. Format| Response([Final Answer])

    style LLM fill:#4CAF50,color:#fff
    style Tools fill:#FF9800,color:#fff
    style Data fill:#2196F3,color:#fff
```

## TAO (Thought-Action-Observation) Pattern

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant LLM
    participant Weather API
    participant Converter

    User->>Agent: "What's the weather in Paris?"

    Note over Agent,LLM: THOUGHT PHASE
    Agent->>LLM: Plan: What do I need?
    LLM->>Agent: Need coordinates for Paris

    Note over Agent,Weather API: ACTION PHASE
    Agent->>Weather API: get_weather(48.8566, 2.3522)
    Weather API->>Agent: {temp: 22°C, conditions: "Clear"}

    Note over Agent,Converter: OBSERVATION & ACTION
    Agent->>Converter: convert_c_to_f(22)
    Converter->>Agent: 71.6°F

    Note over Agent,User: FINAL RESPONSE
    Agent->>User: "Clear sky, 71.6°F in Paris"
```

## Component Details

### 1. LLM (llama3.2)
- **Purpose**: Reasoning and planning
- **Input**: User query + system prompt
- **Output**: Tool calls with arguments
- **Framework**: LangChain-Ollama

### 2. Tools
**get_weather(lat, lon)**
- External API call to Open-Meteo
- Returns: temperature (°C), conditions, weather code

**convert_c_to_f(c)**
- Python function: `c * 9/5 + 32`
- Returns: temperature in Fahrenheit

### 3. System Prompt
Defines available tools and TAO format:
```
You are a helpful weather assistant.
Available tools:
1. get_weather(lat, lon)
2. convert_c_to_f(c)

Use TAO format:
- Thought: Your reasoning
- Action: Tool to call
- Args: JSON arguments
```

## Data Flow

1. **User Input** → "What's the weather in Paris?"
2. **Thought** → LLM determines need coordinates (48.8566, 2.3522)
3. **Action 1** → Call `get_weather(48.8566, 2.3522)`
4. **Observation 1** → Receive weather data (22°C, Clear)
5. **Action 2** → Call `convert_c_to_f(22)`
6. **Observation 2** → Receive 71.6°F
7. **Final Response** → Format and return to user

## Key Learning Points
- **Agentic Behavior**: LLM decides which tools to call
- **TAO Pattern**: Structured reasoning loop
- **Tool Calling**: Functions the LLM can execute
- **Multi-step Workflows**: Chaining tool calls
- **ReAct Pattern**: Reasoning + Acting

## Architecture Characteristics
- **Type**: Synchronous agent loop
- **Complexity**: Medium
- **Dependencies**: Ollama, requests library
- **Tools**: 2 (weather API + converter)
- **LLM Calls**: 2 per query (plan + format)

---

<p align="center">
**For educational use only by the attendees of our workshops.**
</p>

**(C) 2025 Tech Skills Transformations and Brent C. Laster - all rights reserved.**
