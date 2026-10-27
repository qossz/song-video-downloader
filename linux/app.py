#!/usr/bin/python3
import json
import os
import re
import shutil
import subprocess
import threading
from pathlib import Path
from urllib.parse import urlparse

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gio, GLib, Gtk, WebKit2

APP_DIR = Path.home() / ".local/share/download-song-ui"
ENGINE = Path.home() / ".local/bin/download-song-auto"
HTML = APP_DIR / "index.html"
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "music.youtube.com", "m.youtube.com", "youtu.be"}
SPOTIFY_HOSTS = {"open.spotify.com", "www.open.spotify.com", "spotify.link"}


def parse_suggestion(raw):
    parts = [part.strip() for part in raw.strip().split("|") if part.strip()]
    arabic_parts = [part for part in parts if re.search(r"[\u0600-\u06ff]", part)]
    candidate = arabic_parts[-1] if arabic_parts else (parts[-1] if parts else raw.strip())
    candidate = re.sub(r"\s*(?:-|–|—)\s*(?:بالكلمات|كلمات|lyrics?|official\s+(?:audio|video)|music\s+video)\s*.*$", "", candidate, flags=re.I).strip()
    if "..." in candidate:
        artist, title = candidate.split("...", 1)
    elif "…" in candidate:
        artist, title = candidate.split("…", 1)
    elif re.search(r"\s[-–—]\s", candidate):
        artist, title = re.split(r"\s[-–—]\s", candidate, maxsplit=1)
    else:
        artist, title = "", candidate
    return artist.strip(" .…-–—|"), title.strip(" .…-–—|")


def is_valid_url(url, hosts):
    parsed = urlparse(url.strip())
    return parsed.scheme in ("http", "https") and (parsed.hostname or "").lower() in hosts


class DownloadApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="local.karar.DownloadSongUI", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None
        self.webview = None
        self.header = None
        self.active = False
        self.searching = False
        self.child = None

    def do_activate(self):
        if self.window is not None:
            self.window.present()
            return
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("تنزيل أغاني وفيديوهات YouTube")
        self.window.set_default_size(1000, 755)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_icon_name("audio-x-generic")
        self.window.connect("delete-event", self._on_delete)

        header = Gtk.HeaderBar()
        self.header = header
        header.set_show_close_button(True)
        header.set_title("تنزيل أغاني وفيديوهات YouTube")
        header.set_subtitle("واجهة محلية على جهازك")
        self.window.set_titlebar(header)

        manager = WebKit2.UserContentManager()
        manager.register_script_message_handler("native")
        manager.connect("script-message-received::native", self._on_script_message)
        self.webview = WebKit2.WebView.new_with_user_content_manager(manager)
        settings = self.webview.get_settings()
        settings.set_enable_developer_extras(False)
        self.window.add(self.webview)
        self.webview.load_uri(HTML.as_uri())
        self.window.show_all()

    def _on_delete(self, _window, _event):
        if self.active:
            self._eval("window.updateStatus({title:'التنزيل مستمر',detail:'انتظر حتى يكتمل قبل إغلاق النافذة.',kind:'busy'});")
            return True
        self.window = None
        return False

    def _eval(self, script):
        if self.webview is not None:
            self.webview.evaluate_javascript(script, -1, None, None, None, None, None)

    def _send_function(self, function, value):
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        self._eval(f"window.{function}({encoded});")

    def _on_script_message(self, _manager, message):
        try:
            payload = json.loads(message.get_js_value().to_string())
        except Exception:
            return
        kind = payload.get("type")
        if kind == "language":
            language = payload.get("language")
            if language in {"ar", "en"}:
                title = "تنزيل أغاني وفيديوهات YouTube" if language == "ar" else "YouTube Music & Video Downloader"
                subtitle = "واجهة محلية على جهازك" if language == "ar" else "Runs locally on your computer"
                self.window.set_title(title)
                self.header.set_title(title)
                self.header.set_subtitle(subtitle)
        elif kind == "suggest":
            url = str(payload.get("url", "")).strip()
            if not is_valid_url(url, YOUTUBE_HOSTS):
                self._send_function("applySuggestion", {"error": "استخدم رابط YouTube صحيح."})
                return
            threading.Thread(target=self._suggest, args=(url,), daemon=True).start()
        elif kind == "search":
            query = str(payload.get("query", "")).strip()
            if self.active or self.searching:
                return
            if not query:
                self._send_function("showSearchError", "اكتب اسم الفنان أو الأغنية أولاً.")
                return
            if len(query) > 200:
                self._send_function("showSearchError", "خلّي عبارة البحث أقصر من 200 حرف.")
                return
            self.searching = True
            self._send_function("searchState", {"active": True})
            threading.Thread(target=self._search_youtube, args=(query,), daemon=True).start()
        elif kind == "download":
            if self.active or self.searching:
                return
            mode = payload.get("mode")
            urls = payload.get("urls")
            if not isinstance(urls, list):
                urls = []
            urls = [str(url).strip() for url in urls if str(url).strip()]
            self._start_download(mode, urls, str(payload.get("artist", "")).strip(), str(payload.get("title", "")).strip())

    def _search_youtube(self, query):
        command = shutil.which("yt-dlp")
        if not command:
            GLib.idle_add(self._send_function, "showSearchError", "yt-dlp غير مثبت.")
            GLib.idle_add(self._send_function, "searchState", {"active": False})
            self.searching = False
            return
        args = [command, "--force-ipv4", "--js-runtimes", "node", "--remote-components", "ejs:github", "--quiet", "--no-warnings", "--skip-download", "--flat-playlist", "--dump-single-json", "ytsearch5:" + query]
        try:
            result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=60)
            data = json.loads(result.stdout)
            entries = data.get("entries") or []
            items = []
            for entry in entries[:5]:
                if not isinstance(entry, dict):
                    continue
                video_id = str(entry.get("id") or "").strip()
                url = str(entry.get("webpage_url") or entry.get("url") or "").strip()
                if video_id and not url.startswith(("http://", "https://")):
                    url = "https://www.youtube.com/watch?v=" + video_id
                if not url and video_id:
                    url = "https://www.youtube.com/watch?v=" + video_id
                if not url:
                    continue
                items.append({
                    "url": url,
                    "title": str(entry.get("title") or "بدون عنوان"),
                    "channel": str(entry.get("channel") or entry.get("uploader") or "قناة غير معروفة"),
                    "duration": entry.get("duration"),
                    "thumbnail": "https://i.ytimg.com/vi/" + video_id + "/mqdefault.jpg" if re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id) else "",
                })
            GLib.idle_add(self._send_function, "showSearchResults", items)
        except subprocess.TimeoutExpired:
            GLib.idle_add(self._send_function, "showSearchError", "تأخر YouTube بالرد. جرّب مرة ثانية.")
        except Exception:
            GLib.idle_add(self._send_function, "showSearchError", "ما كدرت أجيب نتائج. تحقق من الاتصال وحاول مرة ثانية.")
        finally:
            self.searching = False
            GLib.idle_add(self._send_function, "searchState", {"active": False})

    def _suggest(self, url):
        command = shutil.which("yt-dlp")
        if not command:
            GLib.idle_add(self._send_function, "applySuggestion", {"error": "yt-dlp غير مثبت."})
            return
        args = [command, "--force-ipv4", "--js-runtimes", "node", "--remote-components", "ejs:github", "--quiet", "--no-warnings", "--skip-download", "--print", "%(title)s", url]
        try:
            result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=50)
            raw = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
            artist, title = parse_suggestion(raw)
            GLib.idle_add(self._send_function, "applySuggestion", {"artist": artist, "title": title})
        except subprocess.TimeoutExpired:
            GLib.idle_add(self._send_function, "applySuggestion", {"error": "تأخر YouTube بالرد. جرّب مرة ثانية."})
        except Exception:
            GLib.idle_add(self._send_function, "applySuggestion", {"error": "ما كدرت أجيب عنوان الفيديو."})

    def _start_download(self, mode, urls, artist, title):
        if mode not in {"audio", "video", "spotify"} or not urls:
            self._send_function("updateStatus", {"title": "اختار نوع التنزيل وأضف رابطاً", "kind": "error"})
            return
        if mode == "spotify":
            if len(urls) != 1 or not is_valid_url(urls[0], SPOTIFY_HOSTS):
                self._send_function("updateStatus", {"title": "رابط Spotify غير صحيح", "detail": "الصق رابطاً واحداً من Spotify.", "kind": "error"})
                return
            engine_mode = "spotify"
        else:
            if any(not is_valid_url(url, YOUTUBE_HOSTS) for url in urls):
                self._send_function("updateStatus", {"title": "تأكد من روابط YouTube", "detail": "كل رابط لازم يكون من YouTube.", "kind": "error"})
                return
            if mode == "video":
                engine_mode = "video-batch"
            elif len(urls) > 1:
                engine_mode = "audio-batch"
            else:
                engine_mode = "audio"
        if not ENGINE.is_file():
            self._send_function("updateStatus", {"title": "ملف التنزيل غير موجود", "kind": "error"})
            return
        self.active = True
        self._send_function("updateStatus", {"title": "جارٍ تجهيز التنزيل…", "detail": f"عدد الروابط: {len(urls)}", "kind": "busy"})
        threading.Thread(target=self._download_worker, args=(engine_mode, mode, urls, artist, title), daemon=True).start()

    def _download_worker(self, engine_mode, ui_mode, urls, artist, title):
        if engine_mode == "audio" and (not artist or not title):
            self._post_status("أستخرج اسم الفنان والأغنية…", "هذا يساعد على حفظ الأغنية ببيانات مرتبة.", "busy")
            command = shutil.which("yt-dlp")
            if command:
                try:
                    result = subprocess.run([command, "--force-ipv4", "--js-runtimes", "node", "--remote-components", "ejs:github", "--quiet", "--no-warnings", "--skip-download", "--print", "%(title)s", urls[0]], check=True, capture_output=True, text=True, timeout=50)
                    raw = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
                    suggested_artist, suggested_title = parse_suggestion(raw)
                    artist = artist or suggested_artist
                    title = title or suggested_title
                    self._post_function("applySuggestion", {"artist": artist, "title": title})
                except Exception:
                    pass
        env = os.environ.copy()
        env["DOWNLOAD_SONG_MODE"] = engine_mode
        env["DOWNLOAD_SONG_URLS"] = "\n".join(urls)
        env["DOWNLOAD_SONG_NONINTERACTIVE"] = "1"
        env["DOWNLOAD_SONG_ARTIST"] = artist
        env["DOWNLOAD_SONG_TITLE"] = title
        final_lines = []
        had_failures = False
        status = 1
        try:
            self._post_status("جارٍ التنزيل…", "خلّ النافذة مفتوحة إلى أن يكتمل.", "busy")
            self.child = subprocess.Popen([str(ENGINE)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
            assert self.child.stdout is not None
            for line in self.child.stdout:
                line = line.strip()
                if not line:
                    continue
                final_lines.append(line)
                final_lines = final_lines[-5:]
                if "تعذّر" in line:
                    had_failures = True
                clean = line.lstrip("# ").strip()
                if clean and not clean.startswith("تم التنزيل:"):
                    self._post_status(clean, f"عدد الروابط: {len(urls)}", "busy")
            status = self.child.wait()
            detail = "مجلد الموسيقى" if ui_mode in {"audio", "spotify"} else "مجلد الفيديوهات"
            if status == 0 and had_failures:
                self._post_status("اكتمل التنزيل مع تعذّر بعض الروابط", f"تحقق من الروابط. مكان الحفظ: {detail}.", "done")
            elif status == 0:
                self._post_status("اكتمل التنزيل بنجاح", f"تم حفظ الملفات في {detail}.", "done")
            else:
                last = next((item for item in reversed(final_lines) if "تعذّر التنزيل" in item), "تحقق من الاتصال أو الرابط وحاول مرة ثانية.")
                self._post_status("ما اكتمل التنزيل", last, "error")
        except Exception:
            self._post_status("تعذّر تشغيل التنزيل", "تأكد من تثبيت yt-dlp أو spotDL.", "error")
        finally:
            self.child = None
            self.active = False
            GLib.idle_add(self._send_function, "updateStatus", {"active": False})

    def _post_status(self, title, detail="", kind="busy"):
        GLib.idle_add(self._send_function, "updateStatus", {"title": title, "detail": detail, "kind": kind})

    def _post_function(self, name, data):
        GLib.idle_add(self._send_function, name, data)


def main():
    app = DownloadApp()
    return app.run([])


if __name__ == "__main__":
    raise SystemExit(main())
