#!/usr/bin/env python3
"""Remove all references to kontakt.html from HTML files.
- Remove <a> tags that link to kontakt.html
- Remove kontakt entries from the JSON menu in initPublishedFlyoutMenus
"""
import re
from pathlib import Path

ROOT = Path("/app/mirror/www.easywired.de")

# Remove <li> wrapping an <a href=...kontakt.html...> menu entry
# Multi-line, non-greedy
li_with_kontakt = re.compile(
    r'<li[^>]*>\s*<a[^>]*href="[^"]*kontakt\.html[^"]*"[^>]*>.*?</a>\s*</li>',
    re.IGNORECASE | re.DOTALL,
)

# A bare <a ... kontakt.html ...>...</a> not wrapped in <li>
a_kontakt = re.compile(
    r'<a[^>]*href="[^"]*kontakt\.html[^"]*"[^>]*>.*?</a>',
    re.IGNORECASE | re.DOTALL,
)

# JSON-array entries containing "url":"kontakt.html"
# Match a comma-separated object that contains "kontakt.html"
json_entry = re.compile(
    r',\s*\{[^{}]*"url"\s*:\s*"[^"]*kontakt\.html"[^{}]*\}',
    re.IGNORECASE,
)
# Also match if it's the first entry (preceded by [ )
json_entry_first = re.compile(
    r'\[\s*\{[^{}]*"url"\s*:\s*"[^"]*kontakt\.html"[^{}]*\}\s*,',
    re.IGNORECASE,
)

total = 0
for p in ROOT.rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    orig = text
    text = li_with_kontakt.sub("", text)
    text = a_kontakt.sub("", text)
    text = json_entry.sub("", text)
    text = json_entry_first.sub("[", text)
    if text != orig:
        p.write_text(text, encoding="utf-8")
        total += 1
print(f"Files updated: {total}")

# Sanity check: are there any remaining kontakt.html references?
remaining = 0
for p in ROOT.rglob("*.html"):
    if "kontakt.html" in p.read_text(encoding="utf-8", errors="ignore"):
        remaining += 1
print(f"Files still referencing kontakt.html: {remaining}")
