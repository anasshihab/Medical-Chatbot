"""Utility for calculating AI costs based on token usage"""
import logging

logger = logging.getLogger(__name__)

# Current OpenAI Pricing (per 1k tokens)
# Note: Pricing can change, these are estimates for gpt-4o, gpt-4-turbo, and gpt-3.5-turbo
PRICING = {
    "gpt-4o": {
        "input": 0.005 / 1000,
        "output": 0.015 / 1000
    },
    "gpt-4o-mini": {
        "input": 0.00015 / 1000,
        "output": 0.0006 / 1000
    },
    "gpt-4-turbo": {
        "input": 0.01 / 1000,
        "output": 0.03 / 1000
    },
    "gpt-4-turbo-preview": {
        "input": 0.01 / 1000,
        "output": 0.03 / 1000
    },
    "gpt-3.5-turbo": {
        "input": 0.0005 / 1000,
        "output": 0.0015 / 1000
    }
}

DEFAULT_PRICING = {
    "input": 0.01 / 1000,
    "output": 0.03 / 1000
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the cost of an OpenAI call in dollars
    """
    # Find pricing for the model (exact match or prefix)
    model_pricing = None
    for m in PRICING:
        if model.startswith(m):
            model_pricing = PRICING[m]
            break
    
    if not model_pricing:
        model_pricing = DEFAULT_PRICING
        
    cost = (input_tokens * model_pricing["input"]) + (output_tokens * model_pricing["output"])
    return cost

def log_ai_cost(model: str, input_tokens: int, output_tokens: int, context: str = ""):
    """
    Calculate and log AI cost to terminal
    """
    cost = calculate_cost(model, input_tokens, output_tokens)
    total_tokens = input_tokens + output_tokens
    
    context_str = f" [{context}]" if context else ""
    log_msg = f"💰 AI COST{context_str}: ${cost:.6f} | Model: {model} | Tokens: {total_tokens} (I: {input_tokens}, O: {output_tokens})"
    
    # Print directly to terminal for high visibility (using logger.info as well)
    print(f"\n{log_msg}\n")
    logger.info(log_msg)
    
    return cost
