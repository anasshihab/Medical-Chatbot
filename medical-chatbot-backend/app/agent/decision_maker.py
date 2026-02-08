"""Decision maker for agent actions"""
from typing import Dict, List, Optional
import json
import logging
from openai import AsyncOpenAI
from app.config import settings
from app.agent.prompt_builder import get_tool_decision_prompt

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
        Decide what action to take based on user message using LLM
        """
        conversation_history = conversation_history or []
        
        # Convert history to string for prompt
        history_str = ""
        for msg in conversation_history[-20:]: # Last 20 messages
            history_str += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
        
        # Get decision prompt
        prompt = get_tool_decision_prompt(user_message, history_str)
        
        try:
            # Call OpenAI to decide
            # Using gpt-3.5-turbo for speed/cost, or gpt-4o works too
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": "You are a decision maker for a medical bot. Output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            decision = json.loads(content)
            
            # Validate decision structure
            if "action" not in decision:
                return {
                    "action": "keyword_search", 
                    "reason": "Invalid LLM response", 
                    "params": {"search_query": user_message}
                }
                
            # If action is read_url, ensure we have the url
            if decision["action"] == "read_url" and "url" not in decision.get("params", {}):
                 # Try to extract again if missing
                 pass 

            return decision
            
        except Exception as e:
            logger.error(f"Error in decision maker: {str(e)}")
            # Fallback to keyword search as it's the safest default for a medical bot
            return {
                "action": "keyword_search",
                "reason": "Error in decision process, defaulting to search",
                "params": {
                    "search_query": user_message
                }
            }
