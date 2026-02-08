"""Emergency response templates"""
from typing import Dict
from app.utils.language_detector import detect_language


def get_emergency_response(keyword: str = None, special_cases: Dict[str, bool] = None, user_message: str = "") -> str:
    """
    Get emergency response template
    
    Args:
        keyword: The emergency keyword detected
        special_cases: Dictionary of special case flags
        user_message: The user's original message to detect language
    
    Returns:
        Emergency response message in Markdown (in user's language)
    """
    special_cases = special_cases or {}
    
    # Detect language from user message
    lang = detect_language(user_message) if user_message else 'ar'
    
    if lang == 'ar':
        # Arabic emergency response
        response = """# ⚠️ تم الكشف عن حالة طبية طارئة

**يبدو أن هذه حالة طبية طارئة. يرجى اتخاذ إجراء فوري:**

## ماذا تفعل الآن:

1. **اتصل بخدمات الطوارئ فورًا:**
   - 🚨 **اتصل بـ 911** (الولايات المتحدة) أو رقم الطوارئ المحلي
   - 📞 **اتصل بخط الطوارئ المحلي الخاص بك**

2. **لا تنتظر النصيحة عبر الإنترنت**

3. **إذا لم تتمكن من الاتصال، اطلب من شخص قريب المساعدة**

4. **ابق هادئًا واتبع تعليمات مرسل الطوارئ**

---

## مهم:

⚠️ **أنا مساعد ذكاء اصطناعي، ولست طبيبًا أو خدمة طوارئ.**

⚠️ **لا يمكنني استبدال الرعاية الطبية الطارئة.**

⚠️ **قد تكون حياتك في خطر - اطلب المساعدة المهنية الفورية.**

---
"""
        
        # Add special warnings for children
        if special_cases.get("children"):
            response += """
### 👶 عاجل جدًا - طوارئ طفل

**الأطفال يحتاجون إلى عناية طبية فورية. لا تتأخر!**

اتصل بخدمات الطوارئ الآن وأخبرهم بوضوح أن الأمر يتعلق بطفل.

---
"""
        
        # Add special warnings for pregnancy
        if special_cases.get("pregnancy"):
            response += """
### 🤰 طوارئ حمل

**حالات الطوارئ المتعلقة بالحمل تتطلب عناية طبية فورية.**

اتصل بخدمات الطوارئ الآن وأخبرهم بوضوح أنك حامل.

---
"""
        
        response += """
**بعد أن تكون قد اتصلت طلبًا للمساعدة**، إذا كنت لا تزال بحاجة إلى معلومات أثناء الانتظار، يمكنني محاولة تقديم إرشادات عامة - ولكن **فقط بعد الاتصال بخدمات الطوارئ.**

يرجى تأكيد أنك اتصلت بخدمات الطوارئ قبل أن نستمر.
"""
    
    else:
        # English emergency response
        response = """# ⚠️ MEDICAL EMERGENCY DETECTED

**This appears to be a medical emergency. Please take immediate action:**

## WHAT TO DO NOW:

1. **Call emergency services immediately:**
   - 🚨 **Call 911** (US) or your local emergency number
   - 📞 **Call your local emergency hotline**

2. **Do NOT wait for online advice**

3. **If you cannot call, ask someone nearby to help**

4. **Stay calm and follow emergency dispatcher instructions**

---

## Important:

⚠️ **I am an AI assistant, NOT a doctor or emergency service.**

⚠️ **I CANNOT replace emergency medical care.**

⚠️ **Your life may be in danger - seek immediate professional help.**

---
"""
        
        # Add special warnings for children
        if special_cases.get("children"):
            response += """
### 👶 EXTRA URGENT - CHILD EMERGENCY

**Children require IMMEDIATE medical attention. Do not delay!**

Call emergency services NOW and clearly state this is about a child.

---
"""
        
        # Add special warnings for pregnancy
        if special_cases.get("pregnancy"):
            response += """
### 🤰 PREGNANCY EMERGENCY

**Pregnancy-related emergencies require IMMEDIATE medical attention.**

Call emergency services NOW and clearly state you are pregnant.

---
"""
        
        response += """
**After you have called for help**, if you still need information while waiting, I can try to provide general guidance - but **ONLY after emergency services have been contacted.**

Please confirm you have called emergency services before we continue.
"""
    
    return response


def get_boundary_reminder(lang: str = 'en') -> str:
    """
    Get reminder about chatbot boundaries
    
    Args:
        lang: Language code ('ar' for Arabic, 'en' for English)
        
    Returns:
        Boundary reminder in the specified language
    """
    if lang == 'ar':
        return """
---

**تذكير مهم:**

- أنا **لست طبيبًا** ولا يمكنني تقديم تشخيصات طبية
- لا يمكنني التوصية بأدوية محددة أو جرعات
- أقدم معلومات صحية عامة من مصادر موثوقة فقط
- استشر دائمًا مقدم رعاية صحية مرخص للقرارات الطبية

---
"""
    else:
        return """
---

**Important Reminder:**

- I am **NOT a doctor** and cannot provide medical diagnoses
- I cannot recommend specific medications or dosages
- I provide general health information from trusted sources only
- Always consult a licensed healthcare provider for medical decisions

---
"""
