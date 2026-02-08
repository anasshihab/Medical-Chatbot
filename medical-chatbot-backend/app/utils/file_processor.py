"""File processing utilities for handling various file types"""
import base64
import io
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class FileProcessor:
    """Process different types of file attachments"""
    
    @staticmethod
    async def process_image(file_data: str, file_type: str, file_name: str, user_message: str) -> Dict[str, Any]:
        """
        Process image files using GPT-4 Vision
        
        Args:
            file_data: Base64 encoded image data
            file_type: MIME type (e.g., image/jpeg)
            file_name: Original filename
            user_message: User's message/question about the image
            
        Returns:
            Dict with analysis results
        """
        try:
            # Construct data URL for GPT-4 Vision
            data_url = f"data:{file_type};base64,{file_data}"
            
            # Call GPT-4 Vision
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""أنت مساعد طبي ذكي. يرجى تحليل هذه الصورة الطبية بعناية.

سؤال المستخدم: {user_message}

يرجى تقديم:
1. وصف تفصيلي لما تراه في الصورة
2. إذا كانت تتعلق بأعراض أو حالة طبية، اذكر الملاحظات المهمة
3. أي توصيات أولية (مع التأكيد على ضرورة استشارة الطبيب)

⚠️ تنبيه: هذا تحليل أولي فقط ولا يغني عن استشارة الطبيب المختص."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis,
                "file_name": file_name,
                "type": "image"
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {
                "success": False,
                "error": f"فشل تحليل الصورة: {str(e)}",
                "file_name": file_name,
                "type": "image"
            }
    
    @staticmethod
    async def process_audio(file_data: str, file_type: str, file_name: str) -> Dict[str, Any]:
        """
        Process audio files using Whisper for transcription
        
        Args:
            file_data: Base64 encoded audio data
            file_type: MIME type (e.g., audio/wav, audio/mp3)
            file_name: Original filename
            
        Returns:
            Dict with transcription results
        """
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(file_data)
            
            # Determine file extension from MIME type
            extension_map = {
                "audio/wav": "wav",
                "audio/wave": "wav",
                "audio/mpeg": "mp3",
                "audio/mp3": "mp3",
                "audio/mp4": "mp4",
                "audio/x-m4a": "m4a",
                "audio/webm": "webm",
                "audio/ogg": "ogg"
            }
            
            extension = extension_map.get(file_type, "mp3")
            
            # Create a file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = f"audio.{extension}"
            
            # Transcribe using Whisper
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ar"  # Primarily Arabic, but Whisper auto-detects
            )
            
            return {
                "success": True,
                "transcription": transcription.text,
                "file_name": file_name,
                "type": "audio"
            }
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return {
                "success": False,
                "error": f"فشل تحويل الصوت إلى نص: {str(e)}",
                "file_name": file_name,
                "type": "audio"
            }
    
    @staticmethod
    async def process_document(file_data: str, file_type: str, file_name: str) -> Dict[str, Any]:
        """
        Process document files (PDF, TXT, etc.)
        
        Args:
            file_data: Base64 encoded document data
            file_type: MIME type
            file_name: Original filename
            
        Returns:
            Dict with extracted text
        """
        try:
            # Decode base64 data
            doc_bytes = base64.b64decode(file_data)
            
            # Handle text files
            if file_type in ["text/plain", "text/markdown"]:
                text = doc_bytes.decode('utf-8', errors='ignore')
                return {
                    "success": True,
                    "text": text[:5000],  # Limit to first 5000 chars
                    "file_name": file_name,
                    "type": "document"
                }
            
            # For PDFs and other documents, we need additional libraries
            # For now, return a helpful message
            return {
                "success": False,
                "error": "يرجى نسخ النص من المستند ولصقه مباشرة، أو استخدام صورة للمستند.",
                "file_name": file_name,
                "type": "document",
                "note": "PDF parsing requires additional setup. Use text or image instead."
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                "success": False,
                "error": f"فشل معالجة المستند: {str(e)}",
                "file_name": file_name,
                "type": "document"
            }
    
    @staticmethod
    async def process_file(file_data: str, file_type: str, file_name: str, user_message: str = "") -> Dict[str, Any]:
        """
        Route file to appropriate processor based on type
        
        Args:
            file_data: Base64 encoded file data
            file_type: MIME type
            file_name: Original filename
            user_message: User's message (for context with images)
            
        Returns:
            Processing results
        """
        # Image files
        if file_type.startswith("image/"):
            return await FileProcessor.process_image(file_data, file_type, file_name, user_message)
        
        # Audio files
        elif file_type.startswith("audio/"):
            return await FileProcessor.process_audio(file_data, file_type, file_name)
        
        # Document files
        elif file_type in ["application/pdf", "text/plain", "text/markdown", "application/msword"]:
            return await FileProcessor.process_document(file_data, file_type, file_name)
        
        else:
            return {
                "success": False,
                "error": f"نوع الملف غير مدعوم: {file_type}",
                "file_name": file_name
            }
