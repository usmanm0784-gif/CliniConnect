import re

def sanitize_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^a-zA-Z\s'-]", "", value)
    return value.title()

def sanitize_string(value: str) -> str:
    """General-purpose cleanup: whitespace only, no char restrictions."""
    return re.sub(r"\s+", " ", value.strip())