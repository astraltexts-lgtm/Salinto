/* =========================================================
   Salinto main.js — global UI enhancements
   ========================================================= */

/* ---- Toast / Auto-dismiss messages ---- */
(function () {
  function initToasts() {
    const container = document.querySelector('.sal-messages');
    if (!container) return;

    // Convert each .sal-message into a toast
    Array.from(container.querySelectorAll('.sal-message')).forEach(function (el, i) {
      el.classList.add('sal-toast');
      // Stagger entrance
      setTimeout(function () { el.classList.add('sal-toast--visible'); }, i * 120);
      // Auto-dismiss after 4.5 s
      setTimeout(function () {
        el.classList.remove('sal-toast--visible');
        setTimeout(function () { el.remove(); }, 400);
      }, 4500 + i * 200);

      // Click to dismiss early
      el.addEventListener('click', function () {
        el.classList.remove('sal-toast--visible');
        setTimeout(function () { el.remove(); }, 400);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', initToasts);
})();

/* ---- Smooth-scroll to anchor on load (e.g. #review-42) ---- */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var hash = window.location.hash;
    if (!hash) return;
    var target = document.querySelector(hash);
    if (!target) return;
    setTimeout(function () {
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      target.classList.add('sal-highlight-flash');
      setTimeout(function () { target.classList.remove('sal-highlight-flash'); }, 1800);
    }, 300);
  });
})();

/* ---- Mobile hamburger menu ---- */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('sal-nav-toggle');
    var menu   = document.getElementById('sal-nav-menu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('sal-nav-menu--open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.classList.toggle('sal-nav-toggle--open', open);
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove('sal-nav-menu--open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.classList.remove('sal-nav-toggle--open');
      }
    });
  });
})();

/* ---- Show / Hide password toggle ---- */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.sal-pw-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var target = document.querySelector(btn.dataset.target);
        if (!target) return;
        var isText = target.type === 'text';
        target.type = isText ? 'password' : 'text';
        btn.textContent = isText ? 'Show' : 'Hide';
        btn.setAttribute('aria-pressed', !isText);
      });
    });
  });
})();

/* ---- Password strength meter ---- */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var field  = document.getElementById('id_password1');
    var meter  = document.getElementById('sal-pw-strength');
    var label  = document.getElementById('sal-pw-strength-label');
    if (!field || !meter) return;

    function score(pw) {
      var s = 0;
      if (pw.length >= 8)  s++;
      if (pw.length >= 12) s++;
      if (/[A-Z]/.test(pw)) s++;
      if (/[0-9]/.test(pw)) s++;
      if (/[^A-Za-z0-9]/.test(pw)) s++;
      return s;
    }

    var labels = ['Too short', 'Weak', 'Fair', 'Good', 'Strong', 'Very strong'];
    var colors = ['#b04426', '#a86a12', '#a86a12', '#1f7a4d', '#186a43', '#14532d'];

    field.addEventListener('input', function () {
      var s = score(field.value);
      var pct = Math.round((s / 5) * 100);
      meter.style.width = pct + '%';
      meter.style.background = colors[s] || colors[0];
      if (label) label.textContent = field.value ? labels[s] : '';
    });
  });
})();

/* ---- Confirm-before-delete generic helper ---- */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });
});

/* =========================================================
   Motion layer — scroll reveal, count-up, navbar state
   ========================================================= */

/* ---- Sticky navbar gets a shadow once the page scrolls ---- */
(function () {
  var navbar = document.querySelector('.sal-navbar');
  if (!navbar) return;

  function onScroll() {
    navbar.classList.toggle('sal-navbar--scrolled', window.scrollY > 8);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
})();

/* ---- Reveal-on-scroll with per-row stagger ----
   Elements carry .sal-reveal; html.js (set in <head>) hides
   them so there is no flash when JS is disabled. */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var targets = Array.prototype.slice.call(document.querySelectorAll('.sal-reveal'));
    if (!targets.length) return;

    // Stagger siblings inside the same parent (card grids, lists)
    var seen = new Map();
    targets.forEach(function (el) {
      var parent = el.parentElement;
      var i = seen.get(parent) || 0;
      seen.set(parent, i + 1);
      if (!el.style.getPropertyValue('--sal-reveal-delay')) {
        el.style.setProperty('--sal-reveal-delay', Math.min(i, 7) * 0.07 + 's');
      }
    });

    if (!('IntersectionObserver' in window)) {
      targets.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    targets.forEach(function (el) { io.observe(el); });
  });
})();

/* ---- Count-up for hero / profile stat numbers ---- */
(function () {
  function animateCount(el) {
    var raw = (el.textContent || '').trim();
    var match = raw.match(/([^\d]*)([\d][\d,.]*)(.*)/);
    if (!match) return;

    var prefix = match[1];
    var numStr = match[2];
    var suffix = match[3];
    var target = parseFloat(numStr.replace(/,/g, ''));
    if (isNaN(target)) return;

    var grouped = numStr.indexOf(',') !== -1;
    var decimals = (numStr.split('.')[1] || '').length;
    var duration = 1400;
    var start = null;

    function frame(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3); // expo-out feel
      var val = target * eased;
      var out = grouped
        ? Math.round(val).toLocaleString('en-US')
        : val.toFixed(decimals);
      el.textContent = prefix + out + suffix;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var nums = document.querySelectorAll('.sal-stat-num, .sal-pstat-num');
    if (!nums.length) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    if (!('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    nums.forEach(function (el) { io.observe(el); });
  });
})();

/* ---- Rating distribution bars grow when scrolled into view ---- */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var fills = Array.prototype.slice.call(document.querySelectorAll('.sal-dist-bar-fill'));
    if (!fills.length || !('IntersectionObserver' in window)) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var finals = fills.map(function (el) { return el.style.width; });
    fills.forEach(function (el) { el.style.width = '0%'; });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var idx = fills.indexOf(entry.target);
        if (idx === -1) { io.unobserve(entry.target); return; }
        setTimeout(function () { entry.target.style.width = finals[idx] || '0%'; }, 80);
        io.unobserve(entry.target);
      });
    }, { threshold: 0.4 });
    fills.forEach(function (el) { io.observe(el); });
  });
})();

/* ---- Vote counters pop when AJAX updates them ---- */
(function () {
  function bump(el) {
    el.classList.add('bump');
    setTimeout(function () { el.classList.remove('bump'); }, 350);
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!('MutationObserver' in window)) return;
    document.querySelectorAll('.sal-vote-count').forEach(function (el) {
      new MutationObserver(function () { bump(el); }).observe(el, {
        childList: true,
        characterData: true,
        subtree: true
      });
    });
  });
})();
