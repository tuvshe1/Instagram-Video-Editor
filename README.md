# Instagram Video Editor (Python)

Энэ бол зураг, богино видеоноос босоо 9:16 edit видео үүсгэдэг Python project.

## Боломжууд
- 1080x1920 босоо видео (Instagram Reels / TikTok хэмжээ)
- Зурган дээр зөөлөн zoom-in хөдөлгөөн
- Олон зураг, видеог нэгтгэх
- Зөөлөн crossfade transition
- Гол гарчиг болон доод текст
- Өөрийн хөгжмийг нэмэх
- MP4 (H.264) экспорт

## 1. Шаардлагатай зүйл
- Python 3.10 ба түүнээс дээш
- Windows / macOS / Linux

## 2. Суулгах
Project хавтас дотроос Terminal эсвэл CMD нээгээд:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS / Linux:
```bash
source .venv/bin/activate
```

Дараа нь:
```bash
python -m pip install -r requirements.txt
```

## 3. Зураг, видео нэмэх
- Зураг болон видеогоо `assets/input/` хавтас руу хуул.
- Дэмжих зураг: JPG, JPEG, PNG, WEBP, BMP
- Дэмжих видео: MP4, MOV, AVI, MKV, WEBM
- Хөгжим нэмэх бол MP3 эсвэл WAV файлаа `assets/music/` дотор хий.

## 4. Ажиллуулах

Энгийн:
```bash
python main.py
```

Өөрийн тексттэй:
```bash
python main.py --title "MY STORY" --subtitle "Best moments"
```

Хөгжимтэй:
```bash
python main.py --title "OUR MEMORIES" --music "song.mp3"
```

Зураг бүр 4 секунд байлгах:
```bash
python main.py --duration 4 --fade 0.7
```

Үр дүн `output/my_edit.mp4` дотор гарна.

## 5. GitHub-д оруулах
GitHub дээр `Instagram-Video-Editor` нэртэй шинэ repository үүсгээд энэ хавтасны файлуудыг оруул.

CMD дээр project хавтас руу орж:
```bash
git init
git add .
git commit -m "Create Python Instagram video editor"
git branch -M main
git remote add origin https://github.com/ТАНЫ-USERNAME/Instagram-Video-Editor.git
git push -u origin main
```

`ТАНЫ-USERNAME` хэсгийг өөрийн GitHub username-аар солино.

## Анхаарах зүйл
Энэ project нь жишээ Reels-ийн яг ижил хуулбар биш. Тухайн Reel-ийн бичлэг эсвэл screenshot байхгүй тул ерөнхий cinematic edit загвар бэлдсэн. Ашиглах хөгжим болон зураг/видеоны эрхийг өөрөө шалгаарай.
