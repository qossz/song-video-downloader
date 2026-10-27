#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/download-song-ui"
APP_LAUNCHERS="$HOME/.local/share/applications"
mkdir -p "$BIN_DIR" "$APP_DIR" "$APP_LAUNCHERS"
install -m 755 "$ROOT/linux/download-song-auto" "$BIN_DIR/download-song-auto"
install -m 755 "$ROOT/linux/app.py" "$APP_DIR/app.py"
install -m 644 "$ROOT/linux/index.html" "$APP_DIR/index.html"
cat > "$APP_LAUNCHERS/download-song-auto.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=تنزيل أغاني وفيديوهات YouTube
Name[en]=YouTube Music & Video Downloader
Comment=نزّل ملفات الوسائط التي تملك حق تنزيلها
Comment[en]=Download media you are authorized to download
Exec="$BIN_DIR/download-song-auto"
Icon=audio-x-generic
Terminal=false
Categories=AudioVideo;Audio;Video;
StartupNotify=true
EOF
chmod 644 "$APP_LAUNCHERS/download-song-auto.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APP_LAUNCHERS" >/dev/null 2>&1 || true
fi
printf 'تم التثبيت. افتح «تنزيل أغاني وفيديوهات YouTube» من قائمة التطبيقات.\n'
