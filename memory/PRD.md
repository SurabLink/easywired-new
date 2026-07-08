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

## Backlog / P2
- Optional: Privacy-Banner schlanker machen (deckt ~180px am unteren Rand bis zum Schließen)
- Optional: Grafik-Button "Was ist neu?" (PNG) durch echten HTML-Button ersetzen
- Optional: Legacy-ew-*-Overrides in eigene CSS-Datei auslagern
- Optional: data-testid für CTA-Buttons und Privacy-Banner-Close
