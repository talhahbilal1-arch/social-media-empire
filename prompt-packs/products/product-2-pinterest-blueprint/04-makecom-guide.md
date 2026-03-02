# Make.com Setup Guide — Pinterest Automation

## What Make.com Does in This System

Make.com acts as the bridge between your Python script and Pinterest.
Your script sends a webhook (a JSON payload with all pin details).
Make.com receives it, processes it, and posts to Pinterest via the official API.

Why not post directly from Python? Pinterest's API requires OAuth which is complex
to maintain in automation. Make.com handles the authentication refreshing automatically.

---

## Step 1: Create a Make.com Account

1. Go to make.com → Sign Up
2. Free tier allows 1,000 operations/month (enough for 30+ pins/day)
3. Select your timezone (important for scheduling)

---

## Step 2: Create a New Scenario

1. Dashboard → **Create a new scenario**
2. Name it: "Pinterest Pin Publisher — [Your Brand]"
3. You'll see an empty canvas

---

## Step 3: Add a Webhook Trigger

1. Click the **+** (first module) → Search for **Webhooks**
2. Select **Custom webhook**
3. Click **Add** → name it "[Brand] Pin Webhook"
4. Copy the webhook URL — you'll need this for your GitHub Secret
5. Click **OK**

Your webhook URL looks like: `https://hook.us2.make.com/xxxxxxxxxxxxxxxxxxxx`

**Save this URL.** It goes into your GitHub Secrets as `MAKE_WEBHOOK_FITNESS` (or whichever brand).

---

## Step 4: Add a Pinterest Module

1. Click **+** after the webhook module
2. Search for **Pinterest**
3. Select **Create a Pin**
4. Connect your Pinterest Business Account (OAuth popup — authorize it)

---

## Step 5: Map the Webhook Fields to Pinterest

In the Pinterest "Create a Pin" module, map these fields:

| Pinterest Field | Webhook Field |
|----------------|---------------|
| Board ID | `{{1.board_id}}` |
| Image URL | `{{1.image_url}}` |
| Title | `{{1.title}}` |
| Description | `{{1.description}}` |
| Link (destination URL) | `{{1.destination_url}}` |

**Note on Board ID:** You need your actual Pinterest board IDs (numeric, 18-19 digits).
See the Board ID section below for how to find them.

---

## Step 6: Test the Scenario

1. Turn on the scenario (top-right toggle)
2. Open a terminal and run a test webhook:

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "your-brand",
    "title": "Test Pin Title",
    "description": "Test description #test",
    "image_url": "https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg",
    "board_id": "YOUR_BOARD_ID",
    "destination_url": "https://yoursite.com"
  }'
```

3. In Make.com → click **Run once**
4. Check if the pin appeared on Pinterest

---

## Finding Your Pinterest Board IDs

Pinterest doesn't show board IDs in the UI easily. Two methods:

**Method 1: Pinterest API**
```bash
curl -H "Authorization: Bearer YOUR_PINTEREST_ACCESS_TOKEN" \
  "https://api.pinterest.com/v5/boards?page_size=25"
```
This returns all boards with their IDs.

**Method 2: Browser Dev Tools**
1. Go to Pinterest → Your profile → Click a board
2. Open Dev Tools (F12) → Network tab
3. Refresh the page
4. Find a request to `api.pinterest.com` — the board ID is in the URL

**Method 3: Make.com RPC**
1. In Make.com scenario, add Pinterest module → "List Boards"
2. Run it once — returns all board IDs
3. Copy the IDs you need

---

## Multi-Brand Setup (Multiple Scenarios)

For multiple brands, you have two options:

**Option A: One scenario per brand (Recommended for beginners)**
- Create 3 separate scenarios
- Each has its own webhook URL
- Each connects to a different Pinterest account
- Simple to debug, no routing logic needed

**Option B: One scenario, routing by brand field**
- One webhook URL
- Add a Router module after the webhook
- Route 1: filter on `brand = "fitness-made-easy"` → Pinterest Account 1
- Route 2: filter on `brand = "daily-deal-darling"` → Pinterest Account 2
- Route 3: filter on `brand = "menopause-planner"` → Pinterest Account 3
- More complex but one URL to manage

---

## Error Handling in Make.com

Add error handling so failed pins get retried:

1. Right-click on the Pinterest module → **Add error handler**
2. Select **Break** (pauses scenario on error, logs it)
3. In Make.com → History tab, you can see failed runs and retry them

Or create a retry scenario:
1. New scenario: Supabase → filter `status = "failed"` → Pinterest
2. Schedule it every 6 hours
3. Re-posts any pins that failed

---

## Webhook Security (Optional but Recommended)

By default, your webhook URL is public — anyone who knows it can trigger your scenario.
To add basic security:

1. In Make.com → Webhook settings → **IP Restriction**
2. Add GitHub's IP ranges (available at api.github.com/meta)

Or add a secret header:
1. Your Python script sends: `headers={"X-Webhook-Secret": "your-secret"}`
2. Make.com → Webhook → check for this header before processing

---

## Make.com Operations Budget

Free tier: 1,000 operations/month
Each pin post = 1 operation

1 brand × 5 pins/day × 30 days = 150 operations
3 brands × 5 pins/day × 30 days = 450 operations

You stay well within the free tier for 3 brands.

Paid tier (Core, $9/month) = 10,000 operations — needed if scaling to 10+ brands.

---

## Common Make.com Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Pinterest token expired | Re-connect Pinterest account in Make.com |
| 422 Unprocessable | Board ID invalid | Verify board ID using API method above |
| 400 Bad Request | Image URL unreachable | Ensure image URL is publicly accessible |
| Webhook timeout | Payload too large | Keep image URLs under 2000 chars |
| Scenario paused | Operations limit hit | Upgrade tier or wait until monthly reset |
