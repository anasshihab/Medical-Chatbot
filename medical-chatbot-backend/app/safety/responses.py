"""Emergency response templates"""
from typing import Dict


def get_emergency_response(keyword: str = None, special_cases: Dict[str, bool] = None) -> str:
    """
    Get emergency response template
    
    Args:
        keyword: The emergency keyword detected
        special_cases: Dictionary of special case flags
    
    Returns:
        Emergency response message in Markdown
    """
    special_cases = special_cases or {}
    
    # Base emergency response
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


def get_boundary_reminder() -> str:
    """Get reminder about chatbot boundaries"""
    return """
---

**Important Reminder:**

- I am **NOT a doctor** and cannot provide medical diagnoses
- I cannot recommend specific medications or dosages
- I provide general health information from trusted sources only
- Always consult a licensed healthcare provider for medical decisions

---
"""
