from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    OAuthCodeRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services import discord_auth, google_auth

# TODO: Apple Sign In — requires Apple Developer account and JWKS verification
# (apple_id column already exists on User). See auth-plan.md D7.

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.execute(
        select(User).where(User.email == body.email)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
            headers={"X-Error-Code": "email_conflict"},
        )
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.execute(select(User).where(User.email == body.email)).scalar_one_or_none()
    if (
        not user
        or not user.hashed_password
        or not verify_password(body.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    return _token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    payload = decode_token(body.refresh_token)
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return _token_response(user)


@router.post("/google", response_model=TokenResponse)
async def google(
    body: OAuthCodeRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    identity = await google_auth.exchange_code(body.code, body.redirect_uri)

    user = db.execute(
        select(User).where(User.google_id == identity.google_id)
    ).scalar_one_or_none()

    if not user:
        user = db.execute(
            select(User).where(User.email == identity.email)
        ).scalar_one_or_none()

    if not user:
        user = User(email=identity.email, google_id=identity.google_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.google_id:
        user.google_id = identity.google_id
        db.commit()
        db.refresh(user)

    return _token_response(user)


@router.post("/discord", response_model=TokenResponse)
async def discord(
    body: OAuthCodeRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    identity = await discord_auth.exchange_code(body.code, body.redirect_uri)

    user = db.execute(
        select(User).where(User.discord_id == identity.discord_id)
    ).scalar_one_or_none()

    if not user:
        user = db.execute(
            select(User).where(User.email == identity.email)
        ).scalar_one_or_none()

    if not user:
        user = User(email=identity.email, discord_id=identity.discord_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.discord_id:
        user.discord_id = identity.discord_id
        db.commit()
        db.refresh(user)

    return _token_response(user)
