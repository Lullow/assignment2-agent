from command_runner import run_command
from llm_client import call_llm
from logger import create_log_file, write_log
from react_parser import parse_react_response
from safety import is_command_safe

# Defines the ReAct format that the model must follow.
# The parser depends on these exact section names.
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
- The ACTION field must only contain "bash" or "none".
- The COMMAND field must contain the actual command, not the ACTION field.
- Do not write NOT_DONE outside of the FINAL field.
"""

# Set to True when debugging to see the raw LLM responses.
DEBUG = False


# Prints one parsed ReAct step in readable format for the terminal.
def print_agent_step(step, parsed):
    print(f"\n--------- STEP {step} ---------")

    print("\nThought:")
    print(parsed.get("thought"))

    print("\nAction:")
    print(parsed.get("action"))

    print("\nCommand:")
    print(parsed.get("command"))


def main():
    user_task = input("What should the agent do?\n:")

    # Create a seperate log file for this agent run.
    log_file = create_log_file()
    write_log(log_file, f"User task:\n{user_task}\n")

    # The messages list acts as the agents short-term memory during this run.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_task},
    ]

    # Limit the numer of ReAct steps to avoid to many loops and unnecessary API usage.
    max_steps = 5

    for step in range(max_steps):
        # Ask the model what the next ReAct step should be.
        response = call_llm(messages)

        if DEBUG:
            print("\n ----- AGENT RESPONSE ------")
            print(response)

        # Convert the models text response into structured fields.
        parsed = parse_react_response(response)
        print_agent_step(step + 1, parsed)

        write_log(
            log_file,
            f"""
          STEP {step + 1}

          Thought:
          {parsed.get("thought")}

          Action:
          {parsed.get("action")}

          Command:
          {parsed.get("command")}

          Final:
          {parsed.get("final")}
          """,
        )

        final = parsed.get("final")
        action = parsed.get("action")
        command = parsed.get("command")

        # if FINAL contains a real answer, the agent is done.
        if final and final != "not_done":
            print("\n ---- FINAL ANSWER ----")
            print(final)

            write_log(
                log_file,
                f"""
            FINAL ANSWER:
            {final}
            """,
            )
            break

        # Only bash actions are allowed to request command excecution.
        if action == "bash":
            print(f"\nAgent wants to run command: {command}")

            # Check command safety before asking the user for approval.
            safety_result = is_command_safe(command)

            write_log(
                log_file,
                f"""
            Safety check:
            Safe: {safety_result["safe"]}
            Reason: {safety_result["reason"]}
              """,
            )

            if not safety_result["safe"]:
                print("\n----- COMMAND BLOCKED ----")
                print(safety_result["reason"])

                # Stores the assistants response so the model can see what it prevciously suggested
                messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                # Send the blocked-command result back as a observation so the agent can recover.
                messages.append(
                    {
                        "role": "user",
                        "content": f"OBSERVATION:\nThe command was blocked for safety reasons: {safety_result['reason']}",
                    }
                )

                continue

            # Human approval is required even after the automatic safety check passes.
            approve = input("Allow command? y/n: ")

            if approve.lower() == "y":
                # Execute the approved command and capture stdout, sterr and return code.
                result = run_command(command)

                print("\nObservation:")

                if result["stdout"]:
                    print(result["stdout"])

                if result["stderr"]:
                    print("\nErrors:")
                    print(result["stderr"])

                print(f"\nReturn code: {result['return_code']}")
                print(f"Timed out: {result['timed_out']}")

                # Format the command result as a observation for the next LLM step.
                observation = f"""
Command: {command}
Working directory: project root
Return code: {result["return_code"]}

STDOUT:
{result["stdout"]}

STDERR:
{result["stderr"]}

Timed out: {result["timed_out"]}
"""

                write_log(
                    log_file,
                    f"""
                Observation:
                {observation}
                """,
                )

                # Store the assistants action before adding the command observation
                messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                # Send the command output back to the model as an observation
                messages.append(
                    {
                        "role": "user",
                        "content": f"OBSERVATION:\n{observation}",
                    }
                )

            # Tell the model that the command was denied by the user.
            else:
                print("Command denied by user.")

                messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                messages.append(
                    {
                        "role": "user",
                        "content": "OBSERVATION:\nThe command was denied by the user.",
                    }
                )

        elif action == "none":
            print("\nNo bash action requested.")

            if final:
                print("\n ---- FINAL ANSWER -----")
                print(final)
                break

        else:
            print(f"\nUnknown action: {action}")
            break

    else:
        print("\nAgent stopped because max_steps was reached.")


if __name__ == "__main__":
    main()
