import os
import subprocess

# We sandbox the agent to a specific folder so it doesn't overwrite your real files
WORKSPACE_DIR = "./workspace"

def setup_workspace():
    """Creates the workspace directory if it doesn't exist."""
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

def write_file(filename: str, content: str) -> str:
    """Writes code or text to a file in the workspace."""
    filepath = os.path.join(WORKSPACE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    # We return a string so the LLM knows the action succeeded
    return f"Successfully wrote to {filename}"

def execute_python(filename: str) -> str:
    """Executes a Python script in the workspace and returns its terminal output."""
    filepath = os.path.join(WORKSPACE_DIR, filename)
    try:
        # Run the script, capture the terminal output, and set a 10-second timeout
        result = subprocess.run(
            ['python', filepath], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        # If the script ran perfectly, return the print statements
        if result.returncode == 0:
            return f"Success. Terminal output:\n{result.stdout}"
        # If the script crashed, return the error traceback so the LLM can fix it
        else:
            return f"Error occurred:\n{result.stderr}"
    except Exception as e:
        return f"Execution failed: {str(e)}"