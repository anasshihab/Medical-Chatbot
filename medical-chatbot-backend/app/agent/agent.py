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

# Global client for efficiency
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)

class MedicalChatAgent:
    """Stable Agentic implementation with tool execution and citations"""
    
    def __init__(self):
        self.search_tool = SearchTool()
        self.symptom_checker = SymptomCheckerTool()
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "medical_search",
                    "description": "Search trusted medical sources for conditions, treatments, and health info.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"}
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

        # 2. Build Messages
        messages = [{"role": "system", "content": get_system_prompt()}]
        for msg in conversation_history[-50:]:  # Context window (approx 25 turns)
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": enriched_message})

        # 3. Agent Loop (Handled via stable OpenAI SDK)
        try:
            # Step A: Initial Call to see if tools are needed
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self.tools_schema,
                tool_choice="auto"
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
                        exec_result = await self.search_tool.execute(args.get("query"))
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
                    model="gpt-4o",
                    messages=messages,
                    stream=True
                )
                
                full_content = ""
                async for chunk in stream:
                    if not chunk.choices:
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
                    model="gpt-4o",
                    messages=messages,
                    stream=True
                )
                full_content = ""
                async for chunk in stream:
                    if not chunk.choices:
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
