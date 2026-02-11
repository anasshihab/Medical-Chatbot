"""Conversation Memory Manager - Sliding Window with Arabic Summarization

This service manages conversation history by:
1. Keeping only the last 10-15 exchanges (20-30 messages) in direct context
2. Summarizing older messages in Arabic when conversation grows beyond window
3. Optimizing token usage for cost reduction with GPT-4o-mini
"""

from typing import List, Dict, Optional
import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history with sliding window and summarization"""
    
    def __init__(self, window_size: int = 30):
        """
        Initialize conversation memory manager
        
        Args:
            window_size: Number of recent messages to keep in direct context (default: 30)
        """
        self.window_size = window_size
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    def should_summarize(self, conversation_history: List[Dict[str, str]]) -> bool:
        """
        Check if conversation history needs summarization
        
        Args:
            conversation_history: List of message dicts with 'role' and 'content'
            
        Returns:
            True if history exceeds window size and needs summarization
        """
        return len(conversation_history) > self.window_size
    
    async def summarize_old_messages(
        self, 
        messages_to_summarize: List[Dict[str, str]]
    ) -> str:
        """
        Summarize old messages into concise Arabic context
        
        Args:
            messages_to_summarize: List of messages to summarize
            
        Returns:
            Arabic summary string
        """
        # Build conversation text for summarization
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in messages_to_summarize
        ])
        
        summarization_prompt = f"""أنت مساعد طبي ذكي. يُرجى تلخيص هذه المحادثة السابقة في فقرة واحدة موجزة بالعربية، 
مع الحفاظ على:
1. الأعراض أو الحالات الطبية المذكورة
2. النصائح أو المعلومات الطبية المقدمة  
3. أي سياق شخصي هام (العمر، الجنس، التاريخ المرضي)
4. المصادر الطبية المستخدمة

كن موجزاً ولا تتجاوز 150 كلمة.

المحادثة السابقة:
{conversation_text}

الملخص بالعربية:"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": summarization_prompt}
                ],
                temperature=0.3,  # Lower temperature for consistent summaries
                max_tokens=300
            )
            
            summary = response.choices[0].message.content
            
            # Log summarization for monitoring
            logger.info(
                f"Summarized {len(messages_to_summarize)} messages "
                f"into {len(summary.split())} words"
            )
            
            # Log cost
            if response.usage:
                from app.utils.cost_calculator import log_ai_cost
                log_ai_cost(
                    model="gpt-4o-mini",
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    context="Conversation Summarization"
                )
            
            return summary
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            # Fallback: return simple truncation notice
            return "محادثة سابقة تحتوي على معلومات طبية عامة."
    
    async def process_conversation_history(
        self,
        conversation_history: List[Dict[str, str]],
        system_prompt: str
    ) -> List[Dict[str, str]]:
        """
        Process conversation history with sliding window and summarization
        
        Args:
            conversation_history: Full conversation history
            system_prompt: Base system prompt
            
        Returns:
            Optimized message list for OpenAI API
        """
        # If conversation is short, return as-is with system prompt
        if not self.should_summarize(conversation_history):
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            return messages
        
        # Trigger summarization for long conversations
        logger.info(
            f"Summarization triggered: {len(conversation_history)} messages "
            f"> {self.window_size} window"
        )
        
        # Split: old messages to summarize vs recent to keep
        messages_to_summarize = conversation_history[:-self.window_size]
        recent_messages = conversation_history[-self.window_size:]
        
        # Get summary
        summary = await self.summarize_old_messages(messages_to_summarize)
        
        # Build enhanced system prompt with summary
        enhanced_system_prompt = f"""{system_prompt}

---
**ملخص المحادثة السابقة / Previous Conversation Summary:**
{summary}
---

استمر في الإجابة بناءً على المحادثة الحالية والسياق السابق.
Continue responding based on current conversation and previous context."""
        
        # Build final message list
        messages = [{"role": "system", "content": enhanced_system_prompt}]
        messages.extend(recent_messages)
        
        logger.info(
            f"Context optimized: {len(conversation_history)} messages "
            f"→ summary + {len(recent_messages)} recent messages"
        )
        
        return messages


# Singleton instance for efficiency
_memory_instance = None

def get_conversation_memory(window_size: int = 30) -> ConversationMemory:
    """Get or create conversation memory singleton"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory(window_size=window_size)
    return _memory_instance
