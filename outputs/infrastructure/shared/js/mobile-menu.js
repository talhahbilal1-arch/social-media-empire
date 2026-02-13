/**
 * Mobile Menu Toggle
 */
(function() {
  'use strict';
  document.addEventListener('DOMContentLoaded', function() {
    var btn = document.querySelector('.mobile-menu-btn');
    var nav = document.querySelector('.site-nav');
    if (!btn || !nav) return;
    btn.addEventListener('click', function() {
      nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', nav.classList.contains('open'));
    });
    // Close on outside click
    document.addEventListener('click', function(e) {
      if (!btn.contains(e.target) && !nav.contains(e.target)) {
        nav.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  });
})();
