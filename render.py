#!/usr/bin/env python
"""Render a video from videos/<name>/scenes.py.

    python render.py sine_from_circle             # all parts, high quality, concatenated
    python render.py sine_from_circle --preview   # fast low-quality render, then open it
    python render.py sine_from_circle --part 2    # just Part02, fast

Scene classes are discovered by their numeric prefix (Part01_, Part02_, ...)
and rendered in that order. See CLAUDE.md for the preview-then-final workflow.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VIDEOS_DIR = ROOT / "videos"
OUTPUT_DIR = ROOT / "output"

# Part01_Foo, Part02_Bar, ... — the number is what orders them.
PART_RE = re.compile(r"^Part(\d+)_")


def die(message: str) -> "NoReturn":  # noqa: F821
    print(f"\nerror: {message}\n", file=sys.stderr)
    raise SystemExit(1)


def find_scene_file(video: str) -> Path:
    scenes = VIDEOS_DIR / video / "scenes.py"
    if not scenes.is_file():
        available = sorted(
            d.name for d in VIDEOS_DIR.iterdir() if (d / "scenes.py").is_file()
        ) if VIDEOS_DIR.is_dir() else []
        die(
            f"no such video: {video!r} (looked for {scenes.relative_to(ROOT)})\n"
            f"       available: {', '.join(available) or '(none yet)'}"
        )
    return scenes


def discover_parts(scene_file: Path) -> list[tuple[int, str]]:
    """Return [(number, class_name), ...] ordered by the numeric prefix.

    Parsed statically rather than by importing, so a syntax error in scenes.py
    surfaces as a clear message instead of an import traceback — and so
    discovery doesn't pay manim's import cost.
    """
    tree = ast.parse(scene_file.read_text(encoding="utf-8"), filename=str(scene_file))
    parts = [
        (int(m.group(1)), node.name)
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        if (m := PART_RE.match(node.name))
    ]
    if not parts:
        die(
            f"{scene_file.relative_to(ROOT)} defines no Part<NN>_ scene classes.\n"
            f"       Name them Part01_Something, Part02_SomethingElse, ..."
        )
    parts.sort()
    return parts


def require(tool: str, install_hint: str) -> str:
    path = shutil.which(tool)
    if path is None:
        die(f"{tool} is not on your PATH.\n       Install it with:  {install_hint}")
    return path


def render_scene(scene_file: Path, scene: str, work_dir: Path, preview: bool) -> Path:
    """Render one scene; return the path to its mp4."""
    quality_flag = "-ql" if preview else "-qh"
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag,
        "--media_dir",
        str(work_dir),
        str(scene_file),
        scene,
    ]
    print(f"  -> {scene} ({'preview' if preview else 'high quality'})")
    # cwd=ROOT so manim.cfg and the `common` package both resolve.
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        die(f"manim failed while rendering {scene} (exit {result.returncode})")

    # manim writes to <media_dir>/videos/<module>/<quality>/<Scene>.mp4; glob
    # for it rather than reconstructing the quality directory name.
    matches = sorted(work_dir.rglob(f"{scene}.mp4"), key=lambda p: p.stat().st_mtime)
    if not matches:
        die(f"manim reported success but produced no {scene}.mp4 under {work_dir}")
    return matches[-1]


def concat(clips: list[Path], destination: Path, work_dir: Path) -> None:
    """Stitch the parts into one mp4 with ffmpeg's concat demuxer (no re-encode)."""
    ffmpeg = require(
        "ffmpeg",
        "winget install --id=Gyan.FFmpeg -e   (then restart your terminal)",
    )
    listing = work_dir / "concat.txt"
    listing.write_text(
        "".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-c", "copy", str(destination)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        die(f"ffmpeg concat failed:\n{result.stderr.strip()[-2000:]}")


def open_file(path: Path) -> None:
    """Open a file in the OS default player."""
    try:
        if sys.platform == "win32":
            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except OSError as exc:
        print(f"  (couldn't auto-open: {exc})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a video from videos/<name>/scenes.py.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("video", help="directory name under videos/")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="fast low-quality render, then open it",
    )
    parser.add_argument(
        "--part",
        type=int,
        metavar="N",
        help="render only Part<N> (implies a fast render)",
    )
    args = parser.parse_args()

    scene_file = find_scene_file(args.video)
    parts = discover_parts(scene_file)

    if args.part is not None:
        selected = [p for p in parts if p[0] == args.part]
        if not selected:
            die(
                f"{args.video} has no Part{args.part:02d}. "
                f"Found: {', '.join(name for _, name in parts)}"
            )
        parts = selected

    # A single part is always an iteration render, so it's fast by default.
    preview = args.preview or args.part is not None

    work_dir = OUTPUT_DIR / "_work" / args.video
    print(f"\n{args.video}: {len(parts)} part(s)")

    clips = [render_scene(scene_file, name, work_dir, preview) for _, name in parts]

    # A partial or preview render is for looking at, not for delivering — leave
    # it where manim put it rather than overwriting the final mp4.
    if len(clips) == len(discover_parts(scene_file)) and not preview:
        final = OUTPUT_DIR / f"{args.video}.mp4"
        concat(clips, final, work_dir)
        print(f"\ndone: {final.relative_to(ROOT)}\n")
    else:
        final = clips[-1]
        print(f"\ndone: {final.relative_to(ROOT)}\n")
        if preview:
            open_file(final)


if __name__ == "__main__":
    main()
