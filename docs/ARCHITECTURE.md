# Plex Playlist Manager — Architecture

A local-use web tool for browsing and editing music playlists on a Plex
Media Server. Designed for one developer running it against their own Plex
server on a home network.

## Project goal

Provide a cleaner interface for managing Plex music playlists than the
native Plex web UI, which presents playlists as a single flat unsorted
track list — unworkable for playlists with thousands of tracks.

## Scope philosophy

This is a personal tool for a single developer running against their own
Plex server on a home network. It is explicitly NOT designed to be:

- Multi-user or multi-tenant
- Exposed to the public internet
- Deployed to production infrastructure

Design decisions throughout favor simplicity and local-use ergonomics over
scalability and hardening. The same machine that runs this app is expected
to have filesystem access to the Plex media library (either by running on
the Plex server itself or by mounting the same media share), which enables
direct file access for future features like playback.

---

## Technology stack

| Layer            | Choice                                | Rationale                                                |
| ---------------- | ------------------------------------- | -------------------------------------------------------- |
| Language         | Python 3.13                           | Newest stable with full ecosystem support                |
| Web framework    | FastAPI                               | Async, type-driven, pairs well with Jinja2               |
| Server           | uvicorn                               | Standard async server for FastAPI                        |
| Templates        | Jinja2                                | Native FastAPI integration                               |
| HTTP client      | httpx (async)                         | Modern, async-capable                                    |
| Config           | pydantic-settings                     | Typed config loaded from `.env`                          |
| Frontend CSS     | Tailwind CSS via Play CDN             | No build step; production switch possible later          |
| Frontend JS      | HTMX 1.9.x                            | Server-rendered HTML over JSON+SPA                       |
| Frontend JS      | Alpine.js 3.x                         | Client-side state; minimal footprint                     |
| Expand/collapse  | Native HTML `<details>`/`<summary>`   | Zero JS for tree expansion; accessible by default        |
| Plex access      | Official Plex HTTP API                | Documented contract; less likely to break unexpectedly   |

### Stack decisions explained

**FastAPI + Jinja2 + HTMX vs SPA.** A separate React/Vue frontend would
require a build pipeline, JSON API contracts, and client-side routing for
what is fundamentally CRUD over HTML pages. HTMX with server-rendered
partials eliminates an entire layer of complexity.

**Official Plex HTTP API vs `plexapi` library.** The community-maintained
`plexapi` Python library is widely used but not officially supported by
Plex. Working against the official HTTP API directly means working against
a documented contract, at the cost of slightly more code.

**Two-layer Pydantic models.** Plex API ingestion models
(`PlexPlaylistSummary`, `PlexTrackItem`) are kept separate from domain
models (`Track`, `Album`, `Artist`, `PlaylistTree`). This isolates Plex's
specific field naming (`grandparentTitle`, `parentTitle`) from the rest of
the codebase. If Plex renames a field, only the ingestion layer changes.

**Client-side surgical reconciliation (vs server-side re-render) on
mutations.** When a delete operation modifies the tree, the route returns
204 No Content and the client surgically removes affected DOM nodes and
recomputes every visible count in place. This preserves tree expand state,
scroll position, and letter filter without requiring server involvement
beyond confirming the delete succeeded. All count math is driven by
`data-*` attributes on rendered elements so no displayed text is ever
parsed back.

---

## Project structure

```
plex_playlist_manager/
├── .env                              # Plex URL and token (gitignored)
├── ARCHITECTURE.md                   # This document
├── HANDOFF.md                        # Current-state working notes
├── README.md
├── pyproject.toml
├── ruff.toml
├── plex_playlist_manager/
│   ├── __init__.py
│   ├── main.py                       # FastAPI app, lifespan, entry point
│   ├── config.py                     # pydantic-settings Settings class
│   ├── plex_client.py                # httpx async client for Plex HTTP API
│   ├── models.py                     # Pydantic models + tree builder
│   ├── services.py                   # Orchestration: client -> models
│   ├── scratch.py                    # Ad-hoc API experiments (gitignored)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── playlists.py              # /, /playlists/{id}/tree, /playlists/{id}/items
│   ├── templates/
│   │   ├── base.html                 # Shell: CDN scripts, palette, layout
│   │   ├── index.html                # Sidebar + tree container
│   │   └── partials/
│   │       └── playlist_tree.html    # Tree partial (Artist > Album > Track)
│   └── static/
│       ├── css/                      # Empty; reserved for future custom CSS
│       └── js/
│           └── playlist_tree.js      # Alpine component + reconciliation logic
└── tests/
    └── __init__.py                   # No tests yet
```

