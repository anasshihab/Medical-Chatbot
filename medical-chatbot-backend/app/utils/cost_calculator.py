"""Utility for calculating AI costs based on token usage"""
import logging

logger = logging.getLogger(__name__)

# Official OpenAI Pricing (as of February 2024)
# All prices are per 1 MILLION tokens, converted to per-token cost
# Source: https://openai.com/pricing

PRICING = {
    # CRITICAL: "gpt-4o-mini" MUST come before "gpt-4o" due to startswith() matching logic!
    # If "gpt-4o" is first, "gpt-4o-mini" will incorrectly match to expensive gpt-4o rates.
    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,   # $0.15 per 1M input tokens
        "output": 0.60 / 1_000_000   # $0.60 per 1M output tokens
    },
    "gpt-4o": {
        "input": 2.50 / 1_000_000,   # $2.50 per 1M input tokens
        "output": 10.00 / 1_000_000  # $10.00 per 1M output tokens
    },
    "gpt-4-turbo": {
        "input": 10.00 / 1_000_000,  # $10.00 per 1M input tokens
        "output": 30.00 / 1_000_000  # $30.00 per 1M output tokens
    },
    "gpt-4-turbo-preview": {
        "input": 10.00 / 1_000_000,  # $10.00 per 1M input tokens
        "output": 30.00 / 1_000_000  # $30.00 per 1M output tokens
    },
    "gpt-3.5-turbo": {
        "input": 0.50 / 1_000_000,   # $0.50 per 1M input tokens
        "output": 1.50 / 1_000_000   # $1.50 per 1M output tokens
    }
}

# Default fallback pricing (gpt-4-turbo rates)
DEFAULT_PRICING = {
    "input": 10.00 / 1_000_000,
    "output": 30.00 / 1_000_000
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the cost of an OpenAI API call in dollars.
    
    Args:
        model: The model name (e.g., "gpt-4o-mini", "gpt-4o")
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens generated
    
    Returns:
        Total cost in USD as a float
    """
    # Find pricing for the model (exact match or prefix)
    model_pricing = None
    for m in PRICING:
        if model.startswith(m):
            model_pricing = PRICING[m]
            break
    
    if not model_pricing:
        logger.warning(f"No pricing found for model '{model}', using default pricing")
        model_pricing = DEFAULT_PRICING
        
    # Calculate total cost
    input_cost = input_tokens * model_pricing["input"]
    output_cost = output_tokens * model_pricing["output"]
    total_cost = input_cost + output_cost
    
    return total_cost

def log_ai_cost(model: str, input_tokens: int, output_tokens: int, context: str = ""):
    """
    Calculate and log AI cost to terminal with detailed breakdown.
    
    Args:
        model: The model name used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        context: Optional context string (e.g., "Agent Initial", "Decision Maker")
    
    Returns:
        Total cost in USD
    """
    cost = calculate_cost(model, input_tokens, output_tokens)
    total_tokens = input_tokens + output_tokens
    
    # Format cost display based on magnitude
    if cost < 0.000001:  # Less than $0.000001 (extremely small)
        cost_str = f"${cost:.9f}"
    elif cost < 0.001:   # Less than $0.001
        cost_str = f"${cost:.6f}"
    else:                # $0.001 or more
        cost_str = f"${cost:.4f}"
    
    context_str = f" [{context}]" if context else ""
    log_msg = (
        f"💰 AI COST{context_str}: {cost_str} | "
        f"Model: {model} | "
        f"Tokens: {total_tokens:,} (Input: {input_tokens:,}, Output: {output_tokens:,})"
    )
    
    # Print directly to terminal for high visibility
    print(f"\n{log_msg}\n", flush=True)
    logger.info(log_msg)
    
    return cost

def get_model_pricing_info(model: str) -> dict:
    """
    Get pricing information for a specific model.
    
    Args:
        model: The model name
    
    Returns:
        Dictionary with input and output pricing per 1M tokens
    """
    for m in PRICING:
        if model.startswith(m):
            pricing = PRICING[m]
            return {
                "model": m,
                "input_per_1m": pricing["input"] * 1_000_000,
                "output_per_1m": pricing["output"] * 1_000_000,
                "input_per_token": pricing["input"],
                "output_per_token": pricing["output"]
            }
    
    return {
        "model": "unknown",
        "input_per_1m": DEFAULT_PRICING["input"] * 1_000_000,
        "output_per_1m": DEFAULT_PRICING["output"] * 1_000_000,
        "input_per_token": DEFAULT_PRICING["input"],
        "output_per_token": DEFAULT_PRICING["output"]
    }
