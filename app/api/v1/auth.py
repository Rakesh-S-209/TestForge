"""Authentication router — /api/v1/auth endpoints.

DEMO ONLY — not intended for production use.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import AuthService, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new demo user",
)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Register a new demo user.  Returns 409 if username or email already exists."""
    svc = AuthService(session)
    try:
        user = await svc.register(
            username=data.username,
            email=str(data.email),
            password=data.password,
        )
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse, summary="Login and receive a JWT")
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Authenticate and return a JWT bearer token.  Returns 401 on bad credentials."""
    svc = AuthService(session)
    try:
        user = await svc.authenticate(username=data.username, password=data.password)
        token = create_access_token(subject=user.username)
        return TokenResponse(access_token=token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
