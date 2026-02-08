# Medical Chatbot Backend - Technical Documentation

## 1. Architecture Overview
The backend is built as a production-ready FastAPI application, focusing on modularity, scalability, and stability.

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance asynchronous web framework.
- **Database**: [PostgreSQL](https://www.postgresql.org/) - Relational database for persistent storage.
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) - Modern asynchronous mapping for database operations.
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/) - Database schema version control.
- **AI Engine**: [OpenAI GPT-4o](https://platform.openai.com/) - Orchestrated via an agentic system.
- **Security**: [JOSE (JWT)](https://python-jose.readthedocs.io/) and [Passlib](https://passlib.readthedocs.io/) for authentication and hashing.

## 2. Environment Setup

### Dependencies
Install the required packages using the virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration (.env)
Create a `.env` file in the root directory based on `.env.example`. Key variables include:
- `DATABASE_URL`: Connection string for PostgreSQL.
- `OPENAI_API_KEY`: Your OpenAI secret key.
- `SECRET_KEY`: Random string for signing JWT tokens.
- `ENVIRONMENT`: `development` or `production`.

### Database Initialization
Apply migrations to set up the schema:
```powershell
alembic upgrade head
```

## 3. Core Components

### Authentication
- **User Mode**: standard JWT-based authentication via `/api/auth/signup` and `/api/auth/login`.
- **Guest Mode**: Session-based tracking for unauthenticated users, managed via `guest_session_id`.
- **Merging**: When a guest signs up, their conversation history is automatically merged into their new user account.

### Database Connection Handling
Implemented in [database.py](file:///c:/Users/Fa3el5eerA/Desktop/Medical%20Chatbot/medical-chatbot-backend/app/database.py) using a connection pool for efficiency and health checks (`pool_pre_ping`).
- `get_db()`: A dependency that provides a thread-safe database session per request.

### API & Endpoint Structure
The API is divided into logical routers:
- `auth.py`: Registration, login, and user profile management.
- `chat.py`: The heart of the application, handling streaming AI responses.
- `conversations.py`: CRUD operations for message history.
- `feedback.py`: Capturing user ratings on AI responses.

## 4. AI Agent & Cost Tracking

### Agentic AI
The agent uses a multi-step process:
1. **Decision Maker**: Analyzes if tools (Search, Symptom Checker) are needed using GPT-3.5.
2. **Tool Execution**: Searches medical sources or analyzes symptoms.
3. **Search Recency**: The agent can now prioritize recent information using the `timelimit` parameter, ensuring the latest medical updates are retrieved.
4. **Response Generation**: Streams the final answer using GPT-4o with citations and publication dates when available.

### Cost Tracking
Every AI interaction is logged with its actual dollar cost based on token usage.
- **Utility**: [cost_calculator.py](file:///c:/Users/Fa3el5eerA/Desktop/Medical%20Chatbot/medical-chatbot-backend/app/utils/cost_calculator.py)
- **Visibility**: Costs are printed directly to the terminal for monitoring API spend.

## 5. Error Handling & Logging

### Global Exception Handler
Standardized error responses are handled in `main.py` using a custom `AppException` class. This ensures the frontend receives consistent JSON error objects even for unexpected crashes.

### Logging Strategy
- **Console**: Real-time information, including AI costs and request status.
- **File**: Persistent logs stored in `/logs/medical_chatbot.log` for debugging production issues.

## 6. Deployment Workflow

1. **Local Testing**: Run via `uvicorn app.main:app --reload`.
2. **Migrations**: Always run `alembic revision --autogenerate` after model changes.
3. **Production Readiness**:
   - Set `DEBUG=False` in `.env`.
   - Use a production-grade server like `gunicorn` with `uvicorn` workers.
   - Configure `CORS_ORIGINS` to point to your frontend domain.

## 7. Best Practices Applied
- **Security**: JWT validation, password hashing, and CORS protection.
- **Scalability**: Connection pooling and stateless authentication.
- **Maintainability**: Clear separation of concerns between models, schemas, and logic.
- **Streaming**: Using Server-Sent Events (SSE) for low-latency AI responses.
