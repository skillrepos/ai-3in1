# AI 3-in-1: Agents, RAG and Local Models
## Building out an AI agent that uses RAG and runs locally
## Session labs 
## Revision 2.3 - 07/19/25

**Follow the startup instructions in the README.md file IF NOT ALREADY DONE!**

**NOTE: To copy and paste in the codespace, you may need to use keyboard commands - CTRL-C and CTRL-V. Chrome may work best for this.**

**Lab 1 - Using Ollama to run models locally**

**Purpose: In this lab, we’ll start getting familiar with Ollama, a way to run models locally.**

1. We already have a script that can download and start Ollama and fetch some models we'll need in later labs. Take a look at the commands being done in the [**scripts/startOllama.sh**](./scripts/startOllama.sh) file. 
```
cat scripts/startOllama.sh
```

2. Go ahead and run the script to get Ollama and start it running.
```
scripts/startOllama.sh &
```

The '&' at the end will causes the script to run in the background. You will see a set of startup messages. After those, you can just hit *Enter* to get back to a prompt in the terminal.

![starting ollama](./images/31ai6.png?raw=true "starting ollama")

3. Now let's find a model to use. Go to https://ollama.com and in the *Search models* box at the top, enter *llama*. In the list that pops up, choose the entry for "llama3.2".

![searching for llama](./images/31ai7.png?raw=true "searching for llama")

4. This will put you on the specific page about that model. Scroll down and scan the various information available about this model.
![reading about llama3.2](./images/31ai8.png?raw=true "reading about llama3.2")

5. Switch back to a terminal in your codespace. While it's not necessary to do as a separate step, first pull the model down with ollama. (This will take a few minutes.)

```
ollama pull llama3.2
```
![pulling the model](./images/31ai9.png?raw=true "pulling the model")

6. Once the model is downloaded, run it with the command below.
```
ollama run llama3.2
```

7. Now you can query the model by inputting text at the *>>>Send a message (/? for help)* prompt.  Let's ask it about what the weather is in Paris. What you'll see is it telling you that it doesn't have access to current weather data and suggesting some ways to gather it yourself.

```
What's the current weather in Paris?
```

![answer to weather prompt and response](./images/31ai10.png?raw=true "answer to weather prompt and response")

8. Now, let's try a call with the API. You can stop the current run with a Ctrl-D or switch to another terminal. Then put in the command below (or whatever simple prompt you want). 
```
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "What causes weather changes?",
  "stream": false
}'
```

9. This will take a minute or so to run. You should see a single response object returned with lots of data. But you can make out the text answer if you look for it. You can try out some other prompts/queries if you want.

![query response](./images/31ai11.png?raw=true "Query response")

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
![starting agent code](./images/31ai12.png?raw=true "Starting agent code")

2. As you can see, this outlines the steps the agent will go through without all the code. When you are done looking at it, close the file by clicking on the "X" in the tab at the top of the file.

3. Now, let's fill in the code. To keep things simple and avoid formatting/typing frustration, we already have the code in another file that we can merge into this one. Run the command below in the terminal.

```
code -d extra/lab2-agent.txt agent.py
```

4. Once you have run the command, you'll have a side-by-side in your editor of the completed code and the agent1.py file.
  You can merge each section of code into the agent1.py file by hovering over the middle bar and clicking on the arrows pointing right. Go through each section, look at the code, and then click to merge the changes in, one at a time.

![Side-by-side merge](./images/31ai13.png?raw=true "Side-by-side merge") 

5. When you have finished merging all the sections in, the files should show no differences. Save the changes simply by clicking on the "X" in the tab name.

![Merge complete](./images/31ai14.png?raw=true "Merge complete") 

6. Now you can run your agent with the following command:

```
python agent.py
```

![Running the agent](./images/31ai15.png?raw=true "Running the agent")

7. The agent will start running and will prompt for a location (or "exit" to finish). At the prompt, you can type in a location like "Paris, France" or "London" or "Raleigh" and hit *Enter*. You'll see lots of activity while the model is loaded. After that you'll be able to see the Thought -> Action -> Observation loop in practice as each one is listed out. You'll also see the arguments being passed to the tools as they are called. Finally you should see a human-friendly message summarizing the weather forecast.

![Agent run](./images/31ai16.png?raw=true "Agent run") 

