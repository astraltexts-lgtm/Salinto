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
    var colors = ['#b8563a', '#c68a2b', '#c68a2b', '#4c8f68', '#2b6e48', '#1a4a2f'];

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
