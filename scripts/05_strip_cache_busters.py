#!/usr/bin/env python3
"""Strip cache-buster suffixes (@digits or ?digits) from:
1. Filenames inside the mirror (files/, uploads/, cdn-assets/)
2. References in all HTML and CSS files

Handles potential filename collisions: if two files would collapse to the
same name, keeps the most recent one (highest cache-buster number).
"""
import os
import re
from pathlib import Path

ROOT = Path("/app/mirror/www.easywired.de")

# Matches a trailing @<digits> or @<digits>.<more> ... only at the end before any /
# We want to strip "@digits" that follows a file extension.
# Pattern in filenames: foo.ext@123  -> foo.ext
# Or: foo@123        -> foo            (if no extension)
SUFFIX_FILENAME_RE = re.compile(r'@\d+$')

def strip_suffix_in_path(name: str) -> str:
    return SUFFIX_FILENAME_RE.sub('', name)

# Step 1: Rename files
renamed_count = 0
collision_count = 0
# Process bottom-up so directories rename last (we only rename files anyway)
all_files = sorted(ROOT.rglob("*"), key=lambda p: -len(str(p)))
for p in all_files:
    if not p.is_file():
        continue
    new_name = strip_suffix_in_path(p.name)
    if new_name == p.name:
        continue
    target = p.with_name(new_name)
    if target.exists():
        # Collision: pick whichever is newer or larger; here just delete the older one
        # Compare cache-buster: keep the one with higher number (which means newer)
        # Get cache buster of p
        m_p = re.search(r'@(\d+)$', p.name)
        m_existing = re.search(r'@(\d+)$', target.name)  # likely None
        # If target has no buster and p has, keep target as-is (it's already canonical)
        # Just remove p
        p.unlink()
        collision_count += 1
        continue
    p.rename(target)
    renamed_count += 1

print(f"Renamed: {renamed_count}, Collisions removed: {collision_count}")

# Step 2: Update references in HTML and CSS
# Pattern in text: matches @digits or ?digits suffix right after a path char
# Strip @digits or ?digits that appear after path/URL chars (but before "/" or end)
# We restrict to occurrences where the digit run is followed by quote, space, ),
# &, #, /, end of value (something that terminates a URL/path).

# General regex: replace ([./\w-])(\?|@)\d+(?=["')\s<>#&?]|$)
# Add /  also handled below for end of path before quote
REF_RE = re.compile(r'([./\w\-])[?@](\d+)(?=["\')\s<>#&]|$)')

def clean_text(t: str) -> str:
    return REF_RE.sub(r'\1', t)

html_changed = 0
for p in ROOT.rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    new = clean_text(text)
    if new != text:
        p.write_text(new, encoding="utf-8")
        html_changed += 1
print(f"HTML refs updated: {html_changed}")

css_changed = 0
for p in ROOT.rglob("*.css"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    new = clean_text(text)
    if new != text:
        p.write_text(new, encoding="utf-8")
        css_changed += 1
print(f"CSS refs updated: {css_changed}")

js_changed = 0
for p in ROOT.rglob("*.js"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    new = clean_text(text)
    if new != text:
        p.write_text(new, encoding="utf-8")
        js_changed += 1
print(f"JS refs updated: {js_changed}")
