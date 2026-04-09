# Make.com Scenario Setup Guide

Complete documentation for recreating the Make.com automation scenarios for Social Media Empire.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Agent 2: Value Pins Automation](#agent-2-value-pins-automation)
4. [Agent 3: Affiliate Publisher](#agent-3-affiliate-publisher)
5. [Troubleshooting](#troubleshooting)
6. [Testing Procedures](#testing-procedures)
7. [Scenario Export/Import](#scenario-exportimport)

---

## Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Make.com Scenarios                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Agent 2: Value Pins Automation                                 │
│  ┌──────────┐   ┌─────────┐   ┌────────┐   ┌───────────────┐   │
│  │ Schedule │──▶│ Claude  │──▶│ Pexels │──▶│ Image Process │   │
│  │ Trigger  │   │   API   │   │  API   │   │ (Text Overlay)│   │
│  └──────────┘   └─────────┘   └────────┘   └───────┬───────┘   │
│                                                     │           │
│                        ┌────────────────────────────┘           │
│                        ▼                                        │
│  ┌──────────┐   ┌───────────┐   ┌──────────────┐               │
│  │ Supabase │◀──│ Pinterest │◀──│ Error Handle │               │
│  │ Logging  │   │  Posting  │   │    Module    │               │
│  └──────────┘   └───────────┘   └──────────────┘               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Agent 3: Affiliate Publisher                                   │
│  ┌──────────┐   ┌─────────┐   ┌─────────┐   ┌───────────────┐  │
│  │ Webhook/ │──▶│ Product │──▶│ Content │──▶│ Image Handler │  │
│  │ Schedule │   │  Fetch  │   │  Gen    │   │               │  │
│  └──────────┘   └─────────┘   └─────────┘   └───────┬───────┘  │
│                                                      │          │
│                        ┌─────────────────────────────┘          │
│                        ▼                                        │
│  ┌──────────┐   ┌───────────┐   ┌──────────────┐               │
│  │ Tracking │◀──│ Pinterest │◀──│ Error Handle │               │
│  │ /Logging │   │  Posting  │   │    Module    │               │
│  └──────────┘   └───────────┘   └──────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Webhook Integration Points

The Social Media Empire codebase sends data to Make.com webhooks with this payload structure:

```json
{
  "type": "idea_pin",
  "board_id": "daily-deal-darling-tips",
  "title": "5 Budget Beauty Hacks You Need!",
  "pages": [
    {
      "media_url": "https://example.com/video.mp4",
      "description": "Transform your routine without breaking the bank..."
    }
  ],
  "link": "https://dailydealdarling.com/beauty-hacks"
}
```

---

## Prerequisites

### Required Accounts & API Keys

| Service | Purpose | How to Obtain |
|---------|---------|---------------|
| Make.com | Automation platform | [make.com/en/register](https://make.com/en/register) |
| Anthropic (Claude) | AI content generation | [console.anthropic.com](https://console.anthropic.com) |
| Pexels | Stock images | [pexels.com/api](https://www.pexels.com/api/) |
| Pinterest | Social posting | [developers.pinterest.com](https://developers.pinterest.com) |
| Supabase | Database logging | [supabase.com](https://supabase.com) |

### Make.com Plan Requirements

- **Minimum**: Pro plan (10,000 operations/month)
- **Recommended**: Teams plan for higher limits and priority execution
- Required features: HTTP modules, Image modules, Error handling

### API Rate Limits to Consider

| API | Rate Limit | Recommendation |
|-----|------------|----------------|
| Claude API | 60 RPM (requests per minute) | Add 2-second delays between requests |
| Pexels API | 200 requests/hour | Cache results, use batch requests |
| Pinterest API | 1,000 requests/day | Schedule posts strategically |
| Supabase | Per plan | Use batch inserts |

---

## Agent 2: Value Pins Automation

### Scenario Purpose

Automatically generates and posts valuable Pinterest content (tips, advice, lifestyle content) on a scheduled basis for all brands.

### Complete Module Chain

```
[1] Schedule ──▶ [2] Set Variables ──▶ [3] Claude API ──▶ [4] Pexels Search
                                                                │
        ┌───────────────────────────────────────────────────────┘
        ▼
[5] Image Resize ──▶ [6] Text Overlay ──▶ [7] Pinterest Create Pin
                                                │
        ┌───────────────────────────────────────┘
        ▼
[8] Supabase Insert ──▶ [9] Error Handler ──▶ [Router to notifications]
```

---

### Module 1: Schedule Trigger

**Module Type**: `builtin:BasicScheduler`

**Purpose**: Triggers the automation at optimal Pinterest posting times.

#### Configuration

| Field | Value | Notes |
|-------|-------|-------|
| Interval | Custom | Use specific times for best engagement |
| Run scenario | At specific days and times | |
| Days | Every day | Or select specific days |
| Times | 06:00, 12:00, 18:00, 21:00 | PST timezone (Pinterest optimal times) |
| Time zone | America/Los_Angeles | Match your target audience |

#### JSON Configuration

```json
{
  "schedule": {
    "type": "custom",
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    "times": [
      { "hour": 6, "minute": 0 },
      { "hour": 12, "minute": 0 },
      { "hour": 18, "minute": 0 },
      { "hour": 21, "minute": 0 }
    ],
    "timezone": "America/Los_Angeles"
  }
}
```

#### Error Handling Settings

| Setting | Value |
|---------|-------|
| Continue on error | No |
| Sequential processing | Yes |

---

### Module 2: Set Variables

**Module Type**: `builtin:SetVariables`

**Purpose**: Initialize brand configuration and content parameters for the current run.

#### Configuration

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `brand` | Select from array iterator or random | Current brand to post for |
| `brand_config` | JSON object | Brand-specific settings |
| `posting_time` | `{{now}}` | Current timestamp |
| `content_type` | `"value_pin"` | Type identifier |

#### Variable Definitions

```json
{
  "variables": [
    {
      "name": "brands_config",
      "value": {
        "daily_deal_darling": {
          "name": "Daily Deal Darling",
          "board_id": "daily-deal-darling-tips",
          "niche": "lifestyle deals, beauty finds, home organization",
          "tone": "friendly, excited, relatable",
          "audience": "budget-conscious women 25-45",
          "hashtags": ["deals", "amazonfinds", "budgetfriendly", "lifehacks", "musthaves"],
          "colors": {
            "primary": "#E91E63",
            "secondary": "#FFC107",
            "text": "#FFFFFF"
          }
        },
        "menopause_planner": {
          "name": "Menopause Planner",
          "board_id": "menopause-wellness-tips",
          "niche": "menopause wellness, hormone health, midlife thriving",
          "tone": "supportive, knowledgeable, empowering",
          "audience": "women 45-60 experiencing perimenopause/menopause",
          "hashtags": ["menopause", "perimenopause", "midlifewellness", "hormonehealth", "over50"],
          "colors": {
            "primary": "#9C27B0",
            "secondary": "#E1BEE7",
            "text": "#FFFFFF"
          }
        },
        "nurse_planner": {
          "name": "Nurse Planner",
          "board_id": "nurse-life-tips",
          "niche": "nurse lifestyle, healthcare organization, self-care for nurses",
          "tone": "understanding, practical, encouraging",
          "audience": "nurses and healthcare workers",
          "hashtags": ["nurselife", "nursesofinstagram", "healthcareworker", "nursetips", "rn"],
          "colors": {
            "primary": "#00BCD4",
            "secondary": "#B2EBF2",
            "text": "#FFFFFF"
          }
        },
        "adhd_planner": {
          "name": "ADHD Planner",
          "board_id": "adhd-productivity-tips",
          "niche": "ADHD management, productivity, executive function support",
          "tone": "understanding, non-judgmental, practical",
          "audience": "adults with ADHD seeking organization strategies",
          "hashtags": ["adhd", "adhdtips", "adultadhd", "adhdbrain", "executivefunction"],
          "colors": {
            "primary": "#FF9800",
            "secondary": "#FFE0B2",
            "text": "#212121"
          }
        }
      }
    },
    {
      "name": "current_brand",
      "value": "{{brands_config.keys[mod(floor(timestamp / 21600), 4)]}}"
    }
  ]
}
```

#### Mapping Notes

- Use `{{now}}` for current timestamp
- Use iterator modules to cycle through brands
- Access nested values with dot notation: `{{brands_config.daily_deal_darling.board_id}}`

---

### Module 3: Claude API (Content Generation)

**Module Type**: `http:MakeRequest`

**Purpose**: Generate Pinterest-optimized content using Claude AI.

#### Connection Setup

1. Go to **Connections** in Make.com
2. Click **Add** > **HTTP** > **API Key Authentication**
3. Configure:
   - Name: `Anthropic Claude API`
   - API Key Location: Header
   - Header Name: `x-api-key`
   - API Key: `[Your Anthropic API Key]`

#### HTTP Request Configuration

| Field | Value |
|-------|-------|
| URL | `https://api.anthropic.com/v1/messages` |
| Method | POST |
| Headers | See below |
| Body Type | Raw (JSON) |

#### Headers

```json
{
  "anthropic-version": "2023-06-01",
  "content-type": "application/json"
}
```

#### Request Body

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "Create a Pinterest value pin for {{2.current_brand_config.name}}.\n\nBrand Niche: {{2.current_brand_config.niche}}\nTarget Audience: {{2.current_brand_config.audience}}\nTone: {{2.current_brand_config.tone}}\n\nGenerate content with:\n1. A scroll-stopping hook/title (max 100 characters)\n2. 3 valuable tips or points (each 1-2 sentences)\n3. A clear call-to-action\n4. 5 relevant hashtags\n5. A search query for finding a relevant stock photo\n\nReturn as JSON:\n{\n  \"title\": \"...\",\n  \"hook\": \"...\",\n  \"tips\": [\"tip1\", \"tip2\", \"tip3\"],\n  \"cta\": \"...\",\n  \"hashtags\": [\"#tag1\", \"#tag2\", \"#tag3\", \"#tag4\", \"#tag5\"],\n  \"image_search_query\": \"...\"\n}"
    }
  ]
}
```

#### Response Mapping

| Output Variable | JSON Path | Description |
|----------------|-----------|-------------|
| `generated_content` | `$.content[0].text` | Raw JSON string from Claude |
| `content_parsed` | Parse JSON of above | Structured content object |

#### Parse JSON Module (Add after HTTP)

**Module Type**: `json:ParseJSON`

| Field | Value |
|-------|-------|
| JSON string | `{{3.data.content[0].text}}` |

#### Error Handling Settings

| Setting | Value |
|---------|-------|
| Continue on error | Yes |
| Number of retries | 3 |
| Delay between retries | 10 seconds |

---

### Module 4: Pexels API (Image Search)

**Module Type**: `http:MakeRequest`

**Purpose**: Fetch relevant stock images for the pin.

#### Connection Setup

1. **Connection Name**: `Pexels API`
2. **Type**: API Key in Header
3. **Header Name**: `Authorization`
4. **Value**: `[Your Pexels API Key]`

#### HTTP Request Configuration

| Field | Value |
|-------|-------|
| URL | `https://api.pexels.com/v1/search` |
| Method | GET |
| Query String | See below |

#### Query String Parameters

| Parameter | Value | Mapping |
|-----------|-------|---------|
| query | `{{4.content_parsed.image_search_query}}` | From Claude response |
| orientation | `portrait` | Pinterest optimal |
| per_page | `3` | Options to choose from |
| size | `large` | High quality |

#### Full URL with Parameters

```
https://api.pexels.com/v1/search?query={{encodeURL(4.content_parsed.image_search_query)}}&orientation=portrait&per_page=3&size=large
```

#### Response Mapping

| Output Variable | JSON Path | Description |
|----------------|-----------|-------------|
| `image_url` | `$.photos[0].src.large2x` | High-res image URL |
| `image_id` | `$.photos[0].id` | Pexels image ID |
| `photographer` | `$.photos[0].photographer` | Attribution |

#### Fallback Configuration

If no images found, use brand-specific fallback:

```json
{
  "fallback_images": {
    "daily_deal_darling": "https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg",
    "menopause_planner": "https://images.pexels.com/photos/6787202/pexels-photo-6787202.jpeg",
    "nurse_planner": "https://images.pexels.com/photos/4386467/pexels-photo-4386467.jpeg",
    "adhd_planner": "https://images.pexels.com/photos/6289065/pexels-photo-6289065.jpeg"
  }
}
```

---

### Module 5: Image Resize

**Module Type**: `image:Resize`

**Purpose**: Resize image to Pinterest optimal dimensions (1000x1500px for 2:3 ratio).

#### Configuration

| Field | Value | Notes |
|-------|-------|-------|
| Source file | `{{5.image_url}}` | Download from Pexels URL |
| Width | 1000 | Pinterest recommended |
| Height | 1500 | 2:3 aspect ratio |
| Proportional | Yes | Maintain aspect ratio |
| Fill | Yes | Fill entire canvas |
| Output format | PNG | Best for text overlay |

#### Alternative: Download + Resize Chain

If direct URL resize fails:

1. **HTTP Get Image**: Download to Make.com storage
2. **Image Resize**: Process the downloaded file

```json
{
  "resize_config": {
    "width": 1000,
    "height": 1500,
    "fit": "cover",
    "position": "center",
    "format": "png",
    "quality": 90
  }
}
```

---

### Module 6: Text Overlay Module

**Module Type**: `image:AddText` or Custom HTTP to image processing API

**Purpose**: Add branded text overlays to the image.

#### Option A: Make.com Native Image Module

| Field | Value |
|-------|-------|
| Source image | Output from Module 5 |
| Text | `{{4.content_parsed.title}}` |
| Font | Montserrat Bold |
| Font size | 72 |
| Color | `{{2.current_brand_config.colors.text}}` |
| Position | Center |
| Background | `{{2.current_brand_config.colors.primary}}` with 80% opacity |

#### Option B: Cloudinary API Integration

**Module Type**: `http:MakeRequest`

```json
{
  "url": "https://api.cloudinary.com/v1_1/{{cloudinary_cloud_name}}/image/upload",
  "method": "POST",
  "body": {
    "file": "{{6.image_url}}",
    "upload_preset": "pinterest_pins",
    "transformation": [
      {
        "width": 1000,
        "height": 1500,
        "crop": "fill"
      },
      {
        "overlay": {
          "font_family": "Montserrat",
          "font_size": 60,
          "font_weight": "bold",
          "text": "{{encodeURL(4.content_parsed.title)}}"
        },
        "color": "#FFFFFF",
        "background": "{{2.current_brand_config.colors.primary}}",
        "gravity": "center"
      }
    ]
  }
}
```

#### Text Overlay Positioning Guide

```
┌────────────────────────────┐
│                            │
│   ┌────────────────────┐   │  <- Title Area (top 20%)
│   │    PIN TITLE       │   │     Font: 48-72px, Bold
│   └────────────────────┘   │
│                            │
│   ┌────────────────────┐   │  <- Body Area (middle 50%)
│   │                    │   │     Tips displayed here
│   │    TIP 1           │   │     Font: 32-40px
│   │    TIP 2           │   │
│   │    TIP 3           │   │
│   │                    │   │
│   └────────────────────┘   │
│                            │
│   ┌────────────────────┐   │  <- CTA Area (bottom 20%)
│   │  CALL TO ACTION    │   │     Font: 36px, Brand Color
│   └────────────────────┘   │
│                            │
└────────────────────────────┘
```

---

### Module 7: Pinterest Create Pin

**Module Type**: `pinterest:CreatePin` (Pinterest App Module)

**Purpose**: Post the generated pin to Pinterest.

#### Connection Setup

1. In Make.com, go to **Connections**
2. Click **Add** > **Pinterest**
3. Authorize with your Pinterest Business account
4. Grant required permissions:
   - `boards:read`
   - `boards:write`
   - `pins:read`
   - `pins:write`

#### Module Configuration

| Field | Value | Mapping |
|-------|-------|---------|
| Board | Select or map | `{{2.current_brand_config.board_id}}` |
| Title | Text | `{{4.content_parsed.title}}` |
| Description | Text | See template below |
| Link | URL | `https://{{2.current_brand}}.com?utm_source=pinterest&utm_medium=pin` |
| Media source | File | Output from Module 6 |
| Alt text | Text | `{{4.content_parsed.title}}` |

#### Description Template

```
{{4.content_parsed.hook}}

{{4.content_parsed.tips[0]}}
{{4.content_parsed.tips[1]}}
{{4.content_parsed.tips[2]}}

{{4.content_parsed.cta}}

{{join(4.content_parsed.hashtags, " ")}}
```

#### Alternative: Pinterest API Direct (HTTP Module)

If using the Pinterest API directly:

**Module Type**: `http:MakeRequest`

| Field | Value |
|-------|-------|
| URL | `https://api.pinterest.com/v5/pins` |
| Method | POST |
| Headers | `Authorization: Bearer {{pinterest_access_token}}` |

**Request Body**:

```json
{
  "board_id": "{{2.current_brand_config.board_id}}",
  "title": "{{4.content_parsed.title}}",
  "description": "{{4.content_parsed.hook}}\n\n{{4.content_parsed.tips[0]}}\n{{4.content_parsed.tips[1]}}\n{{4.content_parsed.tips[2]}}\n\n{{4.content_parsed.cta}}\n\n{{join(4.content_parsed.hashtags, ' ')}}",
  "link": "https://{{2.current_brand}}.com?utm_source=pinterest&utm_medium=pin",
  "media_source": {
    "source_type": "image_url",
    "url": "{{7.output_url}}"
  },
  "alt_text": "{{4.content_parsed.title}}"
}
```

#### Response Mapping

| Output Variable | JSON Path | Description |
|----------------|-----------|-------------|
| `pin_id` | `$.id` | Pinterest pin ID |
| `pin_url` | `$.link` | Direct URL to pin |

---

### Module 8: Supabase Logging

**Module Type**: `http:MakeRequest`

**Purpose**: Log the created pin to the database for tracking and analytics.

#### Connection Setup

1. **Connection Name**: `Supabase REST API`
2. **Type**: API Key in Header
3. **Headers**:
   - `apikey`: `[Your Supabase Anon Key]`
   - `Authorization`: `Bearer [Your Supabase Anon Key]`
   - `Content-Type`: `application/json`
   - `Prefer`: `return=representation`

#### HTTP Request Configuration

| Field | Value |
|-------|-------|
| URL | `{{supabase_url}}/rest/v1/videos` |
| Method | POST |
| Body Type | Raw (JSON) |

#### Request Body

```json
{
  "brand": "{{2.current_brand}}",
  "platform": "pinterest",
  "video_url": "{{8.pin_url}}",
  "title": "{{4.content_parsed.title}}",
  "description": "{{4.content_parsed.hook}}",
  "status": "posted",
  "platform_id": "{{8.pin_id}}",
  "created_at": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}"
}
```

#### Response Handling

| Output Variable | JSON Path | Description |
|----------------|-----------|-------------|
| `record_id` | `$[0].id` | Database record ID |

#### Analytics Event Logging (Additional Request)

```json
{
  "url": "{{supabase_url}}/rest/v1/analytics",
  "method": "POST",
  "body": {
    "event_type": "pin_created",
    "brand": "{{2.current_brand}}",
    "platform": "pinterest",
    "data": {
      "pin_id": "{{8.pin_id}}",
      "title": "{{4.content_parsed.title}}",
      "hashtags": "{{4.content_parsed.hashtags}}",
      "image_source": "pexels",
      "image_id": "{{5.image_id}}"
    },
    "created_at": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}"
  }
}
```

---

### Module 9: Error Handling

**Module Type**: `builtin:ErrorHandler` + Router

**Purpose**: Gracefully handle failures and notify on critical errors.

#### Error Handler Configuration

Add error handlers to critical modules (3, 4, 7, 8):

| Module | Error Action | Fallback |
|--------|--------------|----------|
| Claude API | Retry 3x, then use template | Pre-written content bank |
| Pexels API | Retry 2x, then use fallback image | Brand-specific default |
| Pinterest | Log error, retry next schedule | Skip posting |
| Supabase | Log locally, retry later | File-based backup |

#### Router Configuration for Errors

```
[Error Handler]
    │
    ├──▶ [Filter: API Error] ──▶ [Slack Notification]
    │
    ├──▶ [Filter: Rate Limit] ──▶ [Delay + Retry Queue]
    │
    └──▶ [Filter: Other] ──▶ [Email Alert]
```

#### Error Logging Request

**Module Type**: `http:MakeRequest`

```json
{
  "url": "{{supabase_url}}/rest/v1/errors",
  "method": "POST",
  "body": {
    "error_type": "{{error.type}}",
    "error_message": "{{error.message}}",
    "context": {
      "scenario": "value_pins_automation",
      "brand": "{{2.current_brand}}",
      "module": "{{error.module}}",
      "timestamp": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}"
    },
    "resolved": false,
    "created_at": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}"
  }
}
```

#### Slack/Email Notification (Critical Errors)

**Module Type**: `slack:PostMessage` or `email:Send`

```json
{
  "channel": "#social-media-alerts",
  "text": ":warning: Value Pins Automation Error\n*Brand:* {{2.current_brand}}\n*Error:* {{error.message}}\n*Module:* {{error.module}}\n*Time:* {{formatDate(now; 'YYYY-MM-DD HH:mm:ss')}}",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Error Details*\n```{{error.details}}```"
      }
    }
  ]
}
```

---

## Agent 3: Affiliate Publisher

### Scenario Purpose

Automatically publishes affiliate product deals and promotions to Pinterest, including deal tracking and conversion logging.

### Complete Module Chain

```
[1] Webhook/Schedule ──▶ [2] Product Fetch ──▶ [3] Filter Active Deals
                                                       │
        ┌──────────────────────────────────────────────┘
        ▼
[4] Content Generation ──▶ [5] Image Handler ──▶ [6] Pinterest Post
                                                       │
        ┌──────────────────────────────────────────────┘
        ▼
[7] Tracking Update ──▶ [8] Analytics Log ──▶ [9] Error Handler
```

---

### Module 1: Trigger (Schedule or Webhook)

**Module Type**: `builtin:BasicScheduler` OR `builtin:CustomWebhook`

**Purpose**: Trigger scenario either on schedule or via external webhook from the codebase.

#### Option A: Schedule Trigger

| Field | Value | Notes |
|-------|-------|-------|
| Interval | Every 4 hours | Spread throughout day |
| Run scenario | At regular intervals | |
| Start time | 08:00 AM PST | After morning deals drop |

#### Option B: Webhook Trigger

**Webhook URL**: Generated by Make.com when you add the module

**Expected Payload from Codebase**:

```json
{
  "type": "affiliate_pin",
  "brand": "daily_deal_darling",
  "product": {
    "id": "B08XYZ123",
    "name": "Instant Pot Duo 7-in-1",
    "original_price": 89.99,
    "sale_price": 59.99,
    "discount_percent": 33,
    "affiliate_url": "https://amzn.to/abc123",
    "image_url": "https://m.media-amazon.com/images/...",
    "category": "kitchen"
  },
  "urgency": "Deal ends today!"
}
```

#### Webhook Configuration

| Field | Value |
|-------|-------|
| Webhook name | `affiliate-publisher-trigger` |
| Data structure | Create from sample JSON above |
| IP restrictions | Optional: Limit to your server IPs |
| Queue | Enable for high volume |

---

### Module 2: Product/Deal Fetching

**Module Type**: `http:MakeRequest`

**Purpose**: Fetch current deals from affiliate networks or product database.

#### Option A: From Supabase Content Bank

| Field | Value |
|-------|-------|
| URL | `{{supabase_url}}/rest/v1/content_bank` |
| Method | GET |
| Query String | `brand=eq.{{1.brand}}&content_type=eq.deal&used=eq.false&limit=5` |

#### Option B: From Affiliate API (e.g., Amazon Product Advertising API)

| Field | Value |
|-------|-------|
| URL | `https://webservices.amazon.com/paapi5/searchitems` |
| Method | POST |
| Headers | AWS Signature v4 required |

**Request Body**:

```json
{
  "PartnerTag": "{{amazon_associate_tag}}",
  "PartnerType": "Associates",
  "Keywords": "{{1.product.category}} deals",
  "SearchIndex": "All",
  "ItemCount": 5,
  "Resources": [
    "Images.Primary.Large",
    "ItemInfo.Title",
    "Offers.Listings.Price"
  ]
}
```

#### Option C: From Custom Deals Database

| Field | Value |
|-------|-------|
| URL | `https://your-deals-api.com/api/deals` |
| Method | GET |
| Query | `?category={{1.product.category}}&min_discount=20&active=true` |

#### Response Mapping

| Output Variable | JSON Path | Description |
|----------------|-----------|-------------|
| `deals` | `$` or `$.data` | Array of deal objects |
| `deal_count` | `$.length` | Number of deals found |

---

### Module 3: Filter Active Deals (Router/Filter)

**Module Type**: `builtin:BasicRouter` with Filters

**Purpose**: Route only valid, active deals for processing.

#### Filter Conditions

| Filter Name | Condition |
|-------------|-----------|
| Valid Deal | `{{2.deals[].sale_price}} < {{2.deals[].original_price}}` |
| Minimum Discount | `{{2.deals[].discount_percent}} >= 20` |
| Has Image | `{{2.deals[].image_url}} is not empty` |
| Not Expired | `{{2.deals[].expiry_date}} > {{now}}` OR is empty |

#### Iterator Setup

If processing multiple deals:

**Module Type**: `builtin:BasicIterator`

| Field | Value |
|-------|-------|
| Array | `{{2.deals}}` |
| Output | Each deal as separate bundle |

---

### Module 4: Content Generation

**Module Type**: `http:MakeRequest` (Claude API)

**Purpose**: Generate compelling deal-focused Pinterest content.

#### Request Configuration

| Field | Value |
|-------|-------|
| URL | `https://api.anthropic.com/v1/messages` |
| Method | POST |

#### Request Body

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 512,
  "messages": [
    {
      "role": "user",
      "content": "Create a Pinterest deal pin for {{2.current_brand_config.name}}.\n\nProduct: {{3.deal.name}}\nOriginal Price: ${{3.deal.original_price}}\nSale Price: ${{3.deal.sale_price}}\nDiscount: {{3.deal.discount_percent}}% off\nCategory: {{3.deal.category}}\nUrgency: {{1.urgency}}\n\nGenerate:\n1. Attention-grabbing title (max 100 chars, include price or discount)\n2. 3 benefit points for this product\n3. Urgent call-to-action\n4. 5 relevant hashtags\n\nReturn as JSON:\n{\n  \"title\": \"...\",\n  \"benefits\": [\"benefit1\", \"benefit2\", \"benefit3\"],\n  \"cta\": \"...\",\n  \"hashtags\": [\"#deal\", \"#tag2\", ...]\n}"
    }
  ]
}
```

#### Response Parsing

**Module Type**: `json:ParseJSON`

| Field | Value |
|-------|-------|
| JSON string | `{{4.data.content[0].text}}` |

---

### Module 5: Image Handler

**Module Type**: Combination of modules

**Purpose**: Process product image for Pinterest optimization.

#### 5a: Download Product Image

**Module Type**: `http:GetFile`

| Field | Value |
|-------|-------|
| URL | `{{3.deal.image_url}}` |
| Output | Binary data |

#### 5b: Create Deal Graphic

**Module Type**: `image:Composite` or Cloudinary API

**Purpose**: Add deal badge, price overlay, and branding.

```json
{
  "cloudinary_transformation": {
    "width": 1000,
    "height": 1500,
    "crop": "pad",
    "background": "#FFFFFF",
    "layers": [
      {
        "type": "image",
        "public_id": "{{upload_product_image_result}}",
        "width": 800,
        "crop": "fit",
        "gravity": "center",
        "y": -100
      },
      {
        "type": "text",
        "text": "{{3.deal.discount_percent}}% OFF",
        "font_family": "Arial",
        "font_size": 60,
        "font_weight": "bold",
        "color": "#FF0000",
        "background": "#FFFF00",
        "gravity": "north_east",
        "x": 20,
        "y": 20
      },
      {
        "type": "text",
        "text": "Was ${{3.deal.original_price}}",
        "font_family": "Arial",
        "font_size": 36,
        "color": "#999999",
        "text_decoration": "strikethrough",
        "gravity": "south",
        "y": 200
      },
      {
        "type": "text",
        "text": "NOW ${{3.deal.sale_price}}",
        "font_family": "Arial",
        "font_size": 72,
        "font_weight": "bold",
        "color": "#E91E63",
        "gravity": "south",
        "y": 120
      }
    ]
  }
}
```

#### Deal Badge Positioning

```
┌────────────────────────────┐
│  ┌─────────┐               │
│  │ 33% OFF │               │  <- Deal Badge (top-right)
│  └─────────┘               │
│                            │
│     ┌──────────────┐       │
│     │              │       │
│     │   PRODUCT    │       │  <- Product Image (centered)
│     │    IMAGE     │       │
│     │              │       │
│     └──────────────┘       │
│                            │
│     Was $89.99             │  <- Original Price (strikethrough)
│     NOW $59.99             │  <- Sale Price (prominent)
│                            │
│   [ SHOP NOW ]             │  <- CTA Button
│                            │
└────────────────────────────┘
```

---

### Module 6: Pinterest Posting

**Module Type**: `pinterest:CreatePin`

**Purpose**: Post the deal pin with affiliate link.

#### Configuration

| Field | Value | Mapping |
|-------|-------|---------|
| Board | Deal-specific board | `{{2.current_brand_config.deal_board_id}}` |
| Title | From content gen | `{{4.parsed_content.title}}` |
| Description | See template | Multi-line with benefits |
| Link | Affiliate URL | `{{3.deal.affiliate_url}}` |
| Media | Processed image | Output from Module 5 |
| Alt text | Product name | `{{3.deal.name}} - {{3.deal.discount_percent}}% off` |

#### Description Template for Deals

```
{{4.parsed_content.title}}

{{4.parsed_content.benefits[0]}}
{{4.parsed_content.benefits[1]}}
{{4.parsed_content.benefits[2]}}

Was: ${{3.deal.original_price}}
NOW: ${{3.deal.sale_price}} ({{3.deal.discount_percent}}% OFF!)

{{1.urgency}}

{{4.parsed_content.cta}}

{{join(4.parsed_content.hashtags, " ")}}
```

#### Affiliate Link with UTM Parameters

```
{{3.deal.affiliate_url}}?utm_source=pinterest&utm_medium=pin&utm_campaign={{2.current_brand}}_deals&utm_content={{3.deal.id}}
```

---

### Module 7: Tracking Update

**Module Type**: `http:MakeRequest`

**Purpose**: Mark deal as used and log posting details.

#### Update Content Bank (Mark as Used)

| Field | Value |
|-------|-------|
| URL | `{{supabase_url}}/rest/v1/content_bank?id=eq.{{3.deal.id}}` |
| Method | PATCH |

**Request Body**:

```json
{
  "used": true,
  "used_at": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}",
  "details": {
    "pinterest_pin_id": "{{6.pin_id}}",
    "pinterest_url": "{{6.pin_url}}",
    "posted_by": "affiliate_publisher_scenario"
  }
}
```

#### Create Tracking Record

| Field | Value |
|-------|-------|
| URL | `{{supabase_url}}/rest/v1/affiliate_tracking` |
| Method | POST |

**Request Body**:

```json
{
  "deal_id": "{{3.deal.id}}",
  "product_id": "{{3.deal.product_id}}",
  "brand": "{{2.current_brand}}",
  "platform": "pinterest",
  "pin_id": "{{6.pin_id}}",
  "affiliate_url": "{{3.deal.affiliate_url}}",
  "original_price": {{3.deal.original_price}},
  "sale_price": {{3.deal.sale_price}},
  "discount_percent": {{3.deal.discount_percent}},
  "posted_at": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}",
  "clicks": 0,
  "conversions": 0
}
```

---

### Module 8: Analytics Logging

**Module Type**: `http:MakeRequest`

**Purpose**: Log detailed analytics for performance tracking.

#### Request Configuration

| Field | Value |
|-------|-------|
| URL | `{{supabase_url}}/rest/v1/analytics` |
| Method | POST |

**Request Body**:

```json
{
  "event_type": "affiliate_pin_created",
  "brand": "{{2.current_brand}}",
  "platform": "pinterest",
  "data": {
    "pin_id": "{{6.pin_id}}",
    "deal_id": "{{3.deal.id}}",
    "product_name": "{{3.deal.name}}",
    "category": "{{3.deal.category}}",
    "discount_percent": {{3.deal.discount_percent}},
    "sale_price": {{3.deal.sale_price}},
    "content_generated": {
      "title": "{{4.parsed_content.title}}",
      "cta": "{{4.parsed_content.cta}}"
    },
    "processing_time_ms": "{{executionTime}}"
  },
  "created_at": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}"
}
```

---

### Module 9: Error Handling

**Module Type**: `builtin:ErrorHandler` + Router

Similar to Agent 2, with additional deal-specific handling:

#### Deal-Specific Error Cases

| Error Type | Handling |
|------------|----------|
| Product image unavailable | Use fallback category image |
| Affiliate link expired | Skip and mark as expired |
| Pinterest API rate limit | Queue for retry in 1 hour |
| Invalid price data | Log and skip |

#### Error Notification for Affiliate Issues

```json
{
  "slack_message": {
    "channel": "#affiliate-alerts",
    "blocks": [
      {
        "type": "header",
        "text": {
          "type": "plain_text",
          "text": ":rotating_light: Affiliate Publisher Error"
        }
      },
      {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": "*Deal ID:*\n{{3.deal.id}}"
          },
          {
            "type": "mrkdwn",
            "text": "*Product:*\n{{3.deal.name}}"
          },
          {
            "type": "mrkdwn",
            "text": "*Error:*\n{{error.message}}"
          },
          {
            "type": "mrkdwn",
            "text": "*Module:*\n{{error.module}}"
          }
        ]
      }
    ]
  }
}
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Claude API Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid API key | Verify key in Make.com connection |
| 429 Rate Limited | Too many requests | Add delays between requests |
| 500 Server Error | API issue | Retry with exponential backoff |
| Invalid JSON response | Prompt issue | Improve prompt structure |

**Debug Tip**: Add a `json:ParseJSON` module with error handling to catch malformed responses.

#### 2. Pexels API Issues

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid key | Check Authorization header format |
| No results | Query too specific | Broaden search terms |
| Rate limited | 200/hour exceeded | Implement caching or fallbacks |

**Fallback Strategy**:
```json
{
  "if_no_results": {
    "use_fallback_image": true,
    "fallback_by_brand": {
      "daily_deal_darling": "https://...",
      "menopause_planner": "https://...",
      "nurse_planner": "https://...",
      "adhd_planner": "https://..."
    }
  }
}
```

#### 3. Pinterest API Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Token expired | Refresh OAuth token |
| 403 Forbidden | Board access issue | Verify board ownership |
| 429 Rate Limited | Too many pins | Space out posting times |
| Image too small | Below minimum | Ensure 600x900px minimum |

**Token Refresh Flow**:
1. Add scheduled scenario to refresh tokens
2. Store tokens in Make.com data store
3. Update connection before it expires

#### 4. Supabase Connection Issues

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid API key | Wrong key type | Use anon key for REST API |
| 404 Not Found | Wrong table name | Verify table exists |
| 403 RLS error | Policy issue | Check RLS policies |

#### 5. Image Processing Failures

| Error | Cause | Solution |
|-------|-------|----------|
| Timeout | Large image | Resize before processing |
| Format error | Unsupported format | Convert to PNG/JPEG |
| Memory limit | Image too large | Compress first |

---

### Debug Mode Setup

Add these modules for debugging:

#### 1. Execution Logger

**Module Type**: `tools:SetVariable`

```json
{
  "debug_log": {
    "timestamp": "{{now}}",
    "scenario": "{{scenario.name}}",
    "execution_id": "{{execution.id}}",
    "modules_executed": [],
    "data_flow": {}
  }
}
```

#### 2. Data Inspector

After each critical module, add:

**Module Type**: `http:MakeRequest` (to logging service)

```json
{
  "url": "https://your-logging-service.com/debug",
  "method": "POST",
  "body": {
    "module": "{{previous_module_name}}",
    "output": "{{previous_module_output}}",
    "timestamp": "{{now}}"
  }
}
```

---

## Testing Procedures

### Pre-Deployment Checklist

- [ ] All API connections verified
- [ ] Test with single brand first
- [ ] Verify Pinterest board IDs exist
- [ ] Confirm Supabase tables are created
- [ ] Test error handling paths
- [ ] Verify image dimensions
- [ ] Check rate limit compliance

### Step-by-Step Testing

#### Test 1: Connection Verification

1. Create a simple test scenario with just the HTTP modules
2. Test each API connection individually
3. Verify responses match expected format

#### Test 2: Content Generation

1. Run Claude module with sample input
2. Verify JSON output parses correctly
3. Check content quality and formatting

#### Test 3: Image Pipeline

1. Test Pexels search with known query
2. Verify image download works
3. Test resize and text overlay
4. Confirm output dimensions (1000x1500)

#### Test 4: Pinterest Posting

1. Use Pinterest sandbox/test board first
2. Post a single test pin
3. Verify all fields appear correctly
4. Check affiliate link works

#### Test 5: Database Logging

1. Verify Supabase insert succeeds
2. Check all fields populated
3. Query back to confirm data

#### Test 6: Error Handling

1. Intentionally trigger errors
2. Verify error handlers catch them
3. Confirm notifications sent
4. Check error logs in database

### Test Data Samples

#### Sample Value Pin Input

```json
{
  "brand": "daily_deal_darling",
  "content_type": "value_pin",
  "test_mode": true
}
```

#### Sample Affiliate Deal Input

```json
{
  "type": "affiliate_pin",
  "brand": "daily_deal_darling",
  "product": {
    "id": "TEST-001",
    "name": "Test Product - Wireless Earbuds",
    "original_price": 49.99,
    "sale_price": 29.99,
    "discount_percent": 40,
    "affiliate_url": "https://example.com/test",
    "image_url": "https://via.placeholder.com/800x800",
    "category": "electronics"
  },
  "urgency": "TEST - Deal ends soon!"
}
```

---

## Scenario Export/Import

### Exporting Scenarios

1. Open the scenario in Make.com
2. Click the **three dots** menu (top right)
3. Select **Export Blueprint**
4. Save the JSON file

### Blueprint JSON Structure

```json
{
  "name": "Value Pins Automation",
  "flow": [
    {
      "id": 1,
      "module": "builtin:BasicScheduler",
      "version": 1,
      "parameters": {},
      "mapper": {},
      "metadata": {}
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": {},
    "designer": {}
  }
}
```

### Importing Scenarios

1. Create a new scenario in Make.com
2. Click the **three dots** menu
3. Select **Import Blueprint**
4. Upload the JSON file
5. **IMPORTANT**: Update all connections after import

### Post-Import Checklist

- [ ] Reconnect all API connections
- [ ] Update webhook URLs
- [ ] Verify environment-specific values
- [ ] Update Supabase URLs
- [ ] Re-authorize Pinterest
- [ ] Test with dry run

### Version Control Best Practices

1. Export blueprints after significant changes
2. Store in git repository: `/make-blueprints/`
3. Name with version: `value-pins-v2.3.json`
4. Document changes in commit message

---

## Appendix: Complete Field Mapping Reference

### Agent 2 (Value Pins) Data Flow

```
Module 1 (Schedule)
    └── {{1.timestamp}} ──▶ Module 2

Module 2 (Variables)
    ├── {{2.current_brand}} ──▶ Modules 3, 7, 8
    ├── {{2.current_brand_config}} ──▶ Modules 3, 6, 7
    └── {{2.brands_config}} ──▶ Reference only

Module 3 (Claude API)
    └── {{3.data.content[0].text}} ──▶ Module 4 (Parse JSON)

Module 4 (Parse JSON)
    ├── {{4.content_parsed.title}} ──▶ Modules 6, 7
    ├── {{4.content_parsed.tips}} ──▶ Module 7
    ├── {{4.content_parsed.cta}} ──▶ Module 7
    ├── {{4.content_parsed.hashtags}} ──▶ Module 7
    └── {{4.content_parsed.image_search_query}} ──▶ Module 5

Module 5 (Pexels)
    ├── {{5.photos[0].src.large2x}} ──▶ Module 6
    └── {{5.photos[0].id}} ──▶ Module 8

Module 6 (Image Process)
    └── {{6.output_url}} ──▶ Module 7

Module 7 (Pinterest)
    ├── {{7.id}} ──▶ Module 8
    └── {{7.link}} ──▶ Module 8

Module 8 (Supabase)
    └── {{8.id}} ──▶ Confirmation/Analytics
```

### Agent 3 (Affiliate) Data Flow

```
Module 1 (Trigger)
    ├── {{1.brand}} ──▶ Modules 2, 4, 7, 8
    ├── {{1.product}} ──▶ Module 2 (if webhook)
    └── {{1.urgency}} ──▶ Module 4

Module 2 (Product Fetch)
    └── {{2.deals}} ──▶ Module 3

Module 3 (Iterator/Filter)
    ├── {{3.deal.id}} ──▶ Modules 5, 7, 8
    ├── {{3.deal.name}} ──▶ Modules 4, 6, 8
    ├── {{3.deal.original_price}} ──▶ Modules 4, 5, 6
    ├── {{3.deal.sale_price}} ──▶ Modules 4, 5, 6, 7
    ├── {{3.deal.discount_percent}} ──▶ Modules 4, 5, 6, 7
    ├── {{3.deal.image_url}} ──▶ Module 5
    └── {{3.deal.affiliate_url}} ──▶ Modules 6, 7

Module 4 (Content Gen)
    └── {{4.parsed_content}} ──▶ Module 6
        ├── .title
        ├── .benefits[]
        ├── .cta
        └── .hashtags[]

Module 5 (Image Handler)
    └── {{5.processed_image_url}} ──▶ Module 6

Module 6 (Pinterest)
    ├── {{6.pin_id}} ──▶ Modules 7, 8
    └── {{6.pin_url}} ──▶ Modules 7, 8

Module 7 (Tracking)
    └── {{7.tracking_id}} ──▶ Module 8

Module 8 (Analytics)
    └── Final confirmation
```

---

## Quick Reference: Make.com Function Syntax

| Function | Example | Output |
|----------|---------|--------|
| Date format | `{{formatDate(now; "YYYY-MM-DD")}}` | 2025-01-15 |
| Join array | `{{join(array; " ")}}` | item1 item2 item3 |
| URL encode | `{{encodeURL(text)}}` | hello%20world |
| If/else | `{{if(condition; true_val; false_val)}}` | Conditional value |
| Math | `{{1.price * 0.9}}` | Calculated value |
| Length | `{{length(array)}}` | Number |
| First/Last | `{{first(array)}}` / `{{last(array)}}` | Element |
| Substring | `{{substring(text; 0; 100)}}` | Truncated text |
| Replace | `{{replace(text; "old"; "new")}}` | Modified text |
| Lower/Upper | `{{lower(text)}}` / `{{upper(text)}}` | Case changed |

---

*Last Updated: 2025-01-27*
*Version: 2.0*
*Maintained by: Social Media Empire Team*
