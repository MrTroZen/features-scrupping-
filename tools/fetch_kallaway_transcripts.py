#!/usr/bin/env python3
"""
fetch_kallaway_transcripts.py

Fetches transcripts for all videos in sources/youtube-lists/kallaway-videos.csv
and saves them to raw-transcripts/kallaway/videos/serial_{serial}_{video_id}.txt.
"""

import csv
import os
import sys
import time
from youtube_transcript_api import YouTubeTranscriptApi

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CSV_PATH = os.path.join("sources", "youtube-lists", "kallaway-videos.csv")
OUT_DIR = os.path.join("raw-transcripts", "kallaway", "videos")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Total videos to fetch: {len(rows)}")
    api = YouTubeTranscriptApi()

    success_count = 0
    fail_count = 0

    for idx, row in enumerate(rows, 1):
        serial = row["serial"]
        vid = row["video_id"]
        title = row["title"]
        url = row["url"]

        out_file = os.path.join(OUT_DIR, f"serial_{serial}_{vid}.txt")
        if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
            success_count += 1
            continue

        try:
            transcript = api.fetch(vid)
            # Combine snippets into paragraphs or single clean text
            text_snippets = []
            for item in transcript:
                t = getattr(item, 'text', '') if hasattr(item, 'text') else item.get('text', '')
                if t:
                    text_snippets.append(t)
            full_text = " ".join(text_snippets)

            content = f"Title: {title}\nURL: {url}\n\n{full_text}\n"
            with open(out_file, "w", encoding="utf-8") as out_f:
                out_f.write(content)

            success_count += 1
            print(f"[{idx}/{len(rows)}] Fetched serial {serial} ({vid}) - {len(full_text)} chars")
            time.sleep(0.3)
        except Exception as e:
            fail_count += 1
            print(f"[{idx}/{len(rows)}] Failed serial {serial} ({vid}): {e}")

    print("\nFetch complete!")
    print(f"  Successfully fetched: {success_count}")
    print(f"  Failed / No transcript: {fail_count}")

if __name__ == "__main__":
    main()

