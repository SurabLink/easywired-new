#!/usr/bin/env python3
"""Replace the main content of impressum-und-datenschutz.html with a clean,
DSGVO/DDG-compliant Impressum + Datenschutzerklärung that reflects the
actual processing performed by the static archive (no cookies, no tracking,
no third-party scripts, no contact form), and remove the obsolete
"Opt Out of Cookies" link from every page."""
import re
from pathlib import Path

ROOT = Path("/app/easywired-new")

IMPRESSUM_HTML = '''<div id="wsite-content" class="wsite-elements wsite-not-footer">
<div class="wsite-section-wrap"><section class="wsite-section wsite-background wsite-section-bg-color wsite-section-content-align-default" style="background-color: transparent;">
<div class="wsite-section-content-wrap">
<div class="container">
<div class="wsite-section-content">

<h2 class="wsite-content-title" style="text-align:center;"><strong><font color="#a85f2e" size="6">Impressum &amp; Datenschutzerklärung</font></strong></h2>

<div style="height:24px;"></div>

<div class="paragraph"><em>Stand: Januar 2026 — diese Seite ist ein privates, nicht-kommerzielles Fanprojekt für die deutschsprachige Habbo-Community.</em></div>

<div style="height:24px;"></div>

<h2 style="color:#a85f2e;">1. Anbieter &amp; inhaltlich Verantwortlicher</h2>
<div class="paragraph">
Angaben gem. § 5 Digitale-Dienste-Gesetz (DDG, vormals § 5 TMG) und § 18 Abs. 2 Medienstaatsvertrag (MStV):<br /><br />
<strong>Surab Link</strong><br />
Robert-Kircher-Str. 4<br />
36037 Fulda<br />
Deutschland<br /><br />
<strong>Kontakt:</strong><br />
E-Mail: <a href="mailto:kontakt@easywired.de">kontakt@easywired.de</a><br />
<em>Telefonische Erreichbarkeit auf Nachfrage per E-Mail.</em>
</div>

<div style="height:24px;"></div>

<h2 style="color:#a85f2e;">2. Charakter des Angebots</h2>
<div class="paragraph">
easyWIRED ist ein <strong>rein privates Hobbyprojekt</strong> ohne wirtschaftliches Interesse.
Die Seite vermittelt Wissen rund um die Wired-Möbel im Habbo Hotel und richtet sich kostenfrei
an die deutschsprachige Fan-Community. Es findet kein Verkauf von Waren oder Dienstleistungen
statt, es werden keine Mitgliedschaften, Abonnements oder kostenpflichtigen Inhalte angeboten,
und es werden keine Werbeeinnahmen oder Affiliate-Provisionen generiert.
</div>

<div style="height:24px;"></div>

<h2 style="color:#a85f2e;">3. Disclaimer zu Habbo &amp; Sulake</h2>
<div class="paragraph">
„Diese Fansite ist nicht mit Sulake Oy oder Partnerfirmen von Sulake Oy verbunden und wird auch nicht von ihnen befürwortet, unterstützt oder spezifisch genehmigt. Diese Fansite darf die Marken und anderes geistiges Eigentum von Habbo im Rahmen der Richtlinien für Habbo-Fansites verwenden."<br /><br />
© Sulake Oy. HABBO®, HABBO HOTEL® und SULAKE sowie damit zusammenhängende Logos sind eingetragene Warenzeichen der Sulake Oy in den USA, der EU, China und anderen Staaten. Sämtliche Bildmaterialien, GIFs und Marken aus dem Habbo Hotel sind Eigentum der Sulake Oy. Diese Webseite ist weder Eigentum der Sulake Oy noch Teil von HABBO HOTEL® oder eines anderen Dienstes der Sulake Oy. Die Sulake Oy ist nicht verantwortlich für Inhalte auf dieser Webseite und übernimmt keine Verantwortung für hier geäußerte Meinungen.
</div>

<div style="height:24px;"></div>

<h2 style="color:#a85f2e;">4. Haftung für Inhalte</h2>
<div class="paragraph">
Die Inhalte dieser Seite wurden mit größter Sorgfalt erstellt. Für Richtigkeit, Vollständigkeit und Aktualität kann jedoch keine Gewähr übernommen werden. Als Diensteanbieter bin ich gem. § 7 Abs. 1 DDG für eigene Inhalte nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 DDG bin ich als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden entsprechender Rechtsverletzungen werden diese Inhalte umgehend entfernt.
</div>

<div style="height:24px;"></div>

<h2 style="color:#a85f2e;">5. Haftung für Links</h2>
<div class="paragraph">
Dieses Angebot enthält Links zu externen Webseiten Dritter (z. B. Discord, YouTube, Habbo Hotel, Wikipedia, X.com). Auf deren Inhalte habe ich keinen Einfluss; eine Gewähr kann nicht übernommen werden. Für die Inhalte verlinkter Seiten ist stets der jeweilige Betreiber verantwortlich. Zum Zeitpunkt der Verlinkung waren keine rechtswidrigen Inhalte erkennbar. Bei Bekanntwerden von Rechtsverletzungen werden derartige Links umgehend entfernt.
</div>

<div style="height:24px;"></div>

<h2 style="color:#a85f2e;">6. Urheberrecht</h2>
<div class="paragraph">
Eigene erstellte Texte, Tutorials und Layouts auf dieser Seite unterliegen dem deutschen Urheberrecht. Die Verwendung außerhalb des privaten Gebrauchs bedarf meiner vorherigen Zustimmung. Bildmaterial, GIFs und Marken aus dem Habbo Hotel sind Eigentum der Sulake Oy und werden im Rahmen der offiziellen Habbo-Fansite-Richtlinien zitiert. Sollte trotz sorgfältiger Recherche eine Urheberrechtsverletzung vorliegen, bitte ich um einen entsprechenden Hinweis per E-Mail. Bei berechtigten Beanstandungen werden die betreffenden Inhalte umgehend entfernt.
</div>

<div style="height:32px;"></div>
<hr style="border:none;border-top:2px solid #a85f2e;" />
<div style="height:32px;"></div>

<h2 class="wsite-content-title" style="text-align:center;"><strong><font color="#a85f2e" size="6">Datenschutzerklärung</font></strong></h2>

<div style="height:24px;"></div>

<h2 style="color:#a85f2e;">7. Verantwortlicher im Sinne der DSGVO</h2>
<div class="paragraph">
Verantwortlich für die Datenverarbeitung auf dieser Webseite ist die unter Ziffer 1 genannte Person.<br />
Eine Datenschutzbeauftragte oder ein Datenschutzbeauftragter ist nicht bestellt, da hierfür keine gesetzliche Pflicht besteht (Art. 37 DSGVO i. V. m. § 38 BDSG — keine umfangreiche Verarbeitung besonderer Datenkategorien, keine systematische Überwachung).
</div>

<div style="height:20px;"></div>

<h2 style="color:#a85f2e;">8. Welche Daten werden verarbeitet?</h2>
<div class="paragraph">
Diese Webseite ist ein <strong>rein statisches HTML-Archiv</strong>. Es gibt:
<ul style="margin-left:20px;">
  <li>keine Kontaktformulare,</li>
  <li>keine Registrierung oder Benutzerkonten,</li>
  <li>keine Kommentar-Funktion,</li>
  <li>keine Newsletter,</li>
  <li>keine eingebetteten Drittanbieter-Inhalte (kein YouTube-Player, kein Google Maps, kein Facebook-Pixel, kein Tracking-Skript),</li>
  <li>keinerlei Cookies oder vergleichbare Speichertechnologien für Werbe-, Tracking- oder Profilbildungszwecke.</li>
</ul>
Beim Aufruf der Seite werden — wie bei jedem Webserver — durch den Hosting-Provider (STRATO AG, Pascalstr. 10, 10587 Berlin) automatisch sogenannte Server-Logfiles erstellt. Diese enthalten:
<ul style="margin-left:20px;">
  <li>IP-Adresse des anfragenden Geräts,</li>
  <li>Datum und Uhrzeit der Anfrage,</li>
  <li>aufgerufene URL und HTTP-Status,</li>
  <li>übertragene Datenmenge,</li>
  <li>User-Agent (Browser- und Betriebssystem-Information),</li>
  <li>Referrer (zuvor besuchte Seite, sofern vom Browser übermittelt).</li>
</ul>
</div>

<div style="height:20px;"></div>

<h2 style="color:#a85f2e;">9. Zweck und Rechtsgrundlage</h2>
<div class="paragraph">
Die Verarbeitung der Server-Logfiles erfolgt zur Sicherstellung des technischen Betriebs, zur Abwehr von Angriffen und zur Fehleranalyse. Rechtsgrundlage ist <strong>Art. 6 Abs. 1 lit. f DSGVO</strong> (berechtigtes Interesse am sicheren und stabilen Betrieb der Webseite). Eine Zusammenführung mit anderen Daten oder eine Profilbildung findet nicht statt. Die Logs werden grundsätzlich nach <strong>maximal 7 Tagen</strong> automatisiert gelöscht oder anonymisiert; eine längere Aufbewahrung erfolgt nur im Falle eines dokumentierten Sicherheitsvorfalls zur Aufklärung.
</div>

<div style="height:20px;"></div>

<h2 style="color:#a85f2e;">10. Cookies &amp; vergleichbare Technologien (§ 25 TDDDG)</h2>
<div class="paragraph">
Diese Webseite setzt <strong>keine Cookies</strong> und nutzt <strong>kein Local Storage, kein Session Storage und keine vergleichbaren Speichertechnologien</strong> auf Ihrem Endgerät — mit einer Ausnahme: Wenn Sie den einmaligen Datenschutz-Hinweisbalken am Seitenende ausblenden, wird genau ein Flag (<code>ew_privacy_ack=1</code>) im Local Storage Ihres Browsers gesetzt, damit der Hinweis Sie nicht erneut stört. Dieses Flag ist gemäß § 25 Abs. 2 Nr. 2 TDDDG <em>unbedingt erforderlich</em>, um den von Ihnen mit dem Schließen ausdrücklich gewünschten Dienst („Hinweis nicht mehr anzeigen") bereitzustellen und benötigt daher keine Einwilligung. Sie können das Flag jederzeit über die Browser-Einstellungen löschen.
</div>

<div style="height:20px;"></div>

<h2 style="color:#a85f2e;">11. Externe Links</h2>
<div class="paragraph">
Diese Webseite verlinkt auf externe Dienste (insb. Discord, YouTube, Habbo Hotel, Wikipedia). Erst beim aktiven Anklicken eines solchen Links werden Daten an den jeweiligen Anbieter übermittelt. Es werden keinerlei externe Ressourcen (Bilder, Schriftarten, Skripte) von Drittservern beim Seitenaufruf automatisch nachgeladen — sämtliche Assets sind lokal auf diesem Server gespeichert.
</div>

<div style="height:20px;"></div>

<h2 style="color:#a85f2e;">12. Ihre Rechte als betroffene Person</h2>
<div class="paragraph">
Soweit Ihre personenbezogenen Daten verarbeitet werden, stehen Ihnen folgende Rechte zu:
<ul style="margin-left:20px;">
  <li>Auskunft (Art. 15 DSGVO),</li>
  <li>Berichtigung (Art. 16 DSGVO),</li>
  <li>Löschung (Art. 17 DSGVO),</li>
  <li>Einschränkung der Verarbeitung (Art. 18 DSGVO),</li>
  <li>Datenübertragbarkeit (Art. 20 DSGVO),</li>
  <li>Widerspruch gegen eine auf Art. 6 Abs. 1 lit. f DSGVO gestützte Verarbeitung (Art. 21 DSGVO).</li>
</ul>
Zur Wahrnehmung dieser Rechte genügt eine formlose E-Mail an die unter Ziffer 1 genannte Adresse. Sie haben außerdem das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren (Art. 77 DSGVO). Zuständig ist in meinem Fall:<br /><br />
<strong>Der Hessische Beauftragte für Datenschutz und Informationsfreiheit</strong><br />
Postfach 3163, 65021 Wiesbaden<br />
<a href="https://datenschutz.hessen.de" target="_blank" rel="noopener noreferrer">https://datenschutz.hessen.de</a>
</div>

<div style="height:20px;"></div>

<h2 style="color:#a85f2e;">13. Datensicherheit</h2>
<div class="paragraph">
Die Seite wird über einen virtuellen Server der STRATO AG in Deutschland ausgeliefert. Die Übertragung erfolgt verschlüsselt per TLS (HTTPS), sofern Ihr Browser dies unterstützt. Sicherheitsrelevante Header (Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) sind aktiviert. Eine vollständige technische Security-Auditdokumentation finden Sie öffentlich im Quellcode-Repository.
</div>

<div style="height:20px;"></div>

<h2 style="color:#a85f2e;">14. Änderungen dieser Erklärung</h2>
<div class="paragraph">
Diese Datenschutzerklärung wird bei Bedarf angepasst, um aktuellen rechtlichen Anforderungen zu entsprechen oder Änderungen am Webangebot abzubilden. Die jeweils aktuelle Version ist unter dieser URL abrufbar.
</div>

<div style="height:32px;"></div>

</div>
</div>
</div>
</section></div>
</div>'''


