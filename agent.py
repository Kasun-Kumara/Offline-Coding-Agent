import ollama
from tools import write_file, execute_python, setup_workspace

# (Keep the exact same tool_schemas and available_tools as before)
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

available_tools = {
    "write_file": write_file,
    "execute_python": execute_python
}

def interactive_agent():
    setup_workspace()
    
    # 1. THE MEMORY: Initialize the conversation history ONCE before the loop starts
    # We add a 'system' prompt to give the agent its persona
    messages = [
        {'role': 'system', 'content': 'You are a helpful AI coding assistant. You can write and execute Python code in a local workspace.'}
    ]
    
    print("Agent is ready! (Type 'exit' or 'quit' to stop)")
    print("-" * 50)
    
    # 2. THE CHAT LOOP: Continually wait for user input
    while True:
        try:
            # Get your prompt from the terminal
            user_input = input("\nYou: ")
            
            # Check if you want to exit
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            if not user_input.strip():
                continue
                
            # Append your new prompt to the ongoing memory
            messages.append({'role': 'user', 'content': user_input})
            print("\nAgent is thinking...")
            
            # 3. THE REASONING LOOP: The agent decides to use tools or answer directly
            while True:
                response = ollama.chat(
                    model='qwen2.5-coder:7b',
                    messages=messages,
                    tools=tool_schemas
                )
                
                message = response['message']
                
                # Append the agent's thought/action to the memory so it remembers what it did
                messages.append(message)
                
                # If no tools are called, it wants to speak to you. Break the inner loop.
                if not message.get('tool_calls'):
                    print(f"\nAgent: {message['content']}")
                    break 
                    
                # Execute the tools if requested
                for tool_call in message['tool_calls']:
                    tool_name = tool_call['function']['name']
                    arguments = tool_call['function']['arguments']
                    print(f"[Action] -> Calling {tool_name} with {arguments['filename']}...")
                    
                    func = available_tools[tool_name]
                    result = func(**arguments)
                    
                    # Append the tool's result to the memory
                    messages.append({
                        'role': 'tool',
                        'name': tool_name,
                        'content': str(result)
                    })
                    
        # Handle Ctrl+C gracefully
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    interactive_agent()