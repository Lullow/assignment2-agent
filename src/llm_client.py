from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = os.getenv("LLM_MODEL", "qwen2.5-14b-instruct")

client = OpenAI(
  base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1"),
  api_key=os.getenv("OPENAI_API_KEY", "lm-studio"),
)


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
    response = client.chat.completions.create(
      model=MODEL,
      messages=messages,
      temperature=0.2,
    )

    print("RAW RESPONSE:")
    print(response)

    print("DICT RESPONSE:")

    print(response.model_dump())

    return response.choices[0].message.content


  except RateLimitError:
      return (
          "API-anropet misslyckades eftersom OpenAI-kontot saknar tillgänglig quota. "
          "Kontrollera billing, usage limits eller credits i OpenAI dashboard."
      )