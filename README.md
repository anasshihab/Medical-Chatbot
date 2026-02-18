# Medical Chatbot (WebTeb AI) 🩺

A professional, state-of-the-art medical chatbot designed to provide reliable medical information through an intuitive, AI-driven interface. Built with **FastAPI** and **Vanilla JavaScript**, it combines the power of LLMs with specialized medical safety systems and a premium **Glassmorphism** design.

---

## 🚀 Key Features

### 🧠 Intelligent Core
- **Context-Aware AI:** Powered by OpenAI GPT models for accurate and empathetic medical conversations.
- **Real-time Research:** Integrated with DuckDuckGo Search (DDGS) and medical knowledge base search tools for up-to-date information.
- **Symptom Checker:** Integrated with WebTeb's Symptom Checker API (with mock fallback for development).
- **Multi-Modal Support:** Support for attaching medical documents and images for AI-assisted analysis.

### 🛡️ Medical Safety & Ethics
- **Emergency Detection:** Real-time identification of life-threatening symptoms with immediate redirection to professional medical services.
- **Strict Content Boundaries:** Advanced filtering ensures the AI stays within medical informational bounds and avoids providing prohibited or harmful advice.
- **Tone & Terminology:** Sophisticated processing to maintain professional medical terminology and a supportive yet clinical tone.

### 💎 Premium User Experience
- **Full RTL Support:** Native Arabic language support with optimized typography (Almarai, Inter).
- **Glassmorphism UI:** Stunning, responsive interface featuring vibrant gradients, neural network animations (Canvas), and smooth micro-interactions.
- **Voice Commands:** Hands-free interaction through integrated voice recording capabilities.
- **Conversation History:** Secure, persistent storage for tracking previous medical inquiries and AI responses.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Vanilla JS, HTML5, CSS3, Bootstrap 5, FontAwesome |
| **Backend** | FastAPI (Python), uvicorn, SQLAlchemy |
| **Database** | PostgreSQL (Production), SQLite (Local/Development) |
| **AI / LLM** | OpenAI API, DuckDuckGo Search Integration |
| **Security** | JWT Authentication, Bcrypt (Passlib), strict Content Security Policy (CSP) |

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- **Python 3.10+**
- **PostgreSQL** (Optional, falls back to SQLite `sql_app.db`)

### 2. Backend Installation
```bash
# Navigate to the backend folder
cd medical-chatbot-backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the `.env.example` file to create your `.env` and fill in the required credentials:
```bash
cp .env.example .env
```
**Required Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key.
- `DATABASE_URL`: Connection string for PostgreSQL (if not using SQLite).
- `SECRET_KEY`: A secure random string for JWT token generation.
- `WEBTEB_API_KEY`: API key for WebTeb integration (optional, uses mock data if empty).

### 4. Database Initialization
Run migrations to set up the database schema:
```bash
alembic upgrade head
```

### 5. Running the Application
**Start the Backend Server:**
```bash
uvicorn app.main:app --reload
```
**Open the Frontend:**
The frontend resides in the root `index.html`. Open it directly in your browser or use a static server (e.g., Live Server in VS Code).
*Note: Ensure the `API_BASE_URL` in the frontend scripts is configured to match your backend (default: `http://localhost:8000`).*

---

## � Project Structure

```text
├── index.html                  # Main Frontend Application
├── medical-chatbot-backend/    # FastAPI Backend Folder
│   ├── app/
│   │   ├── api/                # Route definitions (Auth, Chat, Feedback)
│   │   ├── core/               # App config, constants, and logging
│   │   ├── models/             # SQLAlchemy Database Models
│   │   ├── safety/             # Medical safety & emergency detection logic
│   │   ├── tools/              # AI Agent tools (Search, Symptom Checker)
│   │   └── main.py             # FastAPI entry point
│   ├── alembic/                # Database migration history
│   └── requirements.txt        # Backend dependencies
└── _deprecated_files/          # Archive of outdated components
```

---

## ⚖️ Disclaimer
**Important:** This application is for informational and educational purposes only. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider for any medical concerns or before making medical decisions.

---
*Developed with a focus on medical safety, user privacy, and intuitive design.*
