#!/usr/bin/env python3
"""
12_delete_weebly_assets.py
============================================================================
Löscht sämtliche verbleibenden Weebly-Reste NACHDEM die Seiten durch das
Custom-Template ersetzt wurden. Dies ist der finale Schritt der Migration.

Löscht ersatzlos:
  - cdn-assets/       (gespiegelte Weebly-CDN-Assets: jQuery 1.8/2.1, main.js,
                       Weebly-Theme-CSS, Sprites, Fonts …)
  - files/            (Weebly-Theme-Ordner mit main_style.css, templateArtifacts.js,
                       theme/ Fonts + Plugins)
  - cdn-cgi/          (Cloudflare-Email-Decoder-Stub)
  - assets/site-theme.css und assets/site-config.js
                      (waren die Zwischenstation vor dem Custom-Template)

Wird durch scripts/11_rebuild_pages_from_template.py obsolet gemacht — hier
nur zu Dokumentationszwecken idempotent aufgeführt.
============================================================================
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TO_DELETE_DIRS = ["cdn-assets", "files", "cdn-cgi"]
TO_DELETE_FILES = ["assets/site-theme.css", "assets/site-config.js"]

for d in TO_DELETE_DIRS:
    p = ROOT / d
    if p.exists():
        shutil.rmtree(p)
        print(f"Removed dir: {p}")
for f in TO_DELETE_FILES:
    p = ROOT / f
    if p.exists():
        p.unlink()
        print(f"Removed file: {p}")

print("Weebly cleanup complete.")
