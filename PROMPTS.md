# Saved Prompts for Social Media Content Empire

## 1. Start of Session (Use this every time you come back)

Read CLAUDE.md, tasks/todo.md, and README.md. Tell me where we left off and what's next.


## 2. End of Session (Use this before logging off)

Update tasks/todo.md with everything we did today and what's next. Push to GitHub.


## 3. Enable Chrome Browser (Use when you need browser automation)

/chrome


## 4. Full Context Reload (Use if Claude seems confused about the project)

Read the README.md and CLAUDE.md files in this folder. This is my Social Media Content Empire - autonomous agents that post content 24/7 to Pinterest, TikTok, Instagram, YouTube for my brands Daily Deal Darling and The Menopause Planner.

Tech stack: GitHub Actions (runs agents), Supabase (database), Claude API (content), Creatomate (videos), Make.com (TikTok/Instagram posting).

GitHub repo: https://github.com/talhahbilal1-arch/social-media-empire
Supabase project: epfoxpgrpsnhlsglxvsa

Check tasks/todo.md for current status and tell me what's next.


## 5. Run Full Setup (Use to complete initial setup)

Execute the setup steps using Chrome:
1. Go to https://supabase.com/dashboard - Open project epfoxpgrpsnhlsglxvsa - Go to SQL Editor - Paste and run database/schema.sql
2. In Supabase Settings → API - Copy Project URL and anon key
3. Go to https://console.anthropic.com/settings/keys - Create new API key
4. Go to https://github.com/talhahbilal1-arch/social-media-empire/settings/secrets/actions - Add SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY
5. Go to GitHub Actions and enable workflows
6. Test Health Monitor workflow

You have full permission to access all sites.


## 6. Create Make.com Scenarios (Use after setup is complete)

Create the Make.com scenario instructions for posting to TikTok and Instagram. The scenarios should:
- Pull pending content from Supabase (status = 'ready' or 'video_ready')
- Post to TikTok and Instagram Reels
- Update status to 'posted' in Supabase after posting
- Log platform post ID to posts_log table
- Respect rate limits (3 posts per day max)
- Run 3x daily (9 AM, 1 PM, 9 PM)
