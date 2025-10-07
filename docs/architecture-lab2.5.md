# Lab 2.5 Architecture: Adding Conversation Memory to Agents

## Overview
Lab 2.5 extends Lab 2's agent with conversation memory using a buffer-based approach for context-aware interactions.

## Detailed Architecture Diagram

```mermaid
graph TB
    subgraph "Agent with Memory"
        User[User Queries]

        subgraph "Memory System"
            Memory[ConversationMemory deque maxlen=5]
            Buffer[(Memory Buffer Q1: Paris Q2: London Q3: Tokyo)]
        end

        subgraph "Agent Loop (with Context)"
            Retrieve[Retrieve Past Conversations]
            Context[Build Context String]
            LLM[LLM + Context llama3.2]
            Tools[Weather Tools]
            Store[Store Exchange]
        end

        User --> Retrieve
        Retrieve --> Memory
        Memory --> Buffer
        Buffer --> Context
        Context --> LLM
        LLM --> Tools
        Tools --> Response[Response]
        Response --> Store
        Store --> Memory
        Response --> User
    end

    style Memory fill:#e1f5ff
    style Buffer fill:#fff4e1
    style LLM fill:#e8f5e9
    style Context fill:#ffe8e8
```

## Presentation Slide Diagram (Simple)

```mermaid
flowchart LR
    Query([New Query]) -->|1. Retrieve| Memory[(Memory Buffer)]
    Memory -->|2. Context| LLM[LLM with Context]
    LLM -->|3. Process| Tools[Tools]
    Tools -->|4. Response| Result([Answer])
    Result -->|5. Store| Memory

    style Memory fill:#4CAF50,color:#fff
    style LLM fill:#2196F3,color:#fff
    style Tools fill:#FF9800,color:#fff
```

## ConversationMemory Class Architecture

```mermaid
classDiagram
    class ConversationMemory {
        -deque memory
        -int max_exchanges
        +__init__(max_exchanges)
        +add_exchange(query, response)
        +get_context_string() str
        +get_summary() str
        +clear()
        +is_empty() bool
    }

    class Exchange {
        +str user
        +str agent
        +str timestamp
    }

    ConversationMemory "1" --> "*" Exchange : contains
```

## Memory Workflow Sequence

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Memory
    participant LLM
    participant Tools

    Note over User,Agent: First Query (No Context)
    User->>Agent: "Weather in Paris?"
    Agent->>Memory: get_context_string()
    Memory->>Agent: "" (empty)
    Agent->>LLM: Query without context
    LLM->>Tools: get_weather(Paris)
    Tools->>Agent: 72°F, Sunny
    Agent->>Memory: store("Paris?", "72°F Sunny")
    Agent->>User: "72°F and Sunny"

    Note over User,Agent: Second Query (With Context)
    User->>Agent: "What about London?"
    Agent->>Memory: get_context_string()
    Memory->>Agent: "Previous: User asked Paris"
    Agent->>LLM: Query + Context
    Note over LLM: LLM knows about Paris
    LLM->>Tools: get_weather(London)
    Tools->>Agent: 65°F, Cloudy
    Agent->>Memory: store("London?", "65°F Cloudy")
    Agent->>User: "65°F and Cloudy"

    Note over User,Agent: Third Query (Uses Both)
    User->>Agent: "Which is warmer?"
    Agent->>Memory: get_context_string()
    Memory->>Agent: "Paris: 72°F, London: 65°F"
    Agent->>LLM: Query + Full Context
    LLM->>Agent: "Paris is warmer"
    Agent->>User: "Paris is warmer at 72°F"
```

## Component Details

### 1. ConversationMemory Class
- **Data Structure**: `deque(maxlen=5)` - Sliding window
- **Storage**: Last 5 query-response pairs
- **Auto-cleanup**: Oldest dropped when full
- **Format**: Dict with user/agent/timestamp

### 2. Context Injection
Before each LLM call:
```python
context = memory.get_context_string()
# Returns:
# "Previous conversation context:
#  User: What's the weather in Paris?
#  Agent: It's 72°F and sunny.
#  User: What about London?
#  Agent: It's 65°F and cloudy."
```

### 3. Memory Buffer States
```
[Empty] → [1/5] → [2/5] → ... → [5/5] → [5/5] (oldest dropped)
```

## Data Flow

**Query 1 (No Context):**
```
User → Empty Memory → LLM → Tools → Response → Store in Memory
```

**Query 2 (With Context):**
```
User → Retrieve Context → LLM + Context → Tools → Response → Store in Memory
```

**Query 3 (Multi-turn):**
```
User → Retrieve All Context → LLM + Full Context → Direct Answer
```

## Memory Visualization

```mermaid
graph LR
    subgraph "Memory Buffer (maxlen=5)"
        E1[Exchange 1 Q: Paris A: 72°F]
        E2[Exchange 2 Q: London A: 65°F]
        E3[Exchange 3 Q: Tokyo A: 68°F]
        E4[Empty]
        E5[Empty]
    end

    New[New Exchange] -->|Add| E4
    E1 -->|If Full Drop Oldest| Dropped[Removed]

    style E1 fill:#e8f5e9
    style E2 fill:#e8f5e9
    style E3 fill:#e8f5e9
    style E4 fill:#f0f0f0
    style E5 fill:#f0f0f0
```

## Key Differences from Lab 2

| Aspect | Lab 2 | Lab 2.5 |
|--------|-------|---------|
| Context | None | Last 5 conversations |
| Multi-turn | No | Yes |
| Memory Type | Stateless | Buffer (deque) |
| Follow-ups | Can't handle | Understands references |
| Complexity | Simple | +30 lines |

## Key Learning Points
- **Sliding Window Memory**: Fixed-size buffer with auto-cleanup
- **Context Injection**: Adding memory to LLM prompts
- **Deque Data Structure**: Efficient FIFO queue
- **Stateful Agents**: Maintaining conversation state
- **Memory Management**: Display, clear, statistics

## Architecture Characteristics
- **Type**: Stateful agent with buffer memory
- **Complexity**: Medium
- **Memory**: In-memory deque (not persistent)
- **Capacity**: 5 exchanges (configurable)
- **Overhead**: ~100 tokens per exchange in context
