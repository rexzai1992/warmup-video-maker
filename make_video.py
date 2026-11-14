"""Make a warm-up video.

  python make_video.py school            # 15-min "Back to School" version
  python make_video.py japan             # 15-min "Hana's Japan Adventure" version
  python make_video.py japan --preview 20 300 600     # quick still images to check the look
  python make_video.py school --workers 6              # use more CPU cores (default: half your cores)
  python make_video.py school --new-audio              # rebuild the soundtrack (after editing a timeline)
  python make_video.py school --sample 36 96           # 1-minute test clip (seconds 36 to 96)
  python make_video.py school --import-flow            # file Google Flow clips from footage/flow_inbox/school/
  python make_video.py school --chapters               # YouTube: one ~3-min video per chapter (or --chapters 2 4)

Output: output/<name>.mp4 (720p, about 100-200 MB for 15 minutes).
"""
import argparse, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "engine"))
import warmup  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Render a warm-up video from a timeline in timelines/")
    ap.add_argument("name", help="timeline name, e.g. school or japan")
    ap.add_argument("--workers", type=int, default=None, help="parallel render workers")
    ap.add_argument("--preview", nargs="*", type=float, help="only render stills at these seconds")
    ap.add_argument("--new-audio", action="store_true", help="rebuild audio/<name>.m4a")
    ap.add_argument("--audio-only", action="store_true", help="only build the soundtrack")
    ap.add_argument("--sample", nargs=2, type=float, metavar=("FROM", "TO"), help="render only this part, in seconds")
    ap.add_argument("--chapters", nargs="*", type=int, metavar="N",
                    help="YouTube chapter videos -> output/youtube/<name>_ch<N>.mp4 (all, or only the listed ones)")
    ap.add_argument("--import-flow", action="store_true",
                    help="move clips from footage/flow_inbox/<name>/ to footage/flow/<name>/<id>.mp4")
    a = ap.parse_args()

    if a.import_flow:
        warmup.import_flow(a.name)
        return
    tl = warmup.load_timeline(a.name)
    print(f"[{a.name}] {tl['title']} - {tl['total'] / 60:.1f} min, {len(tl['segments'])} parts")
    if a.preview is not None:
        warmup.preview(a.name, a.preview or [20, 120, 300, 500])
        return
    audio = warmup.AUDIO / f"{a.name}.m4a"
    if a.new_audio or a.audio_only or not audio.exists():
        print("1) building soundtrack...")
        warmup.build_audio(tl, a.name)
        if a.audio_only:
            return
    else:
        print("1) soundtrack already built (use --new-audio after editing the timeline)")
    print("2) downloading footage...")
    warmup.download_footage(tl)
    print("3) preparing footage frames...")
    warmup.extract_frames(tl)
    warmup.extract_reaction_frames()
    print("4) rendering video...")
    if a.chapters is not None:
        warmup.export_chapters(a.name, a.workers, a.chapters or None)
    elif a.sample:
        warmup.render_video(a.name, a.workers, a.sample[0], a.sample[1])
    else:
        warmup.render_video(a.name, a.workers)


if __name__ == "__main__":
    main()
