import subprocess
import shlex

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
      args = shlex.split(command)

      result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
      )

      return {
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "return_code": result.returncode,
        "timed_out": False,
      }

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
        "stderr": f"Command not found.",
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

if __name__ == "__main__":
  output = run_command("ls")
  print(output)