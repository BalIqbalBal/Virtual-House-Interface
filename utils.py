import subprocess

def execute_command(command):
    try:
        # Run the command with the full path
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.decode()}"
