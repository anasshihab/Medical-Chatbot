"""
File Processing Utility Module (Upgraded)
Handles localized text extraction from documents (PDF, Word), 
audio transcription (Whisper), and image analysis (Vision).
Optimized for cost-effective token usage.
"""
import base64
import io
import logging
from typing import Dict, Any, Optional

# Lightweight libraries for local text extraction
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None

from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class FileProcessor:
    """
    Expert utility to process multimodal files.
    Saves costs by extracting plain text locally when possible.
    """

    @staticmethod
    def truncate_text(text: str, max_chars: int = 12000) -> str:
        """
        Safely truncates text to prevent excessive token costs.
        12k chars ≈ 2.5k-3k tokens.
        """
        if not text:
            return ""
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n\n[... (تم تقليص النص الطويل لتوفير التكلفة) ...]"

    @staticmethod
    def image_to_base64(image_bytes: bytes) -> str:
        """
        Converts raw image bytes to a standard Base64 string.
        Useful for preparing image payloads safely.
        """
        return base64.b64encode(image_bytes).decode("utf-8")

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """
        Extracts plain text from PDF locally using PyMuPDF.
        """
        if not fitz:
            logger.warning("PyMuPDF not installed. Cannot extract PDF text locally.")
            return "خطأ: لم يتم تثبيت أداة معالجة ملفات PDF."
        
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for i, page in enumerate(doc):
                if i > 20: break  # Limit to 20 pages to save local resources
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"PDF Extraction Error: {str(e)}")
            return f"خطأ في استخراج النص من PDF: {str(e)}"

    @staticmethod
    def extract_text_from_word(file_bytes: bytes) -> str:
        """
        Extracts plain text from Word files locally using python-docx.
        """
        if not Document:
            logger.warning("python-docx not installed. Cannot extract Word text locally.")
            return "خطأ: لم يتم تثبيت أداة معالجة ملفات Word."
        
        try:
            doc = Document(io.BytesIO(file_bytes))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            logger.error(f"Word Extraction Error: {str(e)}")
            return f"خطأ في استخراج النص من ملف Word: {str(e)}"

    @staticmethod
    async def process_image(file_data: str, file_type: str, file_name: str, user_message: str) -> Dict[str, Any]:
        """Process image files using Vision model for medical analysis"""
        try:
            data_url = f"data:{file_type};base64,{file_data}"
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"تحليل طبي للصورة المرفقة. سؤال المستخدم: {user_message}"},
                            {"type": "image_url", "image_url": {"url": data_url, "detail": "low"}} # 'low' saved tokens
                        ]
                    }
                ],
                max_tokens=500
            )
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "file_name": file_name,
                "type": "image"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "file_name": file_name, "type": "image"}

    @staticmethod
    async def process_audio(file_data: str, file_type: str, file_name: str) -> Dict[str, Any]:
        """Process audio files using Whisper transcription"""
        try:
            audio_bytes = base64.b64decode(file_data)
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = f"audio.mp3" # Fallback name
            transcription = await client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, language="ar"
            )
            return {"success": True, "transcription": transcription.text, "file_name": file_name, "type": "audio"}
        except Exception as e:
            return {"success": False, "error": str(e), "file_name": file_name, "type": "audio"}

    @staticmethod
    async def process_document(file_data: str, file_type: str, file_name: str) -> Dict[str, Any]:
        """Upgraded: Extract text locally from PDF, Word, or TXT"""
        try:
            doc_bytes = base64.b64decode(file_data)
            text = ""

            if "pdf" in file_type or file_name.lower().endswith(".pdf"):
                text = FileProcessor.extract_text_from_pdf(doc_bytes)
            elif "officedocument" in file_type or file_name.lower().endswith((".docx", ".doc")):
                text = FileProcessor.extract_text_from_word(doc_bytes)
            else:
                # Basic text fallback
                text = doc_bytes.decode('utf-8', errors='ignore')

            return {
                "success": True,
                "text": FileProcessor.truncate_text(text),
                "file_name": file_name,
                "type": "document"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "file_name": file_name, "type": "document"}

    @staticmethod
    async def process_file(file_data: str, file_type: str, file_name: str, user_message: str = "") -> Dict[str, Any]:
        """Router: Routes to appropriate local or AI-powered processor"""
        if file_type.startswith("image/"):
            return await FileProcessor.process_image(file_data, file_type, file_name, user_message)
        elif file_type.startswith("audio/"):
            return await FileProcessor.process_audio(file_data, file_type, file_name)
        elif any(ctx in file_type for ctx in ["pdf", "word", "officedocument", "text"]):
            return await FileProcessor.process_document(file_data, file_type, file_name)
        else:
            return {"success": False, "error": "نوع الملف غير مدعوم", "file_name": file_name}
