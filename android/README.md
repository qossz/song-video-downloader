# Android app

This folder contains a small Android Studio project that wraps a local Arabic WebView UI and uses Android DownloadManager for direct, authorized media-file URLs.

## Build

1. Open the `android/` directory in Android Studio (a recent version with Android Gradle Plugin 8.7.3 support).
2. Allow Gradle sync and install Android SDK 35 if prompted.
3. Select **Build → Build APK(s)**. The debug APK is written under `app/build/outputs/apk/debug/`.

## Scope

- Downloads direct HTTPS file URLs with recognized audio/video extensions only.
- YouTube and Spotify page URLs, searching, extraction, transcoding, and DRM bypass are not supported.
- Downloads are saved in the app-specific external Music/Movies directory; Android DownloadManager shows notifications.
- Only download media you own or are authorized to download.

No APK binary is attached; build it locally with Android Studio.
