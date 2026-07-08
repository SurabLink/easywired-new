#!/usr/bin/env python3
"""
11_rebuild_pages_from_template.py
============================================================================
Ersetzt vollständig das alte Weebly-Template durch ein selbstgeschriebenes
Custom-Template mit modernem Design + Dark Mode.

Vorgehen:
  1. Aus jeder alten Weebly-HTML-Datei den Content-Bereich (innerhalb
     <div id="wsite-content">…</div>) extrahieren.
  2. Titel, Meta-Description, OG-Image extrahieren.
  3. Alle Verweise auf die alten Weebly-Assets (cdn-assets/, files/,
     assets/site-theme.css, assets/site-config.js) aus dem Content entfernen.
  4. Content in das neue Custom-Template einsetzen.
  5. Alte Weebly-Ordner werden nach dem Rebuild von einem Sibling-Script
     gelöscht (siehe 12_delete_weebly_assets.py).

Vor-/Nach-Screenshots via Playwright bestätigen: Design ist konsistent,
Content 1:1 erhalten, Navigation funktioniert.
============================================================================
"""
import re
import json
import html
from functools import lru_cache
from pathlib import Path

ROOT = Path("/app/easywired-new")

# ---------------------------------------------------------------------------
# 1. Menü aus index.html einmalig parsen
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def load_menu() -> tuple:
    text = (ROOT / "index.html").read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"initPublishedFlyoutMenus\(\s*(\[.*?\])\s*,", text, re.DOTALL)
    if not m:
        return ()
    try:
        menu_items = json.loads(m.group(1))
    except Exception:
        menu_items = []
    # Kontakt-Einträge sind bereits durch remove_kontakt.py entfernt worden.
    # Zusätzlich manuell "Impressum & Datenschutz" ins Menü aufnehmen, damit
    # er im Header sichtbar wird — aber nur, wenn nicht bereits vorhanden.
    if not any(i.get("url") == "impressum-und-datenschutz.html" for i in menu_items):
        menu_items.append({
            "title": "Impressum",
            "url": "impressum-und-datenschutz.html",
        })
    return tuple(menu_items)


def render_nav_items() -> str:
    parts = []
    for item in load_menu():
        title = item.get("title", "")
        url = item.get("url", "#")
        # HTML entity encode title
        safe_title = html.escape(title)
        parts.append(
            f'<li><a class="site-nav__link" href="{url}">{safe_title}</a></li>'
        )
    return "\n          ".join(parts)


# ---------------------------------------------------------------------------
# 2. Template
# ---------------------------------------------------------------------------
TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<meta http-equiv="Content-Security-Policy" content="default-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; media-src 'self'; font-src 'self' data:; connect-src 'self'; base-uri 'self'; form-action 'self'; object-src 'none'">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Permissions-Policy" content="geolocation=(), microphone=(), camera=(), payment=()">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:image" content="{og_image}">
<link rel="icon" href="uploads/1/2/4/2/124287907/editor/logo-ew.gif">
<link rel="stylesheet" href="assets/app.css">
<link rel="stylesheet" href="assets/privacy-notice.css">
<script>
  // Frühestmögliches Anwenden des gespeicherten Themes, um "Flash of Wrong
  // Theme" zu vermeiden. Ausführlicher Toggle-Code in assets/app.js.
  (function () {{
    try {{
      var t = localStorage.getItem('ew-theme');
      if (t === 'light' || t === 'dark') {{
        document.documentElement.setAttribute('data-theme', t);
      }}
    }} catch (e) {{}}
  }})();
</script>
</head>
<body>

