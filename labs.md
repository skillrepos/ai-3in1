# AI 3-in-1: Agents, RAG and Local Models
## Building out an AI agent that uses RAG and runs locally
## Session labs 
## Revision 4.5 - 02/23/26

**Follow the startup instructions in the README.md file IF NOT ALREADY DONE!**

**NOTES**
- To copy and paste in the codespace, you may need to use keyboard commands - CTRL-C and CTRL-V. Chrome may work best for this.
- If your codespace has to be restarted, run these commands again!
  ```
  ollama serve &
  python warmup_models.py
  ```

<br><br><br>
**Lab 1 - Using Ollama to run models locally**

**Purpose: In this lab, we’ll start getting familiar with Ollama, a way to run models locally.**

---

**What the Ollama example does**
- Starts a local Ollama server inside the Codespace so you can run models locally.
- Pulls a small model (`llama3.2:1b`) and creates an alias (`llama3.2:latest`) used by the rest of the workshop.
- Runs the model interactively (`ollama run`) and via HTTP (`/api/generate`) to show the two common access patterns.
- Runs a simple Python script (`simple_ollama.py`) that calls Ollama programmatically using LangChain’s Ollama integration.

**What it demonstrates**
- The difference between:
  - **Interactive CLI usage** (quick testing),
  - **Direct HTTP API calls** (service-style integration),
  - **Python integration** (application development).
- Why “local model execution” matters for workshops and prototyping:
  - consistent environment, no cloud account required, predictable tooling.
- The importance of using a consistent model tag/alias (`llama3.2:latest`) so later labs behave consistently.

---

### Steps


1. The Ollama app is already installed as part of the codespace setup via [**scripts/startOllama.sh**](./scripts/startOllama.sh). Start it running with the first command below. (If you need to restart it at some point, you can use the same command. To see the different options Ollama makes available for working with models, you can run the second command below in the *TERMINAL*. 

```
ollama serve &
<Hit Enter>
ollama --help
```

<br><br>

2. Now let's find a model to use. Go to https://ollama.com and in the *Search models* box at the top, enter *llama*. In the list that pops up, choose the entry for "llama3.2".

![searching for llama](./images/31ai7.png?raw=true "searching for llama")

<br><br>

3. This will put you on the specific page about that model. Scroll down and scan the various information available about this model.
![reading about llama3.2](./images/31ai37.png?raw=true "reading about llama3.2")

<br><br>

4. Switch back to a terminal in your codespace. Run the first command to see what models are loaded (none currently). Then pull the latest (3b parameters) model down with the second command. (This will take a few minutes.)

```
ollama list
ollama pull llama3.2
```

![pulling the model](./images/31ai9.png?raw=true "pulling the model")

<br><br>

5. Once the model is downloaded, you can see it with the first command below. Then run the model with the second command below. This will load it and make it available to query/prompt. 

```
ollama list
ollama run llama3.2:latest
```

<br><br>

6. Now you can query the model by inputting text at the *>>>Send a message (/? for help)* prompt.  Let's ask it about what the weather is in Paris. What you'll see is it telling you that it doesn't have access to current weather data and suggesting some ways to gather it yourself.

```
What's the current weather in Paris?
```

![answer to weather prompt and response](./images/31ai10.png?raw=true "answer to weather prompt and response")

<br><br>

7. Now, let's try a call with the API. You can stop the current run with a Ctrl-D or switch to another terminal. Then put in the command below (or whatever simple prompt you want). 

```
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "What causes weather changes?",
  "stream": false
}' | jq -r '.response'
```

<br><br>

8. This will take a minute or so to run. You should see a long text response . You can try out some other prompts/queries if you want.

![query response](./images/aiapps37.png?raw=true "Query response")

<br><br>

9. Now let's try a simple Python script that uses Ollama programmatically. We have a basic example script called `simple_ollama.py`. Take a look at it either via [**simple_ollama.py**](./simple_ollama.py) or via the command below.

```
code simple_ollama.py
```

You should see a simple script that:
- Imports the ChatOllama class from langchain_ollama
- Initializes the Ollama client with the llama3.2 model
- Takes user input
- Sends it to Ollama
- Displays the response

![simple ollama](./images/31ai36.png?raw=true "simple ollama")


<br><br>

10. Now you can run the script with the command below. 

```
python simple_ollama.py
```

<br><br>

11. When prompted, enter a question like "What is the capital of France?" and press Enter. You should see the model's response printed to the terminal. This demonstrates how easy it is to integrate Ollama into a Python application. Feel free to try other prompts. 

![query](./images/31ai35.png?raw=true "query")


<br><br>

12. In preparation for the remaining labs, let's get the model access approaches "warmed up". Start the command below and just leave it running while we continue (if it doesn't finish quickly).

