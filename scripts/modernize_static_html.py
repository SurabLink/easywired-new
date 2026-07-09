"""Modernize legacy static HTML without changing the rendered design.

The site is a static HTML/CSS/Vanilla-JS archive. This script removes obsolete
presentational HTML that is still left from the old Weebly export while keeping
the existing CSS classes and content intact.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FONT_OPEN_RE = re.compile(r"<font\b(?P<attrs>[^>]*)>", re.IGNORECASE)
FONT_CLOSE_RE = re.compile(r"</font\s*>", re.IGNORECASE)
ATTR_RE = re.compile(
    r"""(?P<name>[\w:-]+)\s*=\s*(?P<value>"[^"]*"|'[^']*'|[^\s"'>]+)""",
    re.IGNORECASE,
)

TABLE_TAGS = {
    "table": "div",
    "tbody": "div",
    "tr": "div",
    "td": "div",
}


def _attr_value(raw: str) -> str:
    if (raw.startswith('"') and raw.endswith('"')) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        return raw[1:-1]
    return raw


def _class_token(value: str) -> str:
    token = value.strip().lower()
    if token.startswith("#"):
        token = token[1:]
    token = re.sub(r"[^a-z0-9_-]+", "-", token).strip("-")
    return token or "value"


def _replace_font_open(match: re.Match[str]) -> str:
    attrs = {
        attr.group("name").lower(): _attr_value(attr.group("value"))
        for attr in ATTR_RE.finditer(match.group("attrs"))
    }

    classes = ["legacy-font"]
    size = attrs.get("size")
    color = attrs.get("color")
    existing_classes = attrs.get("class", "").split()

    if size:
        classes.append(f"legacy-font-size-{_class_token(size)}")
    if color:
        classes.append(f"legacy-font-color-{_class_token(color)}")
    classes.extend(existing_classes)

    return f'<span class="{" ".join(classes)}">'


def _replace_layout_table_open(match: re.Match[str]) -> str:
    tag = match.group("tag").lower()
    attrs = match.group("attrs")
    return f"<{TABLE_TAGS[tag]}{attrs}>"


def _replace_layout_table_close(match: re.Match[str]) -> str:
    tag = match.group("tag").lower()
    return f"</{TABLE_TAGS[tag]}>"


def modernize_html(html: str) -> str:
    html = FONT_OPEN_RE.sub(_replace_font_open, html)
    html = FONT_CLOSE_RE.sub("</span>", html)

    html = re.sub(
        r"<(?P<tag>table|tbody|tr|td)\b(?P<attrs>[^>]*)>",
        _replace_layout_table_open,
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"</(?P<tag>table|tbody|tr|td)\s*>",
        _replace_layout_table_close,
        html,
        flags=re.IGNORECASE,
    )

    html = re.sub(r"</hr\s*>", "", html, flags=re.IGNORECASE)
    return html


def modernize_file(path: Path) -> bool:
    original_bytes = path.read_bytes()
    original = original_bytes.decode("utf-8")
    modernized = modernize_html(original)
    if modernized == original:
        return False
    path.write_bytes(modernized.encode("utf-8"))
    return True


def main() -> None:
    changed = 0
    for path in sorted(ROOT.glob("*.html")):
        if modernize_file(path):
            changed += 1
    print(f"Modernized HTML files: {changed}")


if __name__ == "__main__":
    main()
