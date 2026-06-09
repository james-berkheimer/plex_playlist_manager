#!/bin/bash
set -e

VENV_PATH="/opt/plex-playlist-manager/venv"
INSTALL_DIR="/opt/plex-playlist-manager"
SERVICE_NAME="plex-playlist-manager"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
REPO="james-berkheimer/plex_playlist_manager"
BIND_HOST="0.0.0.0"
BIND_PORT="8765"

echo "=== Installing dependencies ==="
apt update
apt install -y python3 python3-venv python3-pip curl

echo "=== Creating installation directory ==="
mkdir -p "$VENV_PATH"

echo "=== Creating virtual environment ==="
python3 -m venv "$VENV_PATH"
"$VENV_PATH/bin/pip" install --upgrade pip setuptools wheel

echo "=== Downloading latest plex-playlist-manager wheel ==="
LATEST_VERSION=$(curl -s https://api.github.com/repos/${REPO}/releases/latest | grep -Po '"tag_name": "v\K[^"]+')
if [ -z "$LATEST_VERSION" ]; then
  echo "Error: Unable to fetch latest plex-playlist-manager version from GitHub."
  exit 1
fi
WHEEL="plex_playlist_manager-${LATEST_VERSION}-py3-none-any.whl"
curl -fL -o "/tmp/${WHEEL}" \
  "https://github.com/${REPO}/releases/download/v${LATEST_VERSION}/${WHEEL}"

echo "=== Installing plex-playlist-manager v${LATEST_VERSION} ==="
"$VENV_PATH/bin/pip" install "/tmp/${WHEEL}"
rm -f /tmp/plex_playlist_manager-*.whl

echo "=== Ensuring .env exists ==="
if [ ! -f "$INSTALL_DIR/.env" ]; then
  cat > "$INSTALL_DIR/.env" << 'EOF'
PLEX_BASE_URL=http://192.168.1.45:32400
PLEX_TOKEN=changeme
EOF
  chmod 600 "$INSTALL_DIR/.env"
  echo "➡ Wrote template $INSTALL_DIR/.env — set PLEX_TOKEN before the app will work."
else
  echo "➡ Existing $INSTALL_DIR/.env left untouched."
fi

echo "=== Creating systemd service ==="
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Plex Playlist Manager
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
EnvironmentFile=${INSTALL_DIR}/.env
ExecStart=${VENV_PATH}/bin/uvicorn plex_playlist_manager.main:app --host ${BIND_HOST} --port ${BIND_PORT}
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "=== Creating update.sh ==="
cat > "$INSTALL_DIR/update.sh" << 'EOF'
#!/bin/bash
set -e
VENV_PATH="/opt/plex-playlist-manager/venv"
SERVICE_NAME="plex-playlist-manager"
REPO="james-berkheimer/plex_playlist_manager"
LATEST_VERSION=$(curl -s https://api.github.com/repos/${REPO}/releases/latest | grep -Po '"tag_name": "v\K[^"]+')
if [ -z "$LATEST_VERSION" ]; then
  echo "Error: Unable to fetch latest plex-playlist-manager version."
  exit 1
fi
echo "➡ Updating to version: $LATEST_VERSION"
WHEEL="plex_playlist_manager-${LATEST_VERSION}-py3-none-any.whl"
curl -fL -o "/tmp/${WHEEL}" \
  "https://github.com/${REPO}/releases/download/v${LATEST_VERSION}/${WHEEL}"
"$VENV_PATH/bin/pip" install --upgrade "/tmp/${WHEEL}"
rm -f /tmp/plex_playlist_manager-*.whl
systemctl restart "$SERVICE_NAME"
systemctl --no-pager status "$SERVICE_NAME" | head -n 5
echo "Update complete"
EOF
chmod +x "$INSTALL_DIR/update.sh"

echo "=== Creating uninstall.sh ==="
cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
set -e
SERVICE_NAME="plex-playlist-manager"
echo "Uninstalling Plex Playlist Manager..."
systemctl disable --now "$SERVICE_NAME" 2>/dev/null || true
rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload
rm -rf /opt/plex-playlist-manager
rm -f /usr/local/bin/ppm_update
rm -f /usr/local/bin/ppm_uninstall
echo "Plex Playlist Manager has been removed."
EOF
chmod +x "$INSTALL_DIR/uninstall.sh"

echo "=== Creating symlinks in /usr/local/bin ==="
ln -sf "$INSTALL_DIR/update.sh" /usr/local/bin/ppm_update
ln -sf "$INSTALL_DIR/uninstall.sh" /usr/local/bin/ppm_uninstall

echo "=== Enabling and starting service ==="
systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
systemctl --no-pager status "$SERVICE_NAME" | head -n 8 || true

echo "=== Installation complete ==="
echo "➡ Service: ${SERVICE_NAME}  →  http://<container-ip>:${BIND_PORT}"
echo "➡ Commands available: ppm_update, ppm_uninstall"
echo "➡ If you just installed, set PLEX_TOKEN in ${INSTALL_DIR}/.env then: systemctl restart ${SERVICE_NAME}"
