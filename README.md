# easywired.de — Statische Custom-Site

Selbstgehostete, statische Website für das private, nicht-kommerzielle Habbo-Fanprojekt **easyWIRED** von Surab Link.

**Kein Weebly, kein CMS, kein Backend, kein Tracking. Nur HTML, CSS und ein bisschen JavaScript.**

---

## Tech-Stack

| Bereich | Wahl |
| --- | --- |
| Hosting | STRATO VPS (Ubuntu 22.04, nginx) |
| Deployment | GitHub Actions → rsync via SSH auf push to `master` |
| Frontend | Statisches HTML (183 Seiten) + eigenes CSS + Vanilla-JS |
| Design | Warmes Orange (#a85f2e), Montserrat (self-hosted woff2), Dark-Mode via CSS-Variablen |
| Framework | **Keins.** ~12 KB CSS + ~4 KB JS, das war's |

---

## Struktur

```
/
├── *.html                       # 183 statische Content-Seiten (alle nutzen das gleiche Custom-Template)
├── 404.html                     # Eigenständige Fehlerseite
├── assets/
│   ├── app.css                  # Design-System + Dark-Mode
│   ├── app.js                   # Theme-Toggle + Mobile-Nav
│   ├── privacy-notice.css       # Datenschutz-Hinweisbalken
│   ├── privacy-notice.js        # Vanilla-JS für Banner
│   └── fonts/                   # Selbst-gehostete Montserrat woff2
├── uploads/                     # Autor-Bilder/GIFs (≈127 MB)
├── media/weebly/                # Ehemalige Weebly-CDN-Videos (jetzt lokal)
├── robots.txt
├── .well-known/security.txt
├── SECURITY_AUDIT.md
├── LEGAL_AUDIT.md
├── REFACTORING_NOTES.md
├── docs/
│   ├── deploy-ssh.md
│   └── nginx-security.conf
├── scripts/                     # Migration + Refactoring Pipeline (01-12)
└── .github/workflows/deploy.yml # Rsync-Deploy auf STRATO
```

---

## Design-System auf einen Blick

**Farben:** Definiert via CSS-Variablen in `assets/app.css`. Der `data-theme="dark"`-Attributschalter auf `<html>` aktiviert Dark-Mode.

**Fonts:** Montserrat (Regular 400, Bold 700) — selbst gehostet, keine Google-Fonts-Verbindung.

**Layout:** Fluid, mobil-first, Breakpoint bei 900 px für Nav-Umschaltung auf Hamburger-Menü.

**Motion:** Sanfte Transitions auf Farb-Änderungen und Hover-States. Kein Framework.

---

## Was Junior-Entwickler wissen müssen

### Neuen Menüpunkt hinzufügen

Öffne alle 183 `.html`-Dateien und ergänze eine neue Zeile in der `<ul class="site-nav__list">`. **Trick:** Nutze VS-Codes „Ersetzen in Dateien"-Funktion.

```html
<li><a class="site-nav__link" href="neue-seite.html">Neue Seite</a></li>
```

### Neue Seite anlegen

Kopie einer bestehenden HTML-Datei; ändere `<title>`, `<h1 class="page-hero__title">` und den Inhalt der `<article class="content">`.

### Design ändern

Alle Farben und Größen liegen als CSS-Variablen ganz oben in `assets/app.css`. Beispiel:

```css
:root {
  --brand: #a85f2e;      /* Akzentfarbe → hier ändern */
  --header-h: 68px;      /* Höhe der oberen Leiste */
  --radius: 8px;         /* Ecken-Abrundung */
}
```

Dark-Mode-Variante des gleichen Tokens:

```css
html[data-theme="dark"] {
  --brand: #e08957;      /* Helleres Orange für dunklen Hintergrund */
}
```

### Dark-Mode-Toggle-Logik

Steckt in `assets/app.js`, Funktion `bindThemeToggle()`. Speichert Auswahl in `localStorage.ew-theme`.

### Datenschutz-Banner

Wörter ändern? → `assets/privacy-notice.js`, Funktion `buildBanner()`.

---

## Deployment

Jeder Push auf `master` (oder `main`) startet automatisch den [`deploy.yml`](.github/workflows/deploy.yml)-Workflow. Dieser rsyncet alles außer `.git*`, `.github/`, `docs/`, `README*`, `.env*`, `node_modules/` nach `/srv/easywired-new/` auf dem STRATO-VPS.

**Benötigte GitHub-Secrets:** `STRATO_HOST`, `STRATO_USER`, `STRATO_SSH_KEY`, optional `STRATO_PORT` (Default 22) und `STRATO_TARGET_DIR` (muss `/srv/easywired-new` sein).

Manueller Dry-Run: GitHub → Actions → „Deploy" → `Run workflow` → `dry_run=true`.

---

## Lokale Vorschau

```bash
git clone https://github.com/SurabLink/easywired-new.git
cd easywired-new
python3 -m http.server 8000
# → http://localhost:8000/
```

---

## Migrationsverlauf

Diese Site ist eine 1:1-Migration der alten Weebly-Version — mit umfangreichem Aufräumen. Die vollständige Pipeline liegt in [`scripts/`](scripts/) (Numerierung 01-12 = chronologische Reihenfolge). Highlights:

- **01-05:** Content von Weebly gecrawlt, CDN-Assets lokalisiert, Cache-Buster entfernt
- **06:** Weebly-Video-iframes durch native HTML5-`<video>`-Player ersetzt
- **07:** Externe Tracker (Zotabox, Cookiebot, Smilingoat, Weebly Lead-Form) rausgeworfen
- **08-09:** Impressum + Datenschutzerklärung DDG/DSGVO-konform neu geschrieben, eigener Info-Banner
- **10:** Google Analytics und Snowplow-Tracker aufgespürt und entfernt (Nachtrag)
- **11:** Alle 183 Seiten in neues Custom-Template gegossen — kein Weebly-Chrome mehr
- **12:** cdn-assets/, files/, cdn-cgi/ und Übergangs-Dateien gelöscht

Vollständige Details siehe [`REFACTORING_NOTES.md`](REFACTORING_NOTES.md), [`SECURITY_AUDIT.md`](SECURITY_AUDIT.md) und [`LEGAL_AUDIT.md`](LEGAL_AUDIT.md).

---

## Kontakt

**Verantwortlich:** Surab Link, Robert-Kircher-Str. 4, 36037 Fulda — `kontakt@easywired.de`

Sicherheits-Findings bitte über [`.well-known/security.txt`](.well-known/security.txt) melden.
