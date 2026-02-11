"""Main agent orchestrator - Optimized for stable performance and citations"""
from typing import AsyncGenerator, List, Dict, Optional, Any
import json
import logging
from openai import AsyncOpenAI
from app.config import settings
from app.agent.prompt_builder import get_system_prompt
from app.tools.search import SearchTool
from app.tools.symptom_checker import SymptomCheckerTool
from app.safety.emergency_detector import is_emergency, detect_special_cases
from app.safety.responses import get_emergency_response
from app.services.conversation_memory import get_conversation_memory

# Global client for efficiency
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)
from app.utils.cost_calculator import log_ai_cost

class MedicalChatAgent:
    """Stable Agentic implementation with tool execution and citations"""
    
    def __init__(self):
        self.search_tool = SearchTool()
        self.symptom_checker = SymptomCheckerTool()
        
        # Initialize Decision Maker for Token Optimization (Gatekeeper Pattern)
        from app.agent.decision_maker import DecisionMaker
        self.decision_maker = DecisionMaker()
        
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "medical_search",
                    "description": "Search trusted medical sources for conditions, treatments, and health info.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"},
                            "timelimit": {
                                "type": "string", 
                                "description": "Filter results by time: 'd' (day), 'w' (week), 'm' (month), 'y' (year). USE THIS for latest news or recent updates.",
                                "enum": ["d", "w", "m", "y"]
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_symptoms",
                    "description": "Analyze symptoms using a medical database.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symptoms": {"type": "array", "items": {"type": "string"}},
                            "age": {"type": "integer"},
                            "gender": {"type": "string", "enum": ["male", "female"]}
                        },
                        "required": ["symptoms"]
                    }
                }
            }
        ]

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict, None]:
        conversation_history = conversation_history or []
        
        # Process file attachments if any
        enriched_message = user_message
        if attachments:
            from app.utils.file_processor import FileProcessor
            
            yield {"type": "metadata", "data": {"status": "processing_files", "count": len(attachments)}}
            
            file_results = []
            for attachment in attachments:
                result = await FileProcessor.process_file(
                    file_data=attachment.get("file_data"),
                    file_type=attachment.get("file_type"),
                    file_name=attachment.get("file_name"),
                    user_message=user_message
                )
                file_results.append(result)
                
                # Enrich user message with file analysis
                if result.get("success"):
                    if result.get("type") == "image":
                        enriched_message += f"\n\n📷 تحليل الصورة ({result.get('file_name')}):\n{result.get('analysis')}"
                    elif result.get("type") == "audio":
                        enriched_message += f"\n\n🎤 النص المسموع ({result.get('file_name')}):\n{result.get('transcription')}"
                    elif result.get("type") == "document":
                        enriched_message += f"\n\n📄 محتوى المستند ({result.get('file_name')}):\n{result.get('text')}"
                else:
                    yield {"type": "content", "data": f"\n⚠️ خطأ في معالجة الملف {result.get('file_name')}: {result.get('error')}\n\n"}
            
            yield {"type": "metadata", "data": {"files_processed": file_results}}
        
        # 1. Immediate Safety Check
        if is_emergency(enriched_message):
            resp = get_emergency_response(
                keyword=user_message, 
                special_cases=detect_special_cases(user_message),
                user_message=user_message
            )
            yield {"type": "metadata", "data": {"is_emergency": True}}
            yield {"type": "content", "data": resp}
            yield {"type": "done", "data": {"tokens_used": 0}}
            return

        # 2. Build Messages with Smart Memory Management
        memory = get_conversation_memory(window_size=30)
        
        # Process conversation history with sliding window + summarization
        messages = await memory.process_conversation_history(
            conversation_history=conversation_history,
            system_prompt=get_system_prompt()
        )
        
        # Add current user message
        messages.append({"role": "user", "content": enriched_message})

        # 3. TOKEN OPTIMIZATION: Use DecisionMaker as Gatekeeper
        # Instead of always sending tools schema, first check if tools are actually needed
        decision = await self.decision_maker.decide_action(
            user_message=enriched_message,
            conversation_history=conversation_history
        )
        
        logger.info(f"DecisionMaker intent: {decision.get('intent')} - {decision.get('reason')}")
        yield {
            "type": "metadata", 
            "data": {
                "decision": decision.get('intent'),
                "decision_reason": decision.get('reason'),
                "decision_confidence": decision.get('confidence', 0.0)
            }
        }

        # 4. Agent Loop - Conditional Tool Schema Passing
        try:
            # PATH 1: DIRECT ANSWER (No Tools Needed) - Saves input tokens!
            if decision.get('intent') == 'direct_answer':
                logger.info("Direct answer path - NO tools schema sent")
                
                # Call OpenAI WITHOUT tools parameter (major cost savings)
                stream = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    stream=True,
                    stream_options={"include_usage": True}
                    # NOTE: No 'tools' parameter = saves input tokens
                )
                
                full_content = ""
                async for chunk in stream:
                    if not chunk.choices:
                        # Handle usage chunk at the end
                        if hasattr(chunk, 'usage') and chunk.usage:
                            log_ai_cost(
                                model="gpt-4o-mini",
                                input_tokens=chunk.usage.prompt_tokens,
                                output_tokens=chunk.usage.completion_tokens,
                                context="Agent Direct (No Tools - Optimized)"
                            )
                        continue
                    content = chunk.choices[0].delta.content
                    if content:
                        full_content += content
                        yield {"type": "content", "data": content}
                
                yield {"type": "done", "data": {"tokens_used": len(full_content.split())}}
                return
            
            # PATH 2: REQUIRES TOOLS (Medical Query) - Use full schema
            logger.info("Tool-enabled path - tools schema included")
            
            # Step A: Initial Call WITH tools to see if they're needed
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools_schema,
                tool_choice="auto"
            )
            
            # Log initial call cost
            if response.usage:
                log_ai_cost(
                    model="gpt-4o-mini",
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    context="Agent Initial (With Tools)"
                )
            
            
            message = response.choices[0].message
            tool_calls = message.tool_calls

            if tool_calls:
                messages.append(message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    yield {"type": "metadata", "data": {"tool_used": function_name, "status": "executing"}}
                    
                    # Execute Tools
                    tool_result = ""
                    if function_name == "medical_search":
                        exec_result = await self.search_tool.execute(
                            args.get("query"), 
                            timelimit=args.get("timelimit")
                        )
                        if exec_result.success:
                            tool_result = json.dumps(exec_result.data)
                            yield {"type": "metadata", "data": {"sources": exec_result.sources}}
                        else:
                            tool_result = f"Error searching: {exec_result.error}"
                            
                    elif function_name == "check_symptoms":
                        exec_result = await self.symptom_checker.execute(**args)
                        if exec_result.success:
                            tool_result = json.dumps(exec_result.data)
                        else:
                            tool_result = f"Error checking symptoms: {exec_result.error}"

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result,
                    })

                # Step B: Final Generation after tool results
                stream = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    stream=True,
                    stream_options={"include_usage": True}
                )
                
                full_content = ""
                async for chunk in stream:
                    if not chunk.choices:
                        # Handle usage chunk at the end
                        if hasattr(chunk, 'usage') and chunk.usage:
                            log_ai_cost(
                                model="gpt-4o-mini",
                                input_tokens=chunk.usage.prompt_tokens,
                                output_tokens=chunk.usage.completion_tokens,
                                context="Agent Final (Streamed)"
                            )
                        continue
                    content = chunk.choices[0].delta.content
                    if content:
                        full_content += content
                        yield {"type": "content", "data": content}
                
                yield {"type": "done", "data": {"tokens_used": len(full_content.split())}}
            
            else:
                # Direct response (no tools needed)
                # Re-run with stream for direct speed
                stream = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    stream=True,
                    stream_options={"include_usage": True}
                )
                full_content = ""
                async for chunk in stream:
                    if not chunk.choices:
                        # Handle usage chunk at the end
                        if hasattr(chunk, 'usage') and chunk.usage:
                            log_ai_cost(
                                model="gpt-4o-mini",
                                input_tokens=chunk.usage.prompt_tokens,
                                output_tokens=chunk.usage.completion_tokens,
                                context="Agent Direct (Streamed)"
                            )
                        continue
                    content = chunk.choices[0].delta.content
                    if content:
                        full_content += content
                        yield {"type": "content", "data": content}
                yield {"type": "done", "data": {"tokens_used": len(full_content.split())}}

        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            yield {"type": "content", "data": f"I apologize, an error occurred: {str(e)}. Please try again later."}
            yield {"type": "done", "data": {"error": str(e)}}
