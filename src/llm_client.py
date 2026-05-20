import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, RateLimitError

# Load enviroment variables from the project root .env file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Allow the model name to be configured from .env.
# MODEL_NAME is supported because some OpenAI-compatible providers use that name
# in their examples, but LLM_MODEL is the project's documented variable.
MODEL = os.getenv("LLM_MODEL") or os.getenv("MODEL_NAME") or "qwen2.5-14b-instruct"

# OpenAI-compatiable client, can point to OpenAI, OpenRouter, LM Studio, etc
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "lm-studio"),
)

# Enable to inspect raw API respones during debugging
DEBUG = False


def call_llm(messages):
    """
    Sends messages to the LLM and returns the assitants text response.

    messages should look like:
    [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ]
    """
    try:
        # Send the current converstion state to the model
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
        )
        
        if DEBUG:
            print("RAW RESPONSE:")
            print(response)

            print("DICT RESPONSE:")

            print(response.model_dump())

        # Return only the assistant message content to the agent loop
        return response.choices[0].message.content

    except RateLimitError:
        return (
            "THOUGHT:\n"
            "The LLM API request failed because the provider reported a rate limit or quota problem.\n\n"
            "ACTION:\n"
            "none\n\n"
            "COMMAND:\n"
            "none\n\n"
            "FINAL:\n"
            "API-anropet misslyckades på grund av rate limit eller saknad quota. "
            "Kontrollera API-nyckel, billing/credits och usage limits hos providern."
        )

    except OpenAIError as e:
        return (
            "THOUGHT:\n"
            "The LLM API request failed before the model could produce a normal ReAct response.\n\n"
            "ACTION:\n"
            "none\n\n"
            "COMMAND:\n"
            "none\n\n"
            "FINAL:\n"
            f"API-anropet misslyckades: {e}"
        )
