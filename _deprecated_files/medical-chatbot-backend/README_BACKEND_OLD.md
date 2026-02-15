# Medical AI Chatbot Backend - MVP

Production-ready backend for a medical AI chatbot with agentic capabilities, safety guardrails, and guest mode support.

## ⚠️ تنويه طبي مهم / Important Medical Disclaimer

**هذا النظام:**
- ❌ **لا يقدم تشخيصات طبية** - Does NOT provide medical diagnoses
- ❌ **لا يصف أدوية** - Does NOT prescribe medications  
- ✅ **يوفر معلومات تعليمية فقط** - Provides educational information only
- ✅ **من مصادر موثوقة** - From trusted sources (NIH, Mayo Clinic, etc.)

**استشر طبيبًا مختصًا دائمًا للحصول على تشخيص أو علاج.**  
**Always consult a qualified healthcare provider for diagnosis or treatment.**

## 🏗️ Architecture Overview

This backend implements a **safety-first medical chatbot** that:
- ✅ Provides medical information from trusted sources only (NIH, MedlinePlus, Mayo Clinic, WebMD, Healthline)
- ✅ **Never** provides diagnoses or medication prescriptions
- ✅ Detects emergencies and provides immediate guidance
- ✅ Supports both authenticated users and guest sessions
- ✅ Enforces plan limits before calling OpenAI
- ✅ Uses streaming responses for better UX
- ✅ Implements feedback loop with automatic improvement

## 📋 Requirements

- Python 3.10+
- PostgreSQL 14+
- OpenAI API key (already configured in `.env`)
- WebTeb Symptom Checker API credentials (optional for MVP)

## 🚀 البدء السريع / Quick Start

### 📌 ملاحظة مهمة / Important Note

**مفتاح OpenAI تم تكوينه مسبقاً في ملف `.env`**  
The OpenAI API key is already configured in the `.env` file

**لا حاجة لإعداد إضافي - فقط شغّل الأمر التالي:**  
No additional setup needed - just run the following command:

```bash
uvicorn app.main:app --reload
```

---

### 1. تثبيت المتطلبات / Install Dependencies

```bash
cd medical-chatbot-backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. إعداد قاعدة البيانات / Setup Database

أنشئ قاعدة بيانات PostgreSQL أولاً، ثم:

```bash
# Create database migrations
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 3. تشغيل الخادم / Run the Server

```bash
uvicorn app.main:app --reload
```

السيرفر سيعمل على: http://localhost:8000  
The server will run at: http://localhost:8000

---

## 🧪 طرق الاختبار / Testing Methods

### 1️⃣ الطريقة الأولى: واجهة الاختبار البسيطة / Simple Test Interface

افتح المتصفح وانتقل إلى:  
Open your browser and go to:

```
http://localhost:8000/test
```

- واجهة بسيطة وسهلة الاستخدام
- تدعم العربية والإنجليزية
- تعرض المصادر المستخدمة
- آمنة ولا تعرض أكواد أو مفاتيح

Features:
- Simple and easy to use
- Supports Arabic and English
- Shows sources used
- Secure - no code or keys exposed

### 2️⃣ الطريقة الثانية: Swagger API Documentation

افتح:  
Open:

```
http://localhost:8000/docs
```

- واجهة تفاعلية لكل نقاط API
- جرّب الطلبات مباشرة
- شاهد التفاصيل الكاملة

Features:
- Interactive API explorer
- Test requests directly
- Full technical details

### 3️⃣ الطريقة الثالثة: واجهة المحادثة الجديدة / New Chat Interface

افتح المتصفح وانتقل إلى:
Open:

```
http://localhost:8000/chat
```

- واجهة محادثة متكاملة
- تدعم الرد المباشر من البوت
- تصميم أنيق وبسيط

Features:
- Full chat interface
- Connects directly to bot API
- Clean, simple design

## ⚠️ تحديث هام لقاعدة البيانات / Important Database Update

