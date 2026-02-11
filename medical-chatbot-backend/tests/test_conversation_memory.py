"""Unit tests for Conversation Memory Service"""

import pytest
import asyncio
from app.services.conversation_memory import ConversationMemory


@pytest.fixture
def memory_service():
    """Create a conversation memory instance for testing"""
    return ConversationMemory(window_size=30)


@pytest.fixture
def short_conversation():
    """Short conversation (< 30 messages)"""
    return [
        {"role": "user", "content": "ما هي أعراض السكري؟"},
        {"role": "assistant", "content": "أعراض السكري الشائعة تشمل: العطش الشديد، كثرة التبول، التعب..."},
        {"role": "user", "content": "هل يمكن الوقاية منه؟"},
        {"role": "assistant", "content": "نعم، يمكن الوقاية من السكري من النوع الثاني عبر..."},
    ]


@pytest.fixture
def long_conversation():
    """Long conversation (> 30 messages) to trigger summarization"""
    messages = []
    for i in range(20):
        messages.append({
            "role": "user",
            "content": f"سؤال طبي رقم {i+1} عن الصحة"
        })
        messages.append({
            "role": "assistant",
            "content": f"إجابة طبية رقم {i+1} من مصادر موثوقة"
        })
    return messages


class TestConversationMemory:
    """Test suite for conversation memory management"""
    
    def test_should_summarize_short_conversation(self, memory_service, short_conversation):
        """Test that short conversations don't trigger summarization"""
        result = memory_service.should_summarize(short_conversation)
        assert result is False, "Short conversations should not trigger summarization"
    
    def test_should_summarize_long_conversation(self, memory_service, long_conversation):
        """Test that long conversations trigger summarization"""
        result = memory_service.should_summarize(long_conversation)
        assert result is True, "Long conversations should trigger summarization"
    
    @pytest.mark.asyncio
    async def test_process_short_conversation(self, memory_service, short_conversation):
        """Test processing short conversation without summarization"""
        system_prompt = "أنت مساعد طبي ذكي."
        
        result = await memory_service.process_conversation_history(
            conversation_history=short_conversation,
            system_prompt=system_prompt
        )
        
        # Should have: 1 system message + all conversation messages
        assert len(result) == 1 + len(short_conversation)
        assert result[0]["role"] == "system"
        assert result[0]["content"] == system_prompt
        # Check that all original messages are preserved
        for i, msg in enumerate(short_conversation):
            assert result[i+1]["role"] == msg["role"]
            assert result[i+1]["content"] == msg["content"]
    
    @pytest.mark.asyncio
    async def test_process_long_conversation(self, memory_service, long_conversation):
        """Test processing long conversation with summarization"""
        system_prompt = "أنت مساعد طبي ذكي."
        
        result = await memory_service.process_conversation_history(
            conversation_history=long_conversation,
            system_prompt=system_prompt
        )
        
        # Should have: 1 system message (with summary) + last 30 messages
        expected_length = 1 + 30
        assert len(result) == expected_length, f"Expected {expected_length} messages, got {len(result)}"
        
        # Check system message contains summary
        assert result[0]["role"] == "system"
        assert "ملخص المحادثة السابقة" in result[0]["content"] or "Previous Conversation Summary" in result[0]["content"]
        assert system_prompt in result[0]["content"]
        
        # Check that last 30 messages are preserved
        for i, original_msg in enumerate(long_conversation[-30:]):
            assert result[i+1]["role"] == original_msg["role"]
    
    @pytest.mark.asyncio
    async def test_summarization_quality(self, memory_service):
        """Test that summarization produces valid Arabic summary"""
        messages = [
            {"role": "user", "content": "عندي ألم في الصدر منذ يومين"},
            {"role": "assistant", "content": "ألم الصدر يمكن أن يكون له أسباب عديدة. هل تعاني من أعراض أخرى؟"},
            {"role": "user", "content": "نعم، عندي ضيق في التنفس أحياناً"},
            {"role": "assistant", "content": "هذه أعراض مهمة. يجب عليك استشارة طبيب فوراً للفحص."},
        ]
        
        summary = await memory_service.summarize_old_messages(messages)
        
        # Check that summary is not empty and is in Arabic
        assert len(summary) > 0, "Summary should not be empty"
        assert any(char in summary for char in "أبتثجحخدذرزسشصضطظعغفقكلمنهوي"), "Summary should contain Arabic text"
        
        # Check summary is concise (approximately)
        word_count = len(summary.split())
        assert word_count <= 200, f"Summary should be concise (<= 200 words), got {word_count} words"
    
    @pytest.mark.asyncio
    async def test_mixed_language_conversation(self, memory_service):
        """Test handling of conversations with mixed Arabic and English"""
        messages = [
            {"role": "user", "content": "What is diabetes?"},
            {"role": "assistant", "content": "Diabetes is a chronic condition..."},
            {"role": "user", "content": "ما هي أعراضه بالعربية؟"},
            {"role": "assistant", "content": "أعراض السكري تشمل العطش الشديد..."},
        ]
        
        summary = await memory_service.summarize_old_messages(messages)
        
        # Summary should be produced successfully
        assert len(summary) > 0
        assert isinstance(summary, str)


@pytest.mark.asyncio
async def test_memory_window_size_customization():
    """Test that window size can be customized"""
    custom_memory = ConversationMemory(window_size=20)
    
    messages = [{"role": "user", "content": f"Message {i}"} for i in range(25)]
    
    result = await custom_memory.process_conversation_history(
        conversation_history=messages,
        system_prompt="Test system prompt"
    )
    
    # Should have 1 system (with summary) + 20 recent messages
    assert len(result) == 21


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
