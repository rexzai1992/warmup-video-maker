"""YouTube thumbnails (1280x720 JPG) for the chapter videos: title card frame, brightened, with a big badge.

  python tools/thumbnails.py            -> output/youtube/<version>_ch<N>_thumb.jpg for every chapter video found
"""
import io, pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
YT = ROOT / "output" / "youtube"
BADGE = {1: "#FF7A1A", 2: "#2EC4B6", 3: "#3D7BFF", 4: "#E63946", 5: "#8E5BBF"}


def font(size):
    for f in ("ariblk.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def frame(video, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(video), "-frames:v", "1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB").resize((1280, 720))


def thumb(video):
    ch = int(video.stem.split("_ch")[1])
    mins = max(2, round(float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True).stdout) / 60))
    im = frame(video, 2.2)                                   # intro card: chapter title + waving character
    im = ImageEnhance.Brightness(im).enhance(1.3)
    im = ImageEnhance.Contrast(im).enhance(1.3)
    im = ImageEnhance.Color(im).enhance(1.25)
    d = ImageDraw.Draw(im)
    # badge: "3 MIN" top-left, tilted look via a rounded box
    f = font(78)
    txt = f"{mins} MIN"
    w = d.textlength(txt, font=f)
    d.rounded_rectangle([28, 24, 28 + w + 60, 24 + 112], radius=30, fill=BADGE.get(ch, "#FF7A1A"),
                        outline="white", width=6)
    d.text((58, 36), txt, font=f, fill="white")
    # bottom strip
    f2 = font(54)
    label = "KIDS WARM-UP  •  BRAIN BREAK"
    w2 = d.textlength(label, font=f2)
    d.rounded_rectangle([640 - w2 / 2 - 34, 610, 640 + w2 / 2 + 34, 700], radius=26, fill="#1B1B3A")
    d.text((640 - w2 / 2, 622), label, font=f2, fill="#FFE14D")
    out = video.with_name(video.stem + "_thumb.jpg")
    im.save(out, quality=90)
    return out


if __name__ == "__main__":
    vids = sorted(YT.glob("*_ch[0-9].mp4"))
    if not vids:
        sys.exit("no chapter videos yet - run: python make_video.py <version> --chapters")
    for v in vids:
        print("  ", thumb(v).relative_to(ROOT))