### Entry points

Two console scripts registered in `pyproject.toml`:

- `ppm` — runs the FastAPI app on `127.0.0.1:8765`
- `scratch` — runs `plex_playlist_manager/scratch.py` for ad-hoc API probes

The scratch script is gitignored. It exists as a sandbox for running
snippets against the live Plex API without polluting the main application.

### Layering

Code is divided into clear layers; each one calls only the layer below.

- **Routes** (`routes/playlists.py`) — HTTP I/O. Receives requests, calls
  services, renders templates or returns status codes.
- **Services** (`services.py`) — Orchestration. Combines client calls,
  validates raw responses into ingestion models, transforms into domain
  models, applies batch logic (sequential deletes, error tolerance).
- **Client** (`plex_client.py`) — Wraps a single async `httpx.AsyncClient`
  with the Plex token preset. One method per Plex API endpoint used.
  Returns raw dicts; no validation here.
- **Models** (`models.py`) — Pydantic types and the tree-building function.
  The boundary between Plex's wire format and the application's domain.

Reasoning: each layer can be replaced or tested without touching the
others. If Plex renames a field, only `models.py` changes. If we want to
support a different mutation policy, only `services.py` changes.

---

## Configuration

`.env` in the project root (gitignored):

```
PLEX_BASE_URL=http://<your-plex-server-ip>:32400
PLEX_TOKEN=<your-plex-token>
```

The token is retrieved from the Plex web app's XML view URL (the
`X-Plex-Token=...` query parameter). Treat it as a password.

Settings are loaded via `pydantic-settings` and validated at import time
(`HttpUrl` validates the URL format).

---

## Deployment

The intended deployment target is a Proxmox LXC container on the
developer's home server. The Plex Media Server itself runs in an LXC
container on the same Proxmox host.

### Two placement options

**Option A: run inside the existing Plex LXC.**

The app runs in the same container as Plex.

Advantages:
- Filesystem paths to media files match exactly with no mount
  configuration — the app sees the same paths Plex sees.
- `PLEX_BASE_URL` can point at `http://127.0.0.1:32400`.
- Fewer moving parts: one container to back up, snapshot, and maintain.

Disadvantages:
- Less isolation: a misbehaving build of this app can affect the Plex
  process.
