# تنزيل أغاني وفيديوهات YouTube / YouTube Music & Video Downloader

## العربية

تطبيق سطح مكتب لـ Ubuntu وبيئات GNOME يستخدم واجهة GTK/WebKit لتنزيل الصوت بصيغة MP3 أو الفيديو، مع البحث بالاسم وإظهار نتائج YouTube. يشمل تنزيل روابط متعددة بالتتابع ودعم روابط Spotify عبر spotDL.

### التثبيت

ثبت الاعتماديات المتاحة في مستودعات Ubuntu:

```bash
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

هذا المستودع يحتوي نسخة Linux فقط. لا يتضمن تطبيق Android، والنسخة الحالية ليست جاهزة للنشر على Google Play. سياسات المتجر تمنع تشجيع تنزيل محتوى محميّ بحقوق النشر من دون إذن؛ راجع [سياسة الملكية الفكرية في Google Play](https://support.google.com/googleplay/android-developer/answer/9888072?hl=en). كما تحدّ [شروط YouTube](https://www.youtube.com/t/terms) تنزيل المحتوى بما تسمح به الخدمة أو بإذن صاحب الحق. يلزم بناء نسخة Android مختلفة ومتوافقة قبل التقديم.

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

This repository contains the Linux app only. It does not include an Android app and is not ready for Google Play submission. Google Play policy prohibits apps that encourage unauthorized downloading of copyrighted content; see the [Google Play intellectual property policy](https://support.google.com/googleplay/android-developer/answer/9888072?hl=en). [YouTube Terms](https://www.youtube.com/t/terms) also limit downloads to what the service permits or what the rights holder authorizes. A separate compliant Android app is required before a Play submission.

## License / الرخصة

No license file is included. A public GitHub repository can be viewed, but others do not receive reuse or redistribution rights unless the owner chooses and adds a license. لم تُضف رخصة بعد؛ نشر المستودع لا يمنح الآخرين حق إعادة استخدام الشيفرة أو توزيعها بدون اختيار الرخصة.
