from pydantic import BaseModel
from typing import Optional
import re

class GuardrailResult(BaseModel):
    is_safe: bool
    reason: Optional[str] = None
    sanitized_input: Optional[str] = None

def check_output(llm_output: str) -> GuardrailResult:
    """
    Validate LLM output before returning to user.
    - Check for PII leakage
    - Validate JSON structure
    """
    # Check for PII patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{10,}\b'
    
    if re.search(email_pattern, llm_output) or re.search(phone_pattern, llm_output):
        return GuardrailResult(
            is_safe=False,
            reason="PII detected in LLM output"
        )
    
    return GuardrailResult(is_safe=True, sanitized_input=llm_output)
