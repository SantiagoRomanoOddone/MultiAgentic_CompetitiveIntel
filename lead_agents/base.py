import os

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled

load_dotenv()

MODEL = os.getenv("CHAT_MODEL", "")

_client = AsyncAzureOpenAI(
    azure_endpoint=os.getenv("OPEN_AI_ENDPOINT", ""),
    api_key=os.getenv("OPEN_AI_KEY", ""),
    api_version="2024-12-01-preview",
)

set_default_openai_client(_client)
set_default_openai_api("chat_completions")
set_tracing_disabled(True)
