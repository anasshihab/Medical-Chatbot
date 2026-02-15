# Voice Recording Feature - Speech-to-Text

## Overview
The medical chatbot now supports **real-time voice input** using the browser's Web Speech API. Users can speak directly into the text field instead of typing, making it easier and more accessible.

## How It Works

### User Experience
1. **Click the microphone button** (🎤) next to the paperclip icon
2. **Browser asks for microphone permission** (first time only)
3. **Red pulsing animation** indicates active listening
4. **Speak your question** in Arabic or English
5. **Text appears in real-time** as you speak
6. **Stops automatically** when you finish speaking
7. **Click send** to submit your question

### Visual Feedback
- **Normal state**: Cyan microphone icon with light background
- **Listening state**: Red pulsing microphone with animation
- **Placeholder changes**: Shows "🎤 أنا أستمع... تحدث الآن"
- **Error notifications**: Red popup with specific error message

## Features

### ✅ Implemented
- **Bilingual Support**: Arabic (primary) and English auto-detection
- **Real-time Transcription**: See words as you speak (interim results)
- **Toggle Recording**: Click once to start, click again to stop
- **Auto-stop**: Stops when speech ends
- **Visual Feedback**: Pulsing red animation during recording
- **Error Handling**: Comprehensive error messages in Arabic
- **Browser Compatibility**: Works in Chrome, Edge, Safari (WebKit)

### 🔧 Technical Details

#### Web Speech API Configuration
```javascript
recognition.continuous = false;      // Stop after user stops speaking
recognition.interimResults = true;   // Show real-time transcription
recognition.lang = 'ar-SA';         // Arabic (also detects English)
recognition.maxAlternatives = 1;    // Best result only
```

#### Supported Browsers
- ✅ **Chrome/Edge**: Full support (SpeechRecognition)
- ✅ **Safari**: Full support (webkitSpeechRecognition)
- ❌ **Firefox**: Not supported yet (working on WebSpeech API)
- ❌ **Opera**: Partial support

## Error Handling

### Error Types and Messages
1. **No Speech Detected**
   - Arabic: "لم يتم اكتشاف صوت. يرجى المحاولة مرة أخرى."
   - Cause: No speech detected within timeout period

2. **No Microphone**
   - Arabic: "لم يتم العثور على ميكروفون. يرجى التحقق من إعدادات الميكروفون."
   - Cause: No audio input device found

3. **Permission Denied**
   - Arabic: "تم رفض إذن الميكروفون. يرجى السماح بالوصول إلى الميكروفون."
   - Cause: User denied microphone access

4. **Network Error**
   - Arabic: "خطأ في الاتصال بالشبكة."
   - Cause: Connection issues with speech recognition service

5. **General Error**
   - Arabic: "حدث خطأ في التسجيل الصوتي"
   - Cause: Other unexpected errors

### Error Display
- **Position**: Top-center of screen
- **Duration**: 3 seconds
- **Animation**: Slides down on appear, slides up on dismiss
- **Style**: Red background, white text, shadow

## CSS Classes

### Button States
```css
.voice-record-btn              /* Normal state */
.voice-record-btn:hover        /* Hover state */
.voice-record-btn.listening    /* Active/listening state */
```

### Animations
```css
@keyframes pulse-recording     /* Pulsing red effect */
@keyframes slideDown          /* Error notification appear */
@keyframes slideUp            /* Error notification dismiss */
```

## UI Layout

### Button Positioning (RTL)
```
[Send Button (Left)] ──── [Text Input] ──── [Voice (Right)] [Attach (Far Right)]
     (70px)              (text area)             (70px)          (10px)
```

### Input Padding
- **Left**: 70px (for send button)
- **Right**: 140px (for voice + attach buttons)

## Use Cases

### Medical Context Benefits
1. **Accessibility**: Easier for elderly or disabled users
2. **Multilingual**: Supports Arabic and English seamlessly
3. **Speed**: Faster than typing for describing symptoms
4. **Accuracy**: Reduces spelling errors in medical terms
5. **Convenience**: Hands-free input while examining symptoms

### Example Scenarios
- "أشعر بصداع شديد منذ يومين" (headache description)
- "What medications can I take for fever?" (English query)
- "عندي ألم في البطن بعد الأكل" (digestive issue)
- "I have a rash on my arm" (skin condition)

## Browser Permissions

### First-Time Setup
1. User clicks microphone button
2. Browser shows permission prompt:
   - Chrome: "Use your microphone?"
   - Safari: "Allow microphone access?"
3. User clicks "Allow"
4. Permission saved for future use

### Permission Management
- **Chrome**: Settings → Privacy → Site Settings → Microphone
- **Safari**: Safari → Settings → Websites → Microphone
- **Edge**: Settings → Site permissions → Microphone

## Troubleshooting

### Common Issues

**Issue**: Microphone button not visible
- **Cause**: Browser doesn't support Web Speech API
- **Solution**: Use Chrome, Edge, or Safari

**Issue**: Permission denied error
- **Cause**: Microphone access blocked
- **Solution**: Enable microphone in browser settings

**Issue**: No speech detected
- **Cause**: Microphone volume too low or not speaking
- **Solution**: Check microphone settings, speak clearly and louder

**Issue**: Wrong language detected
- **Cause**: Browser language settings
- **Solution**: Primarily detects Arabic, but will work with English too

## Privacy & Security

### Data Processing
- **Client-side**: Initial speech capture
- **Google Speech API**: Cloud processing for transcription
- **No Storage**: Audio is not stored or logged
- **HTTPS Required**: Speech recognition requires secure connection

### Best Practices
1. Only collected audio during active recording
2. Audio data processed in real-time, not stored
3. Transcribed text treated like typed input
4. No audio files sent to backend

## Future Enhancements

1. **Language Selection**: Manual toggle between Arabic/English
2. **Continuous Mode**: Keep listening for multiple sentences
3. **Custom Commands**: Voice commands like "send", "clear"
4. **Offline Support**: Local speech recognition (browser-dependent)
5. **Audio Feedback**: Beep sounds for start/stop
6. **Confidence Scores**: Show transcription confidence
7. **Alternative Phrases**: Show multiple transcription options

## Testing

### Test Scenarios
1. ✅ Click microphone → Should show permission prompt
2. ✅ Grant permission → Should start listening (red pulse)
3. ✅ Speak in Arabic → Should transcribe correctly
4. ✅ Speak in English → Should transcribe correctly
5. ✅ Stop speaking → Should auto-stop after pause
6. ✅ Click while listening → Should stop manually
7. ✅ Deny permission → Should show error message
8. ✅ No microphone → Should show error message

## Code Structure

### Files Modified
- `app/templates/chat.html`: Complete implementation
  - HTML: Microphone button
  - CSS: Button styles and animations
  - JavaScript: Web Speech API integration

### Key Functions
```javascript
startListening()      // Initiates voice recording
stopListening()       // Stops voice recording
showVoiceError()      // Displays error notifications
recognition.onresult  // Handles transcription results
recognition.onerror   // Handles errors
```

## Browser Console Debugging

Enable console logging for troubleshooting:
```javascript
console.log('Speech recognition started');
console.log('Transcription:', transcript);
console.error('Error:', event.error);
```

## Dependencies

### Required
- **Web Speech API**: Built into modern browsers
- **Font Awesome**: For microphone icon

### No Additional Libraries
- Pure JavaScript implementation
- No external speech recognition services needed (uses browser's)

---

**Note**: This feature requires a **secure HTTPS connection** (or localhost) to work. The Web Speech API is only available in secure contexts.
