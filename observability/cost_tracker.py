import tiktoken

COST_PER_1K_TOKENS = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "text-embedding-3-small": {"input": 0.00002, "output": 0}
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = COST_PER_1K_TOKENS.get(model, {"input": 0, "output": 0})
    cost = (input_tokens / 1000 * rates["input"]) + \
           (output_tokens / 1000 * rates["output"])
    return round(cost, 6)

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        # Fallback character length approximation if tiktoken encoding fails
        return len(text) // 4
