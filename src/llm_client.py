import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

# Load enviroment variables from the project root .env file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Allow the model name to be configured from .env
MODEL = os.getenv("LLM_MODEL", "qwen2.5-14b-instruct")

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
            "API-anropet misslyckades eftersom OpenAI-kontot saknar tillgänglig quota. "
            "Kontrollera billing, usage limits eller credits i OpenAI dashboard."
        )
