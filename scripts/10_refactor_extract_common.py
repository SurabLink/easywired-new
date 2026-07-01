#!/usr/bin/env python3
"""
refactor_extract_common.py
============================================================================
Ziel: Duplizierten Inline-Code aus den 183 HTML-Seiten entfernen und in
externe Dateien (assets/site-theme.css, assets/site-config.js) auslagern.

Dead-Code / Tracker werden dabei ersatzlos gelöscht:
  - Google Analytics (_gaq + ga.js loader)     [DSGVO-widrig]
  - Snowplow-Tracker (`snowday`)               [DSGVO-widrig]
  - _W.setup_rpc(CustomerAccounts)             [404-Aufrufe]
  - _W.recaptchaUrl                            [keine Captchas]
  - Cookie-Banner-Config (_W.isEUUser/…)       [ersetzt durch site-config.js]
  - jQuery-Blog-Social-Wrapper                 [kein Blog/Shop]

Verhalten (Design, sichtbare Inhalte, Navigation) darf sich NICHT ändern.
Die CSS-Regeln des Weebly-Themes werden 1:1 aus dem inline-<style>-Block
in site-theme.css verschoben — kein Byte umformuliert.
============================================================================
"""
import re
import hashlib
from pathlib import Path

ROOT = Path("/app/easywired-new")

# ---------------------------------------------------------------------------
# 1. Definitionen: welche Blöcke werden was?
# ---------------------------------------------------------------------------
# Hashes wurden vorher aus index.html berechnet; sie identifizieren exakte
# Duplikate über alle 183 Seiten.
STYLE_HASH_TO_REMOVE = "53ff9062eb8a"     # -> ersetzt durch site-theme.css

SCRIPT_HASHES_TO_REMOVE = {
    "c82fcbf885dc": "STATIC_BASE config          -> site-config.js",
    "8a8535a3453d": "RPC init + CustomerAccounts -> gelöscht (404-Aufrufe)",
    "3bc9d84141a2": "_W.securePrefix             -> site-config.js",
    "6f859a2fd4b7": "_W.configDomain             -> site-config.js",
    "d05117e4ab3b": "_W.relinquish()             -> gelöscht (Editor-only)",
    "3d8a5c302532": "_W.recaptchaUrl             -> gelöscht (kein Captcha)",
    "8fb16729862b": "Google Analytics UA-…       -> gelöscht (DSGVO)",
    "dc16b97cfccc": "Snowplow-Tracker             -> gelöscht (DSGVO)",
    "711691aaea3a": "jQuery blog-social wrapper  -> gelöscht (kein Blog/Shop)",
    "af69b104dd5e": "_W.isEUUser stub            -> site-config.js",
}

STYLE_RE = re.compile(r'<style[^>]*>([\s\S]*?)</style>', re.IGNORECASE)
SCRIPT_INLINE_RE = re.compile(
    r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>',
    re.IGNORECASE,
)

# Ersatz für den zu entfernenden <style>-Block: ein <link>-Tag auf die
# ausgelagerte Datei. Nur EIN Ersatz je Seite (der erste Fund).
STYLE_REPLACEMENT = '<link rel="stylesheet" href="assets/site-theme.css">'

# Ersatz für die zu entfernenden <script>-Blöcke: nur beim ERSTEN
# gelöschten Block wird ein <script src="…site-config.js"></script> gesetzt,
# alle weiteren Blöcke werden ersatzlos entfernt.
CONFIG_SCRIPT_TAG = '<script src="assets/site-config.js"></script>'


# ---------------------------------------------------------------------------
# 2. Refactor-Funktion
# ---------------------------------------------------------------------------
def refactor(html: str):
    """Entfernt duplizierte Blöcke, gibt (neuer_html, stats) zurück."""
    stats = {"style_replaced": 0, "scripts_removed": 0}

    # 2a) Style-Block ersetzen (nur einmal, danach löschen falls Duplikat)
    style_seen = False
    def style_repl(m):
        nonlocal style_seen
        content = m.group(1).strip()
        h = hashlib.sha1(content.encode()).hexdigest()[:12]
        if h != STYLE_HASH_TO_REMOVE:
            return m.group(0)
        stats["style_replaced"] += 1
        if style_seen:
            return ""          # ist bereits ersetzt -> löschen
        style_seen = True
        return STYLE_REPLACEMENT

    html = STYLE_RE.sub(style_repl, html)

    # 2b) Alle passenden inline-<script>-Blöcke entfernen; beim ERSTEN
    #     Treffer wird stattdessen der externe site-config.js-Tag gesetzt.
    config_injected = False
    def script_repl(m):
        nonlocal config_injected
        content = m.group(1).strip()
        h = hashlib.sha1(content.encode()).hexdigest()[:12]
        if h not in SCRIPT_HASHES_TO_REMOVE:
            return m.group(0)
        stats["scripts_removed"] += 1
        if not config_injected:
            config_injected = True
            return CONFIG_SCRIPT_TAG
        return ""

    html = SCRIPT_INLINE_RE.sub(script_repl, html)

    # 2c) Aufräumen leerer Zeilen, die durch Löschungen entstanden
    html = re.sub(r'\n[ \t]*\n[ \t]*\n+', '\n\n', html)

    return html, stats


# ---------------------------------------------------------------------------
# 3. Auf alle Seiten anwenden
# ---------------------------------------------------------------------------
def main() -> None:
    total_pages = 0
    total_style = 0
    total_scripts = 0
    for p in ROOT.rglob("*.html"):
        # 404.html ist selbst geschrieben, keine Weebly-Duplikate
        if p.name == "404.html":
            continue
        original = p.read_text(encoding="utf-8", errors="ignore")
        refactored, stats = refactor(original)
        if refactored != original:
            p.write_text(refactored, encoding="utf-8")
            total_pages += 1
        total_style += stats["style_replaced"]
        total_scripts += stats["scripts_removed"]
    print(f"Seiten geändert:              {total_pages}")
    print(f"Duplizierte <style>-Blöcke:  {total_style}")
    print(f"Duplizierte <script>-Blöcke: {total_scripts}")


if __name__ == "__main__":
    main()
