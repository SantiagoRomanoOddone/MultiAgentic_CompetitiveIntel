import os

from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient

load_dotenv()


def get_client() -> AzureOpenAIChatClient:
    return AzureOpenAIChatClient(
        endpoint=os.getenv("OPEN_AI_ENDPOINT"),
        api_key=os.getenv("OPEN_AI_KEY"),
        deployment_name=os.getenv("CHAT_MODEL"),
        api_version="2024-12-01-preview",
    )