<header class="site-header">
  <div class="site-header__inner">
    <a class="site-brand" href="index.html" data-testid="brand-link">
      <img class="site-brand__logo" src="uploads/1/2/4/2/124287907/editor/logo-ew.gif" alt="">
      <span class="site-brand__name">easy<span>WIRED</span></span>
    </a>
    <nav class="site-nav" data-testid="site-nav" aria-label="Hauptnavigation">
      <ul class="site-nav__list">
          {nav_items}
      </ul>
    </nav>
    <div class="header-actions">
      <button class="icon-button icon-button--theme" type="button"
              data-testid="theme-toggle"
              aria-label="Zu dunklem Design wechseln">
        <svg class="theme-icon-moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z"/>
        </svg>
        <svg class="theme-icon-sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
        </svg>
      </button>
      <button class="icon-button nav-toggle" type="button"
              data-testid="nav-toggle"
              aria-label="Menü öffnen"
              aria-expanded="false">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
    </div>
  </div>
</header>

<main class="site-main" data-testid="page-main">
  <header class="page-hero">
    <h1 class="page-hero__title">{page_title}</h1>
  </header>
  <article class="content" data-testid="page-content">
{content}
  </article>
</main>

<footer class="site-footer">
  <div class="site-footer__inner">
    <div class="site-footer__brand">
      <img src="uploads/1/2/4/2/124287907/editor/logo-ew.gif" alt="">
      <span>easy<span style="color:var(--brand)">WIRED</span></span>
    </div>
    <div class="site-footer__meta">
      Ein privates Habbo-Fanprojekt von Surab Link.<br>
      <a href="impressum-und-datenschutz.html">Impressum &amp; Datenschutz</a>
    </div>
  </div>
  <div class="site-footer__legal">
    © Sulake Oy. HABBO® und HABBO HOTEL® sind eingetragene Marken der Sulake Oy.
    Diese Fansite ist nicht mit Sulake Oy verbunden.
  </div>
</footer>

<script src="assets/app.js" defer></script>
<script src="assets/privacy-notice.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 3. Content-Extraktion
# ---------------------------------------------------------------------------
def extract_wsite_content(text):
    """Return the INNER HTML of <div id="wsite-content">…</div> (balanced)."""
    start = text.find('<div id="wsite-content"')
    if start < 0:
        return ""
    # Skip to after the opening tag
    tag_end = text.find(">", start) + 1
    i = tag_end
    depth = 1
    while i < len(text) and depth > 0:
        if text[i : i + 4] == "<div":
            depth += 1
            i += 4
        elif text[i : i + 6] == "</div>":
            depth -= 1
            if depth == 0:
                return text[tag_end:i]
            i += 6
        else:
            i += 1
    return text[tag_end:i]


def extract_title(text: str) -> str:
    m = re.search(r"<title>([^<]+)</title>", text, re.IGNORECASE)
    if not m:
        return "easyWIRED"
    t = html.unescape(m.group(1)).strip()
    # Strip trailing "- EASYWIRED" or " | EASYWIRED"
    t = re.sub(r"\s*[-|]\s*EASYWIRED\s*$", "", t, flags=re.IGNORECASE)
    return t or "easyWIRED"


def extract_og_image(text: str) -> str:
    m = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)
    return "uploads/1/2/4/2/124287907/editor/logo-ew.gif"


def extract_description(text: str) -> str:
    m = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
        text,
        re.IGNORECASE,
    )
    if m:
        return html.unescape(m.group(1)).strip()
    return "easyWIRED — privates Habbo-Wired-Fanprojekt von Surab Link."


