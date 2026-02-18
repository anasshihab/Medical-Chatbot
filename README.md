# Medical AI Chatbot & Agentic Backend 🩺

A professional-grade, HIPAA-compliant (conceptually) medical AI assistant featuring a premium glassmorphism frontend and a sophisticated agentic backend. Built with FastAPI, OpenAI GPT-4o-mini, and advanced token optimization strategies.

This project is a full-stack application designed to provide accurate, source-cited medical information while minimizing operational costs through intelligent decision-making.

--- 

## 🚀 Key Features

### 🧠 Advanced Agentic Core
- **Intelligent Gatekeeper (Decision Maker)**: An initial `gpt-4o-mini` layer classifies user intent to determine if expensive medical tools are needed or if a cheap direct response suffices.
- **Cost-Optimized Execution**: Based on intent, the system dynamically routes queries:
  - **Direct Path**: Zero-tool overhead for greetings and general chitchat.
  - **Tool-Enabled Path**: Full medical search and analysis for health queries.
- **Real-Time Cost Tracking**: precise calculation of input/output tokens and API costs for every single interaction, logged for auditing.

### 🔍 Trusted Medical Intelligence
- **WebTeb & Trusted Sources**: Prioritizes results from WebTeb, Mayo Clinic, NIH, WHO, and CDC via a custom search tool.
- **Symptom Checker**: A specialized tool for analyzing symptoms (mocked for demo safety).
- **Citation System**: Every medical claim is backed by the source URL from the search results.

### 📁 Multi-Modal Capabilities
- **Universal File Analysis**: Upload images (X-rays, lab results), audio (voice notes), or documents (PDF reports).
- **Auto-Enrichment**: The system automatically extracts text/descriptions from files and injects them into the conversation context for the AI to analyze.

### 🛡️ Safety & Compliance
- **Emergency Detection**: Instant pattern matching for life-threatening keywords (e.g., "heart attack", "suicide"). Bypasses AI generation to show immediate emergency hotline numbers.
- **Data Privacy**: Transient processing of files; strict separation of guest and authenticated user data.

---

## 🏗️ Backend Logic Flow

The backend operates on a strict, multi-stage pipeline to ensure safety, accuracy, and efficiency:

### 1. Request Ingestion & Security
- **Authentication**: JWT validation for registered users; ephemeral session tracking for guests.
- **Rate Limiting**: Checks daily question limits *before* any AI processing to prevent abuse.
- **Persistence**: User message is immediately committed to the PostgreSQL/SQLite database.

### 2. Pre-Processing & Enrichment
- **File Processor**: If attachments are present, they are processed:
  - **Images**: Passed to vision models for description.
  - **Audio**: Transcribed to text.
  - **Documents**: Parsed for content.
- **Emergency Filter**: The enriched message is scanned for emergency keywords. If found, the pipeline **halts** and returns a hardcoded emergency response.

### 3. The "Decision Maker" (Gatekeeper)
- The enriched context is sent to a lightweight `gpt-4o-mini` model.
- **Task**: Classify intent as `requires_tools` (medical) or `direct_answer` (conversational).
- **Outcome**: A structured JSON decision that dictates the next step.

### 4. Agent Execution (Conditional Routing)
- **Path A: Direct Answer (Low Cost)**
  - The main Agent model is called **without** tool definitions.
  - This saves significant token overhead.
  - Used for: "Hello", "Thanks", "How are you?".
- **Path B: Medical Analysis (High Intelligence)**
  - The Agent is called **with** `medical_search` and `check_symptoms` tools.
  - **Tool Execution**: If the Agent selects a tool, the backend executes it (e.g., searching DuckDuckGo for limited domains).
  - **Synthesis**: The Agent synthesizes tool outputs into a final answer.

### 5. Streaming & Finalization
- **Stream**: The response is streamed token-by-token to the frontend via Server-Sent Events (SSE).
- **Cost Logging**: Total cost (Gatekeeper + Agent + Tools) is calculated and saved to the database.
- **History Update**: The conversation history is updated with the new exchange.

---

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI (high-performance Python API)
- **AI/LLM**: OpenAI `gpt-4o-mini` (Agent & Decision Maker)
- **Database**: PostgreSQL (Production) / SQLite (Dev) with SQLAlchemy ORM
- **Migrations**: Alembic
- **Search**: DuckDuckGo Search API (filtered for medical reliability)
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism), Vanilla JS (ES6+)

---

## 📂 Project Structure

```text
.
├── index.html                 # Main Chat Interface (Frontend)
├── medical-chatbot-backend/
│   ├── app/
│   │   ├── agent/             # Core AI Logic
│   │   │   ├── agent.py       # Main Orchestrator
│   │   │   ├── decision_maker.py # Gatekeeper Logic
│   │   │   └── prompt_builder.py # System Prompts
│   │   ├── api/               # API Routes (Chat, Auth)
│   │   ├── models/            # Database Models (User, Conversation)
│   │   ├── schemas/           # Pydantic Schemas
│   │   ├── tools/             # AI Tools (Search, Symptom Checker)
│   │   ├── utils/             # Helpers (Cost Calc, File Processing)
│   │   └── main.py            # App Entry Point
│   ├── alembic/               # Database Migrations
│   └── requirements.txt       # Dependencies
```

---

## 🏁 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- An OpenAI API Key

### 2. Environment Setup
Create a `.env` file in `medical-chatbot-backend/`:

```env
OPENAI_API_KEY=your_sk_key_here
DATABASE_URL=sqlite:///./sql_app.db  # Or your PostgreSQL URL
SECRET_KEY=your_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

### 3. Installation

```bash
cd medical-chatbot-backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Initialization

```bash
# Apply migrations to create tables
alembic upgrade head
```

### 5. Running the Application

```bash
# Start the backend server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
Open the `index.html` file in your browser to access the frontend.

---

## ⚖️ Disclaimer
**For Educational Use Only.** This software is a demonstration of AI capabilities and does not replace professional medical advice. In emergencies, contact local health services immediately.

---
*Developed by Antigravity AI Assistant | 2026*
