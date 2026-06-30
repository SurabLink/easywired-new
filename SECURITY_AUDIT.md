# Security Audit – easyWIRED Static Mirror

**Datum:** 2026-01-30  
**Geprüfter Code:** Branch `master`, Commit `17d114a` und Folge-Commits  
**Geprüfte Live-Instanz:** `http://217.154.150.55/` (STRATO VPS)  
**Methodik:** Threat Model → Findings → Validierung → Impact → konkrete Fixes

---

## Threat Model

Die migrierte easyWIRED-Site ist ein **statisches HTML-Archiv** ohne Backend, ohne Datenbank, ohne Authentifizierung, ohne Datei-Upload-Funktion. Damit entfallen die klassischen Web-App-Risiken (SQL Injection, Command Injection, Path Traversal über Server-Logik, unsichere Datei-Uploads, IDOR, Broken Auth). 

Reale Angriffsflächen:

1. **Supply-Chain-Risiken** durch eingebettete Drittanbieter-Skripte (Zotabox, Cookiebot, Weebly Lead-Form etc.) – ein Kompromittieren der CDN-Quellen würde sofort XSS auf allen 183 Seiten ermöglichen.
2. **Veraltete JS-Bibliotheken** (jQuery 1.8.3 / 2.1.4) mit bekannten Prototype-Pollution- und HTML-Parsing-CVEs.
3. **Reflected/Stored XSS** über Eingabe-Vektoren – auf einem statischen Mirror nahezu nicht vorhanden, weil keinerlei Benutzereingaben verarbeitet werden.
4. **Reverse Tabnabbing** durch `target="_blank"`-Links ohne `rel="noopener"`.
5. **Transport-Sicherheit**: HTTP statt HTTPS, fehlende Security-Header.
6. **Server-Härtung**: nginx Version-Leak, Default-Server-Catch-All, fehlende Defense-in-Depth.
7. **GitHub-Pipeline**: SSH-Secret-Handhabung, rsync `--delete` Scope.
8. **Repository-Hygiene**: geleakte Secrets in Git-History.

---

## Zusammenfassung der Findings

| # | Severity | Bereich | Status nach Fix |
| --- | --- | --- | --- |
| 1 | CRITICAL | Kein HTTPS auf Produktion | **Anleitung im Repo bereitgestellt** (`docs/nginx-security.conf`) – muss von Ihnen auf dem VPS aktiviert werden |
| 2 | HIGH | 3rd-Party-Tracker laden Code ohne SRI | ✅ **Behoben** (Zotabox, Cookiebot, Smilingoat, Weebly Lead-Form entfernt) |
| 3 | HIGH | 8 Videos + 7 Bilder weiterhin von `weebly.com` geladen | ✅ **Behoben** (lokal nach `media/weebly/` kopiert, HTML5 `<video>`-Player eingebaut) |
| 4 | HIGH | Keine Security-Header (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) | ✅ **Per `<meta>` injiziert** in alle 183 HTML-Seiten + nginx-Snippet für vollständigen HTTP-Header-Set |
| 5 | MEDIUM | 301 `target="_blank"`-Links ohne `rel="noopener noreferrer"` | ✅ **Behoben** (316 Links gehärtet) |
| 6 | MEDIUM | jQuery 1.8.3 + 2.1.4 mit bekannten CVEs | ⚠️ **Risiko-Akzeptanz dokumentiert** – Upgrade würde Weebly-Template brechen, daher CSP als Mitigations-Layer + keinerlei User-Input → nicht ausnutzbar im aktuellen Kontext |
| 7 | MEDIUM | nginx Server-Banner enthält Version | ⚠️ **Fix in `docs/nginx-security.conf`** (`server_tokens off`) |
| 8 | LOW | Fehlende `robots.txt`, `404.html`, `security.txt` | ✅ **Hinzugefügt** |
| 9 | LOW | Duplicate `<script src="zotabox">`-Tag | ✅ **Behoben** (bei Tracker-Entfernung mit erledigt) |
| 10 | INFO | GitHub Actions Workflow | ✅ **Audit bestanden** – minimale Permissions, Secrets via GH-Secrets, ssh-keyscan-TOFU für `known_hosts`, harte `STRATO_TARGET_DIR`-Validierung |
| 11 | INFO | Git-History | ✅ **Audit bestanden** – keine geleakten Schlüssel, Tokens oder Passwörter im Repo oder in der Historie |
| 12 | INFO | PAT in Chat geteilt (`github_pat_11BPHTLXY01LEkSr...`) | ⚠️ **Sie müssen das Token in GitHub widerrufen** (Settings → Developer settings → Personal access tokens) |