- Plex container updates (Plex's own upgrades) might churn the
  environment around the app.

**Option B: run in a dedicated LXC.**

The app runs in its own container alongside Plex.

Advantages:
- Clean isolation. The app's Python environment, dependencies, and any
  future package additions don't touch the Plex container.
- Independent lifecycle: this container can be restarted, snapshotted,
  rebuilt, or destroyed without touching Plex.

Disadvantages:
- The media library directory must be explicitly bind-mounted into the
  container at the same path Plex uses, otherwise track file paths from
  Plex's metadata won't resolve. This is the critical configuration step
  for filesystem-based playback.
- `PLEX_BASE_URL` must point at the Plex container's IP and port.

**Current leaning:** Option A (inside the existing Plex LXC), since path
matching is automatic and the isolation tradeoff is acceptable for a
single-user local tool. Not yet committed.

### Requirements regardless of placement

- Python 3.13 available in the container.
- The `.env` file with `PLEX_BASE_URL` and `PLEX_TOKEN` configured.
- The `ppm` console script bound to `127.0.0.1:8765` by default. To expose
  the app to other machines on the LAN, change the bind host in
  `main.py`'s `run()` function or add a reverse proxy.
- Filesystem read access to the Plex media library paths (only required
  for future playback features).

---

## Current capabilities

### Browse

- Sidebar lists all editable music playlists (non-smart, audio type).
- Clicking a playlist renders an Artist -> Album -> Track tree.
- Native `<details>` elements allow independent expand/collapse at each
  level.
- Sticky alphabetical letter strip (A-Z plus `#`) filters the tree to one
  letter. Empty letters are rendered but disabled.
- Header shows artist count, track count, and total duration.

### Edit (deletion)

- Every track, album, and artist row has a Plex-style circular selector.
- Selecting a parent cascades selection to all descendant tracks.
- Parents whose children are partially selected show a dash glyph
  (indeterminate state).
- An action bar appears in the header when a selection exists, with a
  count, a Remove button, and Deselect All.
- Remove issues a batch DELETE; deletions run sequentially against Plex
  with errors recorded but not aborting the batch.
- On success, the client surgically removes deleted rows and reconciles
  every visible count (header, per-artist, per-album, letter strip,
  sidebar) in place. Tree expand state and scroll position are preserved.
- If the active letter filter is emptied by a delete, it falls back to ALL.

---

## Plex API characteristics

These are non-obvious behaviors of the Plex API that all current and
future code must account for.

### Smart playlists cannot be edited via API

Smart playlists are computed dynamically from filters; they have no stable
per-item IDs. The Plex API returns `playlistItemID: null` for their items,
making deletion impossible. They are excluded at the client level by
filtering on `smart == False`.

### `leafCount` vs `totalSize` discrepancy

Plex stores a playlist's reference count as `leafCount` and reports the
number of *retrievable* items as `totalSize`. These often differ. When
files are removed from the music library, Plex does not prune the
playlist's stored references — they become orphans. The orphans count
toward `leafCount` but not `totalSize`.

`totalSize` is the source of truth for what we can display and edit.
`leafCount` is misleading and is not surfaced in the UI.

### Pagination behavior

Plex's `/playlists/{id}/items` endpoint paginates large responses. Without
explicit `X-Plex-Container-Start` and `X-Plex-Container-Size` parameters,
the default response caps around 6,341 items. The client paginates with
page size 500 and uses `totalSize` from the response as the loop
termination signal.

### `playlistItemID` vs `ratingKey`

Each track has two distinct IDs:

- `ratingKey` — the track's library ID. Stable across playlists.
- `playlistItemID` — the per-playlist instance ID. Different in every
  playlist the track appears in.

Deletion is keyed on `playlistItemID`, not `ratingKey`. The same track
appearing in two playlists has two different `playlistItemID` values.

### Alphabetical bucketing rules

Following Plex's own convention:

- Leading articles ("the ", "a ", "an ") are stripped before bucketing.
- Accented characters normalize to their base letter via `NFKD`.
- Non-alphabetic first characters bucket to `#`.

### File paths in track metadata

Each track's full Plex metadata includes a `Media.Part.file` field
containing the absolute filesystem path of the audio file on the Plex
server. The current `PlexTrackItem` model does not capture this field; it
would need to be added if filesystem-based playback is implemented.

---

## Color palette

Plex's official brand colors (sourced from `brand.plex.tv`):

- Gamboge orange (`#e5a00d`) — accent
- Dark charcoal (`#282a2d`) — surfaces

The full Tailwind palette is defined inline in `base.html`:

| Token            | Hex       | Use                           |
| ---------------- | --------- | ----------------------------- |
| `plex-bg`        | `#1f1f1f` | Page background               |
| `plex-surface`   | `#282a2d` | Sidebar, headers, cards       |
| `plex-elevated`  | `#3a3a3a` | Hover states                  |
| `plex-accent`    | `#e5a00d` | Active selection, brand mark  |
| `plex-accentHi`  | `#f5b62b` | Accent hover                  |
| `plex-text`      | `#ffffff` | Primary text                  |
| `plex-muted`     | `#b0b0b0` | Secondary text                |
| `plex-border`    | `#3a3a3a` | Dividers                      |

---

## Roadmap

The following feature areas are anticipated but not yet built. Each is
described at the level of shape and key questions — specific design
decisions are made when the feature is picked up.

### Playlist-level CRUD: create, delete, rename

Currently the app reads playlists and edits tracks within them. Missing
operations:

- Create a new empty playlist.
- Delete an entire playlist.
- Rename a playlist.

**Plex API endpoints involved:**

- `POST /playlists?type=audio&title=...&smart=0&uri=...` — create.
- `DELETE /playlists/{id}` — delete entire playlist.
- `PUT /playlists/{id}?title=...` — rename.

**UI surface:** likely a "+ New playlist" affordance at the bottom of the
sidebar, and a contextual menu on each sidebar entry for rename and
delete. Confirmation for delete; rename in-place or via a small modal.

**Open questions:**

- Creation flow: empty playlist + then add, or pick initial tracks first?
- Confirmation pattern for delete: dedicated dialog, or "type the name to
  confirm"?

### Adding tracks to a playlist

A way to browse or search the Plex library and add selected tracks to a
chosen playlist.

**Two complementary discovery modes:**

1. **Browse:** flat artist list (filterable by letter, same pattern as
   the playlist tree). Click an artist to open their catalog (albums
   expandable to tracks). Add buttons at track, album, and artist levels.

2. **Search:** a search box that hits Plex's search endpoint and shows
   matching tracks, albums, and artists with the same selector and "add
   to playlist" affordances.

Both modes share the same destination-playlist picking model and the same
add API.

**Plex API endpoints involved:**

- `GET /library/sections` — find the Music library section ID.
- `GET /library/sections/{id}/all?type=8` — all artists (type 8).
- `GET /library/metadata/{artist_id}/children` — albums for an artist.
- `GET /library/metadata/{album_id}/children` — tracks in an album.
- `GET /search?query=...&sectionId=...` — search.
- `PUT /playlists/{id}/items?uri=...` — add items to a playlist.

**Open questions:**

- Destination-picking UX. Options previously surfaced:
  - One-click add to a "currently selected" playlist.
  - Per-click playlist selection via dropdown.
  - Staging tray that accumulates items and flushes in one batch.
- Browse vs search as primary entry point, or equal weight.
- Whether the library view replaces the tree view or shows alongside it.

### In-tool playback via direct filesystem access

The app should be able to play tracks directly so the user can audition
music while building playlists.

**Approach:** serve audio files directly from the local filesystem rather
than streaming through Plex. The machine running this app has filesystem
access to the same media library Plex sees (either by running on the Plex
server or by mounting the same media share). Plex provides each track's
absolute file path in its metadata; the app reads the file from disk and
streams it to the browser via a FastAPI `StreamingResponse`.

**Why this over streaming through Plex:**

- No Plex token exposure in the browser.
- No transcoding API to navigate (Plex's transcoding endpoints are poorly
  documented for third-party use).
- No byte-range proxying complexity beyond what FastAPI's
  `StreamingResponse` and `Range` header support handle natively.
- Browsers handle the audio decoding; format support is whatever the
  browser supports natively (MP3, AAC reliably; FLAC and ALAC in modern
  browsers).

**Required changes:**

- Extend `PlexTrackItem` to capture `Media.Part.file`.
- Update `Track` (domain model) with `file_path`.
- New route: `GET /audio/{rating_key}` returns the file bytes (or a 416
  range response) with the right `Content-Type` based on file extension.
- New UI element: a persistent player bar at the bottom of the layout,
  living outside the HTMX-swapped regions so navigation between playlists
  doesn't destroy it.
- Per-track play affordance in the tree (a play button on each row, or
  click-to-play on the row itself).
- Optional: a queue model so multiple tracks can play in sequence.

**Open questions:**

- Player library: native `<audio>` element, or a styled wrapper like Plyr?
- Click target on a track row: dedicated play button, or whole-row click
  (which currently does nothing)?
- Queue semantics: implicit (clicking a track plays it, no queue), or
  explicit ("add to queue" vs "play now")?
- Handling formats browsers don't support natively (DSD, some ALAC
  variants): fall back to a "not playable" indicator, or attempt
  server-side transcoding via ffmpeg?

