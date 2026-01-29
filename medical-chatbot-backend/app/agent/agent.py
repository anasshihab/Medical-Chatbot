"""Main agent orchestrator"""
from typing import AsyncGenerator, List, Dict, Optional
import json
from app.agent.streaming import StreamingClient
from app.agent.decision_maker import DecisionMaker
from app.agent.prompt_builder import get_system_prompt
from app.tools.keyword_search import KeywordSearchTool
from app.tools.symptom_checker import SymptomCheckerTool
from app.safety.emergency_detector import is_emergency, detect_special_cases
from app.safety.responses import get_emergency_response, get_boundary_reminder
from app.safety.content_normalizer import normalize_search_results


class MedicalChatAgent:
    """Main agent coordinating safety checks, tools, and responses"""
    
    def __init__(self):
        self.streaming_client = StreamingClient()
        self.decision_maker = DecisionMaker()
        self.keyword_search = KeywordSearchTool()
        self.symptom_checker = SymptomCheckerTool()
    
    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Process user message and stream response
        
        Args:
            user_message: User's message
            conversation_history: Previous messages in conversation
        
        Yields:
            Chunks in format: {"type": "content"|"metadata"|"done", "data": ...}
        """
        conversation_history = conversation_history or []
        
        # 1. Safety check - Emergency detection
        if is_emergency(user_message):
            special_cases = detect_special_cases(user_message)
            emergency_response = get_emergency_response(
                keyword=user_message,
                special_cases=special_cases
            )
            
            # Send emergency response immediately
            yield {
                "type": "metadata",
                "data": {"is_emergency": True, "special_cases": special_cases}
            }
            
            yield {
                "type": "content",
                "data": emergency_response
            }
            
            yield {
                "type": "done",
                "data": {
                    "is_emergency": True,
                    "tokens_used": len(emergency_response.split())
                }
            }
            return
        
        # 2. Decide action
        decision = self.decision_maker.decide_action(user_message, conversation_history)
        
        # Send metadata about decision
        yield {
            "type": "metadata",
            "data": {
                "action": decision["action"],
                "reason": decision["reason"]
            }
        }
        
        # 3. Execute action
        tool_results = None
        sources = []
        
        if decision["action"] == "keyword_search":
            # Execute keyword search
            search_query = decision["params"].get("search_query", user_message)
            tool_result = await self.keyword_search.execute(search_query=search_query)
            
            if tool_result.success:
                # POST-SEARCH SAFETY NORMALIZATION
                # تنظيف المحتوى من التشخيصات والأدوية قبل إرساله للذكاء الاصطناعي
                tool_results = normalize_search_results(tool_result.data)
                sources = tool_result.sources
                
                # Send tool results as metadata
                yield {
                    "type": "metadata",
                    "data": {
                        "tool_used": "keyword_search",
                        "sources": sources
                    }
                }
        
        elif decision["action"] == "symptom_checker":
            # Execute symptom checker
            symptoms = decision["params"].get("symptoms", [user_message])
            tool_result = await self.symptom_checker.execute(symptoms=symptoms)
            
            if tool_result.success:
                tool_results = tool_result.data
                sources = tool_result.sources
                
                # Send tool results as metadata
                yield {
                    "type": "metadata",
                    "data": {
                        "tool_used": "symptom_checker",
                        "sources": sources
                    }
                }
        
        elif decision["action"] == "direct_response":
            # Direct response provided in decision
            response = decision["params"].get("response", "")
            
            yield {
                "type": "content",
                "data": response
            }
            
            yield {
                "type": "done",
                "data": {"tokens_used": len(response.split())}
            }
            return
        
        # 4. Generate response with OpenAI
        messages = self._prepare_messages(
            user_message,
            conversation_history,
            tool_results,
            sources
        )
        
        system_prompt = get_system_prompt()
        
        # Stream response
        full_response = ""
        async for chunk in self.streaming_client.stream_chat(messages, system_prompt):
            full_response += chunk
            yield {
                "type": "content",
                "data": chunk
            }
        
        # Add boundary reminder if needed
        if any(keyword in user_message.lower() for keyword in ["diagnose", "medication", "prescribe"]):
            boundary_reminder = get_boundary_reminder()
            yield {
                "type": "content",
                "data": boundary_reminder
            }
            full_response += boundary_reminder
        
        # 5. Send completion metadata
        yield {
            "type": "done",
            "data": {
                "tokens_used": len(full_response.split()),
                "sources": sources,
                "tool_used": decision["action"] if decision["action"] in ["keyword_search", "symptom_checker"] else None
            }
        }
    
    def _prepare_messages(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        tool_results: any = None,
        sources: List[Dict] = None
    ) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI including tool results"""
        messages = []
        
        # Add conversation history
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message with tool context if available
        user_content = user_message
        
        if tool_results:
            # Inject tool results into context
            tool_context = f"\n\n---\n**Information from trusted sources:**\n{json.dumps(tool_results, indent=2)}\n---\n"
            user_content = f"{user_message}{tool_context}"
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages
