package com.example.authorizeddownloader

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.webkit.JavascriptInterface
import android.webkit.MimeTypeMap
import android.webkit.WebView
import org.json.JSONObject
import java.util.Locale

class AndroidBridge(
    private val context: Context,
    private val webView: WebView
) {
    private val mainHandler = Handler(Looper.getMainLooper())

    @JavascriptInterface
    fun postMessage(message: String) {
        try {
            val payload = JSONObject(message)
            if (payload.optString("type") != "download") {
                status("غير متاح", "هذه النسخة تدعم تنزيل الملفات المباشرة المصرّح بها فقط.", "error")
                return
            }
            enqueue(payload)
        } catch (_: Exception) {
            status("تعذّر فهم الطلب", "تحقق من الرابط وحاول مرة أخرى.", "error")
        }
    }

    private fun enqueue(payload: JSONObject) {
        val mode = payload.optString("mode")
        if (mode != "audio" && mode != "video") {
            status("نوع الملف غير مدعوم", "اختر صوتاً أو فيديو.", "error")
            return
        }
        val urls = payload.optJSONArray("urls")
        if (urls == null || urls.length() == 0) {
            status("أضف رابطاً", "الصق رابط ملف مباشر تملك حق تنزيله.", "error")
            return
        }

        val directory = if (mode == "video") Environment.DIRECTORY_MOVIES else Environment.DIRECTORY_MUSIC
        val manager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
        var queued = 0
        var rejected = 0

        for (index in 0 until urls.length()) {
            val uri = validMediaUrl(urls.optString(index))
            if (uri == null) {
                rejected++
                continue
            }
            val name = safeFileName(uri.lastPathSegment ?: "media_${index + 1}")
            try {
                val request = DownloadManager.Request(uri)
                    .setTitle(name)
                    .setDescription("تنزيل ملف مباشر مصرح به")
                    .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                    .setAllowedOverMetered(true)
                    .setAllowedOverRoaming(false)
                    .setDestinationInExternalFilesDir(context, directory, name)
                val mime = MimeTypeMap.getSingleton()
                    .getMimeTypeFromExtension(name.substringAfterLast('.', "").lowercase(Locale.ROOT))
                if (mime != null) request.setMimeType(mime)
                manager.enqueue(request)
                queued++
            } catch (_: Exception) {
                rejected++
            }
        }

        if (queued == 0) {
            status("ماكو ملف مباشر صالح", "استخدم رابط HTTPS ينتهي بامتداد صوت أو فيديو معروف. روابط صفحات YouTube وSpotify غير مدعومة.", "error")
        } else {
            val extra = if (rejected > 0) " وتم تجاهل $rejected رابط غير صالح." else ""
            status("بدأ التنزيل", "أُضيف $queued ملف. الحفظ داخل مجلد التطبيق في ${if (mode == "video") "الفيديوهات" else "الموسيقى"}.$extra", "done")
        }
    }

    private fun validMediaUrl(raw: String): Uri? {
        val uri = runCatching { Uri.parse(raw.trim()) }.getOrNull() ?: return null
        if (uri.scheme != "https" || uri.host.isNullOrBlank() || uri.userInfo != null) return null
        val host = uri.host!!.lowercase(Locale.ROOT)
        val blockedHosts = listOf("youtube.com", "youtu.be", "youtube-nocookie.com", "spotify.com", "spotify.link")
        if (blockedHosts.any { host == it || host.endsWith(".$it") }) return null
        val extension = uri.lastPathSegment?.substringAfterLast('.', "")?.lowercase(Locale.ROOT) ?: return null
        val allowed = setOf("mp3", "m4a", "aac", "wav", "ogg", "flac", "mp4", "m4v", "mkv", "webm", "mov")
        return uri.takeIf { extension in allowed }
    }

    private fun safeFileName(value: String): String {
        val cleaned = value.replace(Regex("[^\\p{L}\\p{N}._ -]"), "_").trim().take(120)
        return cleaned.ifBlank { "media.bin" }
    }

    private fun status(title: String, detail: String, kind: String) {
        val data = JSONObject()
            .put("title", title)
            .put("detail", detail)
            .put("kind", kind)
            .put("active", false)
        mainHandler.post {
            webView.evaluateJavascript("window.updateStatus && window.updateStatus($data);", null)
        }
    }
}
