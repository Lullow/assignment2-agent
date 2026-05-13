from llm_client import call_llm
from react_parser import parse_react_response
from command_runner import run_command

SYSTEM_PROMPT = """
You are a simple ReAct-style coding agent.

You must always respond in this exact format:

THOUGHT:
Explain what you need to do next.

ACTION:
Either "none" or "bash".

COMMAND:
If ACTION is "bash", write the bash command.
If ACTION is "none", write "none".

FINAL:
If the task is complete, write the final answer.
If the task is not complete yet, write "not_done".

Important rules:
- Do not execute anything yourself.
- Only suggest one command at a time.
- Do not use destructive commands.
"""


def main():
  user_task = input(f"What should the agent do?\n:")

  messages = [
      {"role": "system", "content": SYSTEM_PROMPT},
      {"role": "user", "content": user_task},
  ]

  response = call_llm(messages)

  print(f"\n --- AGENT RESPONSE ---")
  print(response)

  parsed = parse_react_response(response)

  print(f"\n --- PARSED RESPONSE ---")
  print(parsed)

  if parsed["action"] == "bash":
    command = parsed["command"]

    print(f"\nAgent wants to run command: {command}")
    approve = input("Allow command? y/n: ")

    if approve.lower() == "y":
      result = run_command(command)

      print(f"\n --- COMMAND RESULT ---")
      print(result)

    else:
      print("Command denied by user.")
  else:
    print("No bash action requested.")



if __name__ == "__main__":
  main()

