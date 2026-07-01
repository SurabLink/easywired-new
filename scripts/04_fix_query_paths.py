#!/usr/bin/env python3
"""Fix uploads/...?N references -> uploads/...@N (since wget renamed files
with --restrict-file-names=windows). Also fix files/ refs."""
import re
from pathlib import Path

ROOT = Path("/app/mirror/www.easywired.de")

# Match e.g. uploads/...png?123  or files/...css?123
pattern = re.compile(r'((?:uploads|files)/[^"\'<>) \s]+?)\?(\d+)')

total = 0
for p in ROOT.rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    new = pattern.sub(r'\1@\2', text)
    if new != text:
        p.write_text(new, encoding="utf-8")
        total += 1
print(f"HTML updated: {total}")