---

## Conventions

### Process for new features

A pattern that worked well during Phase 1 and Phase 2 and should continue:

1. Discuss the feature's scope and surface design decisions explicitly.
2. Identify edge cases and ask about them before writing code.
3. Build backend pieces first (client, models, services).
4. Verify each backend piece via the `scratch.py` test bed before moving on.
5. Build templates and frontend last, after backend data flow is confirmed.

Avoid building multiple layers speculatively. Each step ends with a
verification that informs the next.

### Ruff configuration

The project uses Ruff with a strict ruleset. Two notable customizations:

- `flake8-bugbear`'s `extend-immutable-calls` whitelists FastAPI's
  `Depends`, `Query`, `Path`, etc., so the framework's normal pattern of
  calling them in argument defaults doesn't trigger `B008`.
- `target-version = "py313"` matches `requires-python` in `pyproject.toml`.

### Frontend JS organization

Application JS lives in `static/js/`. The Alpine component for the
playlist tree (`playlist_tree.js`) is registered as a global function
(`window.playlistTree`) and referenced from the template via
`x-data="playlistTree()"`. Inline multi-line JS in HTML attributes is
avoided — methods on the component are called instead.

CDN scripts (HTMX, Alpine, Tailwind) stay in `base.html`. They are
framework dependencies, not application code.