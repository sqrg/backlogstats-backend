from __future__ import annotations

from datetime import datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.game_type import GameType
from app.models.genre import Genre
from app.models.platform import Platform

_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
_IGDB_GAMES_URL = "https://api.igdb.com/v4/games"
_IGDB_GAME_TYPES_URL = "https://api.igdb.com/v4/game_types"
_IGDB_GENRES_URL = "https://api.igdb.com/v4/genres"
_IGDB_PLATFORMS_URL = "https://api.igdb.com/v4/platforms"

_IGDB_FIELDS = (
    "fields id, name, slug, url, summary, storyline, status,"
    " first_release_date,"
    " cover.image_id, cover.url,"
    " genres.name, themes.name, platforms.name,"
    " release_dates.date, release_dates.human, release_dates.platform.name,"
    " involved_companies.company.name, involved_companies.developer, involved_companies.publisher,"
    " game_modes.name,"
    " rating, rating_count,"
    " aggregated_rating, aggregated_rating_count,"
    " total_rating, total_rating_count,"
    " screenshots.image_id, artworks.image_id,"
    " collections.id, collections.name, collections.slug,"
    " game_type.type, dlcs;"
)


class IGDBService:
    def __init__(self) -> None:
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    def _credentials_configured(self) -> bool:
        return bool(settings.IGDB_CLIENT_ID and settings.IGDB_CLIENT_SECRET)

    async def _get_access_token(self) -> str:
        now = datetime.now()
        if (
            self._access_token
            and self._token_expires_at
            and now < self._token_expires_at
        ):
            return self._access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                _TOKEN_URL,
                params={
                    "client_id": settings.IGDB_CLIENT_ID,
                    "client_secret": settings.IGDB_CLIENT_SECRET,
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            data = response.json()

        self._access_token = data["access_token"]
        # Buffer of 60 seconds so we never use a token right at expiry.
        self._token_expires_at = now + timedelta(seconds=data["expires_in"] - 60)
        return self._access_token

    async def _headers(self) -> dict[str, str]:
        token = await self._get_access_token()
        return {
            "Client-ID": settings.IGDB_CLIENT_ID,
            "Authorization": f"Bearer {token}",
        }

    async def search_games(self, query: str, limit: int = 10) -> list[dict]:
        # IGDB rate limit: 4 req/s, 8 concurrent. No automatic retry in v1 —
        # the router surfaces 429 directly so clients can back off.
        body = f'search "{query}";\n{_IGDB_FIELDS}\nlimit {limit};'
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(_IGDB_GAMES_URL, headers=headers, data=body)
            response.raise_for_status()
        return response.json()

    async def fetch_game(self, igdb_id: int) -> dict | None:
        body = f"where id = {igdb_id};\n{_IGDB_FIELDS}\nlimit 1;"
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(_IGDB_GAMES_URL, headers=headers, data=body)
            response.raise_for_status()
        results = response.json()
        return results[0] if results else None

    async def sync_game_types(self, db: Session) -> list[GameType]:
        body = "fields id, type; limit 50;"
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                _IGDB_GAME_TYPES_URL, headers=headers, data=body
            )
            response.raise_for_status()
        for item in response.json():
            db.merge(GameType(id=item["id"], type=item["type"]))
        db.commit()
        return list(db.execute(select(GameType)).scalars().all())

    async def sync_genres(self, db: Session) -> list[Genre]:
        body = "fields id, name; limit 500; sort id asc;"
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                _IGDB_GENRES_URL, headers=headers, content=body.encode()
            )
            response.raise_for_status()
        for item in response.json():
            existing = db.execute(
                select(Genre).where(Genre.name == item["name"])
            ).scalar_one_or_none()
            if not existing:
                db.add(Genre(name=item["name"]))
        db.commit()
        return list(db.execute(select(Genre).order_by(Genre.name)).scalars().all())

    async def sync_platforms(self, db: Session) -> list[Platform]:
        body = "fields id, name; limit 500; sort id asc;"
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                _IGDB_PLATFORMS_URL, headers=headers, content=body.encode()
            )
            response.raise_for_status()
        for item in response.json():
            existing = db.execute(
                select(Platform).where(Platform.name == item["name"])
            ).scalar_one_or_none()
            if not existing:
                db.add(Platform(name=item["name"]))
        db.commit()
        return list(
            db.execute(select(Platform).order_by(Platform.name)).scalars().all()
        )


igdb_service = IGDBService()
