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
- If ACTION is "none", FINAL must contain a real final answer and must not be "not_done".
- If the user asks for something unsafe or destructive, refuse that part in FINAL instead of using "not_done".
- Use "not_done" only when ACTION is "bash" and you need a command result before answering.
"""

# Set to True when debugging to see the raw LLM responses.
DEBUG = False


def print_agent_step(step, parsed):
    """
    Print one parsed ReAct step in a readable format.

    This makes it easier to follow what the agent is thinking,
    which action it chose, and which command it wants to run.
    """

    print(f"\n--------- STEP {step} ---------")

    print("\nThought:")
    print(parsed.get("thought"))

    print("\nAction:")
    print(parsed.get("action"))

    print("\nCommand:")
    print(parsed.get("command"))


def run_agent_task(user_task):
    """
    Run one full agent task.

    The agent repeatedly asks the model for a ReAct step, optionally executes
    a safe approved command, sends the result back as an observation, and
    continues until it reaches a final answer or max_steps.
    """

    # Create a log file for this run so the agent's behavior can be inspected later.
    log_file = create_log_file()
    write_log(log_file, f"User task:\n{user_task}\n")

    # Start the conversation with the system rules and the user's task.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_task},
    ]

    # Limit the numer of ReAct steps to avoid to many loops and unnecessary API usage.
    max_steps = 5

    for step in range(max_steps):
        # Ask the model what the next ReAct step should be.
        response = call_llm(messages)

        # Optionally print the raw response before parsing.
        if DEBUG:
            print("\n ----- AGENT RESPONSE ------")
            print(response)

        # Convert the models text response into structured fields:
        # thought, action, command, and final.
        parsed = parse_react_response(response)
        print_agent_step(step + 1, parsed)

        # Save this step to the log file.
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

                # Send the blocked-command result back as a observation.
                # This allows the agent to recover instead of crashing or repeating blindly.
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

                # Store the assistants action before adding the command observation.
                messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                # Send the command output back to the model as an observation.
                # This is what gives the agent memory of what happened after the tool ran.
                messages.append(
                    {
                        "role": "user",
                        "content": f"OBSERVATION:\n{observation}",
                    }
                )


            else:
                print("Command denied by user.")
                # Store the assistant's proposed command.
                messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                # Tell the model that the command was denied by the user.
                messages.append(
                    {
                        "role": "user",
                        "content": "OBSERVATION:\nThe command was denied by the user.",
                    }
                )

        elif action == "none":
            print("\nNo bash action requested.")

            if final and final != "not_done":
                print("\n ---- FINAL ANSWER -----")
                print(final)

                write_log(
                    log_file,
                    f"""
                FINAL ANSWER:
                {final}
                """,
                )
                break

            print("Agent returned ACTION none but FINAL was not_done.")
            print("Sending correction back to the model.")

            # Store the invalid assistant response.
            messages.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )

            # Give the model corrective feedback so it can produce a valid final answer.
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "OBSERVATION:\n"
                        "You returned ACTION none, but FINAL was not_done. "
                        "If no more command is needed, provide a real final answer. "
                        "If the requested action is unsafe, refuse it in FINAL."
                    ),
                }
            )

            continue

        else:
            # Stop if the model returned an action that the agent does not support.
            print(f"\nUnknown action: {action}")
            break

    else:
        # This runs only if the loop finishes without hitting break.
        print("\nAgent stopped because max_steps was reached.")


def main():
    """
    Start the terminal interface for the ReAct coding agent.
    """

    print("ReAct Coding Agent")
    print("Type 'quit', 'exit', or 'q' to stop.\n")

    while True:
        # Ask the user for a new task.
        user_task = input("What should the agent do?\n:")

        # Allow the user to exit the program cleanly.
        if user_task.lower().strip() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Do not run the agent if the user entered an empty task.
        if not user_task.strip():
            print("Please enter a task.")
            continue

        # Run the agent on the user's task.
        run_agent_task(user_task)

if __name__ == "__main__":
    # Only start the program when this file is run directly.
    main()
