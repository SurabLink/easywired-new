# easywired.de — Statische Spiegelung

Selbstgehostete, statische 1:1-Spiegelung der ehemaligen Weebly-Website [easywired.de](https://www.easywired.de) durch **Surab Link**.  
Die Seite läuft komplett ohne Weebly, ohne Backend, ohne Datenbank und ohne externe Tracker.

---

## Schnellübersicht

| Aspekt | Wert |
| --- | --- |
| Charakter | Privates, nicht-kommerzielles Habbo-Fanprojekt |
| Stack | Statische HTML-Dateien (183 Seiten), CSS, JS — direkt aus `/srv/easywired-new` |
| Hosting | STRATO VPS (Ubuntu 22.04, nginx) |
| Deployment | GitHub Actions → rsync via SSH on push to `master`/`main` |
| Cookies / Tracking | **Keine** — nur Server-Logs (max. 7 Tage) |
| Security-Audit | [`SECURITY_AUDIT.md`](SECURITY_AUDIT.md) |
| Legal-Audit | [`LEGAL_AUDIT.md`](LEGAL_AUDIT.md) |
| nginx-Config | [`docs/nginx-security.conf`](docs/nginx-security.conf) |

---

## Repository-Struktur

```
/
├── *.html                       # 183 statische Seiten der Originalsite
├── files/                       # Theme-Assets (CSS, JS, Schriftarten)
├── uploads/                     # Vom Autor hochgeladene Bilder/GIFs (≈127 MB)
├── cdn-assets/                  # Lokal gespiegelte Weebly-CDN-Ressourcen
│   ├── cdn11.editmysite.com/
│   └── cdn2.editmysite.com/
├── media/weebly/                # Restliche Weebly-CDN-Mediendateien
│                                #   (Videos + Poster-Bilder)
├── assets/
│   ├── privacy-notice.css       # Hinweisbalken-Styles
│   └── privacy-notice.js        # Vanilla-JS, keine Tracker, keine Deps
├── cdn-cgi/                     # Cloudflare-Email-Decoder (lokaler Stub)
├── 404.html                     # Gehärtete Fehlerseite
├── robots.txt
├── .well-known/security.txt     # RFC 9116 Disclosure-Kontakt
├── SECURITY_AUDIT.md            # Sicherheits-Audit-Bericht
├── LEGAL_AUDIT.md               # DSGVO/DDG-Audit-Bericht
├── README.md                    # diese Datei
├── docs/
│   ├── deploy-ssh.md            # Doku zum Deploy-Workflow
│   └── nginx-security.conf      # Empfohlene nginx-Konfiguration
└── .github/workflows/deploy.yml # CI: rsync auf STRATO
```

---

## Wichtige Änderungen gegenüber der Weebly-Originalsite

1. **Kontaktseite entfernt** – `kontakt.html` wurde nicht migriert; sämtliche internen Links und Menüeinträge auf diese Seite sind raus.
2. **Externe Weebly-CDNs lokalisiert** – Alle `cdn11.editmysite.com` und `cdn2.editmysite.com`-Referenzen wurden auf lokale Pfade umgeschrieben (`cdn-assets/...`).
3. **Restliche Weebly-Medien lokalisiert** – Acht eingebettete Videos (vorher von `weebly.com/weebly/apps/generateVideo.php` per `<iframe>`+`document.write` nachgeladen) wurden durch native HTML5 `<video controls>`-Player ersetzt; alle MP4s liegen unter `media/weebly/`.
4. **Externe Tracker entfernt** – Zotabox, Cookiebot, Smilingoat-Comments und das Weebly-Lead-Form (gesamt 736 Tags auf 183 Seiten) wurden ausgebaut.
5. **Security-Header per Meta-Tag** – Content-Security-Policy, X-Content-Type-Options, Referrer-Policy und Permissions-Policy sind in jedem `<head>` injiziert; zusätzliche HTTP-Header werden über die mitgelieferte nginx-Konfig gesetzt.
6. **`rel="noopener noreferrer"`** auf allen 316 `target="_blank"`-Links – Reverse-Tabnabbing-Schutz.
7. **Impressum & Datenschutz neu** – DDG/MStV/DSGVO/TDDDG-konform, ohne unwahre Cookie- oder Kontaktformular-Erwähnungen.
8. **Eigener Datenschutz-Hinweisbalken** – Vanilla-JS, design-konsistent, informatorisch (kein Consent-Banner-Theater).
9. **Cache-Buster-Suffixe entfernt** – Datei-/Referenz-Suffixe wie `@1782116011` raus, damit nginx-MIME-Detection sauber arbeitet (besonders für WOFF2-Schriftarten).

---

## Lokale Vorschau

```bash
git clone https://github.com/SurabLink/easywired-new.git
cd easywired-new
python3 -m http.server 8000
# http://localhost:8000/
```

---

## Deployment

Bei jedem Push auf `main`/`master` synchronisiert der GitHub-Actions-Workflow das Repository (außer `.github/`, `.git*`, `docs/`, `README*`, `.env*`, `node_modules/`) per `rsync --delete` nach `/srv/easywired-new/` auf den STRATO-VPS.

Benötigte GitHub-Secrets:

- `STRATO_HOST`, `STRATO_USER`, `STRATO_SSH_KEY` (Pflicht)
- `STRATO_PORT` (Default `22`), `STRATO_TARGET_DIR` (muss `/srv/easywired-new` sein)

Manueller Dry-Run: GitHub → Actions → „Deploy" → „Run workflow" → `dry_run=true`.

Details siehe [`docs/deploy-ssh.md`](docs/deploy-ssh.md).

---

## Kontakt

Verantwortlich: Surab Link, Robert-Kircher-Str. 4, 36037 Fulda — `kontakt@easywired.de`

Bei Sicherheits-Findings: bitte über [`.well-known/security.txt`](.well-known/security.txt) melden.