```
python warmup_models.py
```

<p align="center">
**[END OF LAB]**
</p>
</br></br>


**Lab 2 - Creating a simple agent**

**Purpose: In this lab, we’ll learn the basics of agents and create a simple one. We’ll observe the agent loop (plan → tool call → result) via the program’s logged steps and tool inputs/outputs.**

---

**What the agent example does**
- Uses a local Ollama-served LLM (llama3.2) to interpret a weather request and decide when to call a tool.
- Extracts a location (or coordinates) from the input and calls Open-Meteo to fetch current/forecast weather data.
- Produces a short, user-friendly summary by iterating through an agent loop.

**What it demonstrates**
- How to integrate **LangChain + Ollama** to drive an agent workflow.
- An observable agent trace: **plan → tool call → tool result → response** (including tool arguments and outputs).
- Basic tool/function calling patterns and how tools ground the final answer in external data.

---

### Steps

1. For this lab, we have the outline of an agent in a file called *agent.py* in the project's directory. You can take a look at the code either by clicking on [**agent.py**](./agent.py) or by entering the command below in the codespace's terminal.
   
```
code agent.py
```

![starting agent code](./images/31ai38.png?raw=true "Starting agent code")

<br><br>

2. As you can see, this outlines the steps the agent will go through without all the code. When you are done looking at it, close the file by clicking on the "X" in the tab at the top of the file.

<br><br>

3. Now, let's fill in the code. To keep things simple and avoid formatting/typing frustration, we already have the code in another file that we can merge into this one. Run the command below in the terminal.

```
code -d labs/common/lab2_agent_solution.txt agent.py
```

<br><br>

4. Once you have run the command, you'll have a side-by-side in your editor of the completed code and the **agent.py** file.
  You can merge each section of code into **agent.py** by hovering over the middle bar and clicking on the arrows pointing right. Go through each section, look at the code, and then click to merge the changes in, one at a time.

![Side-by-side merge](./images/31ai39.png?raw=true "Side-by-side merge") 

<br><br>

5. When you have finished merging all the sections in, the files should show no differences. Save the changes simply by clicking on the "X" in the tab name.

![Merge complete](./images/31ai40.png?raw=true "Merge complete") 

<br><br>

6. Now you can run your agent with the following command:

```
python agent.py
```

![Running the agent](./images/31ai41.png?raw=true "Running the agent")

<br><br>

7. The agent will start running and will prompt for a location (or "exit" to finish). At the prompt, you can type in a location like "Paris, France" or "London" or "Raleigh" and hit *Enter*. You may see activity while the model is loaded. After that you'll be able to see the Thought -> Action -> Observation loop in practice as each one is listed out. You'll also see the arguments being passed to the tools as they are called. Finally you should see a human-friendly message summarizing the weather forecast.

![Agent run](./images/31ai42.png?raw=true "Agent run") 

<br><br>

8. You can then input another location and run the agent again or exit. Note that if you get a timeout error, the API may be limiting the number of accesses in a short period of time - it should retry on its own and return a result.

<br><br>

9. Try putting in *Sydney, Australia* and then check the output against the weather forecast on the web. Why do you think it doesn't match? How would you fix it?

Here's a clue: "If latitude/longitude is in the Southern or Western hemisphere, use negative values as appropriate"


<p align="center">
**[END OF LAB]**
</p>
</br></br>


**Lab 3 - Exploring MCP**

**Purpose: In this lab, we'll see how MCP can be used to standardize an agent's interaction with tools.**

