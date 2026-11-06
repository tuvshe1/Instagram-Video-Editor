from pathlib import Path
import argparse
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "assets" / "input"
MUSIC_DIR = ROOT / "assets" / "music"
OUTPUT_DIR = ROOT / "output"

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def load_font(size):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def fit_cover(frame, width, height):
    h, w = frame.shape[:2]
    scale = max(width / w, height / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_AREA)
    x = max(0, (nw - width) // 2)
    y = max(0, (nh - height) // 2)
    return resized[y:y + height, x:x + width]


def add_text(frame, text, progress, title, subtitle):
    # Subtle dark gradient at the bottom for readable captions.
    h, w = frame.shape[:2]
    overlay = frame.copy()
    band_h = int(h * 0.28)
    for y in range(h - band_h, h):
        alpha = 0.62 * ((y - (h - band_h)) / max(1, band_h))
        cv2.rectangle(overlay, (0, y), (w, y + 1), (0, 0, 0), -1)
        frame[y] = cv2.addWeighted(overlay[y], alpha, frame[y], 1 - alpha, 0)

    pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil)
    title_font = load_font(max(28, int(w * 0.060)))
    sub_font = load_font(max(18, int(w * 0.030)))

    def centered(txt, y, font, fill):
        if not txt:
            return
        box = draw.textbbox((0, 0), txt, font=font, stroke_width=1)
        tw = box[2] - box[0]
        draw.text(((w - tw) // 2, y), txt, font=font, fill=fill,
                  stroke_width=2, stroke_fill=(0, 0, 0))

    centered(title, int(h * 0.76), title_font, "white")
    centered(subtitle, int(h * 0.84), sub_font, (230, 230, 230))
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def process_image(path, width, height, duration, fps, title, subtitle):
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Зураг уншиж чадсангүй: {path.name}")
    base = fit_cover(image, width, height)
    frames = []
    count = max(1, int(duration * fps))
    # Gentle zoom-in motion.
    for i in range(count):
        p = i / max(1, count - 1)
        zoom = 1.0 + 0.10 * p
        crop_w = max(1, int(width / zoom))
        crop_h = max(1, int(height / zoom))
        x = (width - crop_w) // 2
        y = (height - crop_h) // 2
        crop = base[y:y + crop_h, x:x + crop_w]
        frame = cv2.resize(crop, (width, height), interpolation=cv2.INTER_LINEAR)
        frame = add_text(frame, "", p, title, subtitle)
        frames.append(frame)
    return frames


def process_video(path, width, height, duration, fps, title, subtitle):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Видео нээж чадсангүй: {path.name}")
    source_fps = cap.get(cv2.CAP_PROP_FPS) or fps
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    source_duration = total / source_fps if total else duration
    wanted = min(duration, source_duration) if duration > 0 else source_duration
    frames = []
    count = max(1, int(wanted * fps))
    for i in range(count):
        cap.set(cv2.CAP_PROP_POS_MSEC, (i / fps) * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        frame = fit_cover(frame, width, height)
        frame = add_text(frame, "", i / max(1, count - 1), title, subtitle)
        frames.append(frame)
    cap.release()
    return frames


def crossfade_join(clips, fade_frames):
    if not clips:
        return []
    result = clips[0]
    for clip in clips[1:]:
        n = min(fade_frames, len(result), len(clip))
        if n <= 0:
            result.extend(clip)
            continue
        blended = []
        for i in range(n):
            alpha = (i + 1) / (n + 1)
            blended.append(cv2.addWeighted(result[-n + i], 1 - alpha, clip[i], alpha, 0))
        result = result[:-n] + blended + clip[n:]
    return result


def main():
    parser = argparse.ArgumentParser(description="Vertical Instagram / TikTok video editor")
    parser.add_argument("--title", default="OUR MEMORIES", help="Видео дээр гарах гол текст")
    parser.add_argument("--subtitle", default="A little moment to remember", help="Доод жижиг текст")
    parser.add_argument("--duration", type=float, default=3.0, help="Зураг бүрийн үргэлжлэх секунд")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    parser.add_argument("--music", default="", help="assets/music доторх хөгжмийн файлын нэр")
    parser.add_argument("--output", default="my_edit.mp4")
    parser.add_argument("--fade", type=float, default=0.5, help="Шилжилтийн секунд")
    args = parser.parse_args()

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    items = sorted([p for p in INPUT_DIR.iterdir()
                    if p.suffix.lower() in VIDEO_EXTS | IMAGE_EXTS])
    if not items:
        print("assets/input хавтас дотор зураг эсвэл видео хийнэ үү.")
        return 1

    clips = []
    for path in items:
        print(f"Боловсруулж байна: {path.name}")
        if path.suffix.lower() in IMAGE_EXTS:
            frames = process_image(path, args.width, args.height, args.duration,
                                   args.fps, args.title, args.subtitle)
        else:
            frames = process_video(path, args.width, args.height, args.duration,
                                   args.fps, args.title, args.subtitle)
        if frames:
            clips.append(frames)

    merged = crossfade_join(clips, max(0, int(args.fade * args.fps)))
    if not merged:
        print("Видео үүсгэх frame олдсонгүй.")
        return 1

    temp_path = OUTPUT_DIR / "temp_video.mp4"
    final_path = OUTPUT_DIR / args.output
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_path), fourcc, args.fps,
                             (args.width, args.height))
    for frame in merged:
        writer.write(frame)
    writer.release()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [ffmpeg, "-y", "-i", str(temp_path)]
    music_path = MUSIC_DIR / args.music if args.music else None
    if music_path and music_path.exists():
        command += ["-stream_loop", "-1", "-i", str(music_path),
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k"]
    else:
        command += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
    command += ["-movflags", "+faststart", str(final_path)]
    subprocess.run(command, check=True)
    temp_path.unlink(missing_ok=True)
    print(f"\nБэлэн боллоо: {final_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print("FFmpeg видео экспортлох үед алдаа гарлаа:", exc)
        raise SystemExit(1)
