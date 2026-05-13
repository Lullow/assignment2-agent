# Assignment 2 Agent

A small Python project for building a simple ReAct-style coding agent.

The agent sends a user task to an LLM, parses the response into sections, and can ask for approval before running one suggested shell command.

## Project Structure

```text
assignment2-agent/
├── README.md
├── requirements.txt
├── .env
├── .gitignore
├── .venv/
└── src/
    ├── main.py
    ├── llm_client.py
    ├── react_parser.py
    └── command_runner.py
```

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Environment Variables

Create or update `.env` in the project root:

```bash
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
LLM_MODEL=qwen2.5-14b-instruct
```

For LM Studio, `OPENAI_API_KEY` can be a placeholder value like `lm-studio`.

## Run

From the project root, with the virtual environment activated:

```bash
python src/main.py
```

If your virtual environment is not activated, use:

```bash
.venv/bin/python src/main.py
```