# --- Replace the wsite-content section in impressum file ---
imp_path = ROOT / "impressum-und-datenschutz.html"
text = imp_path.read_text(encoding="utf-8")

start = text.find('<div id="wsite-content"')
assert start >= 0, "wsite-content not found"
i = start
depth = 0
end = -1
while i < len(text):
    if text[i:i+4] == '<div':
        depth += 1
        i += 4
    elif text[i:i+6] == '</div>':
        depth -= 1
        i += 6
        if depth == 0:
            end = i
            break
    else:
        i += 1
assert end > 0, "matching close not found"
new_text = text[:start] + IMPRESSUM_HTML + text[end:]
imp_path.write_text(new_text, encoding="utf-8")
print(f"impressum-und-datenschutz.html updated ({end - start} -> {len(IMPRESSUM_HTML)} bytes)")


# --- Remove "Opt Out of Cookies" links from EVERY page ---
# Pattern: <a ...><span class="wsite-button-inner">Opt Out of Cookies</span></a> wrapped in container
OPT_OUT_RE = re.compile(
    r'<a[^>]*>\s*<span[^>]*class="[^"]*wsite-button-inner[^"]*"[^>]*>\s*Opt Out of Cookies\s*</span>\s*</a>',
    re.IGNORECASE,
)
# Also broader: any element containing "Opt Out of Cookies"
OPT_OUT_RE2 = re.compile(
    r'<[^>]*>[^<]*Opt Out of Cookies[^<]*</[^>]*>',
    re.IGNORECASE,
)

removed = 0
for p in ROOT.rglob("*.html"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    new = OPT_OUT_RE.sub('', text)
    new = OPT_OUT_RE2.sub('', new)
    # Also: leftover JavaScript like cookieOptOut handlers
    new = re.sub(r'<script[^>]*>[^<]*cookieOptOut[^<]*</script>', '', new, flags=re.IGNORECASE | re.DOTALL)
    if new != text:
        p.write_text(new, encoding="utf-8")
        removed += 1
print(f"Files with 'Opt Out of Cookies' link removed: {removed}")
