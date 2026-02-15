"""
Test script to demonstrate language detection and adaptive responses
"""
from app.utils.language_detector import detect_language, is_arabic


# Test cases
test_messages = [
    "ما هو مرض السكري؟",
    "What is diabetes?",
    "أعاني من صداع شديد",
    "I have a severe headache",
    "كيف أعالج الحمى؟",
    "How to treat fever?",
    "أحتاج معلومات عن الضغط",
    "I need information about blood pressure",
    "عندي ألم في المعدة",
    "I have stomach pain",
]


def test_language_detection():
    """Test the language detection on various messages"""
    print("=" * 60)
    print("Testing Language Detection")
    print("=" * 60)
    
    for msg in test_messages:
        lang = detect_language(msg)
        is_ar = is_arabic(msg)
        lang_name = "Arabic (العربية)" if lang == 'ar' else "English"
        
        print(f"\nMessage: {msg}")
        print(f"Detected Language: {lang_name}")
        print(f"Is Arabic: {is_ar}")
        print("-" * 60)


if __name__ == "__main__":
    test_language_detection()
