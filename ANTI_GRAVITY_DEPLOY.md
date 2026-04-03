# Anti-Gravity Home Office Blog - Vercel Deployment Guide

## Overview

Next.js 14 + Tailwind CSS blog with 5 home office affiliate articles. Reads markdown content from `anti_gravity/site/content/articles/`.

## Prerequisites

- Node.js 18+
- Vercel account (https://vercel.com)
- Vercel CLI: `npm i -g vercel`

## Deploy Steps

### Option 1: Vercel CLI (Recommended)

```bash
cd anti_gravity/site
npm install
vercel deploy --prod --yes
```

On first deploy, Vercel will ask you to link to a project. Select "Create new project" and set the root directory to `anti_gravity/site`.

### Option 2: Vercel Dashboard

1. Go to https://vercel.com/new
2. Import the `social-media-empire` repository
3. Set **Root Directory** to `anti_gravity/site`
4. Framework will auto-detect as Next.js
5. Click Deploy

### Option 3: GitHub Integration

1. Connect your GitHub repo to Vercel
2. In project settings, set Root Directory to `anti_gravity/site`
3. Every push to `main` will auto-deploy

## Post-Deploy Checklist

1. **Custom Domain**: Add your domain in Vercel project settings > Domains
2. **Google Analytics**: Replace `G-XXXXXXXXXX` in `anti_gravity/site/app/layout.tsx` with your actual GA4 property ID
3. **Sitemap**: Update the domain in `anti_gravity/site/public/sitemap.xml` from `anti-gravity.vercel.app` to your custom domain
4. **Submit Sitemap**: Add `https://yourdomain.com/sitemap.xml` to Google Search Console

## Affiliate Tags

All articles use the tag `dailydealdarl-20`. Update in the markdown files at `anti_gravity/site/content/articles/` if needed.

## Adding New Articles

1. Create a new `.md` file in `anti_gravity/site/content/articles/`
2. Include frontmatter:
   ```yaml
   ---
   title: "Your Article Title"
   slug: "your-article-slug"
   date: "2026-04-01"
   author: "Author Name"
   category: "home-office"
   tags: ["tag1", "tag2"]
   description: "Meta description for SEO."
   ---
   ```
3. Write article content in markdown below the frontmatter
4. Add the article URL to `public/sitemap.xml`
5. Push to main (auto-deploys if GitHub integration is set up)

## Tech Stack

- **Framework**: Next.js 14.2
- **Styling**: Tailwind CSS 3.4
- **Content**: Markdown with gray-matter + marked
- **Deployment**: Vercel (vercel.json configured)
