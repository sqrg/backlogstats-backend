from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.routers import (
    auth,
    companies,
    game_in_collection,
    game_types,
    games,
    genres,
    import_legacy,
    platforms,
    playthroughs,
    public_lists,
    series,
    stats,
    user_list_entries,
    user_lists,
    users,
)

app = FastAPI(
    title="Backlogstats API",
    version="0.1.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=_API_PREFIX)
app.include_router(users.router, prefix=_API_PREFIX)
app.include_router(games.router, prefix=_API_PREFIX)
app.include_router(genres.router, prefix=_API_PREFIX)
app.include_router(platforms.router, prefix=_API_PREFIX)
app.include_router(companies.router, prefix=_API_PREFIX)
app.include_router(game_in_collection.router, prefix=_API_PREFIX)
app.include_router(playthroughs.router, prefix=_API_PREFIX)
app.include_router(series.router, prefix=_API_PREFIX)
app.include_router(game_types.router, prefix=_API_PREFIX)
app.include_router(user_lists.router, prefix=_API_PREFIX)
app.include_router(user_list_entries.router, prefix=_API_PREFIX)
app.include_router(public_lists.router, prefix=_API_PREFIX)
app.include_router(stats.router, prefix=_API_PREFIX)
app.include_router(import_legacy.router, prefix=_API_PREFIX)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code_map = {
        404: "not_found",
        405: "method_not_allowed",
        403: "forbidden",
    }
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": code_map.get(exc.status_code, "http_error"),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "code": "validation_error",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "code": "internal_server_error",
        },
    )


@app.get("/health")
async def health() -> dict:
    return {
        "app": "Backlogstats API",
        "version": "0.1.0",
        "env": settings.APP_ENV,
    }
