from dataclasses import dataclass

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

_TOKEN_URL = "https://discord.com/api/oauth2/token"
_USER_URL = "https://discord.com/api/users/@me"


@dataclass
class DiscordIdentity:
    discord_id: str
    email: str


async def exchange_code(code: str, redirect_uri: str) -> DiscordIdentity:
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            _TOKEN_URL,
            data={
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.DISCORD_CLIENT_ID,
                "client_secret": settings.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
            },
        )
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange Discord authorization code",
        )
    access_token = token_response.json().get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discord token response missing access_token",
        )
    return await _fetch_user(access_token)


async def _fetch_user(access_token: str) -> DiscordIdentity:
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            _USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if user_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch Discord user",
        )
    data = user_response.json()
    discord_id = data.get("id")
    email = data.get("email")
    if not discord_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discord user missing required fields — ensure the email scope is requested",
        )
    return DiscordIdentity(discord_id=discord_id, email=email)
