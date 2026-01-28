"""JWT authentication utilities"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
from app.utils.errors import UnauthorizedException


def create_access_token(user_id: int) -> str:
    """Create JWT access token for user"""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> int:
    """Decode JWT token and return user_id"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise UnauthorizedException("Invalid token")
        
        return int(user_id)
        
    except JWTError as e:
        raise UnauthorizedException(f"Invalid token: {str(e)}")


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract token from Authorization header"""
    if not authorization:
        return None
    
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]
