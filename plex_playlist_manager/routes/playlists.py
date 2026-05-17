"""HTTP routes for the playlists feature."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from plex_playlist_manager.plex_client import PlexClient
from plex_playlist_manager.services import (
    get_playlist_summaries,
    get_playlist_tree,
)

router = APIRouter()


def _get_plex_client(request: Request) -> PlexClient:
    """Dependency: return the shared PlexClient from app.state."""
    return request.app.state.plex_client


def _get_templates(request: Request) -> Jinja2Templates:
    """Dependency: return the shared Jinja2Templates from app.state."""
    return request.app.state.templates


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    client: PlexClient = Depends(_get_plex_client),
    templates: Jinja2Templates = Depends(_get_templates),
) -> HTMLResponse:
    """Landing page: list of editable music playlists."""
    playlists = await get_playlist_summaries(client)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"playlists": playlists},
    )


@router.get("/playlists/{playlist_id}/tree", response_class=HTMLResponse)
async def playlist_tree(
    request: Request,
    playlist_id: str,
    client: PlexClient = Depends(_get_plex_client),
    templates: Jinja2Templates = Depends(_get_templates),
) -> HTMLResponse:
    """Render the Artist -> Album -> Track tree for a playlist as a partial."""
    tree = await get_playlist_tree(client, playlist_id)
    return templates.TemplateResponse(
        request,
        "partials/playlist_tree.html",
        {"tree": tree},
    )
