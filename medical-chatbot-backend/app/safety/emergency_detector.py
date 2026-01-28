"""Emergency detection and classification"""
from typing import Dict, Optional
from app.utils.constants import EMERGENCY_KEYWORDS, SPECIAL_CASE_KEYWORDS


def detect_emergency(message: str) -> Optional[str]:
    """
    Detect emergency keywords in user message
    
    Returns:
        Emergency keyword if found, None otherwise
    """
    message_lower = message.lower()
    
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in message_lower:
            return keyword
    
    return None


def is_emergency(message: str) -> bool:
    """Check if message contains emergency keywords"""
    return detect_emergency(message) is not None


def detect_special_cases(message: str) -> Dict[str, bool]:
    """
    Detect special case keywords (children, pregnancy)
    
    Returns:
        Dictionary with special case flags
    """
    message_lower = message.lower()
    special_cases = {}
    
    for case_name, keywords in SPECIAL_CASE_KEYWORDS.items():
        special_cases[case_name] = any(kw in message_lower for kw in keywords)
    
    return special_cases
