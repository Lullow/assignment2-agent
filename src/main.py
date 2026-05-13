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

  max_steps = 5

  for step in range(max_steps):
    print(f"\n --------- STEP {step + 1} -----------")

    response = call_llm(messages)

    print(f"\n ----- AGENT RESPONSE ------")
    print(response)


    parsed = parse_react_response(response)

    print(f"\n ----- PARSED RESPONSE -----")
    print(parsed)

    final = parsed.get("final")
    action = parsed.get("action")
    command = parsed.get("command")

    if final and final != "not_done":
      print(f"\n ---- FINAL ANSWER ----")
      print(final)
      break

    if action == "bash":
      print(f"\nAgent wants to run command: {command}")
      approve = input("Allow command? y/n: ")

      if approve.lower() == "y":
        result = run_command(command)

        print(f"\n---- COMMAND RESULT -----")
        print(result)

        observation = f"""
Command: {command}
Return code: {result["return_code"]}
STDOUT:
{result["stdout"]}

STDERR:
{result["stderr"]}

Timed out: {result["timed_out"]}
"""
        messages.append({
          "role": "assistant",
          "content": response,
        })

        messages.append({
          "role": "user",
          "content": f"OBSERVATION:\n{observation}",
        })

      else:
        print("Command denied by user.")

        messages.append({
          "role": "assistant",
          "content": response,
        })

        messages.append({
          "role": "user",
          "content": f"OBSERVATION:\nThe command was denied by the user."
        })

    elif action == "none":
      print(f"\nNo bash action requested.")

      if final:
        print(f"\n ---- FINAL ANSWER -----")
        print(final)
        break

    else:
      print(f"\nUnknown action: {action}")
      break

  else:
    print(f"\nAgent stopped because max_steps was reached.")


if __name__ == "__main__":
  main()

