/**
 * DiagnosTenAI — Multi Disease Prediction System
 * File   : static/js/script.js
 * Author : Dharshan (Mowshik) | github.com/Mowshik1210
 *
 * Table of contents
 * ─────────────────
 *  1.  Constants & DOM refs
 *  2.  Page Loader
 *  3.  Theme Toggle (dark ↔ light, persisted in localStorage)
 *  4.  Navbar — scroll state + active link spy
 *  5.  Hamburger / mobile nav drawer
 *  6.  Creator Badge dropdown
 *  7.  Smooth anchor scrolling
 *  8.  Intersection Observer — fade-up animations
 *  9.  Counter animation (hero stats + stat cards)
 * 10.  Stat-card progress bars
 * 11.  Disease card live search / filter
 * 12.  Initialisation
 */

"use strict";

/* ═══════════════════════════════════════════════════════════════
   1. CONSTANTS & DOM REFS
═══════════════════════════════════════════════════════════════ */

const LS_THEME_KEY = "diagnosai-theme";   // localStorage key for theme preference

const $html          = document.documentElement;
const $body          = document.body;

// Loader
const $loader        = document.getElementById("pageLoader");

// Nav
const $siteNav       = document.getElementById("siteNav");
const $navLinks      = document.getElementById("navLinks");
const $navLinkItems  = document.querySelectorAll(".nav-link-item");

// Theme
const $themeBtn      = document.getElementById("themeToggle");
const $themeIcon     = document.getElementById("themeIcon");

// Hamburger
const $hamburger     = document.getElementById("hamburger");

// Creator badge
const $creatorWrapper  = document.getElementById("creatorWrapper");
const $creatorBtn      = document.getElementById("creatorBtn");
const $creatorDropdown = document.getElementById("creatorDropdown");

// Hero counters (hsr-num elements)
const $heroCounters  = document.querySelectorAll(".hsr-num[data-target]");

// Stats-section counters
const $statCounters  = document.querySelectorAll(".sc-num.counter[data-target]");

// Stat cards (for progress-bar trigger)
const $statCards     = document.querySelectorAll(".stat-card");

// Disease search
const $searchInput   = document.getElementById("diseaseSearch");
const $searchClear   = document.getElementById("searchClear");
const $searchEmpty   = document.getElementById("searchEmpty");
const $searchEmptyTerm = document.getElementById("searchEmptyTerm");
const $clearSearch   = document.getElementById("clearSearch");
const $dcCols        = document.querySelectorAll(".dc-col");

// Sections for scroll-spy
const $sections      = document.querySelectorAll("section[id]");

// Fade-up targets
const $fadeUps       = document.querySelectorAll(".fade-up");


/* ═══════════════════════════════════════════════════════════════
   2. PAGE LOADER
   Hide the loader after all assets finish loading.
   We also set a max wait of 3 s so it never blocks the user.
═══════════════════════════════════════════════════════════════ */

function hideLoader() {
  if (!$loader) return;
  $loader.classList.add("loaded");
  // Remove from DOM after transition completes (0.5 s)
  setTimeout(() => $loader.remove(), 600);
}

// Try on window load first
window.addEventListener("load", hideLoader);

// Safety fallback — never block for more than 3 s
setTimeout(hideLoader, 3000);


/* ═══════════════════════════════════════════════════════════════
   3. THEME TOGGLE
   Persists preference to localStorage.
   CSS handles all visual changes via [data-theme] attribute;
   this function ONLY toggles that attribute + updates the icon.
═══════════════════════════════════════════════════════════════ */

/**
 * Apply a theme ("dark" | "light") immediately.
 * @param {string} theme
 */
function applyTheme(theme) {
  $html.setAttribute("data-theme", theme);

  if ($themeIcon) {
    // Moon icon for dark mode, sun icon for light mode
    $themeIcon.className = theme === "dark"
      ? "fa-solid fa-moon"
      : "fa-solid fa-sun";
  }

  if ($themeBtn) {
    $themeBtn.setAttribute(
      "aria-label",
      theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
    );
  }
}

/**
 * Toggle between dark and light, persist to localStorage.
 */
