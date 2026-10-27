#!/usr/bin/env bash
set -euo pipefail
rm -f "$HOME/.local/bin/download-song-auto"
rm -rf "$HOME/.local/share/download-song-ui"
rm -f "$HOME/.local/share/applications/download-song-auto.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi
printf 'أزيل البرنامج. الملفات التي نزّلتها في Music وVideos لم تُحذف.\n'
