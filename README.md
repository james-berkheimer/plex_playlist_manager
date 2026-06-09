# Plex Playlist Manager

A small [FastAPI](https://fastapi.tiangolo.com/) web app for browsing and
pruning **music playlists** on a Plex Media Server. It renders each playlist as
an Artist → Album → Track tree and lets you remove tracks (or whole albums /
artists) with a Plex-style multi-select, issuing batch deletes against the Plex
API.

## Features

**Browse**
- Sidebar lists every editable music playlist (non-smart, audio type).
- Selecting a playlist renders an Artist → Album → Track tree with independent
  expand/collapse at each level.
- Sticky A–Z letter strip filters the tree to one letter; the header shows
  artist count, track count, and total duration.

**Edit (deletion)**
- Circular selectors on every track / album / artist row; selecting a parent
  cascades to its descendants (with an indeterminate "dash" state for partial
  selections).
- An action bar with a live count, **Remove**, and **Deselect All** appears when
  anything is selected.
- **Remove** issues a batch `DELETE`; deletions run sequentially and a failure
  on one item doesn't abort the batch. On success the page reconciles all
  counts in place without losing expand state or scroll position.

> Smart playlists are intentionally excluded — Plex returns `playlistItemID: null`
> for their items, so they can't be edited via the API. See
> [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for this and other Plex API
> quirks the code accounts for.

## Tech stack

- **Python 3.12+**, FastAPI + Uvicorn
- Jinja2 server-rendered templates, vanilla JS (no build step)
- `httpx` against the Plex HTTP API
- `pydantic-settings` for configuration

## Configuration

Settings are read from environment variables or a `.env` file in the working
directory:

| Variable        | Description                                  | Example                        |
| --------------- | -------------------------------------------- | ------------------------------ |
| `PLEX_BASE_URL` | Base URL of your Plex Media Server           | `http://192.168.1.45:32400`    |
| `PLEX_TOKEN`    | A Plex auth token ([how to find it][token])  | `xxxxxxxxxxxxxxxxxxxx`          |

`.env` is gitignored — keep your token out of version control.

[token]: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

## Local development

```bash
git clone git@github.com:james-berkheimer/plex_playlist_manager.git
cd plex_playlist_manager

python3 -m venv .venv && source .venv/bin/activate
pip install -e .

printf 'PLEX_BASE_URL=http://<plex-ip>:32400\nPLEX_TOKEN=<your-token>\n' > .env

ppm                 # serves http://127.0.0.1:8765
```

`ppm` is the console entry point (defined in `pyproject.toml`); it runs Uvicorn
bound to localhost. Health check: `GET /health` → `{"status": "ok"}`.

## Deploy to an LXC container

The app runs as a systemd service inside an LXC container, installed from the
latest GitHub release wheel (same release pattern as `jb-filetools` /
`jb-download`, plus a systemd unit since this is a long-running web service).
Releases are cut automatically by CI on every push to `main`.

1. **Authorize SSH access** (one time, from your workstation):

   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519.pub root@<container-ip>
   ```

2. **Install** (pulls the latest release + creates the service):

   ```bash
   ssh root@<container-ip> 'curl -L \
     https://github.com/james-berkheimer/plex_playlist_manager/releases/latest/download/install-plex-playlist-manager.tar.gz \
     | tar xz -C /tmp && bash /tmp/plex-playlist-manager-installer/install.sh'
   ```

   The installer creates a venv in `/opt/plex-playlist-manager`, installs the
   wheel, and writes a systemd unit running Uvicorn bound to `0.0.0.0:8765`
   (LAN-reachable, unlike the localhost-only `ppm` default).

3. **Configure Plex credentials** in `/opt/plex-playlist-manager/.env`:

   ```ini
   PLEX_BASE_URL=http://<plex-ip>:32400
   PLEX_TOKEN=<your-token>
   ```

   Then restart: `systemctl restart plex-playlist-manager`

4. **Access** the app at `http://<container-ip>:8765`.

### Maintenance

- Update to the latest release: `ppm_update`
- Remove completely: `ppm_uninstall`
- Status / logs: `systemctl status plex-playlist-manager`,
  `journalctl -u plex-playlist-manager -f`

> **Repo prerequisites for the release pipeline** (one-time GitHub settings):
> the `origin` remote must use **SSH** (the HTTPS token can't push workflow
> files), and Actions **workflow permissions** must be **read and write** (so CI
> can tag versions and create releases).

## Project layout

```
plex_playlist_manager/
├── plex_playlist_manager/
│   ├── main.py            # FastAPI app, lifespan, ppm entry point
│   ├── config.py          # pydantic-settings (PLEX_BASE_URL, PLEX_TOKEN)
│   ├── plex_client.py     # thin async httpx client for the Plex API
│   ├── services.py        # orchestration: client -> domain models
│   ├── models.py          # PlaylistSummary, PlaylistTree, ...
│   ├── routes/            # FastAPI routers (browse + delete)
│   ├── templates/         # Jinja2 templates + partials
│   └── static/            # client-side JS (playlist_tree.js)
├── docs/ARCHITECTURE.md   # design rationale + Plex API characteristics
├── install.sh             # LXC installer (packaged into each release)
└── tests/
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design rationale,
deployment placement options, and a catalogue of non-obvious Plex API behaviors
(smart-playlist exclusion, `leafCount` vs `totalSize`, container pagination)
that the code is built around.
