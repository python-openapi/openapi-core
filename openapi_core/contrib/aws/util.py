from typing import Dict


def parse_forwarded(header: str) -> Dict[str, str]:
    parts = {}
    for part in header.split(";"):
        k, v = part.split("=")
        parts[k] = v
    return parts
