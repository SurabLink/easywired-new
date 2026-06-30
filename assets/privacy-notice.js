/* easyWIRED Privacy Notice — pure-vanilla, no dependencies, no tracking.
 * Shows a one-time information banner. Stores acknowledgment in localStorage.
 * (Legally einwilligungsfrei nach § 25 Abs. 2 Nr. 2 TDDDG, weil das Flag den
 *  vom Nutzer ausdrücklich gewünschten Dienst "nicht mehr anzeigen" umsetzt.)
 */
(function () {
  "use strict";

  var STORAGE_KEY = "ew_privacy_ack";
  var STORAGE_VALUE = "1";

  function storageAvailable() {
    try {
      var t = "__ew_test__";
      window.localStorage.setItem(t, t);
      window.localStorage.removeItem(t);
      return true;
    } catch (e) {
      return false;
    }
  }

  function alreadyAcknowledged() {
    if (!storageAvailable()) return false;
    try {
      return window.localStorage.getItem(STORAGE_KEY) === STORAGE_VALUE;
    } catch (e) {
      return false;
    }
  }

  function setAcknowledged() {
    if (!storageAvailable()) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, STORAGE_VALUE);
    } catch (e) {
      /* noop */
    }
  }

  function buildBanner() {
    var wrap = document.createElement("aside");
    wrap.className = "ew-privacy-notice";
    wrap.setAttribute("role", "complementary");
    wrap.setAttribute("aria-label", "Datenschutz-Hinweis");
    wrap.setAttribute("data-testid", "privacy-notice");

    var title = document.createElement("p");
    title.className = "ew-privacy-notice__title";
    title.textContent = "Datenschutz auf easyWIRED";
    wrap.appendChild(title);

    var body = document.createElement("p");
    body.className = "ew-privacy-notice__body";
    body.innerHTML =
      "Diese Seite ist ein privates, nicht-kommerzielles Habbo-Fanprojekt. " +
      "Es werden <strong>keine Cookies</strong> gesetzt, <strong>kein Tracking</strong> " +
      "und <strong>keine externen Analyse-Dienste</strong> verwendet. Server-Logs " +
      "(IP, Zeitstempel, aufgerufene Seite) speichert der Hoster STRATO ausschließlich " +
      "zur technischen Sicherheit und löscht sie nach maximal 7 Tagen. Details in der " +
      '<a href="impressum-und-datenschutz.html" data-testid="privacy-notice-link">' +
      "Datenschutzerklärung</a>.";
    wrap.appendChild(body);

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "ew-privacy-notice__close";
    btn.setAttribute("aria-label", "Hinweis schließen und nicht erneut anzeigen");
    btn.setAttribute("data-testid", "privacy-notice-dismiss");
    btn.textContent = "\u00D7"; /* × */
    btn.addEventListener("click", function () {
      setAcknowledged();
      wrap.setAttribute("data-visible", "false");
      // Smoothly remove from DOM after CSS transition
      window.setTimeout(function () {
        if (wrap && wrap.parentNode) {
          wrap.parentNode.removeChild(wrap);
        }
      }, 240);
    });
    wrap.appendChild(btn);

    return wrap;
  }

  function show() {
    if (alreadyAcknowledged()) return;
    if (document.querySelector('[data-testid="privacy-notice"]')) return;
    var banner = buildBanner();
    document.body.appendChild(banner);
    // Defer to next frame so CSS transition kicks in
    window.requestAnimationFrame(function () {
      banner.setAttribute("data-visible", "true");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", show, { once: true });
  } else {
    show();
  }
})();
