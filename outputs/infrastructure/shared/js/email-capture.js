/**
 * Email Capture - Sticky Bar + Popup
 * Handles email collection with localStorage persistence
 */
(function() {
  'use strict';

  var STORAGE_KEY = 'pe_email_state';
  var POPUP_DELAY_MS = 30000; // 30 seconds
  var SCROLL_TRIGGER_PCT = 40; // Show sticky bar after 40% scroll
  var DISMISS_DAYS = 7; // Don't show again for 7 days after dismiss

  function getState() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch(e) {
      return {};
    }
  }

  function setState(updates) {
    var state = getState();
    Object.keys(updates).forEach(function(k) { state[k] = updates[k]; });
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch(e) {}
  }

  function isDismissed() {
    var state = getState();
    if (!state.dismissed_at) return false;
    var dismissedAt = new Date(state.dismissed_at);
    var now = new Date();
    var daysSince = (now - dismissedAt) / (1000 * 60 * 60 * 24);
    return daysSince < DISMISS_DAYS;
  }

  function isSubscribed() {
    return getState().subscribed === true;
  }

  // Sticky Bar
  function initStickyBar() {
    var bar = document.querySelector('.email-sticky-bar');
    if (!bar || isSubscribed() || isDismissed()) return;

    var closeBtn = bar.querySelector('.close-bar');
    var form = bar.querySelector('form') || bar;
    var input = bar.querySelector('input[type="email"]');
    var submitBtn = bar.querySelector('button[type="submit"]');

    // Show on scroll
    var shown = false;
    window.addEventListener('scroll', function() {
      if (shown || isSubscribed()) return;
      var scrollPct = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
      if (scrollPct >= SCROLL_TRIGGER_PCT) {
        bar.classList.add('visible');
        shown = true;
      }
    }, { passive: true });

    // Close
    if (closeBtn) {
      closeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        bar.classList.remove('visible');
        setState({ dismissed_at: new Date().toISOString() });
      });
    }

    // Submit
    if (submitBtn && input) {
      submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        handleEmailSubmit(input.value, bar, 'sticky_bar');
      });
    }
  }

  // Popup
  function initPopup() {
    var overlay = document.querySelector('.email-popup-overlay');
    if (!overlay || isSubscribed() || isDismissed()) return;

    var popup = overlay.querySelector('.email-popup');
    var closeBtn = overlay.querySelector('.close-popup');
    var input = overlay.querySelector('input[type="email"]');
    var submitBtn = overlay.querySelector('.submit-btn');

    // Show after delay
    setTimeout(function() {
      if (!isSubscribed() && !isDismissed()) {
        overlay.classList.add('visible');
      }
    }, POPUP_DELAY_MS);

    // Close on overlay click
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) {
        overlay.classList.remove('visible');
        setState({ dismissed_at: new Date().toISOString() });
      }
    });

    // Close button
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        overlay.classList.remove('visible');
        setState({ dismissed_at: new Date().toISOString() });
      });
    }

    // Submit
    if (submitBtn && input) {
      submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        handleEmailSubmit(input.value, overlay, 'popup');
      });
    }

    // Close on Escape
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && overlay.classList.contains('visible')) {
        overlay.classList.remove('visible');
        setState({ dismissed_at: new Date().toISOString() });
      }
    });
  }

  function handleEmailSubmit(email, container, source) {
    if (!email || !isValidEmail(email)) {
      var input = container.querySelector('input[type="email"]');
      if (input) {
        input.style.borderColor = '#E60023';
        input.setAttribute('placeholder', 'Please enter a valid email');
      }
      return;
    }

    // Store subscription
    setState({
      subscribed: true,
      email: email,
      source: source,
      subscribed_at: new Date().toISOString()
    });

    // Send to ConvertKit or backend endpoint if configured
    var endpoint = container.getAttribute('data-action');
    if (endpoint) {
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, source: source })
      }).catch(function() {});
    }

    // Show success
    container.classList.remove('visible');
    showThankYou();
  }

  function showThankYou() {
    var toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:2rem;right:2rem;background:#4CAF50;color:white;padding:1rem 1.5rem;border-radius:8px;font-weight:500;z-index:400;animation:slideIn 0.3s ease';
    toast.textContent = 'Thanks for subscribing!';
    document.body.appendChild(toast);
    setTimeout(function() {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s';
      setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  // Init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initStickyBar();
      initPopup();
    });
  } else {
    initStickyBar();
    initPopup();
  }
})();
