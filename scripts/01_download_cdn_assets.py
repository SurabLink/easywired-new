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

downloaded: set[str] = set()
queue: list[tuple[str, str]] = []

def enqueue(local_path: str, source_url: str) -> None:
    if local_path in downloaded:
        return
    queue.append((local_path, source_url))

def download(url: str, local_path: str) -> bool:
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

def read_css(local_path: str) -> str | None:
    full = os.path.join(CDN_BASE, local_path)
    if not full.endswith(".css") or not os.path.exists(full):
        return None
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None

def resolve_ref(ref: str, source_url: str, base: str) -> str | None:
    """Resolve a url(...) reference from CSS to an absolute URL, or None."""
    if ref.startswith(("data:", "#", "http://www.w3.org")):
        return None
    if ref.startswith("//"):
        return "https:" + ref
    if ref.startswith(("http://", "https://")):
        return ref
    if ref.startswith("/"):
        parsed = urllib.parse.urlparse(source_url)
        return f"{parsed.scheme}://{parsed.netloc}{ref}"
    return urllib.parse.urljoin(base, ref)

def process_css(local_path: str, source_url: str) -> None:
    content = read_css(local_path)
    if content is None:
        return
    base = source_url.rsplit("/", 1)[0] + "/"
    for m in URL_RE.finditer(content):
        abs_url = resolve_ref(m.group(1).strip(), source_url, base)
        if abs_url is None:
            continue
        abs_no_query = abs_url.split("?")[0].split("#")[0]
        parsed = urllib.parse.urlparse(abs_no_query)
        if not parsed.netloc:
            continue
        enqueue(parsed.netloc + parsed.path, abs_no_query)

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
