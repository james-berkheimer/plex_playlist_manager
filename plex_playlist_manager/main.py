"""FastAPI application entry point for Plex Playlist Manager."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from plex_playlist_manager.config import Settings, get_settings
from plex_playlist_manager.plex_client import PlexClient
from plex_playlist_manager.routes.playlists import router as playlists_router

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create and tear down shared resources for the app's lifetime."""
    settings = get_settings()
    client = PlexClient(settings)
    app.state.plex_client = client
    app.state.settings = settings
    app.state.templates = templates
    try:
        yield
    finally:
        await client.close()


app = FastAPI(title="Plex Playlist Manager", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_plex_client(request: Request) -> PlexClient:
    """Dependency: return the shared PlexClient stored on app.state."""
    return request.app.state.plex_client


def get_app_settings(request: Request) -> Settings:
    """Dependency: return the shared Settings stored on app.state."""
    return request.app.state.settings


app.include_router(playlists_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple liveness check."""
    return {"status": "ok"}


def run() -> None:
    """Console script entry point: run the app under uvicorn."""
    uvicorn.run(
        "plex_playlist_manager.main:app",
        host="127.0.0.1",
        port=8765,
        reload=False,
    )
