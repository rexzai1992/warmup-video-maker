"""Write output/youtube/<video>_UPLOAD.txt (title, description, tags, settings) from youtube_uploads.md.

  python tools/upload_kit.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETTINGS = """SETTINGS (YouTube Studio > Create > Upload videos)
- Thumbnail: {thumb}
- Playlist: {playlist}
- Audience: Yes, it's made for kids
- Show more > Altered content: Yes (realistic AI scenes)
- Category: Education
- Visibility: Schedule (2-3 videos per week)
"""


def main():
    md = (ROOT / "youtube_uploads.md").read_text(encoding="utf-8")
    out = ROOT / "output" / "youtube"
    for m in re.finditer(r"### (\w+_ch\d): (.+?)\n(.*?)(?=\n### |\n---|\Z)", md, re.S):
        vid, body = m.group(1), m.group(3)
        title = re.search(r"\*\*Title:\*\* (.+)", body).group(1).strip()
        desc = re.search(r"\*\*Description:\*\*\n```\n(.*?)\n```", body, re.S).group(1).strip()
        tags = re.search(r"\*\*Tags:\*\* (.+)", body).group(1).strip()
        playlist = "Back to School Warm-Up" if vid.startswith("school") else "Japan Adventure Warm-Up"
        txt = (f"VIDEO FILE: {vid}.mp4\n\nTITLE (max 100 chars):\n{title}\n\nDESCRIPTION:\n{desc}\n\n"
               f"TAGS (paste into Show more > Tags):\n{tags}\n\n" + SETTINGS.format(thumb=f"{vid}_thumb.jpg", playlist=playlist))
        (out / f"{vid}_UPLOAD.txt").write_text(txt, encoding="utf-8")
        print(f"  {vid}_UPLOAD.txt  (title {len(title)} chars, tags {len(tags)} chars)")


if __name__ == "__main__":
    main()