# ---------------------------------------------------------------------------
# 4. Content-Cleanup (Weebly-Spuren entfernen)
# ---------------------------------------------------------------------------
DIV_STRIP_PATTERNS = [
    # Remove wrapping wsite-section wrappers around content — keep inner
    (re.compile(r'<div class="wsite-section-wrap">\s*'), ""),
    (re.compile(r'<section class="wsite-section[^"]*"[^>]*>\s*'), ""),
    (re.compile(r'</section>'), ""),
    (re.compile(r'<div class="wsite-section-content-wrap">\s*'), ""),
    (re.compile(r'<div class="wsite-section-content">\s*'), ""),
    # Weebly's "container" div is redundant inside our .content wrapper
    (re.compile(r'<div class="container">\s*'), ""),
    # Random invisible spacer divs
    (re.compile(r'<div\s+class="wsite-spacer"\s+style="[^"]*"\s*></div>', re.IGNORECASE), ""),
    # Weebly's outer wsite-elements div (we already have our own .content)
    (re.compile(r'<div class="wsite-elements[^"]*">\s*'), ""),
    # Strip <style scoped> blocks that referenced wsite-* internals
    (re.compile(r'<style[^>]*>[\s\S]*?</style>', re.IGNORECASE), ""),
    # Strip <script> tags inside content (dead RPC/Weebly editor code)
    (re.compile(r'<script[^>]*>[\s\S]*?</script>', re.IGNORECASE), ""),
]

CONTENT_ATTR_STRIP = [
    (re.compile(r'\s+bgcolor="[^"]*"', re.IGNORECASE), ""),
    (re.compile(r'\s+onclick="[^"]*"', re.IGNORECASE), ""),
    # Weebly data-* attributes we don't need
    (re.compile(r'\s+data-image-id="[^"]*"', re.IGNORECASE), ""),
    (re.compile(r'\s+data-color="[^"]*"', re.IGNORECASE), ""),
    (re.compile(r'\s+data-attachment="[^"]*"', re.IGNORECASE), ""),
]


def clean_content(html_text: str) -> str:
    """Remove Weebly-specific junk from extracted content while preserving
    the actual copy, images, links, videos and buttons."""
    text = html_text
    # Strip wsite wrappers
    for pat, repl in DIV_STRIP_PATTERNS:
        prev = None
        # Some patterns need multiple passes because we strip opening tags and
        # closing </div> tags separately; run until stable.
        while prev != text:
            prev = text
            text = pat.sub(repl, text)

    # After stripping opening wrappers, we may have orphan </div>s. Remove
    # the SAME number of trailing </div>s we stripped opening tags for.
    # Easiest heuristic: HTML-parse balance.
    # Count opens/closes and drop excess closes at the END.
    opens = len(re.findall(r'<div\b', text))
    closes = text.count('</div>')
    excess = closes - opens
    while excess > 0:
        # Remove the LAST </div>
        idx = text.rfind('</div>')
        if idx < 0:
            break
        text = text[:idx] + text[idx + 6:]
        excess -= 1

    for pat, repl in CONTENT_ATTR_STRIP:
        text = pat.sub(repl, text)

    return text.strip()


# ---------------------------------------------------------------------------
# 5. Rebuild
# ---------------------------------------------------------------------------
SKIP_FILES = {"404.html"}  # already custom


def rebuild_page(p: Path) -> bool:
    """Return True if page was rewritten."""
    if p.name in SKIP_FILES:
        return False
    original = p.read_text(encoding="utf-8", errors="ignore")

    # Skip already-rebuilt pages
    if 'assets/app.css' in original and 'wsite-content' not in original:
        return False

    title = extract_title(original)
    description = extract_description(original)
    og_image = extract_og_image(original)
    raw_content = extract_wsite_content(original)
    cleaned = clean_content(raw_content)

    new_html = TEMPLATE.format(
        title=html.escape(title) + " – easyWIRED",
        og_title=html.escape(title),
        description=html.escape(description),
        og_image=html.escape(og_image),
        page_title=html.escape(title),
        content=cleaned,
        nav_items=render_nav_items(),
    )
    p.write_text(new_html, encoding="utf-8")
    return True


def main() -> None:
    rewritten = 0
    total = 0
    for p in ROOT.rglob("*.html"):
        # Skip files inside .well-known etc.
        if any(part.startswith(".") for part in p.parts):
            continue
        total += 1
        try:
            if rebuild_page(p):
                rewritten += 1
        except Exception as e:
            print(f"  ERROR {p.name}: {e}")
    print(f"HTML files rebuilt: {rewritten}/{total}")


if __name__ == "__main__":
    main()