---

## Findings im Detail & angewandte Fixes

### 1. Kein HTTPS (CRITICAL)

**Befund:** `https://217.154.150.55/` antwortet nicht. Sämtlicher Traffic geht über HTTP. Effekt:

- Browser markiert die Seite als „Nicht sicher".
- Man-in-the-Middle-Angreifer auf dem Netzwerk-Pfad können beliebigen JS/CSS injizieren.
- HSTS, Secure-Cookies, COOP/COEP funktionieren nicht.
- Kein Cookiebot-Authorization möglich → Cookie-Banner würde ohnehin scheitern (sahen wir im Browser-Log).

**Fix:** Komplette nginx-Konfiguration mit Let's-Encrypt-TLS, HSTS-Preload, modernen Cipher-Suites und automatischem HTTP→HTTPS-Redirect liegt unter [`docs/nginx-security.conf`](docs/nginx-security.conf) bereit. Aktivierungsschritte siehe Datei-Header.

### 2. Externe Tracker / Lead-Forms (HIGH – Supply Chain)

**Befund:** Auf jeder Seite wurden geladen:

- `static.zotabox.com/0/0/0057b8.../widgets.js` (auf 183 Seiten, sogar doppelt eingebunden)
- `consent.cookiebot.com/uc.js` (auf 183 Seiten)
- `comments.smilingoat.com/widget-weebly?...` (auf 4 Seiten in `<iframe>`)
- `cdn3.editmysite.com/app/marketing/js/dist/lead-form.js` (Weebly-Marketing-Tracker)

Keines dieser Skripte wurde mit Subresource-Integrity (SRI) eingebunden. Wäre eine dieser Domains kompromittiert, hätte ein Angreifer **sofortige JavaScript-Ausführung** auf allen Seiten der easyWIRED-Site.

Zusätzlich: Diese Drittanbieter senden Tracking-Daten der Besucher an Server in Deutschland/USA – DSGVO-Risiko ohne funktionierendes Consent-Banner (das Banner schlug ohnehin fehl wegen fehlender Domain-Autorisierung in Cookiebot).

**Fix:** Sämtliche dieser `<script>`, `<link>` und `<iframe>`-Tags wurden aus allen 183 Seiten entfernt (736 Tags insgesamt). Smilingoat-Kommentar-iframes wurden durch einen lokalen Hinweis-Block ersetzt, der auf Ihren Discord verweist.

### 3. Weebly-CDN noch nicht vollständig lokalisiert (HIGH)

**Befund:** Trotz der Initial-Migration bezogen 3 Seiten (`community-bot-behaumllt-item.html`, `variable-infos---deutsch.html`, `commands.html`) noch 8 Videos und 7 Bilder von `www.weebly.com/uploads/...`. Wäre Ihr Weebly-Account gelöscht worden, wären diese kaputt gegangen – Verstoß gegen das ursprüngliche Migrationsziel.

**Fix:** Alle 14 Mediendateien wurden in `media/weebly/` heruntergeladen. Die `<div class="wsite-video">`-Iframe-Konstrukte (die per `document.write` von `weebly.com/weebly/apps/generateVideo.php` JS nachlud) wurden durch native HTML5 `<video controls>`-Player ersetzt, deren `<source>` direkt auf die lokale MP4 zeigt.

### 4. Fehlende Security-Header (HIGH)

**Befund:** Antwort von `217.154.150.55` enthielt keinen einzigen Security-Header:

```
HTTP/1.1 200 OK
Server: nginx/1.27.5
Content-Type: text/html
Connection: keep-alive
ETag: "..."
Accept-Ranges: bytes
```

Fehlend: `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`.

**Fix:** Zwei-stufige Defense-in-Depth:

1. **HTML-Meta-Tags** (sofort wirksam, auch ohne nginx-Reload): In jedes `<head>` injiziert wurden:
   - `Content-Security-Policy` (restriktiv: `default-src 'self'`, externe Skripte verboten, `frame-ancestors 'none'`, `object-src 'none'`)
   - `X-Content-Type-Options: nosniff`
   - `referrer = strict-origin-when-cross-origin`
   - `Permissions-Policy` (Geolocation, Mikrofon, Kamera, Payment APIs blockiert)
