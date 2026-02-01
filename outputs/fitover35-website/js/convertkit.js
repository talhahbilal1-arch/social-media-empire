/**
 * FitOver35 - ConvertKit Integration
 * Handles email subscriptions via ConvertKit API
 */

const CK_CONFIG = {
  apiKey: 'Qte-u1i9umIV5XFAC2DP4g',
  formId: '8946984',
  tags: {
    subscriber: '15064074',      // fitover35-subscriber
    leadMagnet: '15064075',      // lead-magnet-density-guide
    blogReader: '15064076',      // fitover35-blog-reader
  },
  endpoint: 'https://api.convertkit.com/v3'
};

/**
 * Subscribe email to ConvertKit form with tags
 */
async function subscribeEmail(email, tagIds = []) {
  const url = `${CK_CONFIG.endpoint}/forms/${CK_CONFIG.formId}/subscribe`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        api_key: CK_CONFIG.apiKey,
        email: email,
        tags: tagIds.length > 0 ? tagIds : [CK_CONFIG.tags.subscriber]
      })
    });

    const data = await response.json();

    if (data.subscription) {
      return { success: true, data };
    } else {
      return { success: false, error: data.error || 'Subscription failed' };
    }
  } catch (err) {
    return { success: false, error: err.message };
  }
}

/**
 * Initialize all ConvertKit forms on the page
 */
function initConvertKitForms() {
  document.querySelectorAll('[data-ck-form]').forEach(form => {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();

      const emailInput = this.querySelector('input[type="email"]');
      const submitBtn = this.querySelector('button[type="submit"]');
      const email = emailInput.value.trim();

      if (!email) return;

      // Determine tags based on form context
      const formType = this.dataset.ckForm;
      let tags = [CK_CONFIG.tags.subscriber];

      if (formType === 'lead-magnet') {
        tags.push(CK_CONFIG.tags.leadMagnet);
      }
      if (formType === 'blog') {
        tags.push(CK_CONFIG.tags.blogReader);
      }

      // Show loading state
      const originalText = submitBtn.textContent;
      submitBtn.textContent = 'Subscribing...';
      submitBtn.disabled = true;

      const result = await subscribeEmail(email, tags);

      if (result.success) {
        // Show success
        submitBtn.textContent = 'Subscribed!';
        submitBtn.style.backgroundColor = '#22c55e';
        emailInput.value = '';

        // Show success message
        const msg = document.createElement('p');
        msg.className = 'ck-success-msg';
        msg.textContent = 'Check your inbox for your free guide!';
        msg.style.cssText = 'color: #22c55e; margin-top: 0.5rem; font-size: 0.9rem; text-align: center;';
        if (!this.querySelector('.ck-success-msg')) {
          this.appendChild(msg);
        }

        // Close popup if inside one
        setTimeout(() => {
          const popup = this.closest('.popup-overlay');
          if (popup) popup.style.display = 'none';
        }, 2000);

      } else {
        submitBtn.textContent = 'Try Again';
        submitBtn.style.backgroundColor = '#ef4444';
      }

      // Reset button after 3 seconds
      setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.style.backgroundColor = '';
        submitBtn.disabled = false;
      }, 3000);
    });
  });
}

/**
 * Email Popup Modal
 * Shows after 30s or 60% scroll, once per session
 */
function initEmailPopup() {
  // Don't show if already dismissed
  if (sessionStorage.getItem('ck_popup_shown')) return;

  // Create popup HTML
  const popupHTML = `
    <div class="popup-overlay" id="ckPopup" style="display:none;">
      <div class="popup-modal">
        <button class="popup-close" id="ckPopupClose" aria-label="Close">&times;</button>
        <div class="popup-content">
          <h2 class="popup-title">Get the Free 5-Day Density Training Starter Guide</h2>
          <p class="popup-text">Join men over 35 who train smarter, not longer. Get the free PDF guide + weekly training insights. No spam. Unsubscribe anytime.</p>
          <form class="popup-form" data-ck-form="lead-magnet">
            <input type="email" class="popup-input" placeholder="Enter your email" required>
            <button type="submit" class="btn btn--primary popup-btn">Get the Free Guide</button>
          </form>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', popupHTML);

  const popup = document.getElementById('ckPopup');
  const closeBtn = document.getElementById('ckPopupClose');
  let popupShown = false;

  function showPopup() {
    if (popupShown || sessionStorage.getItem('ck_popup_shown')) return;
    popupShown = true;
    popup.style.display = 'flex';
    sessionStorage.setItem('ck_popup_shown', 'true');
    // Re-init forms to capture the new popup form
    initConvertKitForms();
  }

  function hidePopup() {
    popup.style.display = 'none';
  }

  // Close button
  closeBtn.addEventListener('click', hidePopup);

  // Close on overlay click
  popup.addEventListener('click', function(e) {
    if (e.target === popup) hidePopup();
  });

  // Close on Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') hidePopup();
  });

  // Trigger: after 30 seconds
  setTimeout(showPopup, 30000);

  // Trigger: 60% scroll
  window.addEventListener('scroll', function onScroll() {
    const scrollPercent = (window.scrollY + window.innerHeight) / document.body.scrollHeight;
    if (scrollPercent > 0.6) {
      showPopup();
      window.removeEventListener('scroll', onScroll);
    }
  });

  // Trigger: exit intent (desktop only)
  if (window.innerWidth > 768) {
    document.addEventListener('mouseout', function(e) {
      if (e.clientY < 10 && e.relatedTarget === null) {
        showPopup();
      }
    });
  }
}

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', function() {
  initConvertKitForms();
  initEmailPopup();
});
