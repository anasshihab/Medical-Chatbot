"""Content normalization and safety post-processing
يعمل هذا الملف على تنظيف المحتوى الطبي من التشخيصات والأدوية قبل إرساله للمستخدم
"""
import re
from typing import List, Dict


# Patterns to detect and remove/rewrite medication information
MEDICATION_PATTERNS = [
    r'\b\d+\s*mg\b',  # Dosages like "500mg"
    r'\b\d+\s*ml\b',  # Volume like "10ml"
    r'\btake\s+\d+\s+times?\b',  # Frequency
    r'\b(aspirin|ibuprofen|acetaminophen|paracetamol|amoxicillin)\b',  # Common meds (example)
]

# Diagnosis-related phrases to rewrite
DIAGNOSIS_PHRASES = [
    r'\byou\s+(have|may\s+have|might\s+have)\s+\w+',
    r'\bthis\s+is\s+(likely|probably|possibly)\s+\w+',
    r'\bdiagnosed\s+with\b',
    r'\byou\s+(are|seem\s+to\s+be)\s+suffering\s+from\b',
]

# Medical disclaimer (Arabic + English)
MEDICAL_DISCLAIMER = """

⚠️ **تنويه طبي مهم / Medical Disclaimer:**
هذه المعلومات تعليمية فقط ولا تُعتبر تشخيصًا أو وصفة طبية. يُرجى استشارة طبيب مختص.
This information is educational only and is not a diagnosis or prescription. Please consult a qualified healthcare provider.
"""


def normalize_medical_content(content: str, sources: List[Dict] = None) -> str:
    """
    Normalize medical content to remove diagnostic and prescriptive language
    
    Args:
        content: The medical content to normalize
        sources: Optional list of sources that were used
    
    Returns:
        Normalized, educational content with disclaimer
    """
    normalized = content
    
    # 1. Remove or mask medication dosages
    for pattern in MEDICATION_PATTERNS:
        normalized = re.sub(pattern, '[dosage information removed]', normalized, flags=re.IGNORECASE)
    
    # 2. Rewrite diagnostic language to educational language
    normalized = re.sub(
        r'\byou\s+(have|may\s+have|might\s+have)\b',
        'this condition is characterized by',
        normalized,
        flags=re.IGNORECASE
    )
    
    normalized = re.sub(
        r'\bthis\s+is\s+(likely|probably|possibly)\b',
        'these symptoms are commonly associated with',
        normalized,
        flags=re.IGNORECASE
    )
    
    normalized = re.sub(
        r'\bdiagnosed\s+with\b',
        'conditions that may involve',
        normalized,
        flags=re.IGNORECASE
    )
    
    # 3. Replace prescriptive verbs with educational ones
    normalized = re.sub(
        r'\byou\s+should\s+take\b',
        'healthcare providers may recommend',
        normalized,
        flags=re.IGNORECASE
    )
    
    normalized = re.sub(
        r'\btake\s+this\s+medication\b',
        'medications in this category',
        normalized,
        flags=re.IGNORECASE
    )
    
    # 4. Add disclaimer at the end
    normalized += MEDICAL_DISCLAIMER
    
    return normalized


def normalize_search_results(results: List[Dict]) -> List[Dict]:
    """
    Clean search results to remove diagnostic/prescriptive content
    
    Args:
        results: List of search results with title, snippet, url
    
    Returns:
        Normalized results
    """
    normalized_results = []
    
    for result in results:
        normalized_result = result.copy()
        
        # Normalize snippet content
        if 'snippet' in normalized_result:
            normalized_result['snippet'] = normalize_medical_content(
                normalized_result['snippet']
            )
        
        # Normalize title if it contains diagnostic language
        if 'title' in normalized_result:
            title = normalized_result['title']
            title = re.sub(
                r'\bdiagnosis\b',
                'information about',
                title,
                flags=re.IGNORECASE
            )
            normalized_result['title'] = title
        
        normalized_results.append(normalized_result)
    
    return normalized_results


def is_safe_educational_content(content: str) -> bool:
    """
    Check if content is educational rather than diagnostic/prescriptive
    
    Returns:
        True if content is safe educational content
    """
    # Check for concerning phrases
    concerning_patterns = [
        r'\byou\s+(definitely\s+)?have\b',
        r'\bI\s+diagnose\s+you\b',
        r'\btake\s+\d+mg\b',
        r'\bprescribe\b',
    ]
    
    for pattern in concerning_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False
    
    return True
