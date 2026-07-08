#!/usr/bin/env python3
"""Apply security hardening to all HTML pages of the easywired mirror:

1. Strip dead 3rd-party tracker / lead-form / consent scripts that no longer
   serve any function on the static archive (Zotabox, Cookiebot, Smilingoat,
   Weebly lead-form snippets, cdn3.editmysite.com marketing JS).
2. Add rel="noopener noreferrer" to every <a target="_blank"> link.
3. Inject security <meta> headers (X-Content-Type-Options, Referrer-Policy,
   Content-Security-Policy fallback) into <head>.
4. Remove the dead /ajax/api/JsonRPC RPC setup blocks (they would call a
   non-existent backend on every page load).
"""
import re
from pathlib import Path

ROOT = Path("/app/easywired-new")

# 1) Strip dead 3rd-party tags. We delete entire <script>/<link> tags
#    plus any inline <script>...</script> block that references these hosts.
EXTERNAL_HOSTS = [
    "static.zotabox.com",
    "comments.smilingoat.com",
    "consent.cookiebot.com",
    "cdn3.editmysite.com",
]

# Regex: a single self-closing or pair <script>... that references one of
# these hosts somewhere in its attributes or body.
def strip_external_scripts(text: str):
    count = 0
    # Pattern: <script ...>...</script> matched non-greedily
    pattern = re.compile(r'<script[^>]*>[\s\S]*?</script>', re.IGNORECASE)
    new_parts = []
    last = 0
    for m in pattern.finditer(text):
        body = m.group(0)
        if any(h in body for h in EXTERNAL_HOSTS):
            new_parts.append(text[last:m.start()])
            last = m.end()
            count += 1
    new_parts.append(text[last:])
    text = ''.join(new_parts)

    # Self-closing or single-tag <script src="..."> (no body)
    pattern2 = re.compile(
        r'<script[^>]+src=["\'][^"\']*(?:' + '|'.join(re.escape(h) for h in EXTERNAL_HOSTS) + r')[^"\']*["\'][^>]*></script>',
        re.IGNORECASE,
    )
    text, n2 = pattern2.subn('', text)
    count += n2

    # <link rel=... href="...host..."> tags
    pattern3 = re.compile(
        r'<link[^>]+href=["\'][^"\']*(?:' + '|'.join(re.escape(h) for h in EXTERNAL_HOSTS) + r')[^"\']*["\'][^>]*/?>',
        re.IGNORECASE,
    )
    text, n3 = pattern3.subn('', text)
    count += n3

    return text, count


# 2) Add rel="noopener noreferrer" to all <a target="_blank">
TARGET_BLANK_RE = re.compile(
    r'(<a\b)([^>]*\btarget=["\']_blank["\'][^>]*)(>)',
    re.IGNORECASE,
)


def add_noopener(text: str):
    count = 0
    def repl(m):
        nonlocal count
        tag_start, attrs, tag_end = m.group(1), m.group(2), m.group(3)
        # Already has noopener?
        rel_m = re.search(r'rel=(["\'])([^"\']*)\1', attrs, re.IGNORECASE)
        if rel_m:
            rel_val = rel_m.group(2).lower()
            if 'noopener' in rel_val and 'noreferrer' in rel_val:
                return m.group(0)
            # Append missing tokens
            tokens = set(rel_val.split())
            tokens.update({'noopener', 'noreferrer'})
            new_rel = ' '.join(sorted(tokens))
            new_attrs = (
                attrs[:rel_m.start()] +
                f'rel="{new_rel}"' +
                attrs[rel_m.end():]
            )
            count += 1
            return f'{tag_start}{new_attrs}{tag_end}'
        else:
            count += 1
            return f'{tag_start}{attrs} rel="noopener noreferrer"{tag_end}'

    new_text = TARGET_BLANK_RE.sub(repl, text)
    return new_text, count


# 3) Inject security meta headers right after the first <head> tag.
# We add only headers that work via meta. (X-Frame-Options and HSTS only work
# as HTTP headers and must be set in nginx — provided in docs/nginx-security.conf.)
SECURITY_META = (
    '<meta http-equiv="Content-Security-Policy" '
    'content="default-src \'self\' data:; '
    'script-src \'self\'; '
    'style-src \'self\' \'unsafe-inline\'; '
    'img-src \'self\' data: https:; '
    'media-src \'self\'; '
    'font-src \'self\' data:; '
    'connect-src \'self\'; '
    'frame-src \'self\' https://www.youtube.com https://www.youtube-nocookie.com; '
    'base-uri \'self\'; '
    'form-action \'self\'; '
    'object-src \'none\'">\n'
    '<meta http-equiv="X-Content-Type-Options" content="nosniff">\n'
    '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
    '<meta http-equiv="Permissions-Policy" content="geolocation=(), microphone=(), camera=(), payment=()">\n'
)

HEAD_OPEN_RE = re.compile(r'(<head\b[^>]*>)', re.IGNORECASE)


def inject_meta(text: str):
    if 'Content-Security-Policy' in text:
        return text, 0
    new_text, n = HEAD_OPEN_RE.subn(r'\1\n' + SECURITY_META, text, count=1)
    return new_text, n


# 4) Remove dead Weebly RPC initializer blocks (they POST to /ajax/api/JsonRPC/...
# which doesn't exist on our static server -> 404 noise + reveals legacy paths)
RPC_BLOCK_RE = re.compile(
    r'<script[^>]*>\s*\(function\(\)\{_W\.setup_rpc\([^)]*\)\}\)\(\);?\s*</script>',
    re.IGNORECASE | re.DOTALL,
)


def strip_rpc(text: str):
    return RPC_BLOCK_RE.subn('', text)


changed = 0
script_strip = 0
noopener_added = 0
meta_added = 0
rpc_stripped = 0

for p in ROOT.rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    orig = text

    text, n = strip_external_scripts(text)
    script_strip += n

    text, n = add_noopener(text)
    noopener_added += n

    text, n = inject_meta(text)
    meta_added += n

    text, n = strip_rpc(text)
    rpc_stripped += n

    if text != orig:
        p.write_text(text, encoding="utf-8")
        changed += 1

print(f"HTML files changed: {changed}")
print(f"External tracker tags removed: {script_strip}")
print(f"<a target=_blank> hardened with noopener: {noopener_added}")
print(f"Security meta tags injected into <head>: {meta_added}")
print(f"Dead RPC initializer blocks stripped: {rpc_stripped}")