تم تغيير اسم العمود من `metadata` إلى `meta_data` في جدول الرسائل. يجب عليك إنشاء ترحيل جديد لقاعدة البيانات:
The column `metadata` was renamed to `meta_data`. You MUST create a new database migration:

```bash
# إنشاء الترحيل - Create migration
alembic revision --autogenerate -m "rename metadata to meta_data"

# تطبيق التغييرات - Apply changes
alembic upgrade head
```
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings and environment variables
│   ├── database.py             # Database connection
│   ├── dependencies.py         # FastAPI dependencies
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── guest_session.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── feedback.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   ├── feedback.py
│   │   └── error.py
│   │
│   ├── api/                    # API routes
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── chat.py             # Chat endpoint (streaming)
│   │   ├── conversations.py    # Conversation management
│   │   ├── profile.py          # User profile
│   │   └── feedback.py         # Feedback system
│   │
│   ├── core/                   # Core business logic
│   │   ├── auth.py             # JWT utilities
│   │   ├── security.py         # Password hashing
│   │   ├── plans.py            # Plan limits
│   │   └── usage.py            # Usage tracking
│   │
│   ├── agent/                  # Agentic system
│   │   ├── agent.py            # Main orchestrator
│   │   ├── decision_maker.py   # Action decision logic
│   │   ├── prompt_builder.py   # System prompts
│   │   └── streaming.py        # OpenAI streaming
│   │
│   ├── tools/                  # Agent tools
│   │   ├── base.py
│   │   ├── keyword_search.py   # Medical search
│   │   └── symptom_checker.py  # WebTeb integration
│   │
│   ├── safety/                 # Safety layer
│   │   ├── emergency_detector.py
│   │   ├── boundaries.py
│   │   └── responses.py
│   │
│   └── utils/                  # Utilities
│       ├── errors.py
│       └── constants.py
│
├── alembic/                    # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/signup` | Register new user | No |
| POST | `/api/auth/login` | Login | No |
| POST | `/api/auth/logout` | Logout | Yes |
| GET | `/api/auth/me` | Get current user | Yes |

### Chat

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/chat` | Send message (streaming) | Yes/Guest |

### Conversations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/conversations` | List conversations | Yes |
| GET | `/api/conversations/{id}` | Get conversation | Yes |

### Profile

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/profile` | Get profile | Yes |
| PUT | `/api/profile` | Update profile | Yes |
| DELETE | `/api/profile` | Delete account | Yes |

### Feedback

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/feedback` | Submit feedback | Yes/Guest |

## 💬 Chat Streaming Format

The `/api/chat` endpoint returns Server-Sent Events (SSE):

```javascript
// Event format
data: {"type": "content", "data": "chunk of text"}
data: {"type": "metadata", "data": {"tool_used": "keyword_search", "sources": [...]}}
data: {"type": "done", "data": {"conversation_id": 1, "message_id": 5}}
```

**Event Types:**
- `content`: Text chunks from the AI response
- `metadata`: Information about tools used, sources, etc.
- `done`: Final event with IDs and completion data
- `error`: Error occurred during processing

## 🔐 Authentication

### For Authenticated Users

```bash
# 1. Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass"}'

# Response: {"token": {"access_token": "...", "token_type": "bearer"}, "user": {...}}

# 2. Use token in subsequent requests
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### For Guest Users

```bash
# Send message with guestSessionId (no auth required)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is diabetes?",
    "guest_session_id": "guest-abc123"
  }'
