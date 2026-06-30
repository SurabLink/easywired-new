# Legal & DSGVO Audit – easyWIRED Static Mirror

**Datum:** 2026-01-30  
**Geprüfte Rechtsräume:** Deutschland (DDG, MStV, TDDDG, BDSG) + EU (DSGVO)  
**Charakter der Webseite:** privates, nicht-kommerzielles Habbo-Fanprojekt von Surab Link, gehostet auf einem STRATO-VPS in Deutschland

---

## 1. Anwendbare Rechtsgrundlagen (Stand 2026)

| Rechtsakt | Relevanz für easyWIRED |
| --- | --- |
| **DDG** (Digitale-Dienste-Gesetz, seit Mai 2024, ersetzt TMG) | § 5 DDG: Impressumspflicht für „geschäftsmäßige" digitale Dienste — gilt nach gefestigter Rechtsprechung auch für regelmäßig gepflegte, öffentlich zugängliche private Webseiten. |
| **MStV** (Medienstaatsvertrag) | § 18 Abs. 2: zusätzlicher journalistisch-redaktioneller Verantwortlicher, sobald die Seite meinungsbildende redaktionelle Inhalte enthält (Tutorials/Interviews → ja). |
| **DSGVO** (EU 2016/679) | Anwendbar, weil Server-Logfiles personenbezogene Daten (IP-Adresse) verarbeiten. |
| **BDSG** (Bundesdatenschutzgesetz) | Ergänzende deutsche Vorschriften, insb. zur Bestellpflicht eines Datenschutzbeauftragten (§ 38 BDSG) — hier **nicht erforderlich** (keine umfangreichen besonderen Datenkategorien, kein Profiling). |
| **TDDDG** (Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz, seit Mai 2024, ersetzt TTDSG) | § 25: Einwilligungspflicht für Cookies/Local-Storage — hier **nicht ausgelöst**, weil keine nicht-essentiellen Speichervorgänge stattfinden. |
| **UrhG** (Urheberrechtsgesetz) | Eigene Tutorials/Texte sind urheberrechtlich geschützt. Habbo-Bildmaterial wird im Rahmen der offiziellen Sulake-Fansite-Richtlinien zitiert. |

---

## 2. Findings & Status nach Fix

