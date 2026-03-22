import re


def extract_text(response) -> str:
    """Extract text content from an agent response, handling different response shapes."""
    text = ""

    for attr in ("text", "content", "message", "output"):
        val = getattr(response, attr, None)
        if val and isinstance(val, str):
            text = val
            break

    if not text:
        text = str(response).strip()

    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text.strip())

    return text.strip()
