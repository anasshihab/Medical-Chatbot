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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical AI Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "test_interface": "/test"
    }


# Test interface endpoint
@app.get("/test", response_class=HTMLResponse)
async def test_interface():
    """
    Simple test interface for the chatbot
    واجهة اختبار بسيطة - لا تعرض أي كود خلفي أو مفاتيح API
    """
    import os
    template_path = os.path.join(
        os.path.dirname(__file__),
        "templates",
        "test_interface.html"
    )
    
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


# Simple Chat Interface
@app.get("/chat", response_class=HTMLResponse)
async def simple_chat_interface():
    """
    Simple chat interface requested by user
    """
    import os
    template_path = os.path.join(
        os.path.dirname(__file__),
        "templates",
        "chat.html"
    )
    
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
