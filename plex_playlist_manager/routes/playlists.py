"""HTTP routes for the playlists feature."""

import logging

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from plex_playlist_manager.plex_client import PlexClient
from plex_playlist_manager.services import (
    delete_playlist_items,
    get_playlist_summaries,
    get_playlist_tree,
)

logger = logging.getLogger(__name__)

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


@router.delete("/playlists/{playlist_id}/items", response_class=HTMLResponse)
async def delete_items(
    request: Request,
    playlist_id: str,
    playlist_item_id: list[int] = Query(...),
    client: PlexClient = Depends(_get_plex_client),
    templates: Jinja2Templates = Depends(_get_templates),
) -> HTMLResponse:
    """Delete one or more items from a playlist, then re-render the tree.

    Accepts repeated query parameters:
        ?playlist_item_id=123&playlist_item_id=456

    Deletions run sequentially. Failures are logged and recorded but do not
    abort the batch. After processing, the full updated tree is returned as
    HTML for HTMX to swap into the page.
    """
    result = await delete_playlist_items(client, playlist_id, playlist_item_id)
    logger.info(
        f"Delete batch for playlist {playlist_id}: "
        f"{len(result.succeeded)} succeeded, {len(result.failed)} failed "
        f"(attempted {result.total_attempted})"
    )

    tree = await get_playlist_tree(client, playlist_id)
    return templates.TemplateResponse(
        request,
        "partials/playlist_tree.html",
        {"tree": tree},
    )