function toggleTheme() {
  const current = $html.getAttribute("data-theme") || "light";
  const next    = current === "dark" ? "light" : "dark";
  applyTheme(next);
  try { localStorage.setItem(LS_THEME_KEY, next); } catch (_) {}
}

// Load saved preference (default = dark)
(function initTheme() {
  let saved = "light";
  try { saved = localStorage.getItem(LS_THEME_KEY) || "light"; } catch (_) {}
  applyTheme(saved);
})();

if ($themeBtn) {
  $themeBtn.addEventListener("click", toggleTheme);
}


/* ═══════════════════════════════════════════════════════════════
   4. NAVBAR — scroll state + scroll-spy active link
═══════════════════════════════════════════════════════════════ */

/**
 * Add/remove .scrolled on the nav when page scrolls past 60 px.
 * CSS uses this to add a stronger drop shadow.
 */
function handleNavScroll() {
  if (!$siteNav) return;
  $siteNav.classList.toggle("scrolled", window.scrollY > 60);
}

/**
 * Highlight the nav link whose section is currently in the viewport.
 * Uses a top-biased threshold so the highlight changes as you scroll
 * into each section rather than waiting until it fully fills the view.
 */
function updateActiveNavLink() {
  let currentId = "";
  const scrollMid = window.scrollY + window.innerHeight * 0.4;

  $sections.forEach((section) => {
    if (section.offsetTop <= scrollMid) {
      currentId = section.id;
    }
  });

  $navLinkItems.forEach((link) => {
    const href = link.getAttribute("href");
    link.classList.toggle("active", href === `#${currentId}`);
  });
}

window.addEventListener("scroll", () => {
  handleNavScroll();
  updateActiveNavLink();
}, { passive: true });

// Run once on load in case page is already scrolled
handleNavScroll();
updateActiveNavLink();


/* ═══════════════════════════════════════════════════════════════
   5. HAMBURGER / MOBILE NAV DRAWER
═══════════════════════════════════════════════════════════════ */

function closeMobileNav() {
  if (!$navLinks || !$hamburger) return;
  $navLinks.classList.remove("open");
  $hamburger.classList.remove("open");
  $hamburger.setAttribute("aria-expanded", "false");
}

function toggleMobileNav() {
  if (!$navLinks || !$hamburger) return;
  const isOpen = $navLinks.classList.toggle("open");
  $hamburger.classList.toggle("open", isOpen);
  $hamburger.setAttribute("aria-expanded", String(isOpen));
}

if ($hamburger) {
  $hamburger.addEventListener("click", toggleMobileNav);
}

// Close mobile nav when any nav link is clicked
$navLinkItems.forEach((link) => {
  link.addEventListener("click", closeMobileNav);
});

// Close mobile nav when clicking outside
document.addEventListener("click", (e) => {
  if (
    $navLinks &&
    $navLinks.classList.contains("open") &&
    !$navLinks.contains(e.target) &&
    !$hamburger.contains(e.target)
  ) {
    closeMobileNav();
  }
});


/* ═══════════════════════════════════════════════════════════════
   6. CREATOR BADGE DROPDOWN
   Opens on click. Closes when clicking outside or pressing Escape.
═══════════════════════════════════════════════════════════════ */

function closeCreatorDropdown() {
  if (!$creatorWrapper) return;
  $creatorWrapper.classList.remove("open");
  if ($creatorBtn) $creatorBtn.setAttribute("aria-expanded", "false");
}

function toggleCreatorDropdown(e) {
  e.stopPropagation();
  if (!$creatorWrapper) return;
  const isOpen = $creatorWrapper.classList.toggle("open");
  if ($creatorBtn) $creatorBtn.setAttribute("aria-expanded", String(isOpen));
}

if ($creatorBtn) {
  $creatorBtn.addEventListener("click", toggleCreatorDropdown);
}

// Close on outside click
document.addEventListener("click", (e) => {
  if ($creatorWrapper && !$creatorWrapper.contains(e.target)) {
    closeCreatorDropdown();
  }
});

// Close on Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeCreatorDropdown();
    closeMobileNav();
  }
});

