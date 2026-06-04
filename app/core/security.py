# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt

from app.config import get_settings
from app.core.exceptions import AuthenticationError


def create_access_token(data: dict) -> str:
    """
    Generates a signed JWT access token.
    """
    
    # Fetch configurations
    settings = get_settings()
    
    # Copy the payload data to avoid modifying the original dict
    to_encode = data.copy()
    # Calculate token expiration timestamp (UTC)
    issued = datetime.now(timezone.utc)
    expire = issued + timedelta(minutes=settings.access_token_expire_minutes)
    # Add standard "exp" (expiration time) claim to the payload
    to_encode.update({"exp": expire, "iat": issued})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt

def verify_access_token(token: str) -> Optional[dict]:
    """
    Verifies the JWT token signature and expiration.
    Returns the decoded payload if valid, or None if invalid.
    """

    # Fetch configurations
    settings = get_settings()

    try:
        # Decode automatically validates signature and 'exp' claim
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    
    except jwt.JWTError:
        raise AuthenticationError("Invalid token")