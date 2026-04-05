import asyncio
import urllib.request as _urllib_request
from dataclasses import dataclass

import httpx
from fastapi import HTTPException, status
from google.oauth2 import id_token as google_id_token

from app.core.config import settings

_TOKEN_URL = "https://oauth2.googleapis.com/token"


class _UrllibRequest:
    """Minimal google-auth transport adapter using stdlib urllib (no `requests` needed)."""

    def __call__(self, url, method="GET", body=None, headers=None, **kwargs):
        req = _urllib_request.Request(url, method=method)
        with _urllib_request.urlopen(req) as resp:
            self.status = resp.status
            self.data = resp.read()
            self.headers = dict(resp.headers)
        return self


_google_request = _UrllibRequest()


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


async def _verify_id_token(id_token_str: str) -> GoogleIdentity:
    loop = asyncio.get_event_loop()
    try:
        payload = await loop.run_in_executor(
            None,
            lambda: google_id_token.verify_oauth2_token(
                id_token_str,
                _google_request,
                settings.GOOGLE_CLIENT_ID,
            ),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

    google_id = payload.get("sub")
    email = payload.get("email")
    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID token missing required claims",
        )

    return GoogleIdentity(google_id=google_id, email=email)
