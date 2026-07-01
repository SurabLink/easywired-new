# Migrations- und Refactoring-Pipeline

Dieser Ordner enthält die einmalig verwendeten Python-Skripte, mit denen aus
dem gecrawlten Weebly-HTML die aktuelle statische Site erzeugt wurde. Die
Skripte sind in der Ausführungsreihenfolge numeriert und dokumentieren, wie
aus dem rohen `wget --mirror`-Ergebnis der heutige Zustand geworden ist.

**Zielgruppe:** Nachvollziehbarkeit für spätere Wartung — nicht dafür gedacht,
dass sie routinemäßig neu ausgeführt werden.

## Reihenfolge

| # | Skript | Aufgabe |
| --- | --- | --- |
| 01 | `download_cdn_assets.py` | Rekursiv alle von den Weebly-CDNs (`cdn11/2.editmysite.com`) referenzierten Sub-Assets nachziehen |
| 02 | `rewrite_links.py` | HTML/CSS-Verweise auf `cdn11/2.editmysite.com` in lokale `cdn-assets/...`-Pfade umschreiben |
| 03 | `remove_kontakt.py` | Kontaktseite und alle internen Links darauf entfernen |
| 04 | `fix_query_paths.py` | wget-Umbenennungen (`?123` → `@123`) in HTML-Referenzen korrigieren |
| 05 | `strip_cache_busters.py` | `@digits`- und `?digits`-Cache-Buster aus Dateinamen und Referenzen entfernen |
| 06 | `replace_weebly_media.py` | Verbliebene Weebly-CDN-Videos/Bilder lokalisieren, Iframe-Player → HTML5 `<video>` |
| 07 | `harden_security.py` | Zotabox / Cookiebot / Smilingoat / Weebly-LeadForm raus, `rel="noopener"` setzen, Security-Meta-Header injizieren |
| 08 | `rewrite_impressum.py` | Impressum + Datenschutzerklärung DDG/DSGVO-konform neu schreiben |
| 09 | `inject_privacy_banner.py` | Referenzen auf den eigenen Privacy-Banner (`assets/privacy-notice.*`) in `<head>`/`<body>` einfügen |
| 10 | `refactor_extract_common.py` | Duplizierten Inline-CSS/JS aus allen 183 HTML-Seiten in `assets/site-theme.css` und `assets/site-config.js` auslagern; Google Analytics und Snowplow-Tracker entfernen |

## Ausführung (bei Bedarf)

```bash
cd /pfad/zum/repo
for s in scripts/*.py; do
  echo "==== $s ===="
  python3 "$s"
done
```

Alle Skripte sind idempotent — mehrfaches Ausführen ist harmlos. Sie benötigen
nur die Python-Standardbibliothek, keine externen Dependencies.
