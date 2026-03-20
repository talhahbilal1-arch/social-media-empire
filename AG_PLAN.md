# Antigravity Execution Plan: AI Prompt Pack Launch
**Generated**: 2026-03-20
**Status**: Ready for execution
**Executor**: Antigravity

---

## Phase 1: Image Generation & Persistence Setup
**Goal**: Generate 28 test images and save each with permanent URLs

### Step 1.1 — Database Schema
Create Supabase table to track all image generations:

```sql
CREATE TABLE IF NOT EXISTS prompt_pack_generations (
  id TEXT PRIMARY KEY,
  prompt_name TEXT NOT NULL,
  test_variant CHAR(1) NOT NULL,
  ai_model TEXT NOT NULL,
  blob_url TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Step 1.2 — Generate Midjourney Images (6 prompts × 4 variants = 24 images)
**Platform**: https://www.midjourney.com (Google SSO login)

For each of the 6 prompt groups:
1. Paste exact prompt text into /imagine command
2. Wait for 4-image grid to generate
3. Upscale the BEST image (U1, U2, U3, or U4)
4. Download to: ~/Desktop/midjourney-test-images/prompt-[NUMBER]-test-[LETTER].png
5. Record in Supabase

**Prompts to generate**: Fitness Portrait, Floating Product, App Icon, Interior Design, Food Photography, Flat Lay

### Step 1.3 — Generate DALL-E 3 Logo Images (4 images)
**Platform**: https://chatgpt.com

For each of the 4 logo prompts:
1. Paste prompt into ChatGPT chat
2. Wait for DALL-E 3 to generate
3. Save to: ~/Desktop/dalle-test-images/prompt-3-test-[LETTER].png

### Step 1.4 — Upload All Images to Vercel Blob
For each of 28 images:
1. Upload to Vercel Blob at: prompt-pack/prompt-[N]-test-[LETTER].png
2. Get permanent URL: https://blob.vercel-storage.com/...
3. Update Supabase with blob_url and status: "uploaded"

---

## Phase 2: PromptBase Submissions (10 submissions)
**Platform**: https://promptbase.com

Submit 10 prompts with:
- Full prompt text
- 4 test images as cover photos (or screenshot of output)
- 150-200 word description
- Tags and price
- Correct AI model

**Submissions**:
1. Fitness Portrait ($4.99, Midjourney)
2. Floating Product ($4.99, Midjourney)
3. Logo Mark ($4.99, DALL-E)
4. Email Onboarding ($4.99, ChatGPT)
5. App Icon ($3.99, Midjourney)
6. Interior Design ($4.99, Midjourney)
7. Content Strategy ($4.99, ChatGPT)
8. Food Photography ($3.99, Midjourney)
9. Sales Objection ($4.99, ChatGPT)
10. Flat Lay ($3.99, Midjourney)

Record each PromptBase URL to Supabase after publishing.

---

## Phase 3: Gumroad Product Completion
**Platform**: https://gumroad.com/products/nezsn/edit

### Step 3.1 — Create Cover Collage
Create 2×2 grid of 4 best Midjourney test images with text overlay

### Step 3.2 — Convert PDF
```bash
pandoc ~/Desktop/social-media-empire/prompt-packs/promptbase/deliverable/The-Creators-AI-Prompt-Vault.md -o The-Creators-AI-Prompt-Vault.pdf
```

### Step 3.3 — Update Product
1. Upload cover image and thumbnail (600x600px)
2. Upload PDF to Content tab
3. Change URL slug from "nezsn" to "ai-prompt-vault"
4. Click Publish

Record the live Gumroad URL to Supabase.

---

## Phase 4: Etsy Listings (4 listings)
**Platform**: https://www.etsy.com

### Step 4.1 — Create Bundle Listing
- **Title**: 10 Premium AI Prompt Pack Bundle | Midjourney DALL-E ChatGPT | Product Photography Content Marketing Sales | Digital Download
- **Price**: $24.99
- **Images**: Upload 4 best Midjourney test images
- **Description**: Full bundle description from user spec
- **Tags**: ai prompt, midjourney prompt, chatgpt prompt, dall e prompt, product photography prompt, content marketing, email template, sales script, digital download, business tools, prompt engineering, ai tools, social media
- **Upload file**: The PDF from Gumroad
- **Publish**

### Step 4.2 — Create 3 Individual Listings
1. **Floating Product** — $4.99, 4 images, Prompt 2
2. **90-Day Content Strategy** — $4.99, mockup image, Prompt 7
3. **Sales Objection Playbook** — $4.99, mockup image, Prompt 9

Each with 200-word description, proper tags, and PDF/text file upload.

Record each Etsy listing URL to Supabase after publishing.

---

## Phase 5: Verification & Documentation
- [ ] 28 images generated and uploaded to Vercel Blob with permanent URLs
- [ ] Supabase prompt_pack_generations table fully populated
- [ ] 10 PromptBase products submitted and visible
- [ ] Gumroad product published at talhahbilal.gumroad.com/l/ai-prompt-vault
- [ ] 4 Etsy listings published and searchable
- [ ] All product URLs recorded in Supabase prompt_pack_listings table
- [ ] Screenshots taken for each platform (save to ./proof-of-publication/)

---

## Output Files to Commit
- ./archive/test-images-generated/ — All 28 downloaded images
- ./proof-of-publication/ — Screenshots of each published product
- ./scripts/upload-to-blob.js — Node script for Vercel Blob upload
- Supabase tables: prompt_pack_generations, prompt_pack_listings (populated with all data)
