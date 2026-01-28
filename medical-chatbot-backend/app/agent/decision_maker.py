"""Decision maker for agent actions"""
from typing import Dict, List, Optional
from app.safety.boundaries import (
    is_medical_question,
    check_for_diagnosis_request,
    check_for_medication_request
)


class DecisionMaker:
    """Decides which action the agent should take"""
    
    def decide_action(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """
        Decide what action to take based on user message
        
        Returns:
            {
                "action": "keyword_search" | "symptom_checker" | "ask_followup" | "direct_response",
                "reason": "explanation",
                "params": {} # Parameters for the action
            }
        """
        conversation_history = conversation_history or []
        
        # Check if it's a medical question
        if not is_medical_question(user_message):
            return {
                "action": "direct_response",
                "reason": "Not a medical question",
                "params": {
                    "response": "I'm a medical information assistant. I can only help with medical and health-related questions. How can I assist you with your health concerns?"
                }
            }
        
        # Check for diagnosis request
        if check_for_diagnosis_request(user_message):
            return {
                "action": "direct_response",
                "reason": "Diagnosis request detected - provide boundary reminder",
                "params": {
                    "response": "I cannot provide a diagnosis. However, I can help you understand your symptoms and guide you to appropriate care. Please describe your symptoms, and I'll provide general information."
                }
            }
        
        # Check for medication request
        if check_for_medication_request(user_message):
            return {
                "action": "direct_response",
                "reason": "Medication request detected - provide boundary reminder",
                "params": {
                    "response": "I cannot recommend specific medications or dosages. Only a licensed healthcare provider can prescribe medication. I can provide general information about treatment approaches if that would be helpful."
                }
            }
        
        # Detect if describing symptoms
        symptom_indicators = [
            "i have", "i'm experiencing", "i feel", "my", "pain in",
            "hurts", "aches", "swollen", "rash", "fever", "cough"
        ]
        
        message_lower = user_message.lower()
        is_describing_symptoms = any(ind in message_lower for ind in symptom_indicators)
        
        if is_describing_symptoms:
            # Check if enough information for symptom checker
            if len(user_message.split()) > 5:  # Sufficient detail
                return {
                    "action": "symptom_checker",
                    "reason": "User describing specific symptoms",
                    "params": self._extract_symptoms(user_message)
                }
            else:
                return {
                    "action": "ask_followup",
                    "reason": "Need more details about symptoms",
                    "params": {}
                }
        
        # General medical question - use keyword search
        question_indicators = ["what is", "how does", "why", "can you explain", "tell me about"]
        is_general_question = any(ind in message_lower for ind in question_indicators)
        
        if is_general_question:
            return {
                "action": "keyword_search",
                "reason": "General medical information request",
                "params": {
                    "search_query": user_message
                }
            }
        
        # Default to asking for clarification if uncertain
        if len(conversation_history) == 0:
            return {
                "action": "ask_followup",
                "reason": "First message - need more context",
                "params": {}
            }
        
        # Default to keyword search
        return {
            "action": "keyword_search",
            "reason": "General medical question",
            "params": {
                "search_query": user_message
            }
        }
    
    def _extract_symptoms(self, message: str) -> Dict:
        """
        Extract symptoms from user message
        This is a simplified extraction. In production, use NLP.
        """
        # For MVP, just use the whole message as symptom description
        return {
            "symptoms": [message]
        }