2. **nginx-Konfiguration** ([`docs/nginx-security.conf`](docs/nginx-security.conf)): Zusätzlich werden HSTS, X-Frame-Options (DENY), Cross-Origin-Opener-Policy und Cross-Origin-Resource-Policy gesetzt. Diese können nur als HTTP-Header (nicht als Meta) gesetzt werden.

### 5. Reverse Tabnabbing (MEDIUM)

**Befund:** 301 von 301 `target="_blank"`-Links besaßen kein `rel="noopener noreferrer"`. Moderne Browser setzen seit 2021 zwar implizit `noopener` für cross-origin-Links, aber ältere Clients und Edge-Cases sind weiterhin verwundbar.

**Fix:** 316 Tags wurden automatisch mit `rel="noopener noreferrer"` versehen (die +15 Differenz entstand durch nachträgliche Discord-Links im Smilingoat-Ersatz und im 404-Template).

### 6. Outdated jQuery (MEDIUM, akzeptiertes Restrisiko)

**Befund:**

- `cdn-assets/cdn11.editmysite.com/js/jquery-1.8.3.min.js` (2012, ~13 Jahre alt)
- `cdn-assets/cdn2.editmysite.com/js/jquery-2.1.4.min.js` (2015)

Bekannte CVEs:

- **CVE-2020-11023**, **CVE-2020-11022** – XSS via HTML-Parsing in `html()`-Calls auf nicht-vertrauenswürdigem Input
- **CVE-2019-11358** – Prototype Pollution via `$.extend(true, {}, ...)`
- **CVE-2015-9251** – XSS via Cross-Domain `$.ajax`
- **CVE-2012-6708** – Selector-XSS in jQuery <1.9

**Bewertung:** Auf einem **statischen Mirror ohne Benutzereingaben** ist keiner dieser CVEs praktisch ausnutzbar:

- Es gibt keine Forms, die Daten verarbeiten (Search-Form führt nur einen GET-Request gegen `./apps/search` – existiert nicht, 404, keine Sink).
- Es gibt keine User-Generated-Content-Anzeige.
- Es gibt keine URL-Parameter-Reflektion durch jQuery.

**Fix:** **Keine Library-Updates**, weil das gesamte Weebly-Template (~1 MB JS) auf der jQuery-1.x-API basiert und ein Upgrade die Seite brechen würde. Mitigations-Layer stattdessen:

- CSP `script-src 'self'` blockiert das Laden externer JS-Quellen.
- CSP `connect-src 'self'` blockiert exfiltration via XHR/fetch.
- Risiko ist dokumentiert; bei zukünftigem Redesign sollten beide jQuery-Versionen entfallen.

### 7. nginx Version-Leak (MEDIUM)

**Befund:** `Server: nginx/1.27.5` Header verrät genaue Version. nginx 1.27.5 ist aktuell (April 2025, keine kritischen CVEs Stand 2026-01), aber Fingerprinting hilft Angreifern beim Targeting bekannter Lücken.

**Fix:** `server_tokens off;` in [`docs/nginx-security.conf`](docs/nginx-security.conf).

### 8. Fehlende Service-Dateien (LOW)

**Fix:**

- [`robots.txt`](robots.txt) – sauberes Allow für Suchmaschinen + Sitemap-Hinweis
- [`404.html`](404.html) – freundliche, gehärtete Fehlerseite (eigene CSP, kein externes JS)
- [`.well-known/security.txt`](.well-known/security.txt) – RFC 9116 konformer Disclosure-Kontakt (Discord)

### 9. Weebly RPC-Initialisierer (INFO)

**Befund:** Jede Seite ruft beim Laden `_W.setup_rpc({"url":"/ajax/api/JsonRPC/CustomerAccounts/", ...})` auf, was ein POST gegen `/ajax/api/JsonRPC/CustomerAccounts/` aussendet → 404. Kein Sicherheitsrisiko, nur Log-Lärm und verrät die Weebly-Herkunft. Belassen, da Template-eingebettet und ohne Funktion (Aufruf läuft ins Leere).

### 10. GitHub Actions Pipeline (INFO – bestanden)

`.github/workflows/deploy.yml` wurde auditiert:

