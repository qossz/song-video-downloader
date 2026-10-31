# تنزيل أغاني وفيديوهات YouTube / YouTube Music & Video Downloader
<img width="1920" height="1048" alt="Screenshot From 2026-10-31 05-35-11" src="https://github.com/user-attachments/assets/162a7063-90b1-404f-b5ad-a2138dbb2e34" />

## العربية

تطبيق سطح مكتب لـ Ubuntu وبيئات GNOME يستخدم واجهة GTK/WebKit لتنزيل الصوت بصيغة MP3 أو الفيديو، مع البحث بالاسم وإظهار نتائج YouTube. يشمل تنزيل روابط متعددة بالتتابع ودعم روابط Spotify عبر spotDL.

### التثبيت

ثبت الاعتماديات المتاحة في مستودعات Ubuntu:


sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 zenity ffmpeg nodejs python3-mutagen
```

ثبّت `yt-dlp` و`spotDL` من مصادرهما الرسمية، ثم شغّل:

```bash
bash install.sh
```

افتح التطبيق من قائمة البرامج. ملفات الصوت تذهب إلى `~/Music` والفيديوهات إلى `~/Videos/فيديوهات YouTube`.

### حدود الاستخدام

استخدم التطبيق فقط لتنزيل ملفات تملكها أو لديك إذن صريح بتنزيلها، وبالطريقة التي تسمح بها شروط الخدمة والقوانين السارية. هذا المشروع ليس تابعاً لـ YouTube أو Spotify ولا يستخدم واجهاتهما الرسمية. خدمات yt-dlp وspotDL أدوات خارجية غير مضمّنة هنا.

هذا المستودع يحتوي نسخة Linux فقط. لا يتضمن تطبيق Android، والنسخة الحالية ليست جاهزة للنشر على Google Play. 

## English

A desktop downloader for Ubuntu and GNOME. Its GTK/WebKit interface supports MP3 audio, video, name-based YouTube search, sequential link downloads, and Spotify links through spotDL.

### Install

Install Ubuntu dependencies:

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 zenity ffmpeg nodejs python3-mutagen
```

Install `yt-dlp` and `spotDL` from their official sources, then run:

```bash
bash install.sh
```

Launch the app from the applications menu. Audio is saved to `~/Music`; videos are saved to `~/Videos/فيديوهات YouTube`.

### Use and platform status

Only download media that you own or are explicitly authorized to download, and follow applicable service terms and laws. This project is not affiliated with YouTube or Spotify and does not use their official APIs. yt-dlp and spotDL are external tools and are not bundled.

This repository contains the Linux app only. It does not include an Android app and is not ready for Google Play submission.

## License / الرخصة

No license file is included. A public GitHub repository can be viewed, but others do not receive reuse or redistribution rights unless the owner chooses and adds a license. لم تُضف رخصة بعد؛ نشر المستودع لا يمنح الآخرين حق إعادة استخدام الشيفرة أو توزيعها بدون اختيار الرخصة.
