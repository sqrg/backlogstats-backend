from pydantic import BaseModel


def _cover_url(image_id: str, size: str) -> str:
    return f"https://images.igdb.com/igdb/image/upload/t_{size}/{image_id}.jpg"


class IGDBCover(BaseModel):
    image_id: str
    url_thumb: str
    url_cover_small: str
    url_cover_big: str
    url_720p: str
    url_1080p: str

    @classmethod
    def from_image_id(cls, image_id: str) -> "IGDBCover":
        return cls(
            image_id=image_id,
            url_thumb=_cover_url(image_id, "thumb"),
            url_cover_small=_cover_url(image_id, "cover_small"),
            url_cover_big=_cover_url(image_id, "cover_big"),
            url_720p=_cover_url(image_id, "720p"),
            url_1080p=_cover_url(image_id, "1080p"),
        )


class IGDBReleaseDate(BaseModel):
    date: int | None
    human: str | None
    platform_name: str | None


class IGDBInvolvedCompany(BaseModel):
    name: str
    developer: bool
    publisher: bool


class IGDBSeriesResult(BaseModel):
    igdb_id: int
    name: str
    slug: str | None


class IGDBPlatform(BaseModel):
    igdb_id: int
    name: str
    db_id: int


class IGDBGameResult(BaseModel):
    igdb_id: int
    name: str
    slug: str | None
    url: str | None
    summary: str | None
    storyline: str | None
    cover: IGDBCover | None
    genres: list[str]
    themes: list[str]
    platforms: list[IGDBPlatform]
    release_dates: list[IGDBReleaseDate]
    first_release_date: int | None
    involved_companies: list[IGDBInvolvedCompany]
    game_modes: list[str]
    rating: float | None
    rating_count: int | None
    aggregated_rating: float | None
    aggregated_rating_count: int | None
    total_rating: float | None
    total_rating_count: int | None
    screenshot_image_ids: list[str]
    artwork_image_ids: list[str]
    category: int | None
    game_type: str | None
    status: int | None
    series: list[IGDBSeriesResult]

    @classmethod
    def from_igdb(
        cls,
        data: dict,
        platform_db_ids: dict[int, int] | None = None,
    ) -> "IGDBGameResult":
        cover_data = data.get("cover")
        cover = IGDBCover.from_image_id(cover_data["image_id"]) if cover_data else None
        platform_db_ids = platform_db_ids or {}

        release_dates = [
            IGDBReleaseDate(
                date=rd.get("date"),
                human=rd.get("human"),
                platform_name=rd.get("platform", {}).get("name")
                if rd.get("platform")
                else None,
            )
            for rd in data.get("release_dates", [])
        ]

        involved_companies = [
            IGDBInvolvedCompany(
                name=ic["company"]["name"],
                developer=ic.get("developer", False),
                publisher=ic.get("publisher", False),
            )
            for ic in data.get("involved_companies", [])
            if ic.get("company")
        ]

        return cls(
            igdb_id=data["id"],
            name=data["name"],
            slug=data.get("slug"),
            url=data.get("url"),
            summary=data.get("summary"),
            storyline=data.get("storyline"),
            cover=cover,
            genres=[g["name"] for g in data.get("genres", [])],
            themes=[t["name"] for t in data.get("themes", [])],
            platforms=[
                IGDBPlatform(
                    igdb_id=p["id"],
                    name=p["name"],
                    db_id=platform_db_ids.get(p["id"], -1),
                )
                for p in data.get("platforms", [])
            ],
            release_dates=release_dates,
            first_release_date=data.get("first_release_date"),
            involved_companies=involved_companies,
            game_modes=[gm["name"] for gm in data.get("game_modes", [])],
            rating=data.get("rating"),
            rating_count=data.get("rating_count"),
            aggregated_rating=data.get("aggregated_rating"),
            aggregated_rating_count=data.get("aggregated_rating_count"),
            total_rating=data.get("total_rating"),
            total_rating_count=data.get("total_rating_count"),
            screenshot_image_ids=[s["image_id"] for s in data.get("screenshots", [])],
            artwork_image_ids=[a["image_id"] for a in data.get("artworks", [])],
            category=data.get("category"),
            game_type=data["game_type"]["type"] if data.get("game_type") else None,
            status=data.get("status"),
            series=[
                IGDBSeriesResult(
                    igdb_id=c["id"],
                    name=c["name"],
                    slug=c.get("slug"),
                )
                for c in data.get("collections", [])
            ],
        )


class GameFromIGDB(BaseModel):
    igdb_id: int
