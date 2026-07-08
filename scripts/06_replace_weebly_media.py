#!/usr/bin/env python3
"""Properly replace <div class="wsite-video">...</div> blocks (matching div depth)
with native <video> tags pointing to local media."""
import re
import urllib.parse
from collections.abc import Iterator
from pathlib import Path

ROOT = Path("/app/easywired-new")
MEDIA_DIR = "media/weebly"


def _block_end(text: str, start: int) -> int:
    """Return the index just past the balanced closing </div> of the block
    starting at `start`, or -1 if unbalanced."""
    depth = 0
    j = start
    while j < len(text):
        if text[j:j+4] == "<div":
            depth += 1
            j += 4
        elif text[j:j+6] == "</div>":
            depth -= 1
            j += 6
            if depth == 0:
                return j
        else:
            j += 1
    return -1


def find_video_blocks(text: str) -> Iterator[tuple[int, int, str]]:
    """Yield (start, end, full_block_text) for each top-level
    <div class="wsite-video">...</div> block (matched by div depth)."""
    start = 0
    while True:
        i = text.find('<div class="wsite-video">', start)
        if i < 0:
            return
        end = _block_end(text, i)
        if end < 0:
            return
        yield (i, end, text[i:end])
        start = end


VIDEO_FILENAME_RE = re.compile(r'video=b/124287907-566137816592563923/([^&"\']+\.mp4)')
IMAGE_FILENAME_RE = re.compile(r'image=b/124287907-566137816592563923/([^&"\']+\.jpg)')
ALIGN_RE = re.compile(r'wsite-video-align-(\w+)')


def build_video_html(block: str) -> str | None:
    vm = VIDEO_FILENAME_RE.search(block)
    im = IMAGE_FILENAME_RE.search(block)
    if not vm or not im:
        return None
    video_name = urllib.parse.unquote(vm.group(1))
    image_name = urllib.parse.unquote(im.group(1))
    align_m = ALIGN_RE.search(block)
    align = align_m.group(1) if align_m else "center"
    text_align = align
    style_align = {
        "left": "margin: 10px 0;",
        "center": "margin: 10px auto; display: block;",
        "right": "margin: 10px 0 10px auto; display: block;",
    }.get(align, "margin: 10px 0;")

    return (
        f'<div class="wsite-video wsite-video-align-{align}" '
        f'style="text-align:{text_align};">'
        f'<video controls preload="metadata" '
        f'poster="{MEDIA_DIR}/{image_name}" '
        f'style="max-width:100%; height:auto; {style_align}">'
        f'<source src="{MEDIA_DIR}/{video_name}" type="video/mp4">'
        f'Ihr Browser unterstützt das Video-Element nicht. '
        f'<a href="{MEDIA_DIR}/{video_name}">Video herunterladen</a>'
        f'</video>'
        f'</div>'
    )


# <img ... src="...weebly.com/uploads/b/124287907.../X" ...>
IMG_WEEBLY_RE = re.compile(
    r'<img([^>]*?)src=(["\'])(?:https?:)?//www\.weebly\.com/uploads/b/124287907-566137816592563923/([^"\']+)\2([^>]*)>',
    re.IGNORECASE,
)

# <meta ... content="...weebly.com..."  -> rewrite to local
META_WEEBLY_RE = re.compile(
    r'(<meta[^>]+content=)(["\'])(?:https?:)?//www\.weebly\.com/uploads/b/124287907-566137816592563923/([^"\']+)\2',
    re.IGNORECASE,
)


def img_repl(m):
    fname = urllib.parse.unquote(m.group(3))
    return f'<img{m.group(1)}src={m.group(2)}{MEDIA_DIR}/{fname}{m.group(2)}{m.group(4)}>'


def meta_repl(m):
    fname = urllib.parse.unquote(m.group(3))
    return f'{m.group(1)}{m.group(2)}{MEDIA_DIR}/{fname}{m.group(2)}'


changed = 0
videos = 0
imgs = 0
metas = 0
for p in ROOT.rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    orig = text

    # Find blocks (collect first, then replace from end so offsets stay valid)
    blocks = list(find_video_blocks(text))
    for start, end, blk in reversed(blocks):
        new_html = build_video_html(blk)
        if new_html:
            text = text[:start] + new_html + text[end:]
            videos += 1

    new_text, n1 = IMG_WEEBLY_RE.subn(img_repl, text)
    imgs += n1
    text = new_text

    new_text, n2 = META_WEEBLY_RE.subn(meta_repl, text)
    metas += n2
    text = new_text

    if text != orig:
        p.write_text(text, encoding="utf-8")
        changed += 1

print(f"HTML files changed:  {changed}")
print(f"Video blocks replaced: {videos}")
print(f"<img> tags rewritten:  {imgs}")
print(f"<meta> tags rewritten: {metas}")

# Sanity check
import subprocess
out = subprocess.run(
    ["grep", "-rohE", r"(https?:)?//www\.weebly\.com[^\"')\s<>]+", "--include=*.html", str(ROOT)],
    capture_output=True, text=True,
)
leftover = sorted(set(line for line in out.stdout.splitlines() if line.strip()))
print(f"Remaining weebly.com URLs in HTML: {len(leftover)}")
for ref in leftover[:10]:
    print(f"  {ref[:140]}")
