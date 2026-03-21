"""
Shared base configuration for all agents.
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("CHAT_MODEL")


def get_client() -> AzureOpenAI:
    endpoint = os.getenv("OPEN_AI_ENDPOINT")
    api_key = os.getenv("OPEN_AI_KEY")
    if not endpoint or not api_key or not MODEL:
        raise ValueError("Missing OPEN_AI_ENDPOINT / OPEN_AI_KEY / CHAT_MODEL in .env")
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-12-01-preview",
    )
