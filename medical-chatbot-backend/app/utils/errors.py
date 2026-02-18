"""Custom exceptions for the application"""
from typing import Any, Dict, Optional
from app.utils.constants import ErrorCode


class AppException(Exception):
    """Base exception class for application errors"""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class PlanLimitReachedException(AppException):
    """Raised when user exceeds plan limits — carries structured CTA payload."""

    def __init__(self, limit: int, plan_type: str = "guest", details: Optional[Dict[str, Any]] = None):
        details = details or {}

        # Build human-friendly CTA copy based on plan
        if plan_type == "guest":
            cta_title = "هل تريد المزيد من الإجابات؟"
            cta_body = (
                f"لقد استخدمت أسئلتك المجانية الـ {limit} كزائر. "
                "أنشئ حساباً مجانياً الآن للحصول على 5 أسئلة كل 6 ساعات، "
                "أو اطّلع على خططنا للوصول غير المحدود."
            )
        else:
            cta_title = "لقد استنفدت حصتك"
            cta_body = (
                f"لقد وصلت إلى حد الـ {limit} أسئلة لهذه الدورة. "
                "يرجى الانتظار حتى إعادة التعيين أو الترقية إلى Pro."
            )

        details.update({
            "code": "LIMIT_REACHED",
            "cta_title": cta_title,
            "cta_body": cta_body,
            "limit": limit,
            "plan_type": plan_type,
        })

        super().__init__(
            code=ErrorCode.PLAN_LIMIT_REACHED,
            message=f"You have reached your plan limit of {limit} questions per 6-hour window.",
            details=details,
            status_code=403
        )


class UnauthorizedException(AppException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            details=details,
            status_code=401
        )


class ValidationException(AppException):
    """Raised when request validation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=400
        )


class OpenAIException(AppException):
    """Raised when OpenAI API fails"""
    
    def __init__(self, message: str = "AI service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.OPENAI_ERROR,
            message=message,
            details=details,
            status_code=503
        )


class NotFoundException(AppException):
    """Raised when resource is not found"""
    
    def __init__(self, resource: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=f"{resource} not found",
            details=details,
            status_code=404
        )


class AlreadyExistsException(AppException):
    """Raised when resource already exists"""
    
    def __init__(self, resource: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.ALREADY_EXISTS,
            message=f"{resource} already exists",
            details=details,
            status_code=409
        )