8. You can then input another location and run the agent again or exit. Note that if you get a timeout error, the API may be limiting the number of accesses in a short period of time. You can usually just try again and it will work.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

**Lab 3 - Exploring MCP**

**Purpose: In this lab, we’ll see how MCP can be used to standardize an agent's interaction with tools.**

1. We have partial implementations of an MCP server and an agent that uses an MCP client to connect to tools on the server. So that you can get acquainted with the main parts of each, we'll build them out as we did the agent in the second lab - by viewing differences and merging. Let's start with the server. Run the command below to see the differences.

```
code -d extra/lab3-server.txt mcp_server.py
```
</br></br>
![MCP server code](./images/31ai17.png?raw=true "MCP server code") 

2. As you look at the differences, note that we are using FastMCP to more easily set up a server, with its @mcp.tool decorators to designate our functions as MCP tools. Also, we run this using the *streamable-http* transport protocol. Review each difference to see what is being done, then use the arrows to merge. When finished, click the "x"" in the tab at the top to close and save the files.

3. Now that we've built out the server code, run it using the command below. You should see some startup messages similar to the ones in the screenshot.

```
python mcp_server.py
```
</br></br>
![MCP server start](./images/31ai18.png?raw=true "MCP server start") 

4. Since this terminal is now tied up with the running server, we need to have a second terminal to use to work with the client. So that we can see the server responses, let's just open another terminal side-by-side with this one. To do that, right-click in the current terminal and select *Split Terminal* from the pop-up context menu. Then click into that terminal to do the steps for the rest of the lab.

![Opening a second terminal](./images/31ai20.png?raw=true "Opening a second terminal") 

5. We also have a small tool that can call the MCP *discover* method to find the list of tools from our server. This is just for demo purposes. You can take a look at the code either by clicking on [**tools/discover_tools.py**](./tools/discover_tools.py) or by entering the first command below in the codespace's terminal. The actual code here is minimal. It connects to our server and invokes the list_tools method. Run it with the second command below and you should see the list of tools like in the screenshot.

```
code tools/discover_tools.py
python tools/discover_tools.py
```

![Discovering tools](./images/31ai19.png?raw=true "Discovering tools") 
   


6. Now, let's turn our attention to the agent that will use the MCP server through an MCP client interface. First, in the second terminal, run a diff command so we can build out the new agent.

```
code -d extra/lab3-agent.txt mcp_agent.py
```

7. Review and merge the changes as before. What we're highlighting in this step are the *System Prompt* that drives the LLM used by the agent, the connection with the MCP client at the /mcp/ endpoint, and the mpc calls to the tools on the server. When finished, close the tab to save the changes as before.

![Agent using MCP client code](./images/31ai21.png?raw=true "Agent using MCP client code") 
   
8. After you've made and saved the changes, you can run the client in the terminal with the command below.

```
python mcp_agent.py
```

9. The agent should start up, and wait for you to prompt it about weather in a location. You'll be able to see similar TAO output. And you'll also be able to see the server INFO messages in the other terminal as the MCP connections and events happen. A suggested prompt is below.

```
What is the weather in New York?
```

![Agent using MCP client running](./images/31ai22.png?raw=true "Agent using MCP client running") 

10. When you're done, you can use 'exit' to stop the client and CTRL-C to stop the server. 

<p align="center">
**[END OF LAB]**
</p>
</br></br>

**Lab 4 - Working with Vector Databases**

**Purpose: In this lab, we’ll learn about how to use vector databases for storing supporting data and doing similarity searches.**

1. For this lab and the next one, we have a data file that we'll be usihg that contains a list of office information and details for a ficticious company. The file is in [**data/offices.pdf**](./data/offices.pdf). You can use the link to open it and take a look at it.

![PDF data file](./images/31ai23.png?raw=true "PDF data file") 

2. In our repository, we have some simple tools built around a popular vector database called Chroma. There are two files which will create a vector db (index) for the *.py files in our repo and another to do the same for the office pdf. You can look at the files either via the usual "code <filename>" method or clicking on [**tools/index_code.py**](./tools/index_code.py) or [**tools/index_pdf.py**](./tools/index_pdf.py).

```
code tools/index_code.py
code tools/index_pdf.py
```

