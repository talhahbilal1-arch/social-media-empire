# Pexels Image Selection System

## Why Pexels (Not Unsplash or DALL-E)

- **Free API** — unlimited requests on free tier
- **High-quality lifestyle photography** — real people, real situations
- **No banned images** — all images are properly licensed for commercial use
- **Consistent quality** — curated by Pexels staff, not random uploads
- **Searchable by concept** — finds relevant images without exact file matching

DALL-E generated images don't perform well on Pinterest (they look AI-generated).
Real photography converts significantly better.

---

## Getting Your Pexels API Key

1. Go to pexels.com
2. Join (free) → Your profile → **Pexels API**
3. Apply for API access (instant approval for legitimate use cases)
4. Copy your API key
5. Add as GitHub Secret: `PEXELS_API_KEY`

---

## How the Image Selection Works

The system:
1. Takes the `image_query` field from the Claude-generated pin content
2. Queries Pexels API with that query + orientation=portrait
3. Gets back up to 15 results
4. Filters out images used in the last 25 pins (stored in `recent_image_queries`)
5. Selects a unique image
6. Downloads it temporarily
7. Renders the text overlay on it
8. Uploads the result to Supabase Storage

---

## Writing Effective Image Queries

**The quality of your image query determines the quality of your pin visual.**

### Good vs. Bad Queries

| Bad Query | Good Query | Why |
|-----------|-----------|-----|
| "fitness" | "athletic man over 35 lifting weights gym" | Specific person, action, setting |
| "health" | "meal prep containers healthy food kitchen" | Concrete objects and context |
| "success" | "man working at standing desk home office" | Real scene, not abstract concept |
| "food" | "grilled salmon vegetables plate dinner" | Specific food, presentation context |
| "workout" | "man doing pull-ups outdoor fitness bar morning" | Action, location, time of day |

### Image Query Formula

`[Person/Object] + [Action/State] + [Setting/Context] + [Optional: mood/time]`

Examples:
- `"man over 40 strength training barbell gym"`
- `"meal prep bowls vegetables protein kitchen counter"`
- `"man sleeping peaceful bedroom night recovery"`
- `"testosterone supplements vitamins wooden table"`
- `"older man running trail morning outdoor fitness"`

### Queries to Avoid

- Abstract concepts: "success", "motivation", "health"
- Celebrity names or brand names
- Anything involving minors
- Anything with visible text (will conflict with your overlay)
- Extremely dark or bright images (ruins text overlay readability)

---

## Orientation and Size

Pinterest pins are **1000×1500px (portrait, 2:3 ratio)**.

In your Pexels API call, always specify:
```python
params = {
    "query": image_query,
    "orientation": "portrait",  # Critical for pin format
    "size": "large",
    "per_page": 15
}
```

The `large` size gives you images at least 940px wide — enough to scale to 1000px
without pixelation.

---

## Python Code for Image Selection

```python
import requests
import random

def get_pexels_image(query: str, recent_queries: list, api_key: str) -> dict:
    """
    Fetch a unique Pexels image for a given query.
    Avoids images with queries used in the last 25 pins.
    Returns the image data dict or None if not found.
    """
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "orientation": "portrait",
        "size": "large",
        "per_page": 15
    }

    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers=headers,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        return None

    photos = response.json().get("photos", [])
    if not photos:
        return None

    # Filter out recently used images (by checking description/alt in recent)
    available = [p for p in photos if p.get("alt", "") not in recent_queries]
    if not available:
        available = photos  # Reset if all used

    selected = random.choice(available)
    return {
        "url": selected["src"]["large"],
        "alt": selected.get("alt", query),
        "photographer": selected.get("photographer", ""),
        "pexels_id": selected["id"]
    }
```

---

## The 5 PIL Text Overlay Styles

The system renders text on top of Pexels images using Python PIL.
Each style is optimized for different content types.

### Style 1: Gradient (Most Used)
- Black gradient covering bottom 60% of image
- Large white bold title text centered
- Subtitle in smaller text below
- Brand color accent line at bottom
- **Best for:** General content, clean look
- **Title position:** Bottom third

### Style 2: Box Dark
- Semi-transparent dark box in center of image
- Title centered in box
- Tips listed inside box
- **Best for:** List content, numbered tips
- **Background shows:** Around the box

### Style 3: Numbered List
- Numbered circles (1, 2, 3) on left side
- Text for each item to the right
- Bottom fades out with "...and X more"
- **Best for:** Listicle pins ("5 reasons...")
- **Creates:** Strong curiosity gap

### Style 4: Big Stat
- Giant number/percentage takes 40% of frame
- Supporting text below
- Clean, minimal background overlay
- **Best for:** Data-driven content ("87%", "3x faster", "14 lbs")

### Style 5: Split Layout
- Top 60%: Pexels image (uncovered)
- Bottom 40%: Solid brand-color block
- Title text in the color block
- **Best for:** Lifestyle photography pins

---

## Supabase Storage Setup

Images are uploaded to Supabase Storage before posting.

### Create the Bucket
1. Supabase Dashboard → Storage → New Bucket
2. Name: `pin-images`
3. Set to **Public** (so Make.com can access the URL)
4. Under bucket settings: disable RLS (Row Level Security)

### Python Upload Code
```python
import base64
import requests

def upload_to_supabase(image_bytes: bytes, filename: str,
                        supabase_url: str, supabase_key: str) -> str:
    """
    Upload image bytes to Supabase Storage.
    Returns the public URL.
    """
    upload_url = f"{supabase_url}/storage/v1/object/pin-images/{filename}"

    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "image/jpeg",
    }

    response = requests.post(upload_url, headers=headers, data=image_bytes)

    if response.status_code in (200, 201):
        return f"{supabase_url}/storage/v1/object/public/pin-images/{filename}"
    else:
        raise Exception(f"Upload failed: {response.status_code} {response.text}")
```

### Auto-Cleanup Old Images
To keep storage under the free limit, delete images older than 7 days:
```sql
-- Run in Supabase SQL Editor as a scheduled function
DELETE FROM storage.objects
WHERE bucket_id = 'pin-images'
AND created_at < now() - interval '7 days';
```

---

## Fitness Brand Specific: Male-Only Images

For the men over 35 fitness niche, the system enforces male-only image queries.
This matters because Pexels returns mixed results for "fitness" queries.

**Add these modifiers to ensure male representation:**
- "man" or "male" or "men"
- "athletic man", "fit man", "older man"
- Avoid: "woman", "lady", "female fitness"

**Sample queries that reliably return male fitness images:**
- `"athletic man gym barbell workout"`
- `"man over 40 running outdoor morning"`
- `"male fitness protein shake kitchen"`
- `"man doing push-ups floor home workout"`
- `"older man swimming pool fitness"`
