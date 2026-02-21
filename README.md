# Medical AI Chatbot & Agentic Backend 🩺

A professional-grade, HIPAA-compliant (conceptually) medical AI assistant featuring a **premium glassmorphism frontend** and a **sophisticated agentic backend**. Built with FastAPI, OpenAI GPT-4o-mini, and advanced token optimization strategies.
 
This project is a full-stack application designed to provide accurate, source-cited medical information while minimizing operational costs through intelligent decision-making and strict usage gating.

---

## 🚀 Key Features

### 💎 Premium UX/UI Experience
- **Glassmorphism Design**: Minimalist, card-based interface with real-time blur/transparency and vibrant gradients.
- **Dynamic Animations**: 
  - Interactive **Neural Network Canvas** background.
  - Custom SVG cursor with a particle light trail.
  - Horizontal scrolling medical topic chips with "Pause on Hover".
- **Responsive Layout**: Fully optimized for mobile, tablet, and desktop viewing.

### 🌐 Multimodal Capabilities
- **Voice Transcription**: Built-in Arabic/English speech-to-text for hands-free medical inquiries.
- **Universal File Analysis**: Support for uploading images (X-rays, lab results), documents (PDFs), and more for AI context enrichment.
- **Markdown Rendering**: Beautifully formatted AI responses including tables, bold text, and source citations.

### 🧠 Advanced Agentic Core
- **Intelligent Gatekeeper (Decision Maker)**: An initial `gpt-4o-mini` layer classifies user intent to determine if medical tools are needed or if a direct response suffices.
- **Cost-Optimized Execution**: 
  - **Direct Path**: Zero-tool overhead for greetings and general chitchat.
  - **Tool Path**: Full medical search and analysis for health queries.
- **Real-Time Cost Tracking**: Precise calculation of tokens and API costs for every interaction, logged for auditing.

### 🔍 Trusted Medical Intelligence
- **Priority Sources**: Prioritizes results from WebTeb, Mayo Clinic, NIH, WHO, and CDC via a custom search tool.
- **Advanced Citation System**: Every medical claim is backed by the source URL from the search results.
- **Symptom Analysis**: Specialized logic for analyzing symptoms with built-in safety filters.

### 🛡️ Safety & Compliance
- **Emergency Detection**: Instant pattern matching for life-threatening keywords (e.g., "heart attack", "suicide"). Bypasses AI generation to show immediate emergency hotline numbers.
- **HIPAA-Ready Architecture**: Strict separation of user data and transient processing of sensitive file inputs.

---

## ⏳ Intelligent Rate Limiting & Gating

The system implements a sophisticated multi-tier usage policy based on a **6-hour rolling window**:

| User Tier | Question Limit (per 6h) | Word Limit (per message) | Features |
| :--- | :--- | :--- | :--- |
| **Guest** | 2 Questions | 20 Words | Basic Search |
| **Free Account**| 5 Questions | 25 Words | History + Basic Search |
| **Pro Plan** | **Unlimited** | 1,000 Words | Files + Voice + AI Agent |

- **Live Countdown**: Real-time visual banners and modals show exactly when your limit resets.
- **Onboarding Overlay**: Beautiful authentication gateway for Guest vs. Registered access.
- **Conversion UX**: Interactive pricing modals and "Upgrade" prompts when limits are reached.

---

## 🏗️ Backend Logic Flow

1. **Request Gating**: JWT/Guest session validation + 6-hour window check + word count check.
2. **Context Enrichment**: 
   - Audio transcription (if voice input).
   - Base64 file extraction and descriptions (if attachments).
   - Emergency keyword filter.
3. **The "Decision Maker"**: Classifies intent as conversational or medical.
4. **Agent Orchestration**:
   - **Path A**: Direct response (low token cost).
   - **Path B**: Medical Tool use (Search + Symptom Check).
5. **Streaming Output**: SSE (Server-Sent Events) tokens streamed to UI for real-time engagement.
6. **Persistence & Auditing**: DB commit (SQLAlchemy) + Cost calculation (Metadata logging).

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **AI/LLM**: OpenAI `gpt-4o-mini`
- **Database**: PostgreSQL (Production) / SQLite (Dev)
- **Migrations**: Alembic
- **Search**: DuckDuckGo Search API (filtered domains)
- **Frontend**: Vanilla HTML5/CSS3 (ES6 JS), Bootstrap 5, FontAwesome 6, Marked.js

---

## 📂 Project Structure

```text
.
├── index.html                 # Main Chat Interface (Frontend)
├── medical-chatbot-backend/
│   ├── app/
│   │   ├── agent/             # Core AI Orchestration (Agent + Gatekeeper)
│   │   ├── api/               # API Routes (Auth, Chat, Conversations, Profile)
│   │   ├── core/              # Business Logic (Plans, Usage, Logging)
│   │   ├── models/            # SQLAlchemy Database Models
│   │   ├── schemas/           # Pydantic Content Validation
│   │   ├── tools/             # AI Tools (Search, Symptom Checker)
│   │   ├── utils/             # Helpers (Cost Calc, File Processing, Crypto)
│   │   └── main.py            # FastAPI Entry Point
│   ├── alembic/               # Database Migrations
│   ├── requirements.txt       # Python Dependencies
│   └── .env                   # Environment Secrets
```

---

## 🏁 Getting Started

### 1. Backend Setup
```bash
cd medical-chatbot-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_key
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=your_jwt_secret
DEBUG=True
```

### 3. Running the App
```bash
# Apply migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```
- **Backend API**: `http://localhost:8000`
- **Frontend**: Just open the root `index.html` in any browser.

---

## ⚖️ Disclaimer
**For Educational Use Only.** This software is a demonstration of AI capabilities and does not replace professional medical advice. In emergencies, contact local health services immediately.

---
*Developed by Antigravity AI Assistant | 2026*
