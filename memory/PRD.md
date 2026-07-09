# PRD — easyWIRED Website (Layout-Reparatur)

## Original Problem Statement
Statische deutsche Website (easyWIRED, Habbo-Fanprojekt, ~200 HTML-Seiten, ehemals Weebly-Export) mit kaputtem Layout: mehrfache Scrollbars, geschrumpfte/ultra-kleine Bilder & GIFs, überdimensionierte Buttons, kollabierte Spalten (Überschriften untereinander statt nebeneinander, Elemente schmal nach links eingerückt). Ausrichtung soll komplett mit Flexbox durchdesignt sein.

## User Choices
- Design darf verbessert werden
- Komplett responsive (Desktop + Mobile)
- Schlimmste Seiten: wired-tool.html, update-liste.html

## Architektur
- Reine statische Site im /app-Root (HTML + /assets/app.css + /assets/app.js)
- Kein Backend, kein MongoDB. Preview: /app/frontend/package.json startet `python3 -m http.server 3000 --directory /app` via Supervisor
- Globales Stylesheet: /app/assets/app.css (Design-System mit Light/Dark-Theme)

## Root Cause
Legacy-Weebly-Markup: `<table class="ew-multicol-table">` mit `<td>`-Spalten (Inline-Prozentbreiten) wurde per CSS auf `display:grid` gesetzt — Grid griff nur auf tbody, Spalten kollabierten zu schmalen Streifen. Dazu: negative Margins (`margin:0 -15px`), riesige `<font size="6/7">`-Tags, führende `<br>` in Überschriften, unskalierte YouTube-iframes, Mobile-Nav mit sichtbarem Padding trotz max-height:0.

## Implementiert (08.06.2026)
- [x] Weebly-Multicol → Flexbox: `.ew-multicol-tr` = flex-row, `.ew-multicol-col` = flex-item (Inline-%-Breiten als flex-basis erhalten), Umbruch auf 2 Spalten ≤720px (wirkt auf 182 Seiten)
- [x] Negative Margins am table-wrap neutralisiert, `body { overflow-x: clip }`, `.wcustomhtml` ohne eigene Scrollbars → keine Mehrfach-Scrollbars mehr
- [x] Bilder/GIFs: natürliche Größe, responsive (max-width:100%), kompakte Abstände + zentrierte Captions in Grids
- [x] Buttons normalisiert: .ew-button 14px/10-18px Padding, small/large-Varianten
- [x] `<font size="5/6/7">` auf relative em-Größen gemappt
- [x] Führende/abschließende `<br>` in Überschriften ausgeblendet
- [x] YouTube-iframes responsive (16:9, max 720px, zentriert)
- [x] Mobile-Nav-Fix: kein durchscheinender Menüinhalt bei geschlossenem Menü
- [x] update-liste.html: "Wired Updates"-h2 von Fließtext getrennt
- [x] Testing-Agent-Lauf (iteration_1.json): 95% pass; gemeldeter Mobile-Breakpoint-Bug (1 statt 2 Kacheln/Reihe bei 390px) behoben und verifiziert

## Deployment-Readiness (08.06.2026)
- [x] Minimales FastAPI-Backend unter /app/backend (Health-Endpoint /api/), da Supervisor-Config (readonly) ein Backend erwartet
- [x] Frontend-Start auf Node-basierten Static-Server umgestellt: `serve /app -l 3000` (+ /app/serve.json: cleanUrls off, kein Directory-Listing, Root-Rewrite auf index.html)
- [x] Deployment-Agent-Check: PASS mit einer Warnung (MONGO_URL/DB_NAME in backend/.env ungenutzt — bewusst belassen, Plattform-Konvention)

