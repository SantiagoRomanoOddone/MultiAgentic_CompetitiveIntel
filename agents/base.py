"""
Shared base configuration for all agents.

All agents use the same Anthropic client and model. Centralizing these here
makes it easy to swap models, add retry logic, or configure timeouts in one place.
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Sonnet 4.6 is a great default for multi-agent systems:
# - Strong reasoning for analysis tasks
# - Fast enough for multi-step pipelines
# - Cost-effective when running 3–5 API calls per report
MODEL = "claude-sonnet-4-6"


def get_client() -> anthropic.Anthropic:
    """
    Create and return a configured Anthropic client.
    Reads ANTHROPIC_API_KEY from the environment (or .env file).
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. "
            "Copy .env.example to .env and add your API key."
        )
    return anthropic.Anthropic(api_key=api_key)
