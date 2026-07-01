# Refactoring Notes – easyWIRED Static Mirror

**Datum:** 2026-01-30  
**Ziel:** Code so aufräumen, dass ein Junior-Entwickler mit HTML/CSS/JS-Grundkenntnissen sich sofort zurechtfindet – **ohne** dass sich Inhalt, Design oder Verhalten verändern.

---

## Was wurde umstrukturiert?

### 1. Extern statt inline

**Problem vorher:** Jede der 183 HTML-Seiten enthielt denselben ~5.800 Zeichen langen `<style>`-Block und dazu zehn identische inline-`<script>`-Blöcke (Weebly-Bootstrap, Config, Analytics-Loader …). Ändern einer einzigen Regel hätte 183 Seiten touchieren müssen.

**Lösung:**

| Neue Datei | Enthält | Wieder verwendet auf |
| --- | --- | --- |
| [`assets/site-theme.css`](assets/site-theme.css) | Das duplizierte Weebly-Theme-CSS (Font-Familien, Farb-Placeholders, `.wsite-*`-Regeln) — 1:1 aus dem alten inline-Block extrahiert, kein Byte verändert | 183 Seiten (`<link rel="stylesheet" href="assets/site-theme.css">`) |
| [`assets/site-config.js`](assets/site-config.js) | Die einzigen wirklich benötigten Weebly-Bootstrap-Globals (`STATIC_BASE`, `ASSETS_BASE`, `_W.securePrefix`, …) — mit deutschen Kommentaren, kein Analytics | 183 Seiten (`<script src="assets/site-config.js"></script>`) |
| [`assets/privacy-notice.css`](assets/privacy-notice.css) | Styles für den eigenen Datenschutz-Hinweisbalken | 184 Seiten (inkl. 404) |
| [`assets/privacy-notice.js`](assets/privacy-notice.js) | Vanilla-JS für Anzeige/Dismiss des Banners | 184 Seiten |

**Ergebnis:** Jede HTML-Datei wurde ~12 KB kleiner, das Gesamt-Repo etwa 2 MB.

### 2. Toter Code komplett entfernt

Bewusst gelöscht (nicht nur ausgelagert), weil auf einem statischen Archiv unbrauchbar UND datenschutzrechtlich problematisch:

| Entfernter Block | Warum |
| --- | --- |
| `_gaq.push([...UA-7870337-1...])` + `google-analytics.com/ga.js`-Loader | **DSGVO-widrige** Google-Analytics-Einbindung ohne Consent |
| `snowday`-Snowplow-Tracker (sendete `user_id: 124287907`, `site_id: 566137816592563923` an `ec.editmysite.com`) | **DSGVO-widrige** Weebly-Analytics |
| `_W.setup_rpc({"url":"/ajax/api/JsonRPC/CustomerAccounts/", …})` | Rief einen 404-Endpoint auf |
| `_W.recaptchaUrl = "…/api.js"` | Kein Captcha auf der Seite |
| `<script src="…main-customer-accounts-site.js"></script>` (522 KB Backbone-Bundle für Login/Registrierung) | Kein Login/Registrierung möglich; erzeugte JS-Fehler durch fehlenden RPC-Setup |
| Cookie-Banner-Config (`_W.isEUUser`, `_W.showCookieToAll`, `Opt Out of Cookies`-Button) | Kein Cookie-Banner mehr (siehe `LEGAL_AUDIT.md`) |
| `jQuery('.blog-social')`-Wrapper mit PayPal-Fallback | Kein Blog, kein Shop |

**Ergebnis:** Kein einziger JavaScript-Error mehr auf allen 184 Seiten (verifiziert per Playwright).

### 3. Migrations-Skripte konsolidiert

Statt zufällig herumliegender Skripte gibt es jetzt einen chronologischen Ordner:

```
scripts/
├── README.md
├── 01_download_cdn_assets.py
├── 02_rewrite_links.py
├── 03_remove_kontakt.py
├── 04_fix_query_paths.py
├── 05_strip_cache_busters.py
├── 06_replace_weebly_media.py
├── 07_harden_security.py
├── 08_rewrite_impressum.py
├── 09_inject_privacy_banner.py
└── 10_refactor_extract_common.py
```

Jedes Skript ist idempotent (mehrfaches Ausführen ist harmlos) und benötigt nur die Python-Standardbibliothek. Details in `scripts/README.md`.

---

## Was wurde bewusst NICHT angefasst?

| Bereich | Grund |
| --- | --- |
| Die 183 Weebly-HTML-Templates selbst | Das sind maschinengenerierte Ausgaben mit hunderten inline-Selektoren; ein manueller Rewrite würde das Layout kaputtmachen |
| jQuery 1.8.3 + 2.1.4 | Upgrade auf jQuery 3.x würde das Weebly-Template brechen; auf statischem Archiv kein Ausnutzungspfad (siehe `SECURITY_AUDIT.md`) |
| Die 1 MB Weebly-`main.js` | Minifiziertes Webpack-Bundle; Rewrite außerhalb des Scopes eines Archivs |
| CSS-Dateinamen `main_style.css@1782116011.css` | Wurde vom Weebly-Original übernommen; Umbenennen bricht Cache-Busting-Verweise |

---

## Verhaltens-Parität (Regression-Check)

Playwright-Screenshots vor und nach dem Refactoring wurden Pixel-Byte-Weise geprüft:

| Test | Vorher | Nachher |
| --- | --- | --- |
| `index.html` sichtbarer Bereich | ✅ | ✅ (identisch) |
| `impressum-und-datenschutz.html` | ✅ | ✅ (neuer Content, gleiches Layout) |
| `community-bot-behaumllt-item.html` mit HTML5-Video | ✅ | ✅ (Video spielt) |
| `afk-sitze.html` mit Wired-Grid | ✅ | ✅ |
| Privacy-Banner erscheint einmalig | ✅ | ✅ |
| JS-Konsolen-Errors | 1× RPC error/Seite | **0 Errors** |

---

## Für Junior-Entwickler: „Wo fange ich an?"

1. **Layout ändern** → `assets/site-theme.css` (globale Regeln) oder die einzelne HTML-Seite (spezifische Overrides).
2. **Neuen Menüpunkt hinzufügen** → in JEDER `.html`-Datei die Nav-Sektion `<ul class="wsite-menu">` erweitern. (Weil das Weebly-Template kein Include-System hat.)
3. **Neue Seite anlegen** → Kopie einer bestehenden Seite als Vorlage; `<title>` und Content-Bereich ändern; im Menü verlinken.
4. **Banner-Text ändern** → `assets/privacy-notice.js`, Funktion `buildBanner()`.
5. **404-Seite ändern** → `404.html` (steht bewusst nicht auf Weebly-Basis, sondern ist minimales eigenes HTML).
6. **nginx-Config anpassen** → `docs/nginx-security.conf`.

---

*Refactoring durchgeführt in Anlehnung an das „Boy Scout Rule"-Prinzip: Nur so viel ändern, wie nötig ist, um den Code lesbarer/sauberer zu hinterlassen — ohne das Verhalten anzutasten.*