---

**What the MCP example does**
- Implements an **MCP server** using `FastMCP` that exposes weather-related tools.
- Connects an **MCP client agent** that uses an LLM to decide which MCP tools to invoke.
- Handles retries/timeouts and demonstrates robustness when tool calls fail.

**What it demonstrates**
- How **FastMCP** standardizes tool interfaces via JSON-RPC with minimal boilerplate.
- Clean separation between **tool hosting (server)** and **agent orchestration (client + LLM)**.
- Protocol-first design: capability listing, structured tool schemas, and transport configuration (stdio vs streamable HTTP).

---

### Steps

1. We have partial implementations of an MCP server and an agent that uses an MCP client to connect to tools on the server. So that you can get acquainted with the main parts of each, we'll build them out as we did the agent in the second lab - by viewing differences and merging. Let's start with the server. Run the command below to see the differences.

```
code -d labs/common/lab3_server_solution.txt mcp_server.py
```

As you look at the differences, note that we are using FastMCP to more easily set up a server, with its *@mcp.tool* decorators to designate our functions as MCP tools. Also, we run this using the *streamable-http* transport protocol. Review each difference to see what is being done, then use the arrows to merge. When finished, click the "X" in the tab at the top to close and save the files.

![MCP server code](./images/31ai44.png?raw=true "MCP server code") 

<br><br>

2. Now that we've built out the server code, run it using the command below. You should see some startup messages similar to the ones in the screenshot.

```
python mcp_server.py
```

![MCP server start](./images/31ai18.png?raw=true "MCP server start") 

<br><br>

3. Since this terminal is now tied up with the running server, we need to have a second terminal to use to work with the client. So that we can see the server responses, let's just open another terminal side-by-side with this one. To do that, over in the upper right section of the *TERMINAL* panel, find the plus sign and click on the downward arrow next to it. (See screenshot below.) Then select "Split Terminal" from the popup menu. Then click into that terminal to do the steps for the rest of the lab. (FYI: If you want to open another full terminal at some point, you can just click on the "+" itself and not the down arrow.)

![Opening a second terminal](./images/aiapps38.png?raw=true "Opening a second terminal") 

<br><br>

4. We also have a small helper script that connects to the MCP server and **lists the available tools** (for demo purposes).
  Take a look at the code in `tools/discover_tools.py`, then run it to print the server’s tool list: (Make sure to click back in the terminal before typing the second command.)

```
code tools/discover_tools.py
python tools/discover_tools.py
```

![Discovering tools](./images/31ai33.png?raw=true "Discovering tools") 

<br><br>

5. Now, let's turn our attention to the agent that will use the MCP server through an MCP client interface. First, in the second terminal, run a diff command so we can build out the new agent.

```
code -d labs/common/lab3_agent_solution_dynamic.txt mcp_agent.py
```

<br><br>

6. Review and merge the changes as before. What we're highlighting in this step are the overall flow, the *System Prompt* that drives the LLM used by the agent, how the agent decides which tool to call via MCP via the LLM output, etc. When finished, close the tab to save the changes as before.

![Agent using MCP client code](./images/31ai43.png?raw=true "Agent using MCP client code") 

<br><br>
   
7. After you've made and saved the changes, you can run the client in the terminal with the command below. **Note that there may be a long pause initially while the model is loaded and processed before you get the final answer. This could be on the order of minutes.**

```
python mcp_agent.py
```

<br><br>

8. The agent should start up, and wait for you to prompt it about weather in a location. You'll be able to see similar TAO output. And you'll also be able to see the server INFO messages in the other terminal as the MCP connections and events happen. A suggested prompt is below.

```
What is the weather in New York?
```

![Agent using MCP client running](./images/aiapps40.png?raw=true "Agent using MCP client running") 

<br><br>


9. Because we're using a tool to do the geolocation (get latitude and longitude), you can also put in locations like Sydney, Australia and get accurate results.

![Agent using MCP client running](./images/31ai45.png?raw=true "Agent using MCP client running") 

<br><br>

10.  When you're done, you can use 'exit' to stop the client and CTRL-C to stop the server. 

