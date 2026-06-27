---
name: youtube-learning-notes
description: Use when the user provides a YouTube video URL and wants a transcript-derived summary, comprehensive learning notes, study guide, course notes, timestamps, key concepts, prompt recipes, visual highlights, screenshots, practice plan, or expert-organized notes from a long video.
---

# YouTube Learning Notes

## Overview

Turn a YouTube video into polished learning notes grounded in the transcript. Treat the output as an expert-organized study guide: teach the subject clearly, but do not pretend to be the video author and do not invent content that is not supported by the transcript.

## Workflow

1. Extract metadata and captions.
   - Prefer manual English captions, then English original auto captions, then English auto captions.
   - If `yt-dlp` is missing and Homebrew exists, install with `brew install yt-dlp`.
   - Use `scripts/extract_youtube_transcript.py` when possible:

```bash
python3 ~/.codex/skills/youtube-learning-notes/scripts/extract_youtube_transcript.py "YOUTUBE_URL" --out-dir work/youtube-learning-notes
```

2. Verify transcript coverage.
   - Confirm video ID, title, duration, caption track, first timestamp, last timestamp, and segment count.
   - Spot-check beginning, middle, and end before writing notes.
   - If no usable captions exist, stop and tell the user audio transcription is required.

3. Read the transcript in windows.
   - Use the generated `*_transcript_chunks.md` file.
   - Build a timestamped topic map before drafting.
   - Re-read clipped, ambiguous, or high-density sections from `*_transcript_clean.md`.
   - Mark screenshot-worthy "visual anchors" while reading.

4. Capture screenshots when visuals add learning value.
   - Use screenshots for diagrams, charts, slide frameworks, UI demos, code/app demos, before/after examples, visual comparisons, important on-screen prompts, or moments where the transcript says "this", "shown here", "on the slide", "left/right", "graph", or "example".
   - Skip screenshots for talking-head moments, generic title slides, filler transitions, or visuals that do not clarify the concept.
   - Prefer 3-8 screenshots for a long course unless the user asks for more.
   - Capture slightly after the relevant timestamp if the slide/demo appears after the narration starts.
   - Use `scripts/capture_youtube_screenshots.py`:

```bash
python3 ~/.codex/skills/youtube-learning-notes/scripts/capture_youtube_screenshots.py "YOUTUBE_URL" 00:12:34 01:05:10 --out-dir outputs/video-name-screenshots --cache-dir work/youtube-learning-notes/video-cache
```

5. Write the notes.
   - Save user-facing deliverables in the workspace `outputs/` directory when available.
   - Use a clear title, source URL, metadata, and transcript-source note.
   - Paraphrase and synthesize; avoid long transcript quotes.
   - Organize like a course companion, not a caption dump.
   - Embed only the most useful screenshots near the related section, using local image paths from the screenshot manifest.
   - Add a short caption explaining what the screenshot helps the learner remember.

6. Verify before final response.
   - Confirm output file exists.
   - Check required sections are present.
   - Check notes cover the full duration.
   - If screenshots were captured, confirm image files exist and are referenced in the notes.
   - Report caption source and any limitations.

## Recommended Notes Structure

Use this structure for comprehensive study notes unless the user asks otherwise:

- How to use these notes
- Course thesis or executive summary
- Timestamped course map
- Core mental models
- Module-by-module explanations
- Visual highlights with screenshots when they clarify the material
- Key concepts and definitions
- Practical workflows and checklists
- Reusable prompt patterns or examples from the video's domain
- Common mistakes and better alternatives
- Study questions or flashcards if requested
- Practice plan or next steps
- Final review summary

## Quality Bar

- Be comprehensive enough to replace watching the full video for learning purposes.
- Preserve timestamps for navigation.
- Use screenshots selectively as visual anchors, not decoration.
- Explain why ideas matter, not just what was said.
- Make domain-specific ideas actionable.
- Mark uncertainty from auto-caption errors instead of smoothing it into fake certainty.
- Do not include irrelevant generic advice just to make notes longer.

## Common Failures

| Failure | Fix |
|---|---|
| Notes only summarize the first part | Verify transcript last timestamp and read all chunks |
| Output sounds generic | Build a topic map and add expert commentary tied to transcript content |
| Model imitates the speaker as if it is them | Write as an expert note-taker or teacher, not as the author |
| Auto captions contain errors | Correct obvious terms cautiously and flag uncertain phrases |
| Web search replaces transcript grounding | Use web only for metadata or verification; base notes on transcript |
| Too much transcript copied verbatim | Paraphrase, synthesize, and use only short excerpts when necessary |
| Screenshots become decorative clutter | Capture only visuals that teach, summarize, compare, or preserve an on-screen artifact |
| Screenshot timing is off | Capture a few seconds later or inspect nearby frames before embedding |

## Deliverable Pattern

Final response should be short and include:

- Link to the Markdown notes file.
- Transcript source and coverage.
- Screenshot count and location, if visual highlights were included.
- Any limitations, such as auto captions or missing sections.
