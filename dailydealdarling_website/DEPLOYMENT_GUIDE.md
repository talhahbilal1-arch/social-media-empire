# Daily Deal Darling - Website Deployment Guide

## What's Included

This package contains a complete, conversion-optimized affiliate website with:

### Homepage (`index.html`)
- Urgency announcement bar with animated pulse
- Mobile-responsive sticky CTA bar
- Real Amazon product images (not stock photos)
- Prime badges on eligible products
- Testimonials/social proof section
- Newsletter signup
- Today's Deals with urgency pricing
- Shop by Category cards
- Full SEO meta tags

### Articles (6 pages)
- `articles/best-skincare-products-2026.html`
- `articles/amazon-finds-under-25.html`
- `articles/best-kitchen-gadgets-2026.html`
- `articles/best-home-organization-2026.html`
- `articles/best-fitness-gear-2026.html`
- `articles/best-self-care-products-2026.html`
- `articles/best-amazon-products-2026.html`

### Quiz
- `quizzes/skincare-routine.html`

### CSS
- `css/styles.css` - Complete design system (984 lines)

---

## Deployment to GitHub Pages

### Option 1: Replace Current Site (Recommended)

1. Go to your GitHub repo: `https://github.com/talhahbilal1-arch/social-media-empire`
2. Delete the current website files (or rename as backup)
3. Upload the entire `dailydealdarling_website` folder contents to the root
4. Commit and push
5. Wait 2-3 minutes for GitHub Pages to rebuild

### Option 2: Manual Upload via GitHub Web Interface

1. Go to your repo on GitHub
2. Click "Add file" → "Upload files"
3. Drag and drop the entire folder contents
4. Commit to main branch

### Option 3: Using Git Command Line

```bash
cd your-repo-folder
# Backup existing files
mkdir backup && mv index.html backup/
# Copy new files
cp -r /path/to/dailydealdarling_website/* ./
git add .
git commit -m "Complete website redesign for conversion optimization"
git push
```

---

## Conversion Features Explained

### 1. Urgency Announcement Bar
- Animated pulsing dot draws attention
- "Ends soon" creates FOMO
- Direct link to deals section

### 2. Real Amazon Product Images
- Products now show actual Amazon images
- Matches what users see on Amazon
- Builds trust and increases click-through

### 3. Mobile Sticky CTA
- Appears after scrolling 400px
- Stays fixed at bottom on mobile
- Direct path to deals section

### 4. Prime Badges
- Shows which products have Prime shipping
- Trust signal for Amazon Prime members

### 5. Social Proof
- Testimonials with "Verified Purchase" badges
- Review counts (e.g., "127,000+ reviews")
- Star ratings visible on all products

### 6. Pricing Psychology
- Original price with strikethrough
- Percentage off badges (40% OFF, etc.)
- Current price emphasized

---

## Customization

### Update Sale Messaging
Edit line 24 in `index.html`:
```html
<span>🔥 <strong>January Flash Sale:</strong> Up to 40% off...</span>
```

### Change Products
Products are in the "Best Sellers" and "Today's Deals" sections.
Each product card follows this structure:
```html
<div class="product-card">
  <span class="product-badge">Badge Text</span>
  <div class="product-image" style="background: #f8f8f8; padding: 10px;">
    <img src="AMAZON_IMAGE_URL" alt="Product Name">
  </div>
  <div class="product-content">
    <span class="product-category">Category</span>
    <h4 class="product-title">Product Name</h4>
    <div class="product-rating">
      <div class="stars">★★★★★</div>
      <span class="rating-count">X reviews</span>
    </div>
    <div class="product-price">
      <span class="price-current">$XX.XX</span>
      <span class="price-original">$XX.XX</span>
    </div>
    <a href="AMAZON_LINK?tag=dailydealdarl-20" class="btn btn-amazon product-cta">CTA Text →</a>
  </div>
</div>
```

### Find Amazon Product Images
1. Go to the product page on Amazon
2. Right-click the main product image
3. Select "Copy image address"
4. Use that URL (usually starts with `https://m.media-amazon.com/images/`)

---

## Testing Checklist

Before going live, verify:

- [ ] All Amazon links have your affiliate tag (`?tag=dailydealdarl-20`)
- [ ] Mobile menu opens/closes correctly
- [ ] Mobile sticky CTA appears on scroll
- [ ] All product images load
- [ ] Newsletter form connects to ConvertKit
- [ ] Links to articles work
- [ ] Quiz loads correctly

---

## Performance Notes

- All images lazy-load automatically
- CSS is mobile-first optimized
- Fonts preconnect to Google Fonts
- No JavaScript frameworks = fast load time

---

## Support Files

Your affiliate tag: `dailydealdarl-20`

ASINs used (verified working):
- B00TTD9BRC - CeraVe Moisturizing Cream
- B07XXPHQZK - Laneige Lip Sleeping Mask
- B00006JSUB - Lodge Cast Iron Skillet
- B07QXV6N1B - Anker PowerCore
- B00NGV4506 - Ninja Blender
- B086Z6LNVS - Theragun Mini
- B07D8HJ22H - Storage Bins
- B00FO9ZRYG - BalanceFrom Yoga Mat

---

**Ready to deploy!** The site is production-ready with all conversion elements in place.
