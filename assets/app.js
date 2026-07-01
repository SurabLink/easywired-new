/*
 * app.js — easyWIRED Custom Client Script (2026)
 * ---------------------------------------------------------------------------
 * Ersetzt das komplette Weebly-JavaScript-Bundle. Enthält nur, was die
 * eigene Custom-Site braucht:
 *   1) Dark-Mode-Toggle (mit localStorage-Persistenz + System-Präferenz)
 *   2) Mobile-Navigation (Hamburger-Menü)
 *   3) Kennzeichnung des aktuellen Menüpunkts (aria-current)
 * Keine Dependencies. Läuft in allen modernen Browsern.
 * ---------------------------------------------------------------------------
 */
(function () {
  "use strict";

  var THEME_KEY = "ew-theme"; // 'light' | 'dark'
  var doc = document.documentElement;

  /* --------------------------------------------------------------------- */
  /* 1. Dark-Mode-Toggle                                                   */
  /* --------------------------------------------------------------------- */
  function readStoredTheme() {
    try {
      return window.localStorage.getItem(THEME_KEY);
    } catch (e) {
      return null;
    }
  }

  function storeTheme(value) {
    try {
      window.localStorage.setItem(THEME_KEY, value);
    } catch (e) {
      /* silent */
    }
  }

  function applyTheme(theme) {
    if (theme === "light" || theme === "dark") {
      doc.setAttribute("data-theme", theme);
    } else {
      doc.removeAttribute("data-theme"); // fallback -> System-Prefernz
    }
  }

  function currentTheme() {
    var attr = doc.getAttribute("data-theme");
    if (attr) return attr;
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function bindThemeToggle() {
    var btn = document.querySelector('[data-testid="theme-toggle"]');
    if (!btn) return;
    btn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      applyTheme(next);
      storeTheme(next);
      btn.setAttribute(
        "aria-label",
        next === "dark" ? "Zu hellem Design wechseln" : "Zu dunklem Design wechseln"
      );
    });
  }

  // Apply stored theme early to prevent flash of wrong theme.
  applyTheme(readStoredTheme());

  /* --------------------------------------------------------------------- */
  /* 2. Mobile-Navigation                                                  */
  /* --------------------------------------------------------------------- */
  function bindNavToggle() {
    var btn = document.querySelector('[data-testid="nav-toggle"]');
    var nav = document.querySelector('[data-testid="site-nav"]');
    if (!btn || !nav) return;
    btn.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", open ? "false" : "true");
      btn.setAttribute("aria-expanded", open ? "false" : "true");
    });
    // Close nav on outside click (mobile)
    document.addEventListener("click", function (evt) {
      if (
        nav.getAttribute("data-open") === "true" &&
        !nav.contains(evt.target) &&
        !btn.contains(evt.target)
      ) {
        nav.setAttribute("data-open", "false");
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* --------------------------------------------------------------------- */
  /* 3. Highlight aktueller Nav-Link                                       */
  /* --------------------------------------------------------------------- */
  function markCurrentNav() {
    var here = (window.location.pathname.split("/").pop() || "index.html")
      .toLowerCase();
    if (!here) here = "index.html";
    var links = document.querySelectorAll(".site-nav__link[href]");
    for (var i = 0; i < links.length; i++) {
      var href = links[i].getAttribute("href").split("?")[0].split("#")[0].toLowerCase();
      if (href === here) {
        links[i].setAttribute("aria-current", "page");
      }
    }
  }

  /* --------------------------------------------------------------------- */
  /* Boot                                                                  */
  /* --------------------------------------------------------------------- */
  function boot() {
    bindThemeToggle();
    bindNavToggle();
    markCurrentNav();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
