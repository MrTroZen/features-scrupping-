#!/usr/bin/env python3
"""
verify_kallaway_videos_quality.py

Quality verification script for Kallaway long-form knowledge entries:
1. File naming convention (3-digit serial + lowercase kebab-case slug, .md).
2. Section architecture:
   - YAML frontmatter: serial, title, source, category, tags
   - # Key Information
   - # Numbers / Calculations
   - # Useful Method / Takeaway
   - # Context
   - # Source (valid video URL)
3. Numerical presence: Ensures numerical benchmarks exist in Numbers / Calculations.
4. Tone check: Ensures no prohibited generic marketing hype.
"""

import os
import re
import sys

BASE_DIR = os.path.join("knowledge", "kallaway", "kallaway-full-form")

PROHIBITED_PHRASES = [
    "game changer", "revolutionary", "all-in-one superpower",
    "magic bullet", "unbelievable results"
]

def verify_file(filepath):
    filename = os.path.basename(filepath)
    errors = []

    # 1. Filename check
    if not filename.endswith(".md"):
        errors.append("File must have .md extension")
    slug = filename[:-3]
    if not re.match(r'^\d{3}-[a-z0-9]+(-[a-z0-9]+)*$', slug):
        errors.append(f"Filename '{filename}' does not follow '001-title-slug.md' convention")

    # 2. Content inspection
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Frontmatter check
    if not content.startswith("---"):
        errors.append("Missing opening YAML frontmatter delimiter (---)")
    fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        errors.append("Malformed YAML frontmatter")
    else:
        fm = fm_match.group(1)
        for req_field in ["serial:", "title:", "source:", "category:", "tags:"]:
            if req_field not in fm:
                errors.append(f"Missing frontmatter field '{req_field}'")

    # Section headings check
    for req_sec in ["# Key Information", "# Numbers / Calculations", "# Useful Method / Takeaway", "# Context", "# Source"]:
        if req_sec not in content:
            errors.append(f"Missing required section heading '{req_sec}'")

    # Source link check
    if not re.search(r'Video:\s+https?://(www\.)?youtube\.com/watch\?v=[\w-]+', content):
        errors.append("Missing or invalid 'Video: <url>' link in # Source section")

    # Numbers presence
    nums_match = re.search(r'# Numbers / Calculations\n(.*?)(?=\n#|\Z)', content, re.DOTALL)
    if nums_match:
        nums_sec = nums_match.group(1).strip()
        if not re.search(r'(\d+%|\$\d+|\d+\s+(seconds?|minutes?|hours?|days?|months?|years?|x)|\d+:\d+|\d+)', nums_sec):
            errors.append("Numbers / Calculations section lacks concrete numerical figures")
    else:
        errors.append("Could not isolate Numbers / Calculations section")

    # Tone check
    content_lower = content.lower()
    for phrase in PROHIBITED_PHRASES:
        if phrase in content_lower:
            errors.append(f"Contains prohibited hype phrase '{phrase}'")

    return errors

def main():
    if not os.path.exists(BASE_DIR):
        print(f"Directory {BASE_DIR} does not exist.")
        sys.exit(1)

    files = [f for f in os.listdir(BASE_DIR) if f.endswith(".md") and f != ".gitkeep"]
    print(f"Found {len(files)} dossiers in {BASE_DIR}.\n")

    passed = 0
    failed = 0

    for f in sorted(files):
        path = os.path.join(BASE_DIR, f)
        errors = verify_file(path)
        if not errors:
            passed += 1
        else:
            failed += 1
            print(f"[FAIL] {f}")
            for err in errors:
                print(f"       -> {err}")

    print("\n" + "=" * 50)
    print(f"VERIFICATION SUMMARY: {passed} PASSED | {failed} FAILED (Total: {len(files)})")
    print("=" * 50)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
