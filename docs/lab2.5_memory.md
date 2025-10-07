# Lab 2.5 (Optional): Adding Conversation Memory to Agents

**Duration:** 15-20 minutes
**Difficulty:** Intermediate
**Prerequisites:** Lab 2 completed

## Overview

In Lab 2, you built a basic agent that could answer weather queries. However, each query was independent - the agent had no memory of previous conversations. In this optional lab, you'll add **conversation memory** to make your agent context-aware.

## What is Conversation Memory?

Without memory, each interaction is isolated:
```
User: "What's the weather in Paris?"
Agent: "It's 72°F and sunny in Paris."

User: "What about London?"
Agent: "It's 65°F and cloudy in London."

User: "Which one is warmer?"
Agent: [Has no context - doesn't know what "which one" refers to]
```

With memory, the agent remembers past exchanges:
```
User: "What's the weather in Paris?"
Agent: "It's 72°F and sunny in Paris."
[Memory stores: Paris=72°F]

User: "What about London?"
Agent: "It's 65°F and cloudy in London."
[Memory stores: London=65°F]

User: "Which one is warmer?"
Agent: "Paris is warmer at 72°F compared to London's 65°F."
[Agent uses memory to compare previous queries]
```

## Memory Implementation Types

### 1. **Buffer Memory** (This Lab)
- Stores the last N conversations in a list/queue
- Simple and fast
- Good for short-term context
- Limited by buffer size

### 2. **Vector Memory** (Used in Lab 5)
- Stores conversations as embeddings in a vector database
- Retrieves semantically similar past conversations
- Good for long-term memory across sessions
- More complex but more powerful

## Lab Structure

### Files
- **Starter:** `agent_with_memory.py` (has TODOs for you to complete)
- **Solution:** `labs/common/lab2_5_memory_solution.txt` (complete implementation)

### Learning Approach
This lab uses a **diff-and-merge** approach:
1. Try implementing the TODOs in `agent_with_memory.py`
2. Compare your work with `labs/common/lab2_5_memory_solution.txt`
3. Learn from the differences

## Part 1: Understanding the ConversationMemory Class

Open `agent_with_memory.py` and examine the `ConversationMemory` class structure:

```python
class ConversationMemory:
    def __init__(self, max_exchanges: int = 5):
        # TODO: Initialize a deque to store conversation exchanges
        # TODO: Set max_exchanges limit
        pass

    def add_exchange(self, user_query: str, agent_response: str):
        # TODO: Create exchange dictionary with query, response, and timestamp
        # TODO: Append to memory (deque automatically drops old items when full)
        pass

    def get_context_string(self) -> str:
        # TODO: If memory is empty, return empty string
        # TODO: Format each exchange as "User: ...\nAgent: ...\n"
        # TODO: Join all exchanges with newlines
        pass
```

### Why `deque`?
- A `deque` (double-ended queue) from Python's `collections` module
- Automatically maintains a maximum size
- When full, adding new items removes the oldest items (FIFO)
- Perfect for sliding window memory!

## Part 2: Implementing Memory Storage

### TODO 1: Initialize the Memory Buffer

```python
def __init__(self, max_exchanges: int = 5):
    # Your code here:
    # - Create a deque with maxlen=max_exchanges
    # - Store max_exchanges for later reference
```

**Hint:** Use `from collections import deque` (already imported)

### TODO 2: Add Conversations to Memory

```python
def add_exchange(self, user_query: str, agent_response: str):
    # Your code here:
    # - Create a dictionary with keys: "user", "agent", "timestamp"
    # - Use datetime.now().strftime("%H:%M:%S") for timestamp
    # - Append to self.memory
```

**Hint:** The deque will automatically drop old items when full

### TODO 3: Format Memory for LLM Context

```python
def get_context_string(self) -> str:
    # Your code here:
    # - Return "" if memory is empty
    # - Build a string with format:
    #   "Previous conversation context:
    #    User: [first query]
    #    Agent: [first response]
    #    User: [second query]
    #    Agent: [second response]"
```

## Part 3: Integrating Memory into the Agent

### TODO 4: Modify the Agent Runner

In the `run_with_memory()` function:

```python
def run_with_memory(question: str, memory: ConversationMemory) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # TODO: Add memory context if available
    if not memory.is_empty():
        # Add memory context as a system message
        # Print that memory is being used
        pass

    messages.append({"role": "user", "content": question})

    # ... rest of TAO loop (similar to Lab 2)
```

### TODO 5: Update the REPL

In the `if __name__ == "__main__"` block:

