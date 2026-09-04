import re

BLOCKED_PATTERNS = [
    r"system prompt",
    r"system message",
    r"api[_-]?key",
    r"secret[_-]?key",
    r"password",
    r"database password",
    r"credentials"
]

def check_output_security(content:str):
    if not content:
        return False,"Empty response"
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern,content,re.IGNORECASE):
            return False,"Sensitive information detected"

    return True,None