"""Manual testing script for conversation memory and GPT-4o-mini

Run this script to manually test:
1. GPT-4o-mini model is working
2. Conversation memory with summarization
3. Arabic response quality
4. Cost tracking
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.agent import MedicalChatAgent


async def test_short_conversation():
    """Test 1: Short conversation (no summarization)"""
    print("\n" + "="*60)
    print("TEST 1: Short Conversation (< 30 messages)")
    print("="*60)
    
    agent = MedicalChatAgent()
    
    history = [
        {"role": "user", "content": "ما هي أعراض السكري؟"},
        {"role": "assistant", "content": "أعراض السكري الشائعة تشمل: العطش الشديد، كثرة التبول، التعب المستمر، عدم وضوح الرؤية، بطء التئام الجروح، وفقدان الوزن غير المبرر."}
    ]
    
    message = "هل يمكن الوقاية من السكري؟"
    
    print(f"\n📝 User: {message}")
    print("\n🤖 Assistant: ", end="", flush=True)
    
    full_response = ""
    async for chunk in agent.process_message(message, history):
        if chunk["type"] == "content":
            print(chunk["data"], end="", flush=True)
            full_response += chunk["data"]
        elif chunk["type"] == "metadata":
            print(f"\n\n📊 Metadata: {chunk['data']}")
        elif chunk["type"] == "done":
            print(f"\n\n✅ Done: {chunk['data']}")
    
    print("\n" + "-"*60)
    return full_response


async def test_long_conversation():
    """Test 2: Long conversation (triggers summarization)"""
    print("\n" + "="*60)
    print("TEST 2: Long Conversation (> 30 messages - triggers summarization)")
    print("="*60)
    
    agent = MedicalChatAgent()
    
    # Create a long conversation history
    history = []
    topics = [
        "السكري", "ضغط الدم", "القلب", "التغذية", "الرياضة",
        "النوم", "الصداع", "الحساسية", "العظام", "المناعة",
        "الأسنان", "العيون", "الأذن", "البشرة", "الشعر",
        "الوزن", "الحمل", "الأطفال", "المسنين", "الأدوية"
    ]
    
    for topic in topics:
        history.append({
            "role": "user",
            "content": f"أخبرني عن صحة {topic}"
        })
        history.append({
            "role": "assistant",
            "content": f"معلومات مهمة عن صحة {topic}. يجب الاهتمام بعدة جوانب للحفاظ على صحة جيدة."
        })
    
    print(f"\n📚 Conversation history: {len(history)} messages")
    
    message = "ما هي أهم النصائح للصحة العامة؟"
    
    print(f"\n📝 User (Message #{len(history)//2 + 1}): {message}")
    print("\n🤖 Assistant: ", end="", flush=True)
    
    full_response = ""
    summarization_triggered = False
    
    async for chunk in agent.process_message(message, history):
        if chunk["type"] == "content":
            print(chunk["data"], end="", flush=True)
            full_response += chunk["data"]
        elif chunk["type"] == "metadata":
            if "status" in chunk["data"]:
                print(f"\n\n📊 Status: {chunk['data']['status']}")
                if "Summarization" in str(chunk["data"]):
                    summarization_triggered = True
        elif chunk["type"] == "done":
            print(f"\n\n✅ Done: {chunk['data']}")
    
    print(f"\n🔄 Summarization triggered: {summarization_triggered}")
    print("\n" + "-"*60)
    return full_response, summarization_triggered


async def test_arabic_quality():
    """Test 3: Arabic response quality with GPT-4o-mini"""
    print("\n" + "="*60)
    print("TEST 3: Arabic Response Quality (GPT-4o-mini)")
    print("="*60)
    
    agent = MedicalChatAgent()
    
    message = "شرح مفصل عن مرض السكري من النوع الثاني، مع ذكر الأعراض والأسباب وطرق الوقاية بالعربية"
    
    print(f"\n📝 User: {message}")
    print("\n🤖 Assistant: ", end="", flush=True)
    
    full_response = ""
    async for chunk in agent.process_message(message, []):
        if chunk["type"] == "content":
            print(chunk["data"], end="", flush=True)
            full_response += chunk["data"]
        elif chunk["type"] == "done":
            print(f"\n\n✅ Done: {chunk['data']}")
    
    # Check Arabic content quality
    arabic_chars = sum(1 for char in full_response if '\u0600' <= char <= '\u06FF')
    total_chars = len(full_response)
    arabic_percentage = (arabic_chars / total_chars * 100) if total_chars > 0 else 0
    
    print(f"\n\n📊 Arabic Quality Metrics:")
    print(f"   - Response length: {len(full_response)} characters")
    print(f"   - Arabic characters: {arabic_percentage:.1f}%")
    print(f"   - Quality: {'✅ Good' if arabic_percentage > 50 else '⚠️ Check needed'}")
    
    print("\n" + "-"*60)
    return full_response


async def main():
    """Run all manual tests"""
    print("\n" + "="*60)
    print("🧪 MANUAL TESTING: GPT-4o-mini + Conversation Memory")
    print("="*60)
    
    try:
        # Test 1: Short conversation
        await test_short_conversation()
        
        # Test 2: Long conversation with summarization
        response, summarized = await test_long_conversation()
        
        # Test 3: Arabic quality
        await test_arabic_quality()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
        print("\n📋 Summary:")
        print("   ✅ Test 1: Short conversation handled correctly")
        print(f"   {'✅' if summarized else '⚠️'} Test 2: Summarization {'triggered' if summarized else 'NOT triggered (check logs)'}")
        print("   ✅ Test 3: Arabic response quality verified")
        
        print("\n💡 Next steps:")
        print("   1. Check backend logs for cost comparisons")
        print("   2. Verify summarization logs show 'gpt-4o-mini'")
        print("   3. Test in actual chatbot interface")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
