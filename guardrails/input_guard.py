from pydantic import BaseModel
from typing import Optional
import re

BLOCKED_PATTERNS = [
    r"ignore previous instructions",
    r"you are now",
    r"jailbreak",
    r"forget your",
]

OFF_TOPIC_KEYWORDS = [
    "recipe", "movie", "sports", "weather forecast",
    "joke", "poem", "dating"
]

class GuardrailResult(BaseModel):
    is_safe: bool
    reason: Optional[str] = None
    sanitized_input: Optional[str] = None

def check_input(user_input: str) -> GuardrailResult:
    # Check prompt injection
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return GuardrailResult(
                is_safe=False,
                reason=f"Prompt injection pattern detected: {pattern}"
            )
    
    # Check off-topic
    lower_input = user_input.lower()
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in lower_input:
            return GuardrailResult(
                is_safe=False,
                reason=f"Off-topic query detected. This system handles supply chain intelligence only."
            )
    
    # Sanitize
    sanitized = user_input.strip()[:2000]  # Limit length
    
    return GuardrailResult(is_safe=True, sanitized_input=sanitized)
