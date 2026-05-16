import subprocess
import shlex
from pathlib import Path

# REsolve the project root so commands always run from the same folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_command(command, timeout=5):
    """
    Runs a shell-like command safely without shell=True.

    Example:
    command = "ls -la"

    Returns a dictionary with:
    - stdout
    - stderr
    - return_code
    - timed_out
    """


    try:
      # Split the command into arguments insted of passing one raw string to subprocess.
      args = shlex.split(command)

      # Run without shell=True to reduce the risk of shell injection and command chaining
      result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=PROJECT_ROOT # Always execute from the project root
      )

      return {
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "return_code": result.returncode,
        "timed_out": False,
      }

    # Stop commands that run for to long
    except subprocess.TimeoutExpired:
      return {
        "stdout": "",
        "stderr": f"Command timed out after {timeout} seconds.",
        "return_code": None,
        "timed_out": True,
      }

    except FileNotFoundError:
      return {
        "stdout": "",
        "stderr": "Command not found.",
        "return_code": None,
        "timed_out": False,
      }

    except Exception as e:
      return {
        "stdout": "",
        "stderr": f"Unexpected error: {e}.",
        "return_code": None,
        "timed_out": False,
      }

# Small manual test when running this file directly
if __name__ == "__main__":
  output = run_command("ls")
  print(output)