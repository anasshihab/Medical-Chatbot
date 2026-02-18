"""Main FastAPI application"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from app.config import settings
from app.utils.errors import AppException
from app.schemas.error import ErrorResponse, ErrorDetail
from app.api import auth, chat, conversations, profile, feedback

# Create FastAPI app
app = FastAPI(
    title="Medical AI Chatbot API",
    description="Production-ready medical chatbot backend with agentic AI capabilities",
    version="1.0.0"
)

# Setup logging
from app.core.logging_config import setup_logging

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    setup_logging()

# ---------------------------------------------------------------------------
# CORS — Explicit origin list (wildcard + credentials is rejected by browsers)
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = [
    # ── Production Vercel frontend ──────────────────────────────────────────
    "https://medical-chatbot-ashy.vercel.app",   # <-- your main Vercel domain
    "https://*.vercel.app",                       # Vercel preview deployments
    "https://*.vercel.live",                      # Vercel Live share links
    # ── Render backend (self-calls / health checks) ─────────────────────────
    "https://medical-chatbot-1-m6re.onrender.com",
    # ── Local development ───────────────────────────────────────────────────
    "http://localhost:3000",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",  # catch all preview URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin",
                   "X-Requested-With", "X-Forwarded-For"],
    expose_headers=["Content-Length"],
    max_age=600,  # preflight cache: 10 minutes
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                details=exc.details
            )
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    from app.utils.constants import ErrorCode
    
    # Log the error (in production, use proper logging)
    print(f"Unexpected error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred",
                details={"error": str(exc) if settings.DEBUG else "Internal server error"}
            )
        ).model_dump()
    )


# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(profile.router)
app.include_router(feedback.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Helper to serve chat template
def get_chat_template():
    import os
    template_path = os.path.join(
        os.path.dirname(__file__),
        "templates",
        "chat.html"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


# Root endpoint - serves chat interface
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - Serves premium chat interface"""
    return HTMLResponse(content=get_chat_template())


# Test interface endpoint - also serves premium chat interface
@app.get("/test", response_class=HTMLResponse)
async def test_interface():
    """
    Main chat interface (replaces old test interface)
    """
    return HTMLResponse(content=get_chat_template())


# Simple Chat Interface
@app.get("/chat", response_class=HTMLResponse)
async def simple_chat_interface():
    """
    Premium chat interface
    """
    return HTMLResponse(content=get_chat_template())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
