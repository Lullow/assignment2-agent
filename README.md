# Assignment 2: ReAct Coding Agent

This project is a simple Python-based ReAct coding agent built for Assignment 2.

The agent can receive a task from the user, ask an LLM what to do next, parse the model response, run approved bash commands, and send the result back to the model as an observation. The loop continues until the model returns a final answer.

The agent logic is built manually in Python. It does not use Cursor, Claude Code, Codex, OpenCode, KiloCode, or built-in function calling as part of the agent loop.

## Features

- ReAct-style reasoning loop
- Custom text-based action parsing
- Bash command execution with `subprocess.run`
- Safety checks before command execution
- Manual user approval before running commands
- Command timeout handling
- Run logs saved to `logs/`
- OpenAI-compatible LLM client

## How The Agent Works

The basic flow is:

```text
User task
  -> LLM response
  -> Parse THOUGHT / ACTION / COMMAND / FINAL
  -> Safety check
  -> User approval
  -> Run command
  -> Send observation back to the LLM
  -> Repeat until FINAL
```

The model is instructed to respond using this format:

```text
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
```

## Project Structure

```text
assignment2-agent/
├── README.md
├── requirements.txt
├── .env
├── .gitignore
├── logs/
└── src/
    ├── main.py
    ├── llm_client.py
    ├── react_parser.py
    ├── command_runner.py
    ├── safety.py
    └── logger.py
```

## File Responsibilities

| File | Responsibility |
| --- | --- |
| `main.py` | Main agent loop and control flow |
| `llm_client.py` | Sends messages to the LLM and returns the response |
| `react_parser.py` | Parses the ReAct response into structured fields |
| `command_runner.py` | Runs approved bash commands |
| `safety.py` | Checks whether a command is safe before execution |
| `logger.py` | Saves each agent run to a log file |

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
LLM_MODEL=qwen2.5-14b-instruct
```

The project uses an OpenAI-compatible client, so it can work with providers such as LM Studio, OpenRouter, local OpenAI-compatible servers, or similar setups.

## Running The Agent

From the project root:

```bash
python3 src/main.py
```

You can also run it from inside `src/`:

```bash
python3 main.py
```

Commands are still executed from the project root because `command_runner.py` sets the working directory explicitly.

## Example Run

User task:

```text
List the files in the project folder
```

Example model response:

```text
THOUGHT:
To list the files in the project folder, I need to use an appropriate bash command.

ACTION:
bash

COMMAND:
ls -l

FINAL:
not_done
```

The response is parsed into structured data:

```json
{
  "thought": "To list the files in the project folder, I need to use an appropriate bash command.",
  "action": "bash",
  "command": "ls -l",
  "final": "not_done"
}
```

After the command runs, the result is sent back to the model as an observation:

```text
Command: ls -l
Working directory: project root
Return code: 0

STDOUT:
README.md
requirements.txt
src

STDERR:

Timed out: False
```

When the model has enough information, it returns a final answer:

```text
ACTION:
none

COMMAND:
none

FINAL:
The files in the project folder are README.md, requirements.txt and src.
```

## Safety Features

The agent includes several safety features:

- Max step limit to avoid infinite loops
- Timeout for bash commands
- No `shell=True`
- Blocked dangerous commands
- Blocked dangerous command patterns
- Blocked shell operators
- Manual user confirmation before execution
- Project-root working directory
- Logging of agent runs

Examples of blocked commands and patterns include:

```text
rm
sudo
shutdown
reboot
mkfs
dd
chmod
chown
curl
wget
ssh
scp
rm -rf
curl | bash
wget | bash
/dev/sda
/dev/nvme
```

Examples of blocked shell operators include:

```text
;
&&
||
|
>
>>
<
$(
`
```

If a command is blocked, it is not executed. Instead, the blocked result is sent back to the model as an observation so the agent can try a safer approach.

## Logging

Each agent run is saved as a log file inside:

```text
logs/
```

The log includes:

- User task
- Agent step number
- Thought
- Action
- Command
- Safety result
- User approval
- Observation
- Final answer

Generated log files should normally not be committed to Git. The project ignores `logs/` in `.gitignore`.

## Limitations

This is a learning-focused project and not a production-ready coding assistant.

Current limitations:

- The parser depends on the model following the exact ReAct format.
- The safety system is based on blocklists and patterns.
- Blocklists cannot catch every possible dangerous command.
- Some safe commands may be blocked because the safety rules are intentionally strict.
- The agent currently only supports `bash` and `none` actions.
- Command execution still requires careful human review.

## Summary

This project demonstrates the core mechanics of a ReAct-style coding agent:

```text
reason -> act -> observe -> reason again
```

The most important part is that the agent loop is built manually in Python. The model only outputs structured text, and the Python code parses that text, checks safety, executes approved commands, and returns observations back to the model.