<p align="center">
**[END OF LAB]**
</p>
</br></br>

**Lab 4 - Working with Vector Databases**

**Purpose: In this lab, we’ll learn about how to use vector databases for storing supporting data and doing similarity searches.**

---

**What the vector database example does**
- Builds a local vector index using ChromaDB for:
  - the repository’s Python files (code indexing), and
  - a PDF document (`data/offices.pdf`) containing office information.
- Uses an embedding model to convert chunks of text into vectors.
- Runs a search tool that retrieves the top matching chunks using similarity scoring.

**What it demonstrates**
- **Retrieval-only semantic search**:
  - embeddings + vector similarity return relevant chunks,
  - but do **not** generate a natural-language answer by themselves.
- Why chunking + embeddings enable “meaning-based” search beyond keywords.
- How the same retrieval approach applies to different sources (code vs PDF).
- How similarity scores help you compare results and judge confidence before you generate an answer (Lab 5).

---

### Steps

1. For this lab and the next one, we have a data file that we'll be usihg that contains a list of office information and details for a ficticious company. The file is in [**data/offices.pdf**](./data/offices.pdf). You can use the link to open it and take a look at it.

![PDF data file](./images/31ai23.png?raw=true "PDF data file") 

<br><br>

2. In our repository, we have some simple tools built around a popular vector database called Chroma. There are two files which will create a vector db (index) for the *.py files in our repo and another to do the same for the office pdf. You can look at the files either via the usual "code <filename>" method or clicking on [**tools/index_code.py**](./tools/index_code.py) or [**tools/index_pdf.py**](./tools/index_pdf.py). 

```
code tools/index_code.py
code tools/index_pdf.py
```

<br><br>

3. Let's create a vector database of our local python files. Run the program to index those as below. You'll see the program loading Chroma's built-in embedding model that will turn the code chunks into numeric represenations in the vector database and then it will read and index our *.py files. **When you run the command below, there may be a pause while things get loaded.**

```
python tools/index_code.py
```

![Running code indexer](./images/31ai53.png?raw=true "Running code indexer")

<br><br>

4. To help us do easy/simple searches against our vector databases, we have another tool at [**tools/search.py**](./tools/search.py). This tool connects to the ChromaDB vector database we create, and, using cosine similarity metrics, finds the top "hits" (matching chunks) and prints them out. You can open it and look at the code in the usual way if you want. No changes are needed to the code.

```
code tools/search.py
```

<br><br>

5. Now, let's run the search tool against the vector database we built in step 3. You can prompt it with phrases related to our coding like any of the ones shown below. When done, just type "exit".  Notice the top hits and their respective cosine similarity values. Are they close? Farther apart?

```
python tools/search.py

convert celsius to farenheit
fastmcp tools
embed model sentence-transformers
async with Client mcp
```

![Running search](./images/31ai54.png?raw=true "Running search")

<br><br>

6.  Now, let's recreate our vector database based off of the PDF file. Type "exit" to end the current search. Then run the indexer for the pdf file.

```
python tools/index_pdf.py
```

![Indexing PDF](./images/31ai55.png?raw=true "Indexing PDF")

<br><br>

7. Now, we can run the same search tool to find the top hits for information about offices. Below are some prompts you can try here. Note that in some of them, we're using keywords only found in the PDF document. Notice the cosine similarity values on each - are they close? Farther apart?  When done, just type "exit".

```
python tools/search.py

Queries:
Corporate Operations office
Seaside cities
Tech Development sites
High revenue branch
```

![PDF search](./images/31ai56.png?raw=true "PDF search")

<br><br>

8. Keep in mind this is **retrieval only**: it uses an **embedding model** to find similar chunks, but it does **not** use a generative model to compose a natural-language answer. In Lab 5, we’ll add a generative step to produce a more user-friendly response grounded in retrieved content.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

    
**Lab 5 - Using RAG with Agents**

**Purpose: In this lab, we’ll explore how agents can leverage external data stores via RAG and tie in our previous tool use.**

---

