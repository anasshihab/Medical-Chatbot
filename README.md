# WebTeb Medical AI Chatbot 🩺

Comprehensive medical AI assistant featuring a premium frontend interface and a robust agentic backend. Powered by the WebTeb theme and OpenAI's advanced models.

---

## 🚀 Key Features

### 🧠 Intelligent Agentic Core
- **Decision Maker (Gatekeeper)**: Automatically determines if a query needs medical database tools or a direct response, significantly reducing token costs.
- **Path-Optimized Logic**: Conditional tool schema passing to minimize input payload for simple greetings.
- **Cost Tracking**: Real-time monitoring of token consumption and API costs for every interaction.

### 🔍 Trusted Medical Intelligence
- **WebTeb Prioritization**: Primary search engine that always consults WebTeb.com first.
- **Restricted Sources**: Verified info from authorities: NIH (MedlinePlus, PubMed), Mayo Clinic, WHO, CDC, WebMD, and Healthline.
- **Symptom Checker**: Intelligent analysis (mocked in MVP) for condition assessment.

### 📁 Multi-Modal Capabilities
- **Image Analysis**: Automatic description and medical assessment of uploaded images.
- **Voice Recognition**: Real-time Arabic/English speech-to-text for hands-free queries.
- **Document Processing**: Extracts and analyzes text from PDF/TXT uploads.

### 💾 Smart Conversation Memory
- **Sliding Window**: Keeps context relevant by managing message history.
- **Arabic Summarization**: Older messages are summarized in Arabic to preserve context while saving tokens.

### 🛡️ Safety & Compliance
- **Emergency Detector**: Built-in detection for life-threatening scenarios with instant redirection to emergency services.
- **Content Normalizer**: Rewrites clinical language into educational terms and appends mandatory medical disclaimers.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla CSS (Glassmorphism), Javascript (ES6+), Bootstrap 5.
- **Backend**: FastAPI (Python 3.10+), Uvicorn.
- **LLM Engine**: OpenAI GPT-4o-mini (Agent) & GPT-4o (Decision Maker).
- **Search Engine**: DuckDuckGo API (DDGS).
- **Database**: SQLite / PostgreSQL with Alembic Migrations.

---

## 🏗️ Project Structure

```text
.
├── index.html                 # Main premium frontend interface
├── _deprecated_files/         # Isolated legacy code and obsolete documentation
├── medical-chatbot-backend/
│   ├── app/
│   │   ├── agent/             # Core AI orchestration (Agent, Decision Maker, Memory)
│   │   ├── api/               # REST Endpoints (Chat, Auth, Conversations)
│   │   ├── tools/             # Capabilities (Search, Symptom Checker, Web Reader)
│   │   ├── safety/            # Security & Normalization (Emergency detection)
│   │   └── utils/             # Utilities (Cost Calculator, File Processor)
│   ├── alembic/               # Database migration scripts
│   └── tests/                 # Unit and integration tests
└── .env                       # API Keys and configuration (Not in Source Control)
```

---

## 🏁 Getting Started

### 1. Requirements
Ensure you have Python 3.10+ installed.

### 2. Configuration
Create a `.env` file in the `medical-chatbot-backend/` directory:
```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./sql_app.db
DEBUG=True
```
### 3. Installation
```bash
cd medical-chatbot-backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Unix/MacOS:
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Running the App
```bash
# From the backend directory
uvicorn app.main:app --reload
```
The application will be available at (http://localhost:8000).

---

## ⚖️ Disclaimer
**This system is for educational purposes only.** It does NOT provide medical diagnoses, prescriptions, or clinical advice. Always consult a qualified healthcare professional for medical emergencies or specific health concerns.

---
*Developed by Antigravity AI Assistant | 2026*
