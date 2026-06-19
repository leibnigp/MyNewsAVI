import os
import anthropic
from config import ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_MODEL

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not ANTHROPIC_AUTH_TOKEN:
            raise RuntimeError("ANTHROPIC_AUTH_TOKEN is not configured")
        _client = anthropic.Anthropic(
            base_url=ANTHROPIC_BASE_URL,
            api_key=ANTHROPIC_AUTH_TOKEN,
            timeout=120.0,
        )
    return _client


def get_model() -> str:
    return os.getenv("ANTHROPIC_MODEL", ANTHROPIC_MODEL)
