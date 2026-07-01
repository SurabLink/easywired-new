#!/usr/bin/env python3
"""Inject the privacy-notice CSS link and JS script tag into every HTML page.
CSS goes into <head>, JS just before </body>."""
import re
from pathlib import Path

ROOT = Path("/app/easywired-new")

CSS_LINK = '<link rel="stylesheet" href="assets/privacy-notice.css">\n'
SCRIPT_TAG = '<script src="assets/privacy-notice.js" defer></script>\n'

HEAD_CLOSE_RE = re.compile(r'</head>', re.IGNORECASE)
BODY_CLOSE_RE = re.compile(r'</body>', re.IGNORECASE)

changed = 0
for p in ROOT.rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    orig = text

    # Skip if already injected
    has_css = "assets/privacy-notice.css" in text
    has_js = "assets/privacy-notice.js" in text

    if not has_css:
        text = HEAD_CLOSE_RE.sub(CSS_LINK + '</head>', text, count=1)
    if not has_js:
        text = BODY_CLOSE_RE.sub(SCRIPT_TAG + '</body>', text, count=1)

    if text != orig:
        p.write_text(text, encoding="utf-8")
        changed += 1

print(f"Pages with privacy-notice injected: {changed}")