```

**Guest Limits:**
- 1 conversation
- 10 questions maximum
- Data merged to user account upon registration

## 🎯 Features Implementation

### 1. Safety Layer

**Emergency Detection:**
- Detects critical symptoms (chest pain, severe bleeding, etc.)
- Immediately stops normal flow
- Provides emergency response with instructions to call 911
- Extra warnings for children and pregnancy

**Medical Boundaries:**
- Never provides diagnoses
- Never recommends specific medications or dosages
- Always includes disclaimers
- Redirects diagnosis/medication requests

### 2. Agentic System

**Decision Making:**
- Analyzes user input to determine best action
- Decides when to use keyword search vs symptom checker
- Asks follow-up questions when needed

**Available Actions:**
- `keyword_search`: Search WebTeb, WHO, Mayo Clinic
- `symptom_checker`: Analyze symptoms with WebTeb API
- `ask_followup`: Request more information
- `direct_response`: Answer simple questions directly

### 3. Tools System

**Keyword Search Tool:**
- Searches only approved domains (WebTeb, WHO, Mayo Clinic)
- Ranks results by domain priority
- Returns structured sources with citations

**Symptom Checker Tool:**
- Integrates with WebTeb Symptom Checker API
- Validates inputs
- Normalizes results
- Includes disclaimers

### 4. Plan Limits

**Free Plan:**
- 10 questions
- All basic features

**Pro Plan (Stub):**
- Essentially unlimited (999,999 questions)
- No payment integration in MVP

**Enforcement:**
- Limits checked BEFORE calling OpenAI
- Returns `PLAN_LIMIT_REACHED` error when exceeded
- Usage tracked per user/guest session

### 5. Feedback System

**Thumbs Up:**
- Stored in database
- No further action

**Thumbs Down:**
- Triggers review agent
- Re-runs search with review context
- Generates improved answer
- Stores improved response
- Links to original message

## 🛠️ Development

### Running Tests

```bash
# Tests directory is stubbed for MVP
# Add your tests in tests/ directory
pytest
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Reset database
alembic downgrade base
alembic upgrade head
```

### Code Quality

The codebase follows these principles:
- **Clean Architecture**: Clear separation of concerns
- **Type Hints**: Extensive use of Python type hints
- **Error Handling**: Unified error format with custom exceptions
- **Documentation**: Docstrings for all major functions
- **Arabic Comments**: Where manual setup is required

## ⚠️ Important Notes

### Safety Considerations

1. **This chatbot is NOT a doctor** - Always include disclaimers
2. **Emergency detection is keyword-based** - Consider ML-based detection for production
3. **Test thoroughly** - Especially emergency scenarios and boundary cases
4. **Monitor responses** - Review AI-generated content regularly
5. **Legal compliance** - Consult with legal team before deployment

### Production Considerations

1. **Search Implementation**: Current keyword search uses web scraping. For production:
   - Use official APIs from WebTeb, WHO, Mayo Clinic
   - Implement caching to reduce API calls
   - Add rate limiting

2. **OpenAI Costs**: Monitor token usage and implement:
   - Response length limits
   - Usage alerts
   - Budget caps

3. **Database**: 
   - Enable connection pooling (already configured)
   - Set up backups
   - Monitor performance

4. **Security**:
   - Use strong SECRET_KEY
   - Enable HTTPS only
   - Implement rate limiting
   - Add input sanitization

5. **Logging**:
   - Add structured logging
   - Monitor errors and performance
   - Track user behavior (GDPR compliant)

## 📊 Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `PLAN_LIMIT_REACHED` | User exceeded question limit | 403 |
| `UNAUTHORIZED` | Authentication required/failed | 401 |
| `VALIDATION_ERROR` | Request validation failed | 422 |
| `OPENAI_ERROR` | OpenAI API error | 503 |
| `INTERNAL_ERROR` | Unexpected server error | 500 |
| `NOT_FOUND` | Resource not found | 404 |
| `ALREADY_EXISTS` | Resource already exists | 409 |

## 🤝 Contributing

This is an MVP implementation. Key areas for improvement:
1. Comprehensive unit and integration tests
2. ML-based emergency detection
3. Official API integrations (instead of web scraping)
4. Enhanced NLP for symptom extraction
5. Conversation summarization
6. Multi-language support

## 📄 License

[Your License Here]

## 👥 Support

For issues or questions, contact: [Your Contact Info]

---

**Built with ❤️ for better healthcare information access**
