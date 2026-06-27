# YouTube Learning Notes

A Codex skill for turning a YouTube video into comprehensive, transcript-grounded learning notes with optional visual highlights.

The skill extracts YouTube metadata and captions, verifies transcript coverage, organizes the content into study-guide style notes, and can capture selected screenshots when on-screen visuals add learning value.

## What's included

- `SKILL.md` - the Codex skill instructions and workflow.
- `scripts/extract_youtube_transcript.py` - downloads metadata and English captions with `yt-dlp`, then writes cleaned transcript artifacts.
- `scripts/capture_youtube_screenshots.py` - captures timestamped frames from a YouTube video with `yt-dlp` and `ffmpeg`.
- `agents/openai.yaml` - optional display metadata and starter prompt.

## Requirements

- Python 3.10+
- `yt-dlp`
- `ffmpeg` for screenshot capture

On macOS:

```bash
brew install yt-dlp ffmpeg
```

## Install as a local Codex skill

Clone or copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R youtube-learning-notes ~/.codex/skills/
```

Then use the skill in Codex by asking for YouTube learning notes, for example:

```text
Use $youtube-learning-notes to turn this YouTube video into comprehensive learning notes with visual highlights: https://www.youtube.com/watch?v=...
```

## Script usage

Extract transcript artifacts:

```bash
python3 scripts/extract_youtube_transcript.py "YOUTUBE_URL" --out-dir work/youtube-learning-notes
```

Capture screenshots:

```bash
python3 scripts/capture_youtube_screenshots.py "YOUTUBE_URL" 00:12:34 01:05:10 \
  --out-dir outputs/video-screenshots \
  --cache-dir work/youtube-learning-notes/video-cache
```

## Output policy

Generated transcripts, downloaded video cache files, screenshots, and final notes are intentionally ignored by Git. Keep the repository focused on the reusable skill and scripts.

## License

No license has been selected yet. Add a license before publishing publicly if you want others to reuse or modify the skill under clear terms.
