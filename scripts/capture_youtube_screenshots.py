#!/usr/bin/env python3
"""Capture selected YouTube video frames for visual learning notes."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, check=False, text=True, capture_output=True)
    if check and result.returncode != 0:
        details = "\n".join(
            part
            for part in (
                f"Command failed: {' '.join(cmd)}",
                f"Exit code: {result.returncode}",
                f"stdout:\n{result.stdout.strip()}" if result.stdout.strip() else "",
                f"stderr:\n{result.stderr.strip()}" if result.stderr.strip() else "",
            )
            if part
        )
        raise RuntimeError(details)
    return result


def metadata_for(url: str) -> dict[str, str]:
    template = "%(id)s\t%(title)s\t%(duration_string)s\t%(webpage_url)s"
    result = run(["yt-dlp", "--print", template, url])
    parts = result.stdout.strip().split("\t")
    if len(parts) != 4:
        raise RuntimeError(f"Unexpected yt-dlp metadata output: {result.stdout!r}")
    return {
        "id": parts[0],
        "title": parts[1],
        "duration_string": parts[2],
        "webpage_url": parts[3],
    }


def validate_timestamp(value: str) -> str:
    if re.fullmatch(r"\d{1,2}:\d{2}:\d{2}(?:\.\d+)?", value):
        return value
    if re.fullmatch(r"\d{1,2}:\d{2}(?:\.\d+)?", value):
        return f"00:{value}"
    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        total = float(value)
        h = int(total // 3600)
        m = int((total % 3600) // 60)
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}"
    raise argparse.ArgumentTypeError(f"Invalid timestamp: {value!r}. Use HH:MM:SS, MM:SS, or seconds.")


def slug_time(value: str) -> str:
    return re.sub(r"[^0-9]+", "-", value).strip("-")


def download_video(url: str, out_dir: Path, video_id: str, max_height: int) -> Path:
    existing = sorted(out_dir.glob(f"{video_id}_source.*"))
    if existing:
        return existing[0]

    fmt = (
        f"bestvideo[height<={max_height}][ext=mp4]/"
        f"best[height<={max_height}][ext=mp4]/"
        f"bestvideo[height<={max_height}]/"
        f"best[height<={max_height}]/worst"
    )
    run(
        [
            "yt-dlp",
            "--no-playlist",
            "-f",
            fmt,
            "-o",
            str(out_dir / f"{video_id}_source.%(ext)s"),
            url,
        ]
    )
    downloaded = sorted(out_dir.glob(f"{video_id}_source.*"))
    if not downloaded:
        raise RuntimeError("yt-dlp completed but no source video file was found.")
    return downloaded[0]


def capture_frame(video: Path, timestamp: str, output: Path) -> None:
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            timestamp,
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture selected screenshots from a YouTube video.")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("timestamps", nargs="+", type=validate_timestamp, help="Timestamps: HH:MM:SS, MM:SS, or seconds")
    parser.add_argument("--out-dir", default="work/youtube-learning-notes/screenshots", help="Screenshot output directory")
    parser.add_argument("--cache-dir", default="work/youtube-learning-notes/video-cache", help="Downloaded video cache directory")
    parser.add_argument("--max-height", type=int, default=480, help="Maximum downloaded video height")
    args = parser.parse_args()

    for tool in ("yt-dlp", "ffmpeg"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} is required. Install it before capturing screenshots.")

    out_dir = Path(args.out_dir).expanduser().resolve()
    cache_dir = Path(args.cache_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    metadata = metadata_for(args.url)
    video = download_video(args.url, cache_dir, metadata["id"], args.max_height)

    screenshots = []
    for timestamp in args.timestamps:
        output = out_dir / f"{metadata['id']}_{slug_time(timestamp)}.jpg"
        capture_frame(video, timestamp, output)
        screenshots.append({"timestamp": timestamp, "path": str(output)})

    manifest = out_dir / f"{metadata['id']}_screenshots_manifest.md"
    lines = [
        "# Screenshot Manifest",
        "",
        f"Source: {metadata['webpage_url']}",
        f"Video ID: {metadata['id']}",
        f"Title: {metadata['title']}",
        f"Duration: {metadata['duration_string']}",
        "",
        "| Timestamp | File | Note |",
        "|---|---|---|",
    ]
    for item in screenshots:
        lines.append(f"| {item['timestamp']} | `{item['path']}` |  |")
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "video_id": metadata["id"],
                "title": metadata["title"],
                "source_video": str(video),
                "screenshots": screenshots,
                "manifest": str(manifest),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
