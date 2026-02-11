"""Decision maker for agent actions"""
from typing import Dict, List, Optional
import json
import logging
from app.utils.cost_calculator import log_ai_cost
from openai import AsyncOpenAI
from app.config import settings


logger = logging.getLogger(__name__)

class DecisionMaker:
    """Decides which action the agent should take using LLM"""
    
    def __init__(self):
        # Initialize OpenAI client with key from settings
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def decide_action(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """
        Decide what action to take based on user message using LLM.
        Returns intent classification: requires_tools (medical query) or direct_answer (greeting/simple chat)
        """
        conversation_history = conversation_history or []
        
        # Convert history to string for prompt
        history_str = ""
        for msg in conversation_history[-10:]: # Last 10 messages for context
            history_str += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
        
        # Enhanced prompt for gatekeeper pattern
        prompt = f"""You are a decision maker for a medical AI chatbot. Analyze the user's message and determine if it requires medical tools/search or can be answered directly.

**Conversation History:**
{history_str if history_str else "No previous messages"}

**User Message:**
{user_message}

**Classify the intent:**

1. **requires_tools**: Medical questions, symptom checks, drug information, health conditions, treatment options, or any medical topic that needs verified sources
2. **direct_answer**: Greetings (hello, hi, how are you), basic chat, thank you messages, simple questions about the bot itself, or general conversation

**Examples:**
- "Hello" → direct_answer
- "What is diabetes?" → requires_tools  
- "Thank you" → direct_answer
- "I have a headache and fever" → requires_tools
- "How does this bot work?" → direct_answer
- "What are the side effects of aspirin?" → requires_tools

Respond in strict JSON format:
{{
  "intent": "requires_tools" or "direct_answer",
  "reason": "brief explanation",
  "confidence": 0.0-1.0
}}"""
        
        try:
            # Call OpenAI with gpt-4o-mini (cheaper and more capable than gpt-3.5-turbo)
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are a decision maker for a medical chatbot. Output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            # Log cost
            if response.usage:
                log_ai_cost(
                    model="gpt-4o-mini",
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    context="Decision Maker (Gatekeeper)"
                )
            
            content = response.choices[0].message.content
            decision = json.loads(content)
            
            # Validate decision structure
            if "intent" not in decision:
                logger.warning("Invalid decision structure, defaulting to requires_tools")
                return {
                    "intent": "requires_tools", 
                    "reason": "Invalid LLM response", 
                    "confidence": 0.5
                }

            return decision
            
        except Exception as e:
            logger.error(f"Error in decision maker: {str(e)}")
            # Fallback to requires_tools to be safe for medical queries
            return {
                "intent": "requires_tools",
                "reason": "Error in decision process, defaulting to tool-enabled mode for safety",
                "confidence": 0.5
            }
