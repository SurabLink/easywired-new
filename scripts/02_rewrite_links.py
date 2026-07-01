#!/usr/bin/env python3
"""
Rewrite all HTML/CSS files in the mirror to use local cdn-assets paths
instead of cdn11.editmysite.com / cdn2.editmysite.com URLs.
Also remove references to the contact page (kontakt.html).
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path("/app/mirror/www.easywired.de")

CDN_HOSTS = ("cdn11.editmysite.com", "cdn2.editmysite.com")

def rel_path_to_cdn_assets(html_file: Path) -> str:
    """Return relative path from html_file to cdn-assets/ folder."""
    depth = len(html_file.relative_to(ROOT).parts) - 1
    return ("../" * depth) + "cdn-assets"

def rewrite_html(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"skip {path}: {e}", file=sys.stderr)
        return False
    orig = text
    prefix = rel_path_to_cdn_assets(path)

    # Replace https://cdnXX.editmysite.com/PATH with prefix/cdnXX.editmysite.com/PATH
    # Handle both https:// and protocol-relative //
    for host in CDN_HOSTS:
        # Pattern: optional protocol+slashes then host
        pattern = re.compile(
            r'(?:https?:)?//' + re.escape(host) + r'(/[^\s"\'<>)]*)',
            re.IGNORECASE,
        )
        def repl(m):
            sub = m.group(1)
            # strip query string for filesystem mapping
            clean = sub.split("?", 1)[0].split("#", 1)[0]
            return f"{prefix}/{host}{clean}"
        text = pattern.sub(repl, text)

    # Rewrite absolute easywired.de references to relative
    # Replace https://www.easywired.de/... and http://www.easywired.de/...
    rel_root_depth = len(path.relative_to(ROOT).parts) - 1
    rel_root = ("../" * rel_root_depth) if rel_root_depth else ""
    text = re.sub(
        r'https?://(?:www\.)?easywired\.de/',
        rel_root if rel_root else "./",
        text,
        flags=re.IGNORECASE,
    )

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False

def rewrite_css(path: Path):
    """CSS files in cdn-assets reference paths like /images/... or relative ../"""
    # We leave the CSS untouched IF the references resolve correctly via the
    # downloaded folder structure. The original CSS uses paths like:
    #   url(/images/old/fancybox/blank.gif)   <- absolute on host
    #   url(../sprites/...)                   <- relative to css path
    # When CSS is loaded as cdn-assets/cdn11.editmysite.com/css/sites.css,
    # the browser resolves /images/... to /images/ on OUR host, which won't
    # work. We must rewrite absolute-on-host paths to be relative to the CSS.
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    orig = text

    # Find host from path
    rel = path.relative_to(ROOT / "cdn-assets")
    host = rel.parts[0]  # cdn11.editmysite.com or cdn2.editmysite.com
    # Depth of CSS file inside host
    depth_inside_host = len(rel.parts) - 1  # parts after host
    up_to_host = "../" * (depth_inside_host - 1) if depth_inside_host > 0 else ""

    # Replace url(/path) with url(<up_to_host>path)  -> staying within same host
    def repl_abs(m):
        path_ref = m.group(1)
        # strip query/fragment
        clean = path_ref.split("?", 1)[0].split("#", 1)[0]
        return f'url({up_to_host}{clean.lstrip("/")}'+ (m.group(2) if m.group(2) else "") + ')'

    # url(/...) form (no quotes)
    text = re.sub(
        r'url\(\s*(/[^"\')\s]+)([?#][^)\s]*)?\s*\)',
        repl_abs,
        text,
    )
    # url("/...") and url('/...')
    def repl_quoted(m):
        quote = m.group(1)
        path_ref = m.group(2)
        suffix = m.group(3) or ""
        clean = path_ref.split("?", 1)[0].split("#", 1)[0]
        return f'url({quote}{up_to_host}{clean.lstrip("/")}{suffix}{quote})'

    text = re.sub(
        r'url\(\s*(["\'])(/[^"\']+?)([?#][^"\']*)?\1\s*\)',
        repl_quoted,
        text,
    )

    # Replace //cdnX.editmysite.com/path with relative path within cdn-assets
    for h in CDN_HOSTS:
        # url(//host/path)
        def repl_proto_rel(m):
            quote = m.group(1) or ""
            full_path = m.group(2)
            clean = full_path.split("?", 1)[0].split("#", 1)[0]
            # We need to navigate from current file to ../<h>/<clean>
            # current file at host/<sub>, target at <h>/<clean>
            # so: go up to cdn-assets, then into h
            up_to_cdn_assets = "../" * depth_inside_host  # back to host root
            target = f"../{h}{clean}"
            return f"url({quote}{up_to_cdn_assets}{target}{quote})"

        text = re.sub(
            r'url\(\s*(["\']?)(?:https?:)?//' + re.escape(h) + r'(/[^"\')\s]+?)(?:[?#][^"\')\s]*)?\1\s*\)',
            repl_proto_rel,
            text,
        )

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False

# Process all HTML files
changed = 0
for p in ROOT.rglob("*.html"):
    if rewrite_html(p):
        changed += 1
print(f"HTML files rewritten: {changed}")

# Process all CSS files in cdn-assets
changed_css = 0
for p in (ROOT / "cdn-assets").rglob("*.css"):
    if rewrite_css(p):
        changed_css += 1
print(f"CDN CSS files rewritten: {changed_css}")

# Also process easywired's own main_style.css
own_css = ROOT / "files" / "main_style.css@1782116011.css"
if own_css.exists():
    # This CSS may also reference cdn URLs; rewrite like HTML
    text = own_css.read_text(encoding="utf-8", errors="ignore")
    orig = text
    # files/ is depth 1, so cdn-assets is at ../cdn-assets
    for host in CDN_HOSTS:
        pattern = re.compile(
            r'(?:https?:)?//' + re.escape(host) + r'(/[^\s"\'<>)]*)',
            re.IGNORECASE,
        )
        def repl(m):
            sub = m.group(1)
            clean = sub.split("?", 1)[0].split("#", 1)[0]
            return f"../cdn-assets/{host}{clean}"
        text = pattern.sub(repl, text)
    if text != orig:
        own_css.write_text(text, encoding="utf-8")
        print("Rewrote main_style.css")
