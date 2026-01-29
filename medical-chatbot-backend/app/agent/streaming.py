"""OpenAI streaming wrapper"""
from typing import AsyncGenerator, List, Dict
import json
from openai import AsyncOpenAI
from app.config import settings
from app.utils.errors import OpenAIException


class StreamingClient:
    """Wrapper for OpenAI streaming API"""
    
    def __init__(self):
        # تحقق من وجود مفتاح OpenAI - Check if OpenAI key exists
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-your"):
            raise OpenAIException(
                message="OpenAI API key is missing or not configured. Please set OPENAI_API_KEY in .env file.",
                details={"error": "OPENAI_KEY_NOT_CONFIGURED"}
            )
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion from OpenAI
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
        
        Yields:
            Content chunks as they arrive
        """
        try:
            # Prepare messages
            full_messages = []
            
            if system_prompt:
                full_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            full_messages.extend(messages)
            
            # Create streaming completion
            stream = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=full_messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Stream chunks
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            raise OpenAIException(
                message=f"OpenAI streaming failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None
    ) -> str:
        """
        Get non-streaming chat completion
        
        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
        
        Returns:
            Complete response text
        """
        try:
            # Prepare messages
            full_messages = []
            
            if system_prompt:
                full_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            full_messages.extend(messages)
            
            # Create completion
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=full_messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise OpenAIException(
                message=f"OpenAI request failed: {str(e)}",
                details={"error": str(e)}
            )
