# AI for App Development
## Building AI Apps that leverage agents, MCP, and RAG
## Session labs 
## Revision 2.2 - 10/09/25
## (c) 2025 Tech Skills Transformations

**Follow the startup instructions in the README.md file IF NOT ALREADY DONE!**

**NOTE: To copy and paste in the codespace, you may need to use keyboard commands - CTRL-C and CTRL-V. Chrome may work best for this.**

**Lab 1 - Using Ollama to run models locally**

**Purpose: In this lab, we’ll start getting familiar with Ollama, a way to run models locally.**

1. The Ollama app is already installed as part of the codespace setup via [**scripts/startOllama.sh**](./scripts/startOllama.sh). Start it running with the first command below. (If you need to restart it at some point, you can use the same command. To see the different options Ollama makes available for working with models, you can run the second command below in the *TERMINAL*. 

```
ollama serve &
<Hit Enter>
ollama
```

<br><br>

2. Now let's find a model to use. Go to https://ollama.com and in the *Search models* box at the top, enter *llama*. In the list that pops up, choose the entry for "llama3.2".

![searching for llama](./images/31ai7.png?raw=true "searching for llama")

<br><br>

3. This will put you on the specific page about that model. Scroll down and scan the various information available about this model.
![reading about llama3.2](./images/31ai8.png?raw=true "reading about llama3.2")

<br><br>

4. Switch back to a terminal in your codespace. Run the first command to see what models are loaded (none currently). Then pull the model down with the second command. (This will take a few minutes.) 

```
ollama list
ollama pull llama3.2
```

![pulling the model](./images/31ai9.png?raw=true "pulling the model")

<br><br>

5. Once the model is downloaded, you can see it with the first command below. Then run the model with the second command below. This will load it and make it available to query/prompt. 

```
ollama list
ollama run llama3.2
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

<br><br>

10. Now you can run the script with the command below. 

```
python simple_ollama.py
```

<br><br>

11. When prompted, enter a question like "What is the capital of France?" and press Enter. You should see the model's response printed to the terminal. This demonstrates how easy it is to integrate Ollama into a Python application. Feel free to try other prompts. 


12. In preparation for the remaining labs, let's get the model access approaches "warmed up". Start the command below and just leave it running while we continue (if it doesn't finish quickly).

```
python warmup_models.py
```

<p align="center">
**[END OF LAB]**
</p>
</br></br>


**Lab 2 - Creating a simple agent**

**Purpose: In this lab, we’ll learn about the basics of agents and see how tools are called. We'll also see how Chain of Thought prompting works with LLMs and how we can have ReAct agents reason and act.**

1. For this lab, we have the outline of an agent in a file called *agent.py* in that directory. You can take a look at the code either by clicking on [**agent.py**](./agent.py) or by entering the command below in the codespace's terminal.
   
```
code agent.py
```

![starting agent code](./images/31ai32.png?raw=true "Starting agent code")

<br><br>

2. As you can see, this outlines the steps the agent will go through without all the code. When you are done looking at it, close the file by clicking on the "X" in the tab at the top of the file.

<br><br>

3. Now, let's fill in the code. To keep things simple and avoid formatting/typing frustration, we already have the code in another file that we can merge into this one. Run the command below in the terminal.

```
code -d labs/common/lab2_agent_solution.txt agent.py
```

<br><br>

4. Once you have run the command, you'll have a side-by-side in your editor of the completed code and the agent1.py file.
  You can merge each section of code into the agent1.py file by hovering over the middle bar and clicking on the arrows pointing right. Go through each section, look at the code, and then click to merge the changes in, one at a time.

![Side-by-side merge](./images/31ai13.png?raw=true "Side-by-side merge") 

<br><br>

5. When you have finished merging all the sections in, the files should show no differences. Save the changes simply by clicking on the "X" in the tab name.

![Merge complete](./images/31ai14.png?raw=true "Merge complete") 

<br><br>

6. Now you can run your agent with the following command:

```
python agent.py
```

![Running the agent](./images/31ai15.png?raw=true "Running the agent")

<br><br>

7. The agent will start running and will prompt for a location (or "exit" to finish). At the prompt, you can type in a location like "Paris, France" or "London" or "Raleigh" and hit *Enter*. You may see activity while the model is loaded. After that you'll be able to see the Thought -> Action -> Observation loop in practice as each one is listed out. You'll also see the arguments being passed to the tools as they are called. Finally you should see a human-friendly message summarizing the weather forecast.

![Agent run](./images/31ai16.png?raw=true "Agent run") 

<br><br>

8. You can then input another location and run the agent again or exit. Note that if you get a timeout error, the API may be limiting the number of accesses in a short period of time. You can usually just try again and it will work.

<p align="center">
**[END OF LAB]**
</p>
</br></br>


**Lab 3 - Exploring MCP**

**Purpose: In this lab, we'll see how MCP can be used to standardize an agent's interaction with tools.**

1. We have partial implementations of an MCP server and an agent that uses an MCP client to connect to tools on the server. So that you can get acquainted with the main parts of each, we'll build them out as we did the agent in the second lab - by viewing differences and merging. Let's start with the server. Run the command below to see the differences.

```
code -d labs/common/lab3_server_solution.txt mcp_server.py
```

![MCP server code](./images/aiapps18.png?raw=true "MCP server code") 

<br><br>

2. As you look at the differences, note that we are using FastMCP to more easily set up a server, with its *@mcp.tool* decorators to designate our functions as MCP tools. Also, we run this using the *streamable-http* transport protocol. Review each difference to see what is being done, then use the arrows to merge. When finished, click the "x"" in the tab at the top to close and save the files.

<br><br>

3. Now that we've built out the server code, run it using the command below. You should see some startup messages similar to the ones in the screenshot.

```
python mcp_server.py
```

![MCP server start](./images/31ai18.png?raw=true "MCP server start") 

<br><br>

4. Since this terminal is now tied up with the running server, we need to have a second terminal to use to work with the client. So that we can see the server responses, let's just open another terminal side-by-side with this one. To do that, find the icon that looks like a square with two column in the upper right of the terminal area and click it. (See screenshot below). Then click into that terminal to do the steps for the rest of the lab.

![Opening a second terminal](./images/aiapps5.png?raw=true "Opening a second terminal") 

<br><br>

5. We also have a small tool that can call the MCP *discover* method to find the list of tools from our server. This is just for demo purposes. You can take a look at the code either by clicking on [**tools/discover_tools.py**](./tools/discover_tools.py) or by entering the first command below in the codespace's terminal. The actual code here is minimal. It connects to our server and invokes the list_tools method. Run it with the second command below and you should see the list of tools like in the screenshot.

```
code tools/discover_tools.py
python tools/discover_tools.py
```

![Discovering tools](./images/aiapps19.png?raw=true "Discovering tools") 

<br><br>

6. Now, let's turn our attention to the agent that will use the MCP server through an MCP client interface. First, in the second terminal, run a diff command so we can build out the new agent.

```
code -d labs/common/lab3_agent_solution.txt mcp_agent.py
```

<br><br>

7. Review and merge the changes as before. What we're highlighting in this step are the *System Prompt* that drives the LLM used by the agent, the connection with the MCP client at the /mcp/ endpoint, and the mpc calls to the tools on the server. When finished, close the tab to save the changes as before.

![Agent using MCP client code](./images/aiapps20.png?raw=true "Agent using MCP client code") 

<br><br>
   
8. After you've made and saved the changes, you can run the client in the terminal with the command below. **Note that there will be a long pause initially while the model is loaded and processed before you get the final answer. This could be on the order of minutes.**

```
python mcp_agent.py
```

<br><br>

9. The agent should start up, and wait for you to prompt it about weather in a location. You'll be able to see similar TAO output. And you'll also be able to see the server INFO messages in the other terminal as the MCP connections and events happen. A suggested prompt is below.

```
What is the weather in New York?
```

![Agent using MCP client running](./images/31ai22.png?raw=true "Agent using MCP client running") 

<br><br>

10. When you're done, you can use 'exit' to stop the client and CTRL-C to stop the server. 

<p align="center">
**[END OF LAB]**
</p>
</br></br>

**Lab 4 - Working with Vector Databases**

**Purpose: In this lab, we’ll learn about how to use vector databases for storing supporting data and doing similarity searches.**

1. For this lab and the next one, we have a data file that we'll be usihg that contains a list of office information and details for a ficticious company. The file is in [**data/offices.pdf**](./data/offices.pdf). You can use the link to open it and take a look at it.

![PDF data file](./images/31ai23.png?raw=true "PDF data file") 

<br><br>

2. In our repository, we have some simple tools built around a popular vector database called Chroma. There are two files which will create a vector db (index) for the *.py files in our repo and another to do the same for the office pdf. You can look at the files either via the usual "code <filename>" method or clicking on [**tools/index_code.py**](./tools/index_code.py) or [**tools/index_pdf.py**](./tools/index_pdf.py). 

```
code tools/index_code.py
code tools/index_pdf.py
```

<br><br>

3. Let's create a vector database of our local python files. Run the program to index those as below. You'll see the program loading the embedding model that will turn the code chunks into numeric represenations in the vector database and then it will read and index our *.py files. **When you run the command below, there will be a very long pause while things get loaded.**

```
python tools/index_code.py
```

![Running code indexer](./images/31ai24.png?raw=true "Running code indexer")

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

![Running search](./images/31ai25.png?raw=true "Running search")

<br><br>

6.  Now, let's recreate our vector database based off of the PDF file. Type "exit" to end the current search. Then run the indexer for the pdf file.

```
python tools/index_pdf.py
```

![Indexing PDF](./images/31ai26.png?raw=true "Indexing PDF")

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

![PDF search](./images/31ai27.png?raw=true "PDF search")

<br><br>

8. Keep in mind that this is not trying to intelligently answer your prompts at this point. This is a simple semantic search to find related chunks. In lab 5, we'll add in the LLM to give us better responses. In preparation for that lab, make sure that indexing for the PDF is the last one you ran and not the indexing for the Python files.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

    
**Lab 5 - Using RAG with Agents**

**Purpose: In this lab, we’ll explore how agents can leverage external data stores via RAG and tie in our previous tool use.**

1. For this lab, we're going to combine our previous agent that looks up weather with RAG to get information about offices based on a prompt and tell us what the weather is like for that locaion.

<br><br>

2. We have a starter file for the new agent with rag in [**rag_agent.py**](./rag_agent.py). As before, we'll use the "view differences and merge" technique to learn about the code we'll be working with. The command to run this time is below. There are a number of helper functions in this code that are useful to understand. Take some time to look at each section as you merge them in.

```
code -d labs/common/lab5_agent_solution.txt rag_agent.py
```

![Code for rag agent](./images/31ai28.png?raw=true "Code for rag agent") 

<br><br>

3. When you're done merging, close the tab as usual to save your changes. Now, in a terminal, start the MCP server running again:

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

<br><br>

6. What you should see after that are some messages that show internal processing, such as the retrieved items from the RAG datastore.  Then the agent will run through the necessary steps like parsing the query to find a location, getting the coordinates for the location, getting the weather etc. At the end it will print out an answer to your prompt and the weather determined from the tool.
 
![Running the RAG agent](./images/31ai29.png?raw=true "Running the RAG agent") 

<br><br>

7. After the initial run, you can try prompts about other offices or cities mentioned in the PDF. Type *exit* when done.

<br><br>

8. While this works, it could be more informative and user-friendly. Let's change the prompt and directions to the LLM to have it add an additional fact about the city where the office is located and include that and the weather in a more user-friendly response. To see and make the changes you can do the usual diff and merge using the command below.

```
code -d labs/common/lab5_agent_solution_v2.txt rag_agent.py
```

![Updating the RAG agent](./images/31ai30.png?raw=true "Updating the RAG agent") 

<br><br>

9. Once you've finished the merge, you can run the new agent code the same way again.

```
python rag_agent.py
```

<br><br>

10. Now, you can try the same queries as before and you should get more user-friendly answers.

```
Tell me about HQ
Tell me about the Southern office
```

![Running the updated RAG agent](./images/31ai31.png?raw=true "Running the updated RAG agent")

<p align="center">
**[END OF LAB]**
</p>
</br></br>

**Lab 6 - Building a Classification MCP Server**

**Purpose: In this lab, we'll transform our simple MCP server to use classifications and prompt templates. This creates a scalable architecture where the server manages query interpretation and templates, while the client focuses on LLM execution.**

1. First, let's understand what we're building. The classification approach separates concerns:
   - **Server**: Query catalog, classification logic, prompt templates, data access
   - **Client**: LLM execution, workflow orchestration, result formatting

   This makes adding new analysis capabilities much easier - you just update server configuration instead of modifying agent code.

<br><br>

2. We have a skeleton file for our new classification server that shows the structure. Let's examine it and then build it out using our familiar diff-and-merge approach.

```
code -d labs/common/lab6_mcp_server_solution.txt mcp_server_classification.py
```

![Updating the MCP server](./images/aiapps21.png?raw=true "Updating the MCP server") 

<br><br>

3. As you review the differences, note the key components:
   - **CANONICAL_QUERIES**: A catalog of supported analysis types with templates and examples
   - **Classification tools**: `classify_canonical_query()` matches user intent to canonical queries
   - **Template tools**: `get_query_template()` returns structured prompts for the LLM
   - **Data tools**: `get_filtered_office_data()` provides specific data columns needed
   - **Validation tools**: `validate_query_parameters()` ensures proper inputs

<br><br>

4. Merge each section by clicking the arrows. Pay attention to:
   - How canonical queries are defined with descriptions, parameters, templates, and examples
   - The keyword matching logic in `classify_canonical_query()`
   - How templates use `{data}` placeholder for client-side data substitution
   - The filtering capabilities in `get_filtered_office_data()`

<br><br>

5. When finished merging, save the file by closing the tab. Now start the new server:

```
python mcp_server_classification.py
```

![Running the MCP server](./images/aiapps7.png?raw=true "Running the MCP server") 

<br><br>

6. The server should start and initialize its vector database. **This will take awhile to load and be ready.** You'll see:

   - Loading of the embedding model (all-MiniLM-L6-v2)
   - Initialization of ChromaDB at ./mcp_chroma_db
   - Population of two vector collections:
     * office_locations (from PDF data)
     * office_analytics (from CSV data)
   - List of available tool categories

   The server now provides several categories of tools:
   - **Vector Search** : Semantic search for locations and analytics
   - **Weather** : Weather and geocoding tools (from previous labs)
   - **Classification** : Query intent classification
   - **Templates** : Prompt template management
   - **Structured Data** : Raw CSV data access
   - **Legacy Tools** : Alternative keyword-based search


![Running the MCP server](./images/aiapps8.png?raw=true "Running the MCP server") 

<br><br>

7. Understanding the vector database architecture:
    - The MCP server now owns and manages the vector database
    - Both PDF (locations) and CSV (analytics) data are embedded
    - This centralized approach allows multiple agents to share the same data
    - The server creates semantic embeddings for intelligent query matching 

Let's see the list of tools the MCP server makes available. Run the discovery tool again.

```
python tools/discover_tools.py
```

<br><br>

8.  You should see several tool categories:
   - **New vector search tools**: `vector_search_locations`, `vector_search_analytics`
   - **Classification tools**: `classify_canonical_query`, `get_query_template`
   - **Data access tools**: `get_office_dataset`, `get_filtered_office_data`
   - **Validation tools**: `validate_query_parameters`
   - **Weather tools**: `get_weather`, `geocode_location`, `convert_c_to_f`

![Discover tools](./images/aiapps22.png?raw=true "Discover tools") 

<br><br>

9. The server is now ready to handle sophisticated query interpretation and provide structured templates for analysis. In the next lab, we'll build an agent that leverages these capabilities, so you can leave it running.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

**Lab 7 - Building an Classification-Based RAG Agent**

**Purpose: In this lab, we'll build an agent that uses the classification server from Lab 6. This agent demonstrates the 4-step classification workflow: classify → template → data → execute.**

1.  Let's build out the classification-based agent using our skeleton file. This agent demonstrates a **centralized data architecture** where:
   - The MCP server owns all data access (vector DB, raw files, embeddings)
   - The agent is pure orchestration (no local files, no local vector DB)
   - Queries are routed to either weather workflow (vector search + weather API) or classification workflow (structured analytics)

   This represents best practices for production RAG systems with clear separation of concerns.

```
code -d labs/common/lab7_rag_agent_solution.txt rag_agent_classification.py
```

![Updating the RAG agent](./images/aiapps10.png?raw=true "Updating the RAG agent") 

<br><br>

2. As you review and merge the differences, observe the key architectural patterns:
   - **Simplified imports**: No chromadb, pdfplumber, or sentence-transformers needed
   - **MCP-centric data access**: All data comes from MCP server tools
   - **Query routing**: Keyword matching determines weather vs. analytics workflow
   - **Weather workflow**: Uses MCP's `vector_search_locations()` for semantic location matching
   - **Classification workflow**: 4-step process (classify → template → data → execute)
   - **Local LLM execution**: Agent only runs the LLM, data comes from server

<br><br>

3.  Merge each section carefully. Notice two key functions:
   - `handle_weather_query()`: Now uses MCP's `vector_search_locations()` instead of local ChromaDB
   - `handle_canonical_query_with_classification()`: Orchestrates the 4-step classification workflow

   The agent has no local file reading, no embeddings, no vector database - everything comes from MCP.

<br><br>

4. When finished merging, save the file. Make sure your classification server from Lab 6 is still running (if not, restart it).

<br><br>

5. Now start the classification agent in a second terminal:

```
python rag_agent_classification.py
```

<br><br>

6. The agent will start and explain that it uses classification and prompt templates. Try the demo mode first to see several example queries:

```
demo
```

![Running the RAG agent](./images/aiapps11.png?raw=true "Running the RAG agent") 

<br><br>

7. You'll see the agent process various queries, showing the classification workflow in action:
   - Classifying canonical query from user input
   - Server suggests the best matching query type  
   - Retrieving the appropriate prompt template
   - Fetching required data columns
   - Executing LLM locally with template + data

![Running the RAG agent](./images/aiapps12.png?raw=true "Running the RAG agent") 

<br><br>

8. Now try some individual queries. You can pick a couple from the list below. Test both weather queries (uses MCP vector search) and data analysis queries (uses classification workflow):

```
What's the weather like at our Chicago office?
Which office has the highest revenue?
What's the average revenue across our offices?
Which office has the most employees?
Tell me about the Austin office
What offices opened after 2014?
```

<br><br>

9. Observe the workflow differences:

    **Weather queries** ("What's the weather at HQ?"):
    - Agent calls MCP's `vector_search_locations("What's the weather at HQ?")`
    - MCP performs semantic search in its vector database
    - Returns: "HQ 123 Main St, New York, NY..."
    - Agent extracts location and calls `geocode_location` and `get_weather`

    **Analytics queries** ("Which office has the most employees?"):
    - Agent calls MCP's `classify_canonical_query(...)`
    - MCP returns: "employee_analysis"
    - Agent calls `get_query_template("employee_analysis")`
    - Agent calls `get_filtered_office_data(columns=["employees", "city"])`
    - Agent executes LLM locally with template + data

10. Notice the architectural benefits:
   - **Weather queries**: Use MCP's semantic vector search (RAG via server)
   - **Analytics queries**: Use MCP's classification system (structured via server)
   - **No duplication**: MCP server owns all data, agent is pure orchestration
   - **Scalability**: Multiple agents could use the same MCP server
   - **Fallback**: If LLM times out, agent provides calculated results directly

   This centralized architecture follows best practices.

  The power of this architecture is that you can add new canonical queries just by updating the server configuration - no agent code changes needed. Type 'exit' when done to stop the agent.



<p align="center">
**[END OF LAB]**
</p>
</br></br>

**Lab 8 - Creating a Streamlit Web Application**

**Purpose: In this lab, we'll create a modern web interface for our classification-based RAG agent using Streamlit. This provides a user-friendly way to interact with our canonical query system.**

1. For efficiency, we've already created a Streamlit application for you:
   - `streamlit_app.py` - A user-friendly interface for general use
 
<br><br>

2. Open it up and take a look at the code for it - either via [**streamlit_app.py**](./scripts/streamlit_app.py) or by using the command below.

```
code streamlit_app.py
```

![app code](./images/aiapps27.png?raw=true "app code") 

<br><br>

3. Before we use the Streamlit app, make sure your MCP classification server from Lab 6 is running:

```
python mcp_server_classification.py
```

![server running](./images/aiapps28.png?raw=true "server running") 

<br><br>

4. In an unused terminal, start the Streamlit application:

```
streamlit run streamlit_app.py
```

![app running](./images/aiapps29.png?raw=true "app running") 

<br><br>

5. Your codespace will start the Streamlit app running at http://localhost:8501. You will probably see a dialog pop up to open Open a browser tab to that location. If you can't open it via the dialog, then go to the *PORTS* tab (next to *TERMINAL*), find the row for *8501* and then hover over the *Forwarded Address* column and click on the "globe icon".  See second screenshot below.

![Running the Streamlit app](./images/aiapps23.png?raw=true "Running the Streamlit app") 

![Running the Streamlit app](./images/aiapps30.png?raw=true "Running the Streamlit app") 

<br><br>

6. Explore the web interface:
   - **Sidebar**: Shows system status, query examples, and available data information
   - **Main area**: Enter queries and see real-time processing steps
   - **Processing indicators**: Watch as the system analyzes your query intent and routes it appropriately

![Exploring the Streamlit app](./images/aiapps24.png?raw=true "Exploring the Streamlit app") 

<br><br>

7. Here are some example queries you can try in the web interface: (the ones that go through the canonical flow may take a while initially)
   - "Tell me about the Chicago office"
   - "How are employees distributed?"
   - "Which office has the highest revenue?"
   - "What's the weather at our New York office?"
   - "Which office has the most employees?"

<br><br>

8. Notice how the web interface shows:
   - Query analysis and intent detection
   - Workflow routing (weather vs. data analysis)
   - AI processing with the classification system
   - Completion with structured results

<br><br>

9. The web interface provides several advantages:
   - **User-friendly**: Non-technical users can easily interact with the AI
   - **Visual feedback**: Clear indication of processing steps
   - **System monitoring**: Shows MCP server connection status
   - **Example guidance**: Built-in query examples and help

<br><br>


10. The Streamlit app includes a conversation memory dashboard in the sidebar (a feature of Streamlit). Look for:
    - **Total Exchanges**: Counter showing how many conversations have been stored
    - **Estimated Tokens**: Approximate token usage with progress bar
    - **Offices Discussed**: Entity tracking showing which offices were mentioned
    - **Clear Memory Button**: Reset conversation history
    - **View History Button**: Toggle to see recent conversation excerpts

<br><br>

11. Try using the memory features:
    - Ask about multiple offices and watch the "Offices Discussed" list grow
    - Make several queries and see the token counter increase
    - Click "View History" to see recent exchanges
    - Click "Clear Memory" to reset and start fresh

![App memory features](./images/aiapps31.png?raw=true "App memory features")     

<br><br>

12. When finished, stop the Streamlit app and the server with Ctrl-C in their respective terminals.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

**Lab 9 - Deploying to Hugging Face Spaces**

**Purpose: In this lab, we'll deploy our classification-based RAG agent to Hugging Face Spaces, creating a publicly accessible web application.**

1. **Prerequisites**: You'll need a free Hugging Face account. Go to https://huggingface.co and sign up if you haven't already.

<br><br>

2. Make sure you are logged in to your Hugging Face account. We need to have an access token to work with. Go to this URL: https://huggingface.co/settings/tokens/new?tokenType=write to create a new token. (Alternatively, you can go to your user Settings, then select Access Tokens, then Create new token, and select Write for the token type.) Select a name for the token and then Create token.

![creating a new token](./images/aiapps13.png?raw=true "Creating a new token")
</br></br></br>

3. After you click the Create button, your new token will be displayed on the screen. **Make sure to copy it and save it somewhere you can get to it for the next steps. You will not be able to see it again.**

![new token displayed](./images/aiapps14.png?raw=true "New token displayed")  
</br></br></br>

4. Run the following command to login with your Hugging Face account credentials. Replace "*<YOUR_SAVED_TOKEN>*" with the actual value of the token you created in the previous steps.

```
hf auth login --token <YOUR_SAVED_TOKEN>
```

![logging in with token](./images/aiapps15.png?raw=true "Logging in with token") 
</br></br></br>

5. Now let's create a new Hugging Face Space. This can be done via the browser interface. But it can be quicker just to use this command line. Run the command below. ("aiapp" is the name of the space we're creating.

```
hf repo create --repo-type space --space_sdk docker aiapp
```

![creating a space](./images/aiapps16.png?raw=true "Creating a space") 

<br><br>

6. Next, clone your space repository. Make sure you are in the root of your project first.
   
   ```
   cd /workspaces/ai-apps
   git clone https://huggingface.co/spaces/YOUR_USERNAME/aiapp
   ```

![cloning a space](./images/aiapps17.png?raw=true "Cloning a space") 

<br><br>

7. Now, we need to copy the deployment files we need into the new repo. Run the following copy commands. To make this simple, there's already a script that will copy and locate the needed files in [**scripts/copyfiles.sh**](./scripts/copyfiles.sh). You can look at that with the usual methods if you want. When ready, go ahead and change into the *aiapp* directory and run it. **This will run very quickly.**
   ```
   cd aiapp
   ../scripts/copyfiles.sh
   ```

<br><br>

8. Push the changes back to the Hugging Face repo. **Notice there is a required "." at the end of the command.**
   ```
   hf upload --repo-type space aiapp .
   ```

![Uploading](./images/aiapps26.png?raw=true "Uploading")

<br><br>

9. Monitor your deployment by going to your space page on Hugging Face. Go to **https://huggingface.co/spaces/<userid>/aiapp**.
   - You'll see the build process and container execution in the logs
   - The Space will automatically start once the build completes (takes several minutes)

![Deployment in progress](./images/aiapps35.png?raw=true "Deployment in progress") 

<br><br>

10. Test your deployed application.
    - Once the Space is running, you'll see your Streamlit app
    - Try the same queries you tested locally

![Testing deployed app](./images/aiapps25.png?raw=true "Testing deployed app") 

<br><br>


11. You can share your URL to share your app with others.
    - Your Space is now publicly accessible at: `https://huggingface.co/spaces/YOUR_USERNAME/aiapp`
    - You can share this URL with others to demonstrate your AI application


<br><br>


**Congratulations!** You've successfully deployed an AI application with sophisticated classification capabilities on the web. Your application demonstrates advanced concepts like canonical query classification, use of RAG and MCP protocols and user-friendly AI interfaces.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

<p align="center">
**For educational use only by the attendees of our workshops.**
</p>

<p align="center">
**(c) 2025 Tech Skills Transformations and Brent C. Laster. All rights reserved.**
</p>
