# Plex Playlist Manager

A small FastAPI web app for browsing and managing Plex playlists.

## Deploy to an LXC container

The app runs as a systemd service inside an LXC container, installed from the
latest GitHub release wheel (same release pattern as `jb-filetools` /
`jb-download`, plus a systemd unit since this is a long-running web service).

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
- Service status / logs: `systemctl status plex-playlist-manager`,
  `journalctl -u plex-playlist-manager -f`
