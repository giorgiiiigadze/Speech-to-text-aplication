import re

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

def sanitize_text(text: str) -> str:
    text = CONTROL_CHARS.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text