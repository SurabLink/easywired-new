#!/usr/bin/env python3
"""
13_update_navigation.py
============================================================================
Ergänzt das Header-Menü um Dropdown-Untermenüs. Nach 11_rebuild_pages_
from_template.py hatten die neuen Seiten nur die 6 Haupt-Menüpunkte, weil
Weeblys initPublishedFlyoutMenus-JSON die Sub-Items nicht enthielt.

Diese Sub-Items sind in der Original-HTML als <a class="wsite-menu-subitem">
vorhanden gewesen und werden hier händisch als neuer Menü-Baum eingesetzt.

Findet in jeder HTML-Datei den bestehenden <nav class="site-nav">...</nav>-
Block und ersetzt ihn durch die neue Version mit Dropdowns.
============================================================================
"""
import re
import html as html_lib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Menü-Struktur (kanonische Quelle der Wahrheit)
# ---------------------------------------------------------------------------
MENU = [
    {"title": "Start", "url": "index.html"},
    {
        "title": "News",
        "url": "news.html",
        "children": [
            {"title": "easyWIRED", "url": "easywired.html"},
            {"title": "Update Liste", "url": "update-liste.html"},
            {"title": "Interview", "url": "interview1.html"},
            {"title": "Community-Fragen", "url": "community-fragen.html"},
            {"title": "Wired-Forschung", "url": "wired-forschung.html"},
        ],
    },
    {
        "title": "Wireds Lernen",
        "url": "wireds-lernen.html",
        "children": [
            {"title": "Wired-Artikel", "url": "wired-artikel.html"},
            {"title": "Wired-Tool", "url": "wired-tool.html"},
            {"title": "Kurztutorials", "url": "kurztutorials.html"},
            {"title": "Videotutorials", "url": "videotutorials.html"},
        ],
    },
    {
        "title": "Wired Szene",
        "url": "wired-szene.html",
        "children": [
            {"title": "Wired Career", "url": "wired-career.html"},
            {"title": "Wired Räume", "url": "wired-raumlume.html"},
        ],
    },
    {
        "title": "Tipps & Tricks",
        "url": "tipps--tricks.html",
        "children": [
            {"title": "Commands", "url": "commands.html"},
            {"title": "Bodenlayout Editor", "url": "bodenlayout-editor.html"},
            {"title": "AFK-Leveln", "url": "afk-leveln.html"},
            {"title": "Sonstiges", "url": "sonstiges.html"},
        ],
    },
    {"title": "Teammitglieder", "url": "teammitglieder.html"},
    {"title": "Impressum", "url": "impressum-und-datenschutz.html"},
]

# SVG caret icon
CARET = (
    '<svg class="site-nav__caret" viewBox="0 0 12 12" aria-hidden="true">'
    '<path d="M2 4l4 4 4-4"/></svg>'
)


def render_menu() -> str:
    lines = ['<ul class="site-nav__list">']
    for item in MENU:
        title = html_lib.escape(item["title"])
        url = item["url"]
        children = item.get("children") or []
        if not children:
            lines.append(
                f'    <li class="site-nav__item">'
                f'<a class="site-nav__link" href="{url}">{title}</a>'
                f'</li>'
            )
            continue
        # Item with dropdown
        lines.append('    <li class="site-nav__item" data-has-children="true" data-open="false">')
        lines.append(
            f'      <a class="site-nav__link" href="{url}">{title}{CARET}</a>'
        )
        lines.append('      <ul class="site-nav__submenu" role="menu">')
        for sub in children:
            sub_title = html_lib.escape(sub["title"])
            sub_url = sub["url"]
            lines.append(
                f'        <li role="none">'
                f'<a class="site-nav__sublink" role="menuitem" href="{sub_url}">'
                f'{sub_title}</a></li>'
            )
        lines.append('      </ul>')
        lines.append('    </li>')
    lines.append('  </ul>')
    return "\n  ".join(lines)


# ---------------------------------------------------------------------------
# Replace the existing <nav class="site-nav">…</nav> block in every page.
# ---------------------------------------------------------------------------
NAV_RE = re.compile(
    r'<nav class="site-nav"[^>]*>[\s\S]*?</nav>',
    re.IGNORECASE,
)

NEW_NAV = (
    '<nav class="site-nav" data-testid="site-nav" aria-label="Hauptnavigation">\n'
    '  ' + render_menu() + '\n'
    '    </nav>'
)


def main() -> None:
    changed = 0
    total = 0
    missing_nav = 0
    for p in ROOT.rglob("*.html"):
        if p.name == "404.html":
            continue
        total += 1
        text = p.read_text(encoding="utf-8", errors="ignore")
        if '<nav class="site-nav"' not in text:
            missing_nav += 1
            continue
        new_text, n = NAV_RE.subn(NEW_NAV, text, count=1)
        if n and new_text != text:
            p.write_text(new_text, encoding="utf-8")
            changed += 1
    print(f"Pages updated: {changed}/{total}")
    if missing_nav:
        print(f"Pages without <nav>: {missing_nav}")


if __name__ == "__main__":
    main()
