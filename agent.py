import ollama
from tools import write_file, execute_python, setup_workspace

# 1. Define the tools for the LLM using JSON Schema format
# This tells the model exactly what the tools do and what arguments they require
tool_schemas = [
  {
    'type': 'function',
    'function': {
      'name': 'write_file',
      'description': 'Writes code to a file in the workspace.',
      'parameters': {
        'type': 'object',
        'properties': {
          'filename': {'type': 'string', 'description': 'Name of the file (e.g., script.py)'},
          'content': {'type': 'string', 'description': 'The exact code to write'}
        },
        'required': ['filename', 'content']
      }
    }
  },
  {
    'type': 'function',
    'function': {
      'name': 'execute_python',
      'description': 'Executes a Python script in the workspace and returns its terminal output.',
      'parameters': {
        'type': 'object',
        'properties': {
          'filename': {'type': 'string', 'description': 'Name of the python file to run (e.g., script.py)'}
        },
        'required': ['filename']
      }
    }
  }
]

# Map the string names the LLM returns to our actual Python functions
available_tools = {
    "write_file": write_file,
    "execute_python": execute_python
}

def run_agent(prompt: str):
    setup_workspace()
    
    # 2. Initialize the conversation history with your prompt
    messages = [{'role': 'user', 'content': prompt}]
    print(f"Task: {prompt}\n")
    print("Agent is working...")

    # The infinite ReAct (Reasoning and Acting) loop
    while True:
        # 3. Call the local model
        response = ollama.chat(
            model='qwen2.5-coder:7b',
            messages=messages,
            tools=tool_schemas
        )
        
        # 4. Add the model's response to the conversation history
        message = response['message']
        messages.append(message)
        
        # 5. Check if the model wants to use a tool
        if not message.get('tool_calls'):
            # If no tool is called, the agent has finished the task and is talking to you directly
            print("\nFinal Answer:")
            print(message['content'])
            break
            
        # 6. Execute the requested tools
        for tool_call in message['tool_calls']:
            tool_name = tool_call['function']['name']
            
            # The model returns the arguments as a Python dictionary
            arguments = tool_call['function']['arguments']
            print(f"[Action] -> Calling {tool_name} with {arguments['filename']}...")
            
            # Look up the actual Python function and run it with the arguments
            func = available_tools[tool_name]
            result = func(**arguments)
            
            # 7. Feed the tool's terminal output back to the model as a new message
            messages.append({
                'role': 'tool',
                'name': tool_name,
                'content': str(result)
            })

if __name__ == "__main__":
    # Give the agent a multi-step task
    task = "Write a python script that calculates the first 10 fibonacci numbers, write it to fib.py, and then execute it to show me the result."
    run_agent(task)