// Keep clicks inside the dropdown from bubbling to the document
if ($creatorDropdown) {
  $creatorDropdown.addEventListener("click", (e) => e.stopPropagation());
}


/* ═══════════════════════════════════════════════════════════════
   7. SMOOTH ANCHOR SCROLLING
   Native scroll-behavior:smooth is set in CSS, but this adds an
   offset so content isn't hidden behind the fixed navbar (68 px).
═══════════════════════════════════════════════════════════════ */

const NAV_HEIGHT = 68; // must match .site-nav height in CSS

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    const targetId = this.getAttribute("href").slice(1);
    const target   = document.getElementById(targetId);
    if (!target) return;

    e.preventDefault();

    const top = target.getBoundingClientRect().top + window.scrollY - NAV_HEIGHT;
    window.scrollTo({ top, behavior: "smooth" });
  });
});


/* ═══════════════════════════════════════════════════════════════
   8. INTERSECTION OBSERVER — fade-up animations
   Adds .visible to elements with class .fade-up when they enter
   the viewport. CSS handles the actual transition.
═══════════════════════════════════════════════════════════════ */

if ($fadeUps.length > 0) {
  const fadeObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          fadeObserver.unobserve(entry.target); // animate once only
        }
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
  );

  $fadeUps.forEach((el) => fadeObserver.observe(el));
}

// Also auto-apply fade-up to major card groups that aren't manually tagged
document.querySelectorAll(
  ".disease-card, .stat-card, .how-card, .footer-brand, .footer-links"
).forEach((el, i) => {
  el.style.transitionDelay = `${(i % 4) * 80}ms`; // stagger in groups of 4
  el.classList.add("fade-up");

  const obs = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        obs.unobserve(entry.target);
      }
    },
    { threshold: 0.10, rootMargin: "0px 0px -30px 0px" }
  );
  obs.observe(el);
});


/* ═══════════════════════════════════════════════════════════════
   9. COUNTER ANIMATION
   Animates numeric counters from 0 to their data-target value
   using a smooth easing function. Triggered by IntersectionObserver
   so numbers count up the moment they scroll into view.
═══════════════════════════════════════════════════════════════ */

/**
 * Animate a single counter element from 0 → target.
 * @param {HTMLElement} el      - The element whose textContent is updated
 * @param {number}      target  - The final number to count to
 * @param {number}      duration - Animation duration in ms
 */
function animateCounter(el, target, duration = 1600) {
  const start     = performance.now();
  const startVal  = 0;

  function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
  }

  function tick(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased    = easeOutQuart(progress);
    const value    = Math.round(startVal + (target - startVal) * eased);

    el.textContent = value;

    if (progress < 1) {
      requestAnimationFrame(tick);
    } else {
      el.textContent = target; // ensure exact final value
    }
  }

  requestAnimationFrame(tick);
}

/**
 * Set up an IntersectionObserver for a NodeList of counter elements.
 * @param {NodeList} counters
 */
function observeCounters(counters) {
  if (!counters || counters.length === 0) return;

  const obs = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el     = entry.target;
          const target = parseInt(el.dataset.target, 10);
          if (!isNaN(target)) {
            animateCounter(el, target);
          }
          obs.unobserve(el);
        }
      });
    },
    { threshold: 0.5 }
  );

  counters.forEach((el) => obs.observe(el));
}

// Hero mini-stats (hsr-num) + Stats section (sc-num.counter)
observeCounters($heroCounters);
observeCounters($statCounters);


/* ═══════════════════════════════════════════════════════════════
   10. STAT-CARD PROGRESS BARS
   Adds .animated to .stat-card when it enters the viewport.
   CSS [data-theme] rule then transitions .sc-bar width to --bar-w.
═══════════════════════════════════════════════════════════════ */

if ($statCards.length > 0) {
  const barObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          // Slight delay so counter + bar start together
          setTimeout(() => entry.target.classList.add("animated"), 200);
          barObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.4 }
  );

  $statCards.forEach((card) => barObserver.observe(card));
}


/* ═══════════════════════════════════════════════════════════════
   11. DISEASE CARD LIVE SEARCH / FILTER
   Filters .dc-col cards by matching the search string against
   the data-name attribute (set in index.html Jinja loop).
   Shows an empty state when no cards match.
═══════════════════════════════════════════════════════════════ */

