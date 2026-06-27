#!/usr/bin/env python3
"""Extract YouTube metadata and a cleaned timestamped transcript via yt-dlp."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def fmt(ms: int) -> str:
    seconds = round(ms / 1000)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("\u200b", "")
    return re.sub(r"\s+", " ", value).strip()


def read_json3(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments: list[dict[str, object]] = []
    for event in data.get("events", []):
        text = clean_text("".join(seg.get("utf8", "") for seg in event.get("segs") or []))
        if not text or text in {"[Music]", "[Applause]"}:
            continue
        start = int(event.get("tStartMs", 0) or 0)
        duration = int(event.get("dDurationMs", 0) or 0)
        current = {
            "start_ms": start,
            "end_ms": start + duration,
            "time": fmt(start),
            "text": text,
        }
        if segments and str(segments[-1]["text"]).lower() == text.lower():
            segments[-1]["end_ms"] = max(int(segments[-1]["end_ms"]), start + duration)
        else:
            segments.append(current)
    return segments


def write_outputs(segments: list[dict[str, object]], metadata: dict[str, str], out_dir: Path) -> None:
    video_id = metadata["id"]
    (out_dir / f"{video_id}_transcript_segments.json").write_text(
        json.dumps(segments, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Clean Timestamped Transcript",
        "",
        f"Source: {metadata['webpage_url']}",
        f"Video ID: {video_id}",
        f"Title: {metadata['title']}",
        f"Duration: {metadata['duration_string']}",
        f"Uploader: {metadata['uploader']}",
        f"Caption track: {metadata['caption_track']}",
        "",
    ]
    lines.extend(f"[{seg['time']}] {seg['text']}" for seg in segments)
    (out_dir / f"{video_id}_transcript_clean.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    chunk_ms = 5 * 60 * 1000
    chunks: list[tuple[int, int, str]] = []
    if segments:
        max_ms = max(int(seg["start_ms"]) for seg in segments)
        for base in range(0, max_ms + chunk_ms, chunk_ms):
            text = " ".join(
                str(seg["text"]) for seg in segments if base <= int(seg["start_ms"]) < base + chunk_ms
            )
            if text:
                chunks.append((base, base + chunk_ms, text))

    chunk_lines = [
        "# Transcript Chunks (5-minute windows)",
        "",
        "Use for synthesis; paraphrase in final notes rather than quote.",
        "",
    ]
    for base, end, text in chunks:
        chunk_lines.append(f"## {fmt(base)}-{fmt(end)}")
        chunk_lines.append(textwrap.fill(text, width=110))
        chunk_lines.append("")
    (out_dir / f"{video_id}_transcript_chunks.md").write_text("\n".join(chunk_lines), encoding="utf-8")


def metadata_for(url: str) -> dict[str, str]:
    template = "%(id)s\t%(title)s\t%(duration_string)s\t%(uploader)s\t%(upload_date)s\t%(webpage_url)s"
    result = run(["yt-dlp", "--print", template, url])
    parts = result.stdout.strip().split("\t")
    if len(parts) != 6:
        raise RuntimeError(f"Unexpected yt-dlp metadata output: {result.stdout!r}")
    return {
        "id": parts[0],
        "title": parts[1],
        "duration_string": parts[2],
        "uploader": parts[3],
        "upload_date": parts[4],
        "webpage_url": parts[5],
    }


def download_caption(url: str, out_dir: Path, video_id: str) -> tuple[Path, str]:
    candidates = [
        ("manual English captions", ["--write-sub", "--sub-lang", "en"]),
        ("English original auto captions", ["--write-auto-sub", "--sub-lang", "en-orig"]),
        ("English auto captions", ["--write-auto-sub", "--sub-lang", "en"]),
    ]
    for label, flags in candidates:
        for stale in out_dir.glob(f"{video_id}*.json3"):
            stale.unlink()
        cmd = [
            "yt-dlp",
            *flags,
            "--sub-format",
            "json3",
            "--skip-download",
            "-o",
            str(out_dir / "%(id)s"),
            url,
        ]
        result = run(cmd, check=False)
        files = sorted(out_dir.glob(f"{video_id}*.json3"))
        if result.returncode == 0 and files:
            return files[0], label
    raise RuntimeError("No usable English manual or automatic captions were downloaded.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract YouTube transcript artifacts for learning notes.")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--out-dir", default="work/youtube-learning-notes", help="Directory for extracted artifacts")
    args = parser.parse_args()

    if not shutil.which("yt-dlp"):
        print("yt-dlp is not installed. On macOS, install with: brew install yt-dlp", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = metadata_for(args.url)
    caption_file, caption_track = download_caption(args.url, out_dir, metadata["id"])
    metadata["caption_track"] = caption_track
    segments = read_json3(caption_file)
    if not segments:
        raise RuntimeError(f"Caption file contained no transcript segments: {caption_file}")
    write_outputs(segments, metadata, out_dir)
    print(
        json.dumps(
            {
                "video_id": metadata["id"],
                "title": metadata["title"],
                "duration": metadata["duration_string"],
                "caption_track": caption_track,
                "segments": len(segments),
                "first_timestamp": segments[0]["time"],
                "last_timestamp": segments[-1]["time"],
                "out_dir": str(out_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