## Bugfixes nach Deployment-Check
- [x] index.html: Abgeschnittener Button "Zum Selektor Experiments Lab" — Ursache: nicht geschlossene Spacer-Divs (height:10px, overflow:hidden) umschlossen den Button; Markup repariert inkl. fehlender Multicol-Wrapper-Schließtags (08.06.2026)
- [x] Header-Breakpoint von 900px auf 1180px erhöht: Zwischen 900–1180px überlappte die Navigation Logo und Header-Icons; jetzt greift dort das Hamburger-Menü (08.06.2026)
- [x] YouTube-Videos (123 Embeds) wurden von der Content-Security-Policy blockiert (kein frame-src): `frame-src 'self' youtube.com youtube-nocookie.com` in CSP-Meta aller 183 Seiten UND in docs/nginx-security.conf ergänzt (08.06.2026)

## Backlog / P2
- Optional: Privacy-Banner schlanker machen (deckt ~180px am unteren Rand bis zum Schließen)
- Optional: Grafik-Button "Was ist neu?" (PNG) durch echten HTML-Button ersetzen
- Optional: Legacy-ew-*-Overrides in eigene CSS-Datei auslagern
- Optional: data-testid für CTA-Buttons und Privacy-Banner-Close

## Implementiert (09.07.2026) — Bugfix Steckbrief-Überschrift-Bilder
- [x] Zentraler CSS-Fix in assets/app.css (von allen 117 wired-tool-*.html eingebunden, keine HTML-Änderungen)
- [x] Selektor: `.ew-multicol-tr:has(> .ew-multicol-col:first-child .ew-image):has(> .ew-multicol-col:last-child .ew-image):has(h2.ew-content-title)` — trifft NUR die Steckbrief-Kopfzeile (Bild–Titel–Bild); Logo-Header (Bild+Titel, 2 Spalten) und Inhalts-Tabellen ausgeschlossen
- [x] Flexbox: align-items:center, justify-content:center, gap:clamp(12px,2.5vw,28px), nowrap auf Desktop; Inline-td-Breiten (8.9%/53.6%/37.5%) neutralisiert (width:auto !important, flex 0 0 auto für Bildspalten)
- [x] Bilder: height:clamp(48px,8vw,96px), width:auto, object-fit:contain — gleich groß, unverzerrt; center/left-Asymmetrie behoben (text-align:center !important)
- [x] Mobile <600px: flex-wrap, Titelspalte flex 1 1 100% + order:-1 → Überschrift oben, Bilder symmetrisch darunter
- [x] Verifiziert (Playwright-Metriken): 6 Steckbriefe Desktop (96px/96px, gap 28/28, midDiff 0) + Mobile 390px (60×48/60×48, kein Overflow); Phase-4-Check: andere ew-multicol-Tabellen unberührt
- Hinweis: :has() ohne Fallback (User-Entscheidung: nur aktuelle Browser)

## Implementiert (09.07.2026) — CSS-Auslagerung (Inline & <style> → externe Dateien)
- [x] Aktueller Stand von GitHub (042a6fd) gesynct; reine Vanilla HTML/CSS/JS-Site (kein Framework)
- [x] Scan: 184 HTML-Seiten, 8534 Inline-style-Attribute (nur 461 einzigartige Werte), 1 <style>-Block (404.html)
- [x] assets/legacy-inline.css: jede einzigartige Inline-Deklaration als dedupe Klasse .iw-001….iw-461 (nach Häufigkeit), Deklarationen mit !important zur Erhaltung der Inline-Priorität ggü. app.css
- [x] Alle 8534 style="…"-Attribute durch Klassen ersetzt (Merge in bestehende class-Attribute), HTML-Entities unescaped, paren-sicheres Splitten
- [x] <style>-Block aus 404.html → assets/404.css
- [x] Link-Einbindung: legacy-inline.css nach app.css in 183 Seiten, 404.css in 404.html
- [x] Skript: scripts/extract_inline_css.py (idempotent nutzbar)
- [x] Verifikation: FNV-Hash aller berechneten Styles pro Element vor/nachher identisch auf 5 Seiten (index, wired-tool [887 Elemente], update-liste, variable-infos, Steckbrief) → 0 visuelle Änderung; 0 verbleibende style=/style-Tags
