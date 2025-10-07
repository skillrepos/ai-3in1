# simple_ollama.py - Basic Ollama interaction

from langchain_ollama import ChatOllama

# Initialize Ollama client
llm = ChatOllama(model="llama3.2")

# Get user input
user_prompt = input("Enter your prompt: ")

# Send to Ollama and get response
response = llm.invoke(user_prompt)

# Display result
print(f"\nResponse: {response.content}")
