#!/usr/bin/env python3
"""Recursively download CDN assets referenced from already-mirrored CSS files."""
import os
import re
import urllib.request
import urllib.parse
import sys

CDN_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mirror", "www.easywired.de", "cdn-assets"))

# Mapping of local file path -> URL where it came from (so we can resolve relative refs)
file_source_map = {}

# Initial seed: files we already downloaded with their source URLs
initial = {
    "cdn11.editmysite.com/css/sites.css": "https://cdn11.editmysite.com/css/sites.css",
    "cdn11.editmysite.com/css/old/fancybox.css": "https://cdn11.editmysite.com/css/old/fancybox.css",
    "cdn11.editmysite.com/css/social-icons.css": "https://cdn11.editmysite.com/css/social-icons.css",
    "cdn2.editmysite.com/css/old/slideshow/slideshow.css": "https://cdn2.editmysite.com/css/old/slideshow/slideshow.css",
    "cdn2.editmysite.com/fonts/Montserrat/font.css": "https://cdn2.editmysite.com/fonts/Montserrat/font.css",
}

URL_RE = re.compile(r'url\(\s*["\']?([^"\')\s]+)["\']?\s*\)', re.IGNORECASE)

downloaded = set()
queue = []

def enqueue(local_path, source_url):
    if local_path in downloaded:
        return
    queue.append((local_path, source_url))

def download(url, local_path):
    full = os.path.join(CDN_BASE, local_path)
    if os.path.exists(full):
        return True
    os.makedirs(os.path.dirname(full), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        with open(full, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  FAIL {url}: {e}", file=sys.stderr)
        return False

def process_css(local_path, source_url):
    full = os.path.join(CDN_BASE, local_path)
    if not os.path.exists(full):
        return
    if not full.endswith(('.css',)):
        return
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return
    base = source_url.rsplit("/", 1)[0] + "/"
    for m in URL_RE.finditer(content):
        ref = m.group(1).strip()
        if ref.startswith(("data:", "#", "http://www.w3.org")):
            continue
        # Resolve URL
        if ref.startswith("//"):
            abs_url = "https:" + ref
        elif ref.startswith("http://") or ref.startswith("https://"):
            abs_url = ref
        elif ref.startswith("/"):
            # Absolute path on the CDN host
            parsed = urllib.parse.urlparse(source_url)
            abs_url = f"{parsed.scheme}://{parsed.netloc}{ref}"
        else:
            abs_url = urllib.parse.urljoin(base, ref)
        # Strip query
        abs_no_query = abs_url.split("?")[0].split("#")[0]
        parsed = urllib.parse.urlparse(abs_no_query)
        if not parsed.netloc:
            continue
        new_local = parsed.netloc + parsed.path
        enqueue(new_local, abs_no_query)

# Seed
for lp, su in initial.items():
    downloaded.add(lp)
    process_css(lp, su)

while queue:
    lp, su = queue.pop(0)
    if lp in downloaded:
        continue
    downloaded.add(lp)
    if download(su, lp):
        print(f"DL {lp}")
        if lp.endswith(".css"):
            process_css(lp, su)

print(f"\nTotal downloaded: {len(downloaded)}")
