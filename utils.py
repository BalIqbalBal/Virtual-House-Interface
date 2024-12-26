import subprocess
import time

# Shared dictionary to store task statuses (for demonstration)
cmd_status = {}

import subprocess

def execute_command_in_background(cmd, task_id):
    """Function to execute the command in the background and update the status."""
    try:
        # Initialize the task status if it doesn't exist
        if task_id not in cmd_status:
            cmd_status[task_id] = {'status': 'pending', 'output': []}

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        output_lines = []
        
        # Capture stdout and update status
        for line in process.stdout:
            output_lines.append(line.strip())
            cmd_status[task_id] = {'status': 'running', 'output': output_lines}

        # Capture stderr and update status if there's an error
        for line in process.stderr:
            output_lines.append(line.strip())
            cmd_status[task_id] = {'status': 'error', 'output': output_lines}

        process.wait()  # Wait for the process to finish

        # Mark task as complete
        cmd_status[task_id] = {'status': 'complete', 'output': output_lines}

    except Exception as e:
        # Handle any exception and mark the task as error
        cmd_status[task_id] = {'status': 'error', 'output': [str(e)]}


def get_cmd_status(task_id):
    """Return the status of a command/task."""
    return cmd_status.get(task_id, {'status': 'not_found', 'output': []})

def set_cmd_status(task_id, status, output):
    """Update the status of a command/task."""
    cmd_status[task_id] = {'status': status, 'output': output}
    
def execute_command(command):
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Return a generator that yields output lines
        for line in iter(process.stdout.readline, ''):
            yield line.strip()
            
        # Get the return code after process completes
        process.stdout.close()
        return_code = process.wait()
        
        if return_code != 0:
            yield f"Process exited with code {return_code}"
            
    except Exception as e:
        yield f"Error executing command: {str(e)}"
