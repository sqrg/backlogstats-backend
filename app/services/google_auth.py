from dataclasses import dataclass

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
_VALID_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


@dataclass
class GoogleIdentity:
    google_id: str
    email: str


async def exchange_code(code: str, redirect_uri: str) -> GoogleIdentity:
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            _TOKEN_URL,
            data={
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "grant_type": "authorization_code",
            },
        )
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange Google authorization code",
        )
    id_token = token_response.json().get("id_token")
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token response missing id_token",
        )
    return await _verify_id_token(id_token)


async def _verify_id_token(id_token: str) -> GoogleIdentity:
    async with httpx.AsyncClient() as client:
        certs_response = await client.get(_CERTS_URL)
        certs_response.raise_for_status()
    jwks = certs_response.json()

    try:
        header = jwt.get_unverified_header(id_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

    kid = header.get("kid")
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google signing key not found",
        )

    try:
        payload = jwt.decode(
            id_token,
            key,
            algorithms=["RS256"],
            audience=settings.GOOGLE_CLIENT_ID,
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

    if payload.get("iss") not in _VALID_ISSUERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token issuer",
        )

    google_id = payload.get("sub")
    email = payload.get("email")
    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID token missing required claims",
        )

    return GoogleIdentity(google_id=google_id, email=email)
