"""
MeTTa Runner for Nimo Project
This script allows running MeTTa scripts using the Rust REPL without needing the Python bindings.
"""
import os
import sys
import subprocess
import json

# Define the path to the MeTTa REPL executable
HYPERON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                           "hyperon-experimental")
METTA_REPL = os.path.join(HYPERON_PATH, "target", "debug", "metta-repl.exe")

# Path to MeTTa scripts
RULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules")

def run_metta_script(script_path, capture_output=True):
    """
    Run a MeTTa script using the MeTTa REPL
    
    Args:
        script_path: Path to the MeTTa script
        capture_output: Whether to capture and return the output
        
    Returns:
        The output of the MeTTa script if capture_output is True
    """
    if not os.path.exists(METTA_REPL):
        raise FileNotFoundError(f"MeTTa REPL not found at {METTA_REPL}")
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    cmd = [METTA_REPL, script_path]
    
    try:
        result = subprocess.run(cmd, 
                               capture_output=capture_output,
                               text=True,
                               check=True)
        if capture_output:
            return result.stdout
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running MeTTa script: {e}")
        if capture_output:
            print(f"Error output: {e.stderr}")
        return None

def run_metta_query(metta_code):
    """
    Run a MeTTa query directly
    
    Args:
        metta_code: MeTTa code to run
        
    Returns:
        The output of the MeTTa query
    """
    # Create a temporary script file
    temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_script.metta")
    with open(temp_file, "w") as f:
        f.write(metta_code)
        f.write('\n')  # Add newline
    
    try:
        # Try running with echo to pipe the code directly
        cmd = [METTA_REPL, temp_file]
        result = subprocess.run(cmd, 
                               capture_output=True,
                               text=True,
                               timeout=10)  # Add timeout
        
        # Return the stdout, which should contain the MeTTa output
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: MeTTa query timed out"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
        output = run_metta_script(script_path)
        print(output)
    else:
        # Run the example script
        example_script = os.path.join(RULES_DIR, "metta_example.metta")
        output = run_metta_script(example_script)
        print(output)