/**
 * Filter disease cards by a search term.
 * @param {string} term - lower-cased search string
 */
function filterDiseaseCards(term) {
  let visibleCount = 0;

  $dcCols.forEach((col) => {
    const name    = (col.dataset.name || "").toLowerCase();
    const matches = name.includes(term);
    col.classList.toggle("hidden", !matches);
    if (matches) visibleCount++;
  });

  // Show / hide empty state
  if ($searchEmpty) {
    $searchEmpty.classList.toggle("d-none", visibleCount > 0);
    if (visibleCount === 0 && $searchEmptyTerm) {
      $searchEmptyTerm.textContent = term;
    }
  }

  // Show / hide the clear (×) button
  if ($searchClear) {
    $searchClear.hidden = term.length === 0;
  }
}

if ($searchInput) {
  $searchInput.addEventListener("input", (e) => {
    const term = e.target.value.trim().toLowerCase();
    filterDiseaseCards(term);
  });
}

// Clear button resets the filter
function clearSearch() {
  if ($searchInput) {
    $searchInput.value = "";
    $searchInput.focus();
  }
  filterDiseaseCards("");
}

if ($searchClear)  $searchClear.addEventListener("click",  clearSearch);
if ($clearSearch)  $clearSearch.addEventListener("click",  clearSearch);


/* ═══════════════════════════════════════════════════════════════
   12. INITIALISATION
   Final setup calls that run after DOM is ready.
═══════════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {

  // ── Nav link smooth scroll (re-bind for dynamically missed links)
  document.querySelectorAll(".nav-link-item[href^='#']").forEach((link) => {
    link.addEventListener("click", (e) => {
      const id  = link.getAttribute("href").slice(1);
      const el  = document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      const top = el.getBoundingClientRect().top + window.scrollY - NAV_HEIGHT;
      window.scrollTo({ top, behavior: "smooth" });
      closeMobileNav();
    });
  });

  // ── Stagger hero stat items in on load
  document.querySelectorAll(".hsr-item, .hsr-divider").forEach((el, i) => {
    el.style.opacity    = "0";
    el.style.transform  = "translateY(16px)";
    el.style.transition = "opacity .5s ease, transform .5s ease";
    setTimeout(() => {
      el.style.opacity   = "1";
      el.style.transform = "translateY(0)";
    }, 800 + i * 120);
  });

  // ── Hero copy fade-in on load
  const $heroCopy = document.querySelector(".hero-copy");
  if ($heroCopy) {
    $heroCopy.style.opacity   = "0";
    $heroCopy.style.transform = "translateY(24px)";
    $heroCopy.style.transition= "opacity .7s ease, transform .7s ease";
    setTimeout(() => {
      $heroCopy.style.opacity   = "1";
      $heroCopy.style.transform = "translateY(0)";
    }, 200);
  }

  // ── Hero illustration fade-in
  const $illus = document.querySelector(".hero-illus");
  if ($illus) {
    $illus.style.opacity   = "0";
    $illus.style.transform = "scale(.94)";
    $illus.style.transition= "opacity .9s ease, transform .9s ease";
    setTimeout(() => {
      $illus.style.opacity   = "1";
      $illus.style.transform = "scale(1)";
    }, 400);
  }

  // ── Add .fade-up to section headers that weren't manually tagged
  document.querySelectorAll(".section-header").forEach((el) => {
    el.classList.add("fade-up");
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        obs.unobserve(entry.target);
      }
    }, { threshold: 0.2 });
    obs.observe(el);
  });

  // ── Disease card: redirect on Enter key for keyboard accessibility
  document.querySelectorAll(".disease-card").forEach((card) => {
    const cta = card.querySelector(".dc-cta");
    if (!cta) return;
    card.setAttribute("tabindex", "0");
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        cta.click();
      }
    });
  });

  console.log(
    "%c DiagnosTenAI ",
    "background:#00D4B8;color:#060D1B;font-weight:900;padding:4px 12px;border-radius:4px;font-size:14px;",
    "— Multi Disease Prediction System ready."
  );
});
