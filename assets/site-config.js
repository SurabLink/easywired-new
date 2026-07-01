/*
 * site-config.js
 * ----------------------------------------------------------------------------
 * Konfigurations-Globals, die das Weebly-Template (main.js im cdn-assets/
 * Ordner) beim Bootstrap erwartet. Diese Werte sind auf allen 183 Seiten
 * identisch und wurden aus den einzelnen inline-<script>-Blöcken in diese
 * zentrale Datei ausgelagert.
 *
 * BEWUSST ENTFERNT (im Vergleich zum Original-Weebly-Bootstrap):
 *   - Google Analytics `_gaq` Loader (UA-7870337-1) — DSGVO-widrig
 *   - Snowplow-Tracker (`snowday`) — sendete Daten an ec.editmysite.com
 *   - `_W.setup_rpc(CustomerAccounts)` — rief /ajax/api/JsonRPC/... 404
 *   - `_W.recaptchaUrl` — kein Captcha auf statischem Archiv
 *   - `initCustomerAccountsModels()` — kein Login-Flow
 *   - jQuery-Wrapper für Blog-Kommentare + PayPal — keine Produkte/Blog
 *
 * Warum wir das Template dennoch mit einem leeren `_W.Analytics.trackers`
 * initialisieren: das Weebly-main.js prüft an mehreren Stellen
 * `_W.Analytics.trackers.<key>` — mit einem leeren Objekt kracht nichts.
 * ----------------------------------------------------------------------------
 */

// Basis-Pfade, auf die main.js und andere Weebly-Scripts zugreifen.
var STATIC_BASE = "//cdn1.editmysite.com/";
var ASSETS_BASE = "cdn-assets/cdn11.editmysite.com/";
var STYLE_PREFIX = "wsite";

// Globaler Weebly-Namespace (idempotent).
window._W = window._W || {};

// Domain-Kontext (nur kosmetisch — main.js liest diese Werte an ein paar
// Stellen für Fehlermeldungen aus).
_W.securePrefix = "www.easywired.de";
_W.configDomain = "www.weebly.com";

// Analytics-Layer: absichtlich leer. Damit main.js nicht auf undefined
// zugreift, aber keine echten Tracker registriert sind.
_W.Analytics = { trackers: {} };

// EU/Cookie-Banner-Flags: markieren, dass wir NICHT versuchen, Consent zu
// sammeln (siehe LEGAL_AUDIT.md). main.js wertet das aus, um seinen alten
// Cookie-Banner zu unterdrücken.
_W.isEUUser = true;
_W.showCookieToAll = "none";

// Kein Customer-Accounts-Backend vorhanden — der zuvor eingebundene
// 522-KB-Bundle `main-customer-accounts-site.js` wurde ersatzlos entfernt.
// Wir belassen nur diese leere Stub-Funktion, falls im Weebly-Code irgendwo
// noch ein Event `customer_accounts_ready` gefeuert wird.
function initCustomerAccountsModels() {
  /* no-op */
}