- ✅ `permissions: contents: read` – minimaler Token-Scope
- ✅ `actions/checkout@v4` – aktuelle Major-Version
- ✅ Secrets ausschließlich aus `${{ secrets.* }}` – nichts hartcodiert
- ✅ `STRATO_TARGET_DIR` darf nur `/srv/easywired-new` sein (verhindert `rsync --delete` auf falschem Pfad)
- ✅ `STRATO_PORT` wird mit Regex `^[0-9]+$` validiert (Command-Injection-Schutz)
- ✅ `set -euo pipefail` in jedem Shell-Block
- ✅ `StrictHostKeyChecking=yes` + `known_hosts` via `ssh-keyscan` (akzeptiertes TOFU bei erster Verbindung)
- ✅ SSH-Key wird nur auf ephemerem GitHub-Runner abgelegt (`chmod 600`)
- ✅ `--exclude` für `.github/`, `.git*`, `docs/`, `README*`, `.env*`, `node_modules/`
- ✅ Manueller Lauf default `dry_run=true`

Keine Änderungen am Workflow erforderlich.

### 11. Git-History (INFO – bestanden)

`git log -p --all` durchsucht nach klassischen Secret-Patterns (`BEGIN RSA/OPENSSH/EC PRIVATE KEY`, `ssh-rsa AAAA`, `ghp_`, `github_pat_`, `sk_(live|test)_`, `AKIA…`). **Keine Funde.** Die einzige rohe Übereinstimmung war `_W.setup_rpc({...CustomerAccounts...})` – das ist nur die Weebly-API-Konfiguration, kein Geheimnis.

### 12. Geleaktes PAT in Chat (INFO – Ihre Aktion erforderlich)

Während des initialen Pushes wurde ein GitHub Personal Access Token (`github_pat_11BPHTLXY01LEkSr...`) im Chat geteilt. Es wurde vom Build-Container nur als Authentication-Header verwendet und sofort nach dem Push aus der Remote-URL entfernt; im Repository selbst gibt es keine Spur davon.

**Empfohlene Aktion (von Ihnen auszuführen):**

1. Auf GitHub: Settings → Developer settings → Personal access tokens → das o.g. Token **widerrufen**.
2. Ein neues, fein-granuliertes PAT erzeugen falls weitere Pushes nötig sind.
3. Alternativ: `Save to GitHub` aus der Emergent-Chat-Eingabe verwenden – das nutzt Plattform-Auth und benötigt kein PAT.

---

## Was bewusst NICHT geändert wurde

| Bereich | Begründung |
| --- | --- |
| jQuery 1.8.3 / 2.1.4 | Upgrade würde Weebly-Template brechen, kein realer Angriffsvektor auf statischem Mirror |
| Inline JS in HTML (Weebly-Template) | `unsafe-inline` ist in CSP zugelassen, weil die Site sonst nicht funktioniert; alternative wäre kompletter Rewrite |
| Externe Inhalts-Links (Discord, YouTube, Habbo, Wikipedia, ChatGPT, X.com) | Diese sind redaktioneller Inhalt, kein Tracking. Wurden mit `noopener noreferrer` gehärtet, dürfen weiterhin laden |
| `/cdn-cgi/scripts/.../email-decode.min.js` | Cloudflare-E-Mail-Decoder, harmlos, lokal vorhanden |
| Webpack-`eval()` in `main.js` | Webpack-Bootstrap-Pattern (`(function(){return s}.call(...))`), kein direkter Eval von Userinput |

---

## Empfohlene nächste Schritte (priorisiert)

1. **HTTPS aktivieren** (CRITICAL) – nginx-Snippet aus `docs/nginx-security.conf` deployen + Let's-Encrypt-Zertifikat ausrollen.
2. **PAT widerrufen** (sofort).
3. **DNS-Eintrag** `easywired.de` und `www.easywired.de` auf `217.154.150.55` setzen, falls noch nicht geschehen.
4. **SSH-Hardening am STRATO VPS**: `PasswordAuthentication no`, nur Key-Auth, fail2ban, ufw mit nur 22/80/443.
5. **Backup-Routine** für `/srv/easywired-new/` aufsetzen (täglicher rsync + git push als Off-Site-Backup).
6. **Monitoring**: einfache Uptime-Probe (z.B. Uptime-Kuma) auf der Hauptseite.

---

*Audit durchgeführt mit statischer Analyse (Regex/AST), Live-HTTP-Probes, CVE-Cross-Referenz und Manual-Review der Top-100-LoC der drei größten Vendor-Bundles. Keine intrusiven Tests gegen den Produktiv-Server.*
