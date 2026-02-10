/**
 * Pinterest Pin It Button Handler
 * Adds Pinterest sharing functionality to all pin-image-wrapper elements
 */
(function() {
  'use strict';

  const PINTEREST_SHARE_URL = 'https://www.pinterest.com/pin/create/button/';

  function getPageUrl() {
    return encodeURIComponent(window.location.href);
  }

  function initPinButtons() {
    const pinWrappers = document.querySelectorAll('.pin-image-wrapper');

    pinWrappers.forEach(function(wrapper) {
      const img = wrapper.querySelector('img');
      const btn = wrapper.querySelector('.pin-it-btn');
      if (!img || !btn) return;

      btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        var imageUrl = encodeURIComponent(img.src);
        var description = encodeURIComponent(
          img.getAttribute('data-pin-description') ||
          img.getAttribute('alt') ||
          document.title
        );
        var pageUrl = getPageUrl();

        var pinUrl = PINTEREST_SHARE_URL +
          '?url=' + pageUrl +
          '&media=' + imageUrl +
          '&description=' + description;

        window.open(pinUrl, 'pinterest-share', 'width=750,height=550,scrollbars=yes');
      });
    });
  }

  function createPinButton() {
    var btn = document.createElement('button');
    btn.className = 'pin-it-btn';
    btn.setAttribute('aria-label', 'Pin this image');
    btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738.098.119.112.224.083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg> Save';
    return btn;
  }

  // Auto-add pin buttons to images that don't have one
  function autoAddPinButtons() {
    var wrappers = document.querySelectorAll('.pin-image-wrapper');
    wrappers.forEach(function(wrapper) {
      if (!wrapper.querySelector('.pin-it-btn')) {
        wrapper.appendChild(createPinButton());
      }
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      autoAddPinButtons();
      initPinButtons();
    });
  } else {
    autoAddPinButtons();
    initPinButtons();
  }
})();
