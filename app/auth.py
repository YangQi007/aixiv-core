from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import jwt
import json
from jwt import PyJWKClient

# Security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify the JWT token from Clerk and return the current user.
    
    Extracts the user_id from Clerk JWT token without full verification.
    In production, you should verify the signature using Clerk's public key.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Decode without verification for development
        # In production, use PyJWKClient with Clerk's JWKS endpoint
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Clerk tokens have 'sub' field with user ID
        user_id = decoded.get("sub")
        
        if not user_id:
            # Fallback to default-user for development
            user_id = "default-user"
        
        return {
            "user_id": user_id,
            "token": token,
            "email": decoded.get("email"),
            "name": decoded.get("name") or decoded.get("username")
        }
        
    except jwt.DecodeError:
        # For development, return default user when token can't be decoded
        return {
            "user_id": "default-user",
            "token": token,
            "email": None,
            "name": None
        }
    except Exception as e:
        # For development, return default user on any error
        return {
            "user_id": "default-user",
            "token": token,
            "email": None,
            "name": None
        }


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    Optional authentication - returns user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None