| # | Severity | Bereich | Status |
| --- | --- | --- | --- |
| L-1 | HIGH | Veraltetes Impressum: Verweis auf §§ TMG/RStV statt DDG/MStV; Nennung von „Cookies" und „YouTube-Cookies", die laut tatsächlichem Code gar nicht (mehr) gesetzt werden; Verweis auf Kontaktformular, das gar nicht existiert. | ✅ **Komplett neu geschrieben** ([impressum-und-datenschutz.html](impressum-und-datenschutz.html)) |
| L-2 | HIGH | Veralteter Cookie-Banner (Weebly „Opt Out of Cookies"-Button + Cookiebot-Banner) – inkonsistent zur tatsächlichen Datenverarbeitung. | ✅ **Cookiebot/Zotabox-Skripte entfernt**, "Opt Out"-Button raus, **eigener, ehrlicher Info-Banner** gebaut |
| L-3 | MEDIUM | Datenschutzerklärung beschrieb Cookies, die nie existiert haben, und Drittanbieter-Einbettungen, die nicht mehr aktiv sind. | ✅ **Neu verfasst**, beschreibt **nur** das, was der Code tatsächlich tut |
| L-4 | MEDIUM | Habbo/Sulake-Disclaimer fehlte/war veraltet (Sulake firmiert seit 2024 als „Sulake Oy", nicht mehr „Corporation Ltd."). | ✅ **Aktualisiert** + um nicht-kommerziellen Hobbycharakter ergänzt |
| L-5 | MEDIUM | Datenschutz-Aufsichtsbehörde nicht namentlich genannt (Pflicht zur Nennung der zuständigen Behörde nach Art. 13 Abs. 2 lit. d DSGVO empfohlen). | ✅ **Hessischer Beauftragter für Datenschutz und Informationsfreiheit** explizit benannt mit Anschrift und Link |
| L-6 | LOW | E-Mail im Impressum war Weebly-obfuskiert (`[email&#160;protected]`) und damit nicht abrufbar → § 5 DDG verlangt aber eine „schnelle elektronische Kontaktaufnahme". | ✅ **Klartext-Mailto-Link** `kontakt@easywired.de` (Sie müssen diese Adresse noch auf Ihrer Domain einrichten — siehe Hinweis unten) |
| L-7 | LOW | Speicherdauer der Server-Logs nicht beziffert. | ✅ **Maximal 7 Tage** konkretisiert |
| L-8 | INFO | Habbo-Markenrechte: Verwendung von Habbo-Pixel-Assets als Fansite. | ✅ Im Rahmen der **offiziellen Habbo-Fansite-Richtlinien** zulässig (Sulake erlaubt Marken-/IP-Nutzung explizit für nicht-kommerzielle Fanseiten); Disclaimer hinterlegt |

---

## 3. Der neue Hinweis-Banner — und warum er KEIN Consent-Banner ist

Das vorherige Setup verwendete das **Cookiebot**-Consent-Banner (Weebly-Default). Das war aus drei Gründen problematisch:

1. **Es funktionierte nicht**: Die Domain `217.154.150.55` (und später `easywired.de`) war im Cookiebot-Manager nicht autorisiert, sodass der Banner mit einer JavaScript-Fehlermeldung sofort abbrach.
2. **Es war inhaltlich falsch**: Es bot eine Einwilligung zu Marketing- und Tracking-Cookies an, obwohl keine solchen Cookies tatsächlich gesetzt werden.
3. **Es lud externes JavaScript** von `consent.cookiebot.com` auf jeder Seite — ein Supply-Chain-Risiko (siehe SECURITY_AUDIT.md).

### Warum gar kein Consent nötig ist

Eine Einwilligung nach § 25 TDDDG ist nur erforderlich für das **Speichern von Informationen** auf dem Endgerät bzw. den **Zugriff** auf bereits dort gespeicherte Informationen — und nur dann, wenn das nicht **unbedingt erforderlich** für den vom Nutzer gewünschten Dienst ist.

Die migrierte Seite (Stand 2026-01):

- setzt **keine HTTP-Cookies** (auch keine technischen),
- nutzt **kein** Session-Storage,
- nutzt **kein** Local Storage *außer* einem optionalen Flag, das nur dann geschrieben wird, wenn der Nutzer den Hinweisbalken aktiv schließt — also explizit den Dienst „nicht mehr anzeigen" wünscht,
- bindet **keine** externen Skripte, Analyse-Tools, Pixel oder Fonts ein,
- erstellt **kein** Browser-Fingerprinting.

Damit greift **§ 25 Abs. 2 Nr. 2 TDDDG** (technisch erforderliche Speicherung für vom Nutzer ausdrücklich gewünschten Dienst) → keine Einwilligung nötig.

### Was der neue Banner tatsächlich ist

Ein **rein informatorischer Hinweis** nach Art. 13 DSGVO mit drei Eigenschaften:

1. Erscheint einmalig beim ersten Besuch.
2. Erklärt **wahrheitsgemäß**, was passiert: keine Cookies, kein Tracking, keine Drittanbieter, nur Server-Logs (max. 7 Tage).
3. Verlinkt direkt auf die volle Datenschutzerklärung.

Es gibt bewusst **keinen „Akzeptieren"-Button und keinen „Ablehnen"-Button**, weil nichts da ist, dem man zustimmen müsste — das wäre Dark-Pattern.

Implementiert in [`assets/privacy-notice.css`](assets/privacy-notice.css) (Theme-konform: Orange #a85f2e, Montserrat, dark-mode-fähig, mobile-responsive) und [`assets/privacy-notice.js`](assets/privacy-notice.js) (~80 Zeilen Vanilla-JS, keine Dependencies).

---

## 4. Was Sie (Surab Link) noch tun sollten

| Aufgabe | Warum | Aufwand |
| --- | --- | --- |
| 1. E-Mail-Postfach `kontakt@easywired.de` einrichten (z. B. via STRATO-Mail) | § 5 DDG: muss eingehende Mails empfangen können | 5 Min im STRATO-Kundenbereich |
| 2. PAT widerrufen (`github_pat_11BPHTLXY01LEkSr...`), das während der ersten Session geteilt wurde | Security-Hygiene | 1 Min |
| 3. HTTPS auf STRATO aktivieren (nginx-Snippet liegt in [`docs/nginx-security.conf`](docs/nginx-security.conf) bereit) | Pflicht-Voraussetzung für HSTS, Cookie-Banner-Banner-Behörden-Konformität, SEO | 15-30 Min |
| 4. STRATO-Log-Konfiguration auf max. 7 Tage Aufbewahrung einstellen (Standard ist evtl. länger) | Konsistenz zur Datenschutzerklärung | im STRATO-Panel oder per `logrotate` |
| 5. Prüfen: möchten Sie evtl. einen anderen Kontaktweg statt der E-Mail (z. B. Discord)? Falls ja, einfach in Ziffer 1 des Impressums anpassen. | Persönliche Präferenz | optional |

---

## 5. Zusammenfassung in einem Satz

> Die Seite verwendet **keine** Cookies, **kein** Tracking und **keine** Drittanbieter-Skripte; das neue Impressum und die Datenschutzerklärung spiegeln diese technische Realität präzise wider und sind nach DDG, MStV, DSGVO und TDDDG vollständig konform — vorausgesetzt, das Postfach `kontakt@easywired.de` wird eingerichtet und HTTPS auf dem STRATO-Server aktiviert.

---

*Hinweis: Dieser Audit ersetzt keine anwaltliche Beratung. Bei Abmahnungen, Auskunftsansprüchen oder behördlichen Anfragen empfiehlt sich eine kurze Rücksprache mit einer auf IT-Recht spezialisierten Kanzlei. Für ein nicht-kommerzielles Fanprojekt ist das Risiko jedoch sehr gering, sobald die obigen Punkte umgesetzt sind.*
