# easywired.de — Statische Spiegelung

Dieses Repository enthält eine vollständige, selbstgehostete Spiegelung der ehemaligen Weebly-Website [easywired.de](https://www.easywired.de). Die Seite läuft komplett ohne Weebly: alle benötigten Assets (HTML, CSS, JavaScript, Bilder, GIFs, Schriftarten, Favicons) werden lokal aus dem Repository ausgeliefert.

## Inhalt

- Statische HTML-Seiten direkt im Repository-Root, identisch zur Originalstruktur (`index.html`, `news.html`, `wireds-lernen.html`, …)
- `files/` — Theme-Assets (CSS, JS, Schriftarten) aus dem ursprünglichen Weebly-Theme
- `uploads/` — Vom Autor hochgeladene Bilder/GIFs der Originalseite
- `cdn-assets/cdn11.editmysite.com/` und `cdn-assets/cdn2.editmysite.com/` — Lokale Kopien aller von den Weebly-CDNs referenzierten Ressourcen (CSS, JS, Schriftarten, Sprites). Alle Pfade in den HTML- und CSS-Dateien wurden auf diese lokalen Kopien umgeschrieben.
- `cdn-cgi/` — Originale Cloudflare-Beacon-Stubs (harmlos, ohne Funktion)
- `docs/deploy-ssh.md` — Deployment-Dokumentation (wird nicht zum Server synchronisiert)
- `.github/workflows/deploy.yml` — GitHub-Actions-Workflow für Rsync-Deployment auf den STRATO-VPS

## Wichtige Änderungen gegenüber dem Original

1. **Kontaktseite entfernt:** Die Seite `kontakt.html` wurde nicht migriert. Alle internen Links auf `kontakt.html` (inkl. Menüeinträge in `initPublishedFlyoutMenus`) wurden aus allen Seiten entfernt.
2. **Externe Weebly-CDNs lokalisiert:** Sämtliche Referenzen auf `cdn11.editmysite.com` und `cdn2.editmysite.com` wurden auf den lokalen Pfad `./cdn-assets/...` umgeschrieben.
3. **Cache-Buster entfernt:** Datei-Suffixe wie `@1782116011` bzw. `?1782116011` wurden sowohl aus den Dateinamen als auch aus allen HTML/CSS/JS-Referenzen entfernt, damit Webserver wie nginx korrekte MIME-Typen liefern (besonders relevant für Schriftarten).
4. **Absolute Easywired-URLs:** Verbliebene absolute `https://www.easywired.de/`-Links wurden in relative Pfade umgeschrieben.

Externe Inhalts-Links (Discord, Wikipedia, ChatGPT, smilingoat-Kommentare, Cookiebot-Banner, Habview u. a.) bleiben unverändert. Sie verweisen weiterhin auf die Original-Drittquellen.

## Lokales Vorschauen

```bash
cd /pfad/zum/repo
python3 -m http.server 8000
# Öffne http://localhost:8000/index.html
```

## Deployment auf STRATO

Bei jedem Push auf `main` oder `master` synchronisiert der GitHub-Actions-Workflow das gesamte Repository (außer `.github/`, `.git*`, `docs/`, `README*`, `.env*`, `node_modules/`) per `rsync` nach `/srv/easywired-new/` auf den STRATO-VPS. Die Secrets sind im Repository hinterlegt:

- `STRATO_HOST`, `STRATO_USER`, `STRATO_SSH_KEY` (Pflicht)
- `STRATO_PORT` (Standard 22), `STRATO_TARGET_DIR` (muss `/srv/easywired-new` sein)

Für ein manuelles Dry-Run-Deployment kann der Workflow „Deploy“ über die GitHub-Actions-Oberfläche mit `dry_run=true` gestartet werden. Details siehe [`docs/deploy-ssh.md`](docs/deploy-ssh.md).

## Migrations-Skripte

Die genutzten Skripte zur Reproduktion liegen außerhalb dieses Repos (`/app/scripts/` in der Build-Umgebung):

| Skript | Aufgabe |
| --- | --- |
| `wget --mirror ...` | Vollständiger Crawl von `www.easywired.de` ohne `/kontakt.html` |
| `download_cdn_assets.py` | Rekursiver Download aller von Weebly-CDNs referenzierten Sub-Assets |
| `rewrite_links.py` | Pfade auf lokale `cdn-assets/`-Kopien umschreiben |
| `remove_kontakt.py` | Entfernt sämtliche Verweise auf `kontakt.html` |
| `strip_cache_busters.py` | Entfernt `@digits`/`?digits`-Cache-Buster aus Dateinamen und Referenzen |
