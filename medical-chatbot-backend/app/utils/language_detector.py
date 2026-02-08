"""Language detection utility for medical chatbot"""
import re


def detect_language(text: str) -> str:
    """
    Detect the primary language of the text.
    
    Args:
        text: The text to analyze
        
    Returns:
        'ar' for Arabic, 'en' for English
    """
    # Count Arabic characters (Unicode range for Arabic)
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
    
    # Count English/Latin characters
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    # Determine dominant language
    if arabic_chars > english_chars:
        return 'ar'
    elif english_chars > 0:
        return 'en'
    else:
        # Default to Arabic if no clear indicators
        return 'ar'


def is_arabic(text: str) -> bool:
    """
    Check if text is primarily in Arabic.
    
    Args:
        text: The text to check
        
    Returns:
        True if text is primarily Arabic, False otherwise
    """
    return detect_language(text) == 'ar'