```python
# TODO: Initialize conversation memory
memory = ConversationMemory(max_exchanges=5)

while True:
    # TODO: Display memory status before each query

    loc = input("Location (or 'exit'/'clear'): ").strip()

    # TODO: Handle 'clear' command to reset memory

    try:
        response = run_with_memory(query, memory)
        # TODO: Add exchange to memory after successful response
    except Exception as e:
        print(f"Warning: Error: {e}\n")
```

## Part 4: Testing Your Implementation

### Test 1: Basic Memory
```bash
python agent_with_memory.py
```

Try:
1. Ask about Paris
2. Ask about London
3. Ask a follow-up that requires context (e.g., "Which was warmer?")

### Test 2: Memory Overflow
1. Ask about 6 different cities (memory holds 5)
2. Use the `memory` command to see stats
3. Verify oldest conversation was dropped

### Test 3: Memory Clearing
1. Build up some memory
2. Type `clear`
3. Verify memory is reset

## Expected Output

```
Weather Agent with Memory (type 'exit' to quit, 'clear' to reset memory)

============================================================
Memory Status: 0/5 exchanges stored
============================================================

Location (or 'exit'/'clear'): Paris
[Processing query...]
Today will be **Clear sky** with a high of **75.2 °F** and a low of **64.4 °F**.

============================================================
Memory Status: 1/5 exchanges stored
Context available for next query
============================================================

Location (or 'exit'/'clear'): London
[Using memory: 1/5 exchanges stored]
[Processing query...]
Today will be **Partly cloudy** with a high of **68.0 °F** and a low of **59.0 °F**.
```

## Key Concepts Learned

1. **Sliding Window Memory** - Keeping N most recent exchanges
2. **Context Injection** - Adding memory to LLM prompts
3. **Memory Management** - Adding, retrieving, and clearing memory
4. **Memory Visualization** - Displaying memory status to users
5. **Conversation Tracking** - Storing user-agent exchanges with timestamps

## Common Pitfalls

### 1. Forgetting to Add Exchanges
```python
# Wrong - memory never gets updated
response = run_with_memory(query, memory)
# Missing: memory.add_exchange(query, response)

# Right
response = run_with_memory(query, memory)
memory.add_exchange(query, response)
```

### 2. Memory Context Format
```python
# Wrong - LLM might not understand
context = str(memory.memory)  # Dumps raw Python dict

# Right - Human-readable format
context = memory.get_context_string()  # "User: ...\nAgent: ..."
```

### 3. Not Checking if Memory is Empty
```python
# Wrong - might add empty context
messages.append({"role": "system", "content": memory.get_context_string()})

# Right - only add if memory exists
if not memory.is_empty():
    messages.append({"role": "system", "content": memory.get_context_string()})
```

## Verification Checklist

- [ ] ConversationMemory class implemented
- [ ] Memory initialized with max_exchanges=5
- [ ] add_exchange() stores conversations correctly
- [ ] get_context_string() formats memory properly
- [ ] Memory is injected into LLM prompts
- [ ] Memory stats displayed before each query
- [ ] 'clear' command resets memory
- [ ] Oldest conversations dropped when buffer full

## Next Steps

- **Lab 3:** Explore tool routing and multi-tool agents
- **Lab 5:** See vector-based memory in the RAG agent
- **Lab 8:** Build a Streamlit UI with persistent memory dashboard

## Troubleshooting

**Memory not being used?**
- Check that `memory.get_context_string()` is being added to messages
- Verify `not memory.is_empty()` check is working

**Memory growing indefinitely?**
- Ensure you're using `deque(maxlen=...)` not a regular list
- Check that maxlen is being set correctly

**Exchanges not storing?**
- Verify `add_exchange()` is called after each response
- Check that the exchange dictionary has correct keys

## Comparison with Solution

After attempting the implementation, compare your code with `labs/common/lab2_5_memory_solution.txt`:

```bash
# View the solution
cat labs/common/lab2_5_memory_solution.txt

# Or run the complete solution directly
python labs/common/lab2_5_memory_solution.txt
```

Look for differences in:
1. How memory is initialized
2. How context is formatted
3. How exchanges are stored
4. How memory is displayed

## Advanced Extensions (Optional)

If you finish early, try these enhancements:

1. **Token Counting:** Add approximate token counting to prevent context overflow
2. **Selective Memory:** Only store certain types of exchanges (successful queries only)
3. **Memory Export:** Add ability to save/load memory from disk
4. **Memory Search:** Add command to search through stored conversations

---

**Time to complete:** ~15-20 minutes
**Key takeaway:** Conversation memory makes agents context-aware and enables multi-turn interactions
