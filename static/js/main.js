/**
 * PHYB site JS — deliberately framework-free. Two responsibilities:
 * 1. Mobile nav open/close (replaces what Bootstrap's JS used to do).
 * 2. Theme toggle (light/dark), persisted in localStorage.
 *
 * Theme is applied as early as possible via an inline script in
 * base.html's <head> (before this file loads) to avoid a flash of the
 * wrong theme on page load — this file only handles the *toggle button*
 * after that.
 */
(function () {
  "use strict";

  function initNavToggle() {
    var toggler = document.querySelector(".navbar-toggler");
    var collapse = document.getElementById("mainNav");
    if (!toggler || !collapse) return;

    toggler.addEventListener("click", function () {
      var isOpen = collapse.classList.toggle("is-open");
      toggler.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    // Close the menu after tapping a link — mobile users expect this.
    collapse.querySelectorAll(".nav-link, .btn-brand").forEach(function (link) {
      link.addEventListener("click", function () {
        collapse.classList.remove("is-open");
        toggler.setAttribute("aria-expanded", "false");
      });
    });
  }

  function initThemeToggle() {
    var toggleBtn = document.querySelector(".theme-toggle");
    if (!toggleBtn) return;

    toggleBtn.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme");
      var next = current === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", next);
      try {
        localStorage.setItem("phyb-theme", next);
      } catch (e) {
        /* localStorage unavailable (private mode etc) — theme just won't persist */
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initNavToggle();
    initThemeToggle();
  });
})();
