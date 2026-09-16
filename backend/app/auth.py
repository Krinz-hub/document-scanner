"""Authentication, Authorization, and Role-Based Access Control (RBAC)."""

import hashlib
from typing import List, Optional
from fastapi import Header, HTTPException, status, Depends
from pydantic import BaseModel
from backend.app.config import get_settings

settings = get_settings()


class AuthenticatedUser(BaseModel):
    user_id: str
    username: str
    role: str  # PRIMARY_OFFICER, SUPERVISOR, AUDITOR


# Pre-configured operational identity tokens for local & station deployment
OPERATIONAL_CREDENTIALS = {
    "officer-token-secret": AuthenticatedUser(
        user_id="OFFICER-042",
        username="officer_lane1",
        role="PRIMARY_OFFICER",
    ),
    "supervisor-token-secret": AuthenticatedUser(
        user_id="SUPERVISOR-007",
        username="supervisor_smith",
        role="SUPERVISOR",
    ),
    "auditor-token-secret": AuthenticatedUser(
        user_id="AUDITOR-019",
        username="compliance_auditor",
        role="AUDITOR",
    ),
}


def get_current_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
) -> AuthenticatedUser:
    """Extract and validate authentication token from Authorization or X-API-Key header."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
    elif x_api_key:
        token = x_api_key.strip()

    # In development/test mode without headers, default to standard primary officer
    if not token:
        if settings.APP_ENV == "development" or settings.DEBUG:
            return AuthenticatedUser(
                user_id="OFFICER-DEFAULT",
                username="default_officer",
                role="PRIMARY_OFFICER",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token in OPERATIONAL_CREDENTIALS:
        return OPERATIONAL_CREDENTIALS[token]

    # Check HMAC hash or secret key match
    if token == settings.SECRET_KEY:
        return AuthenticatedUser(
            user_id="SYSTEM-ADMIN",
            username="admin",
            role="SUPERVISOR",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_roles(allowed_roles: List[str]):
    """Dependency factory enforcing role-based permissions."""
    def role_checker(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: User role '{user.role}' lacks required permissions ({', '.join(allowed_roles)})",
            )
        return user

    return role_checker


def hash_identifier(identifier: str) -> str:
    """One-way cryptographic hash (SHA-256) of document/passport identifiers for audit trails."""
    if not identifier:
        return ""
    salted = f"{identifier}:{settings.SECRET_KEY}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()
