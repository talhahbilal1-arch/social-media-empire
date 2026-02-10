# Netlify Subdomain DNS Setup Guide

## Overview

Each subdomain is deployed as a separate Netlify site. This guide covers setting up DNS records for all 10 subdomains across both domains.

## Prerequisites

- Access to domain registrar for dailydealdarling.com and fitover35.com
- Netlify account (talhahbilal1)
- All subdomain sites deployed to Netlify

## Step 1: Create Netlify Sites

Create 10 Netlify sites (one per subdomain):

### Daily Deal Darling Sites:
| Site Name | Custom Domain |
|-----------|--------------|
| ddd-home | home.dailydealdarling.com |
| ddd-beauty | beauty.dailydealdarling.com |
| ddd-kitchen | kitchen.dailydealdarling.com |
| ddd-selfcare | selfcare.dailydealdarling.com |
| ddd-mom | mom.dailydealdarling.com |

### Fit Over 35 Sites:
| Site Name | Custom Domain |
|-----------|--------------|
| fo35-workouts | workouts.fitover35.com |
| fo35-nutrition | nutrition.fitover35.com |
| fo35-recovery | recovery.fitover35.com |
| fo35-mindset | mindset.fitover35.com |
| fo35-homegym | homegym.fitover35.com |

### Creating each site via CLI:
```bash
# Install Netlify CLI if not already
npm install -g netlify-cli

# Login
netlify login

# For each subdomain directory, deploy:
cd outputs/infrastructure/dailydealdarling/home
netlify sites:create --name ddd-home
netlify deploy --prod

# Repeat for each subdomain...
```

### Or via Netlify Dashboard:
1. Go to https://app.netlify.com/teams/talhahbilal1/sites
2. Click "Add new site" → "Deploy manually"
3. Drag & drop the subdomain folder
4. Name the site appropriately

## Step 2: Configure Custom Domains in Netlify

For each site:
1. Go to Site Settings → Domain Management → Custom Domains
2. Click "Add custom domain"
3. Enter the subdomain (e.g., `home.dailydealdarling.com`)
4. Netlify will show required DNS records

## Step 3: Add DNS Records at Domain Registrar

### For dailydealdarling.com:

Add these CNAME records:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | home | ddd-home.netlify.app | 3600 |
| CNAME | beauty | ddd-beauty.netlify.app | 3600 |
| CNAME | kitchen | ddd-kitchen.netlify.app | 3600 |
| CNAME | selfcare | ddd-selfcare.netlify.app | 3600 |
| CNAME | mom | ddd-mom.netlify.app | 3600 |

### For fitover35.com:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | workouts | fo35-workouts.netlify.app | 3600 |
| CNAME | nutrition | fo35-nutrition.netlify.app | 3600 |
| CNAME | recovery | fo35-recovery.netlify.app | 3600 |
| CNAME | mindset | fo35-mindset.netlify.app | 3600 |
| CNAME | homegym | fo35-homegym.netlify.app | 3600 |

### Common Registrar Instructions:

**Namecheap:**
1. Go to Domain List → Manage → Advanced DNS
2. Click "Add New Record"
3. Select Type: CNAME
4. Host: subdomain name (e.g., `home`)
5. Value: Netlify site URL (e.g., `ddd-home.netlify.app`)
6. TTL: Automatic

**GoDaddy:**
1. Go to My Domains → DNS → Manage
2. Click "Add" under Records
3. Type: CNAME, Name: subdomain, Value: netlify URL

**Cloudflare:**
1. Go to DNS → Records → Add record
2. Type: CNAME, Name: subdomain, Target: netlify URL
3. **Important:** Set proxy status to "DNS only" (gray cloud) for Netlify SSL to work

## Step 4: SSL Certificates

Netlify automatically provisions free SSL certificates via Let's Encrypt:

1. After DNS propagation (5-30 minutes), go to each site's Domain settings
2. Netlify should show "HTTPS: Your site has HTTPS enabled"
3. If not, click "Verify DNS configuration" then "Provision certificate"
4. Enable "Force HTTPS" under HTTPS settings

## Step 5: Verify All Sites

Check each subdomain loads correctly:

```bash
# Quick verification script
domains=(
  "home.dailydealdarling.com"
  "beauty.dailydealdarling.com"
  "kitchen.dailydealdarling.com"
  "selfcare.dailydealdarling.com"
  "mom.dailydealdarling.com"
  "workouts.fitover35.com"
  "nutrition.fitover35.com"
  "recovery.fitover35.com"
  "mindset.fitover35.com"
  "homegym.fitover35.com"
)

for domain in "${domains[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://$domain")
  echo "$domain: $status"
done
```

## Step 6: Set Up Continuous Deployment (Optional)

For automated deployments via GitHub:

1. In Netlify, go to Site Settings → Build & Deploy → Continuous Deployment
2. Link to GitHub repo: social-media-empire
3. Set branch: pinterest-empire-v2
4. Set base directory to the subdomain folder path
5. Build command: (none — static files)
6. Publish directory: .

Or use the GitHub Actions workflow to deploy all sites on push.

## Troubleshooting

**DNS not propagating:**
- Wait up to 48 hours for full propagation
- Check with `dig home.dailydealdarling.com CNAME`
- Try flushing local DNS: `sudo dscacheutil -flushcache` (macOS)

**SSL certificate not provisioning:**
- Ensure DNS is pointing to Netlify (not proxied through Cloudflare)
- Check domain verification status in Netlify
- Try removing and re-adding the custom domain

**Subdomain shows wrong site:**
- Verify the CNAME points to the correct Netlify site
- Check Netlify site settings for correct custom domain
- Clear browser cache

**Mixed content warnings:**
- Ensure all resource URLs use https:// or protocol-relative //
- Check for hardcoded http:// URLs in HTML/CSS
