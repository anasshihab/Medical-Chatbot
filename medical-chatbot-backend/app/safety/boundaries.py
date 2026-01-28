"""Medical boundary enforcement"""


def is_medical_question(message: str) -> bool:
    """
    Determine if the question is medical-related
    
    This is a basic implementation. In production, you might want to use
    a more sophisticated ML-based classifier.
    """
    # Medical-related keywords
    medical_keywords = [
        "symptom", "pain", "hurt", "sick", "disease", "condition", "doctor",
        "health", "medical", "treatment", "diagnose", "medicine", "hospital",
        "injury", "bleeding", "fever", "cough", "headache", "infection",
        "pregnant", "pregnancy", "baby", "child", "allergy", "rash",
        "vitamin", "nutrition", "diet", "exercise", "sleep", "stress",
        "anxiety", "depression", "mental health", "weight", "blood pressure",
        "diabetes", "cancer", "heart", "lung", "kidney", "liver", "stomach"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in medical_keywords)


def check_for_diagnosis_request(message: str) -> bool:
    """Check if user is requesting a diagnosis"""
    diagnosis_keywords = [
        "what do i have", "do i have", "am i sick",
        "what's wrong with me", "diagnose me", "what disease"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in diagnosis_keywords)


def check_for_medication_request(message: str) -> bool:
    """Check if user is requesting medication advice"""
    medication_keywords = [
        "what medication", "what medicine", "what drug",
        "what should i take", "recommend medication",
        "prescribe", "dosage", "how much should i take"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in medication_keywords)