**What the RAG + agent example does**
- Adds a **RAG search tool** (`search_offices`) that the agent can call to find office information from the Lab 4 vector database.
- Uses the same **TAO (Thought-Action-Observation) loop** from Labs 2 and 3, where the **LLM decides** which tools to call and in what order.
- Combines **local tools** (vector search) with **remote tools** (MCP server) in a single agent workflow.
- Produces office information grounded in retrieved content + live weather from MCP tools.

**What it demonstrates**
- A complete “AI 3-in-1” agentic workflow:
  - **Local model** (LLM via Ollama drives all decisions),
  - **RAG retrieval** (ChromaDB vector search as an agent tool),
  - **MCP tool use** (weather/geocoding via the Lab 3 server).
- **True agentic behavior**: the LLM controls the workflow — it decides to search offices first, extract the city, geocode it, get weather, and convert the temperature. The code doesn't hardcode this sequence.
- How “version 2” enhances the agent's final answer by having the LLM compose a natural language summary with an interesting fact about the city.

---

### Steps

1. For this lab, we're going to build an agent that uses RAG (from Lab 4's vector database) combined with MCP tools (from Lab 3's server) to answer questions about company offices and their local weather — all driven by the LLM through a TAO loop (like Labs 2 and 3).

<br><br>

2. We have a starter file for the new agent in [**rag_agent.py**](./rag_agent.py). As before, we'll use the "view differences and merge" technique to learn about the code we'll be working with. The command to run this time is below. Note how this agent has a system prompt describing all four tools (`search_offices` + three MCP tools) and a TAO loop that can dispatch to either local or remote tools. Take some time to look at each section as you merge them in.

```
code -d labs/common/lab5_agent_solution.txt rag_agent.py
```

![Code for rag agent](./images/31ai49.png?raw=true "Code for rag agent") 

<br><br>

3. When you're done merging, close the tab as usual to save your changes. Now, if the MCP server is not still running from lab3, in a terminal, start it running again:

```
python mcp_server.py
```

<br><br>

4. In a separate terminal, start the new agent running.

```
python rag_agent.py
```

<br><br>

5. You'll see a *User:* prompt when it is ready for input from you. The agent is geared around you entering a prompt about an office. Try a prompt like one of the ones below about office "names" that are only in the PDF. **NOTE: After the first run, subsequent queries may take longer due to retries required for the open-meteo API that the MCP server is running.** 

```
Tell me about HQ
Tell me about the Southern office
```

![Agent query about HQ](./images/31ai50.png?raw=true "Agent query about HQ") 

<br><br>

6. What you should see is the agent's TAO loop in action — just like in Labs 2 and 3! The LLM will think about what to do, call `search_offices` to find relevant office data from the vector database, then geocode the city, get the weather, and convert the temperature. Each step shows the Thought, Action, and Observation. At the end, it displays the collected office and weather information.
 
![Running the RAG agent](./images/31ai47.png?raw=true "Running the RAG agent") 

<br><br>

7. After the initial run, you can try prompts about other offices or cities mentioned in the PDF. Type *exit* when done.

<br><br>

8. While the agent works well and demonstrates true agentic behavior, the final output just displays the raw collected data. Let's enhance the agent so that when it finishes, the LLM composes a friendly, natural language summary that includes office details, weather, and an interesting fact about the city. To see and make the changes you can do the usual diff and merge using the command below.

```
code -d labs/common/lab5_agent_solution_v2.txt rag_agent.py
```

![Updating the RAG agent](./images/31ai51.png?raw=true "Updating the RAG agent") 

<br><br>

9. Once you've finished the merge, you can run the new agent code the same way again.

```
python rag_agent.py
```

<br><br>

10. Now, you can try the same queries as before and you should get more user-friendly answers with the LLM generating a natural language summary.

```
Tell me about HQ
Tell me about the Southern office
```

![Running the updated RAG agent](./images/31ai52.png?raw=true "Running the updated RAG agent")

<br><br>

11. When done, you can stop the MCP server via Ctrl-C and "exit" out of the agent.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

<p align="center">
**For educational use only by the attendees of our workshops.**
</p>

<p align="center">
**(c) 2026 Tech Skills Transformations and Brent C. Laster. All rights reserved.**
</p>

