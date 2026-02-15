# File Attachment Feature

## Overview
The medical chatbot now supports file attachments, allowing users to upload:
- **Images** (medical photos, scans, symptoms pictures)
- **Audio files** (voice recordings of symptoms description)
- **Documents** (text files with medical history)

## Supported File Types



### Images
- **Formats**: JPG, PNG, GIF, WebP, etc.
- **Processing**: Analyzed using GPT-4 Vision
- **Use cases**: 
  - Skin conditions
  - X-rays or scans (note: not for diagnosis)
  - Medication labels
  - Symptoms visualization

### Audio
- **Formats**: MP3, WAV, M4A, WebM, OGG
- **Processing**: Transcribed using Whisper AI
- **Use cases**:
  - Voice recordings of symptoms
  - Easier input for users who prefer speaking

### Documents
- **Formats**: TXT, PDF (basic support)
- **Processing**: Text extraction
- **Use cases**:
  - Medical history
  - Previous doctor notes
  - Medication lists

## How It Works

### Frontend (User Experience)
1. User clicks the paperclip icon (📎) next to the search box
2. File picker opens, allowing selection of multiple files (max 10MB each)
3. Selected files show as preview cards with:
   - File icon or thumbnail (for images)
   - File name and size
   - Remove button (×)
4. User types their question and sends
5. Files are converted to base64 and sent with the message

### Backend Processing

#### Image Processing
```python
# Uses GPT-4o Vision API
- Receives base64 encoded image
- Constructs data URL
- Sends to GPT-4 Vision with medical analysis prompt
- Returns detailed description and observations
```

#### Audio Processing
```python
# Uses Whisper API
- Receives base64 encoded audio
- Converts to audio file in memory
- Transcribes using Whisper (Arabic auto-detect)
- Returns text transcription
```

#### Document Processing
```python
# Text extraction
- Decodes base64 data
- For text files: direct UTF-8 decode
- For PDF: Returns guidance to use image/text instead (requires additional setup)
```

### Integration with Chat Agent

The agent's `process_message` method now accepts an optional `attachments` parameter:

```python
async def process_message(
    self,
    user_message: str,
    conversation_history: List[Dict[str, str]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None
) -> AsyncGenerator[Dict, None]:
```

**Processing flow:**
1. Files are processed before the main message
2. Results are enriched into the user message:
   - Image analysis is appended
   - Audio transcription is appended
   - Document text is appended
3. Enriched message is sent to OpenAI for response
4. Safety checks and emergency detection work on enriched content

## API Changes

### Request Schema
```json
{
  "message": "ما رأيك بهذه الأعراض؟",
  "guest_session_id": "u_1234567890",
  "conversation_id": 1,
  "attachments": [
    {
      "file_data": "base64_encoded_data...",
      "file_type": "image/jpeg",
      "file_name": "symptom.jpg",
      "file_size": 245678
    }
  ]
}
```

### Response (Streaming)
```json
// File processing metadata
{"type": "metadata", "data": {"status": "processing_files", "count": 1}}

// File analysis results
{"type": "metadata", "data": {"files_processed": [...]}}

// Regular content stream
{"type": "content", "data": "تحليل الصورة يظهر..."}

// Done
{"type": "done", "data": {...}}
```

## UI Components

### CSS Classes
- `.attach-btn` - The paperclip button
- `.file-preview-container` - Container for file previews
- `.file-preview-card` - Individual file card
- `.file-thumbnail` - Image thumbnail
- `.remove-file` - Remove button

### JavaScript Functions
- `createFilePreview(file)` - Creates preview card
- `removeFile(fileName)` - Removes file from selection
- `formatFileSize(bytes)` - Formats file size in Arabic
- `fileToBase64(file)` - Converts file to base64

## Security & Limits

### File Size
- **Maximum**: 10MB per file
- **Validation**: Client-side and should be added server-side

### File Types
- **Whitelist**: Only specified MIME types accepted
- **Validation**: Check file type before processing

### Privacy
- Files are processed in memory (not saved to disk)
- Base64 encoding for transmission
- Files included in conversation context only

## Future Enhancements

1. **PDF Support**: Add PyPDF2 or similar for better PDF parsing
2. **File Compression**: Compress images before sending to reduce bandwidth
3. **Multiple Images**: Better support for comparing multiple images
4. **Medical Image Analysis**: Specialized models for X-rays, MRIs
5. **Server-side File Storage**: Optional file storage for conversation history
6. **File Type Icons**: Better visual indicators for different file types
7. **Progress Indicators**: Upload progress for large files
8. **Drag & Drop**: Drag files directly into chat area

## Testing

### Test Cases
1. Upload a single image → Should analyze and describe
2. Upload an audio file → Should transcribe to text
3. Upload multiple files → Should process all
4. Upload >10MB file → Should show error
5. Upload unsupported type → Should show error message
6. Remove file before sending → Should update preview
7. Send message with files → Should enrich message and respond

### Test Files
- `test_symptom.jpg` - Sample skin condition image
- `test_audio.mp3` - Sample voice recording
- `test_document.txt` - Sample medical history text

## Error Handling

- File too large → Alert message in Arabic
- Unsupported file type → Error in response
- Processing failure → Continue with text-only message
- API error → Show error message in chat

## Dependencies

### Backend
```python
openai>=1.0.0  # For GPT-4 Vision and Whisper
```

### Frontend
- Font Awesome (for icons)
- Native File API
- FileReader API for base64 conversion

## Configuration

No additional configuration required. Uses existing OpenAI API key from settings.
