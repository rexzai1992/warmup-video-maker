"""One still per Flow clip on a single image, to check all scenes at once.

  python tools/contact_sheet.py school        -> output/contact_school.jpg
"""
import json, pathlib, subprocess, sys, io
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, COLS = 320, 180, 6


def still(clip, t=4.0):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(clip), "-frames:v", "1",
                        "-vf", f"scale={W}:{H}", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB") if r.stdout else None


def sheet(version):
    items = json.loads((ROOT / "flow_prompts" / f"{version}.json").read_text(encoding="utf-8"))
    rows = -(-len(items) // COLS)
    img = Image.new("RGB", (COLS * W, rows * (H + 24)), (20, 20, 28))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arialbd.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    have = 0
    for k, e in enumerate(items):
        x, y = (k % COLS) * W, (k // COLS) * (H + 24)
        clip = ROOT / "footage" / "flow" / version / e["save_as"]
        im = still(clip) if clip.exists() else None
        if im:
            img.paste(im, (x, y + 24)); have += 1
        else:
            d.rectangle([x + 2, y + 26, x + W - 2, y + H + 22], outline=(90, 90, 90))
            d.text((x + W // 2 - 30, y + H // 2 + 14), "missing", fill=(140, 140, 140), font=font)
        d.text((x + 6, y + 3), f"{e['n']}. {e['id']}", fill=(255, 220, 80), font=font)
    out = ROOT / "output" / f"contact_{version}.jpg"
    out.parent.mkdir(exist_ok=True)
    img.save(out, quality=85)
    print(f"  {out.relative_to(ROOT)}: {have}/{len(items)} clips")
    return out


if __name__ == "__main__":
    for v in sys.argv[1:] or ["school", "japan"]:
        sheet(v)