3. Let's create a vector database of our local python files. Run the program to index those as below. You'll see the program loading the embedding model that will turn the code chunks into numeric represenations in the vector database and then it will read and index our *.py files.

```
python tools/index_code.py
```

![Running code indexer](./images/31ai24.png?raw=true "Running code indexer")

4. To help us do easy/simple searches against our vector databases, we have another tool at [**tools/search.py**](./tools/search.py). This tool connects to the ChromaDB vector database we create, and, using cosine similarity metrics, finds the top "hits" (matching chunks) and prints them out. You can open it and look at the code in the usual way if you want. No changes are needed to the code.

```
code tools/search.py
```

5. Now, let's run the search tool against the vector database we built in step 3. You can prompt it with phrases related to our coding like any of the ones shown below. When done, just type "exit".  Notice the top hits and their respective cosine similarity values. Are they close? Farther apart?

```
python tools/search.py

convert celsius to farenheit fastmcp tools
embed model sentence-transformers
async with Client mcp
```

![Running search](./images/31ai25.png?raw=true "Running search")

6.  Now, let's recreate our vector database based off of the PDF file. Just run the indexer for the pdf file.

```
python tools/index_pdf.py
```

![Indexing PDF](./images/31ai26.png?raw=true "Indexing PDF")

7. Now, we can run the same search tool to find the top hits for information about offices. Below are some prompts you can try here. Note that in some of them, we're using keywords only found in the PDF document. Notice the cosine similarity values on each - are they close? Farther apart?  When done, just type "exit".

```
python tools/search.py

Queries:
Corporate Operations office
Seaside cities
Tech Development sites
High revenue branch
```

<br><br>

![PDF search](./images/31ai27.png?raw=true "PDF search")

8. Keep in mind that this is not trying to intelligently answer your prompts at this point. This is a simple semantic search to find related chunks. In lab 5, we'll add in the LLM to give us better responses. In preparation for that lab, make sure that indexing for the PDF is the last one you ran and not the indexing for the Python files.


<p align="center">
**[END OF LAB]**
</p>
</br></br>

    
**Lab 5 - Using RAG with Agents**

**Purpose: In this lab, we’ll explore how agents can leverage external data stores via RAG and tie in our previous tool use.**

1. For this lab, we're going to combine our previous agent that looks up weather with RAG to get information about offices based on a prompt and tell us what the weather is like for that locaion.

2. We have a starter file for the new agent with rag in [**rag-agent.py**](./rag_agent.py). As before, we'll use the "view differences and merge" technique to learn about the code we'll be working with. The command to run this time is below. There are a number of helper functions in this code that are useful to understand. Take some time to look at each section as you merge them in.
   
```
code -d extra/lab5-agent.txt rag_agent.py
```

![Code for rag agent](./images/31ai28.png?raw=true "Code for rag agent") 


3. When you're done merging, close the tab as usual to save your changes. Now, in a terminal, start the MCP server running again:

```
python mcp_server.py
```

4. In a separate terminal, start the new agent running.

```
python rag_agent.py
```

5. You'll see a *User:* prompt when it is ready for input from you. The agent is geared around you entering a prompt about an office. Try a prompt like one of the ones below about office "names" that are only in the PDF.

```
Tell me about HQ
Tell me about the Southern office
```

6. What you should see after that are some messages that show internal processing, such as the retrieved items from the RAG datastore.  Then the agent will run through the necessary steps like parsing the query to find a location, getting the coordinates for the location, getting the weather etc. At the end it will print out an answer to your prompt and the weather determined from the tool.
 
![Running the RAG agent](./images/31ai29.png?raw=true "Running the RAG agent") 

7. After the initial run, you can try prompts about other offices or cities mentioned in the PDF. Type *exit* when done.

8. While this works, it could be more informative and user-friendly. Let's change the prompt and directions to the LLM to have it add an additional fact about the city where the office is located and include that and the weather in a more user-friendly response. To see and make the changes you can do the usual diff and merge using the command below.

```
code -d extra/lab5-agent-2.txt rag_agent.py
```

![Updating the RAG agent](./images/31ai30.png?raw=true "Updating the RAG agent") 

9. Once you've finished the merge, you can run the new agent code the same way again.

```
python rag_agent.py
```

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

<p align="center">
**THANKS!**
</p>
