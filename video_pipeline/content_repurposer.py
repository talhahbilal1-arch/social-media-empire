"""
Content Repurposing Pipeline — turns video script JSON into multi-format content.

Generates:
  1. blog.md        — SEO-optimized blog post (1000+ words) with Amazon affiliate links
  2. email.md       — Short newsletter with CTA driving traffic to the brand site
  3. social.md      — Platform-optimized captions (Twitter/X, Instagram, Facebook)
  4. pin_description.txt — Pinterest static-pin description with keywords & hashtags

Usage:
    # Repurpose a single script JSON
    python -m video_pipeline.content_repurposer output/fitover35_20260405_160547.json

    # Repurpose all today's JSONs for a brand
    python -m video_pipeline.content_repurposer --brand fitover35 --today

    # Repurpose every JSON in the output dir from today
    python -m video_pipeline.content_repurposer --all --today
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("content_repurposer")

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
CONTENT_DIR = OUTPUT_DIR / "content"

# ── Load env ──────────────────────────────────────────────────────────────────
_env_path = PROJECT_ROOT / ".env"
load_dotenv(_env_path)

# ── Brand metadata (mirrors config.py but keeps this module self-contained) ───
BRAND_META = {
    "fitover35": {
        "name": "Fitness Made Easy",
        "site_url": "https://fitover35.com",
        "amazon_tag": "fitover3509-20",
        "tone": "authoritative, motivational, no-nonsense, results-focused",
        "audience": "men aged 35-60 who want to build muscle, stay lean, and feel strong",
        "niche": "Men's fitness over 35",
        "email_from_name": "Coach Mike",
        "newsletter_tagline": "Your weekly edge for building muscle after 35.",
    },
    "deals": {
        "name": "Daily Deal Darling",
        "site_url": "https://dailydealdarling.com",
        "amazon_tag": "dailydealdarl-20",
        "tone": "warm, excited, friendly, relatable, conversational",
        "audience": "women aged 25-45 who love Amazon deals, home decor, and beauty finds",
        "niche": "Budget home, beauty & lifestyle Amazon finds",
        "email_from_name": "Daily Deal Darling",
        "newsletter_tagline": "The best daily deals, delivered to your inbox.",
    },
    "menopause": {
        "name": "Menopause Planner",
        "site_url": "https://menopause-planner-website.vercel.app",
        "amazon_tag": "dailydealdarl-20",
        "tone": "warm, empathetic, supportive, informative, reassuring",
        "audience": "women aged 45-60 navigating perimenopause and menopause",
        "niche": "Menopause wellness & symptom management",
        "email_from_name": "The Menopause Planner",
        "newsletter_tagline": "Practical tips for thriving through menopause.",
    },
    "pilottools": {
        "name": "PilotTools",
        "site_url": "https://pilottools.ai",
        "amazon_tag": None,
        "tone": "professional, tech-savvy, insightful, practical, enthusiastic",
        "audience": "professionals, entrepreneurs, and creators who use AI tools",
        "niche": "AI tool reviews & productivity",
        "email_from_name": "PilotTools Team",
        "newsletter_tagline": "The smartest AI tools, reviewed weekly.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
#  Gemini Client
# ═══════════════════════════════════════════════════════════════════════════════

def _init_gemini() -> genai.Client:
    """Configure and return a Gemini client instance."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY or GOOGLE_API_KEY must be set in .env"
        )
    return genai.Client(api_key=api_key)


MODEL_ID = "gemini-2.0-flash"


def _call_gemini(client: genai.Client, prompt: str, max_retries: int = 3) -> str:
    """Call Gemini with retry logic and rate-limit backoff."""
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=4096,
                ),
            )
            return response.text.strip()
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "rate" in err_str or "quota" in err_str:
                wait = 2 ** attempt * 5
                logger.warning(f"Rate limited (attempt {attempt}/{max_retries}), waiting {wait}s...")
                time.sleep(wait)
            else:
                logger.error(f"Gemini API error (attempt {attempt}): {e}")
                if attempt == max_retries:
                    raise
                time.sleep(2)
    raise RuntimeError("Gemini API call failed after retries")


# ═══════════════════════════════════════════════════════════════════════════════
#  Prompt Builders
# ═══════════════════════════════════════════════════════════════════════════════

def _build_blog_prompt(script: dict, brand: dict) -> str:
    """Build prompt for an SEO-optimized blog post with affiliate links."""
    affiliate_instruction = ""
    if brand["amazon_tag"]:
        affiliate_instruction = f"""
AMAZON AFFILIATE LINKS:
- Where relevant, recommend 2-3 specific products that relate to the topic.
- Format affiliate links as: https://www.amazon.com/dp/ASIN?tag={brand['amazon_tag']}
- Use real-sounding but placeholder ASINs like B0XXXXXXXXX (the user will replace them).
- Weave product recommendations naturally into the content — never force them.
- Include a small "Recommended Products" section near the end with 2-3 picks.
- Add FTC disclosure at the bottom: "This post contains affiliate links. We may earn a small commission at no extra cost to you."
"""
    else:
        affiliate_instruction = "Do NOT include any Amazon affiliate links for this brand."

    return f"""You are an expert SEO content writer for the brand "{brand['name']}".

BRAND CONTEXT:
- Niche: {brand['niche']}
- Target audience: {brand['audience']}
- Tone: {brand['tone']}
- Website: {brand['site_url']}

VIDEO SCRIPT TO EXPAND:
- Title: {script['title']}
- Topic: {script['topic']}
- Hook: {script['hook']}
- Key Points: {json.dumps(script['body_points'])}
- CTA: {script['cta']}
- Hashtags: {json.dumps(script.get('hashtags', []))}

TASK: Write a comprehensive, SEO-optimized blog post of 1000-1500 words expanding on this video script topic.

REQUIREMENTS:
1. Start with an engaging H1 title (different from the video title but same topic).
2. Write a compelling intro paragraph that hooks the reader (use the video hook as inspiration).
3. Include 4-6 H2 subheadings that break the content into scannable sections.
4. Each section should be 150-250 words with actionable, specific advice.
5. Use the brand's tone consistently throughout.
6. Include a meta description (under 160 chars) at the top in a comment block.
7. End with a strong CTA directing readers to the site or to subscribe.
8. Include internal linking suggestions as [INTERNAL: topic suggestion] placeholders.

SEO:
- Primary keyword should appear in the title, first paragraph, one H2, and naturally 3-5 more times.
- Use related LSI keywords naturally throughout.
- Write for humans first, search engines second.

{affiliate_instruction}

FORMAT: Output as clean Markdown. Start with the meta description as an HTML comment, then the post.
"""


def _build_email_prompt(script: dict, brand: dict) -> str:
    """Build prompt for a short, engaging email newsletter."""
    return f"""You are a conversion-focused email copywriter for "{brand['name']}".

BRAND CONTEXT:
- Niche: {brand['niche']}
- Target audience: {brand['audience']}
- Tone: {brand['tone']}
- Website: {brand['site_url']}
- Newsletter tagline: {brand['newsletter_tagline']}
- From name: {brand['email_from_name']}

VIDEO SCRIPT CONTEXT:
- Title: {script['title']}
- Topic: {script['topic']}
- Hook: {script['hook']}
- Key Points: {json.dumps(script['body_points'])}

TASK: Write a short, punchy email newsletter (250-400 words) about this topic.

REQUIREMENTS:
1. Subject line: Short, curiosity-driven, under 50 chars. Provide 3 options.
2. Preview text: Under 90 chars, complements the subject line.
3. Opening: Personal, conversational — like writing to a friend who needs this info.
4. Body: 2-3 short paragraphs. Give ONE genuinely useful tip or insight from the topic.
5. CTA button text + URL: Drive traffic to {brand['site_url']}. Make the CTA specific and action-oriented (not just "Click here").
6. P.S. line: Add urgency or a secondary hook.
7. Unsubscribe footer placeholder.

TONE: Match the brand tone — {brand['tone']}. Keep it scannable. Short paragraphs. No fluff.

FORMAT: Output as Markdown with clear section labels.
"""


def _build_social_prompt(script: dict, brand: dict) -> str:
    """Build prompt for platform-optimized social media captions."""
    return f"""You are a social media strategist for "{brand['name']}".

BRAND CONTEXT:
- Niche: {brand['niche']}
- Target audience: {brand['audience']}
- Tone: {brand['tone']}
- Website: {brand['site_url']}

VIDEO SCRIPT CONTEXT:
- Title: {script['title']}
- Topic: {script['topic']}
- Hook: {script['hook']}
- Key Points: {json.dumps(script['body_points'])}
- CTA: {script['cta']}
- Hashtags: {json.dumps(script.get('hashtags', []))}

TASK: Write optimized social media captions for THREE platforms.

─── TWITTER / X ───
- 280 chars max (including hashtags).
- Lead with a bold statement or question.
- Include 2-3 relevant hashtags at the end.
- Make it punchy and shareable — like a hot take or surprising stat.

─── INSTAGRAM ───
- 300-500 words.
- Start with a strong hook line (the first line must stop the scroll).
- Use line breaks liberally for readability.
- Include 3-5 emoji strategically (not overdone).
- Add a clear CTA (save, share, comment, link in bio).
- End with a block of 20-25 relevant hashtags (mix of popular + niche).

─── FACEBOOK ───
- 100-200 words.
- Conversational and relatable tone.
- Ask a question to drive comments/engagement.
- Include 1-2 hashtags max.
- End with a CTA to visit the site or watch the video.

FORMAT: Output as Markdown with clear H2 headers for each platform: ## Twitter/X, ## Instagram, ## Facebook
"""


def _build_pin_description_prompt(script: dict, brand: dict) -> str:
    """Build prompt for a Pinterest static pin description."""
    return f"""You are a Pinterest SEO specialist for "{brand['name']}".

BRAND CONTEXT:
- Niche: {brand['niche']}
- Target audience: {brand['audience']}
- Website: {brand['site_url']}

VIDEO SCRIPT CONTEXT:
- Title: {script['title']}
- Topic: {script['topic']}
- Hook: {script['hook']}
- Key Points: {json.dumps(script['body_points'])}
- Hashtags: {json.dumps(script.get('hashtags', []))}

TASK: Write a Pinterest pin description optimized for search and saves.

REQUIREMENTS:
1. Length: 150-300 characters for the main description.
2. Front-load the most important keywords in the first sentence.
3. Write 2-3 sentences: what + why + CTA.
4. Include a keyword-rich title suggestion (separate from main description).
5. After the description, add a line of 8-12 relevant hashtags.
6. Include 5 SEO keyword suggestions that should be targeted.

PINTEREST SEO TIPS TO FOLLOW:
- Use natural language, not keyword stuffing.
- Include the problem + solution format.
- Mention specific benefits.
- End with a CTA: "Click to read more", "Save for later", "Visit {brand['site_url']}".

FORMAT: Plain text. Structure as:
TITLE: ...
DESCRIPTION: ...
HASHTAGS: ...
SEO KEYWORDS: ...
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  Core Repurposing Logic
# ═══════════════════════════════════════════════════════════════════════════════

def repurpose_script(
    script_json_path: Path,
    client: Optional[genai.Client] = None,
    formats: Optional[list[str]] = None,
) -> dict:
    """
    Take a script JSON file and generate all content formats.

    Args:
        script_json_path: Path to the {brand}_{timestamp}.json file
        model: Optional pre-initialized Gemini model
        formats: List of formats to generate. Default: all four.

    Returns:
        Dict with paths to generated files and metadata.
    """
    if formats is None:
        formats = ["blog", "email", "social", "pin"]

    # ── Load script data ──────────────────────────────────────────────────────
    with open(script_json_path, "r") as f:
        raw_data = json.load(f)

    # Handle both nested and flat script structures
    if "script" in raw_data:
        script = raw_data["script"]
        brand_key = raw_data.get("brand", "unknown")
    else:
        script = raw_data
        brand_key = raw_data.get("brand", "unknown")

    brand = BRAND_META.get(brand_key)
    if not brand:
        logger.error(f"Unknown brand '{brand_key}'. Known brands: {list(BRAND_META.keys())}")
        raise ValueError(f"Unknown brand: {brand_key}")

    # ── Determine output directory ────────────────────────────────────────────
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content_out = CONTENT_DIR / brand_key / today_str
    content_out.mkdir(parents=True, exist_ok=True)

    # Use a subfolder per script to avoid collisions when running multiple
    slug = re.sub(r"[^a-z0-9]+", "-", script["title"].lower()).strip("-")[:60]
    script_out = content_out / slug
    script_out.mkdir(parents=True, exist_ok=True)

    # ── Initialize Gemini ─────────────────────────────────────────────────────
    if client is None:
        client = _init_gemini()

    results = {
        "brand": brand_key,
        "title": script["title"],
        "topic": script["topic"],
        "output_dir": str(script_out),
        "files": {},
    }

    # ── Generate each format ──────────────────────────────────────────────────
    generators = {
        "blog": (_build_blog_prompt, "blog.md"),
        "email": (_build_email_prompt, "email.md"),
        "social": (_build_social_prompt, "social.md"),
        "pin": (_build_pin_description_prompt, "pin_description.txt"),
    }

    for fmt in formats:
        if fmt not in generators:
            logger.warning(f"Unknown format '{fmt}', skipping")
            continue

        prompt_fn, filename = generators[fmt]
        output_path = script_out / filename

        logger.info(f"  [{brand_key}] Generating {fmt} → {filename}...")

        try:
            prompt = prompt_fn(script, brand)
            content = _call_gemini(client, prompt)

            # Write the file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            results["files"][fmt] = str(output_path)
            logger.info(f"  [{brand_key}] ✓ {fmt} saved ({len(content)} chars)")

        except Exception as e:
            logger.error(f"  [{brand_key}] ✗ {fmt} failed: {e}")
            results["files"][fmt] = f"ERROR: {e}"

        # Small delay between API calls to avoid rate limits
        if fmt != formats[-1]:
            time.sleep(1)

    # ── Save a manifest ───────────────────────────────────────────────────────
    manifest_path = script_out / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(
            {
                **results,
                "source_script": str(script_json_path),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            f,
            indent=2,
        )
    results["manifest"] = str(manifest_path)

    return results


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════════

def _find_todays_jsons(brand: Optional[str] = None) -> list[Path]:
    """Find all script JSONs generated today in the output directory."""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    pattern = f"*_{today}_*.json"

    found = sorted(OUTPUT_DIR.glob(pattern))

    if brand:
        found = [p for p in found if p.name.startswith(f"{brand}_")]

    # Exclude non-script files (test_props.json etc.)
    found = [p for p in found if not p.name.startswith("test_")]

    return found


def main():
    parser = argparse.ArgumentParser(
        description="Repurpose video scripts into blog posts, emails, social captions, and pin descriptions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m video_pipeline.content_repurposer output/fitover35_20260405_160547.json
  python -m video_pipeline.content_repurposer --brand deals --today
  python -m video_pipeline.content_repurposer --all --today
  python -m video_pipeline.content_repurposer output/menopause_20260405_160800.json --formats blog,email
""",
    )

    parser.add_argument(
        "json_path",
        nargs="?",
        help="Path to a specific script JSON file to repurpose",
    )
    parser.add_argument(
        "--brand",
        choices=list(BRAND_META.keys()),
        help="Filter by brand when using --today",
    )
    parser.add_argument(
        "--today",
        action="store_true",
        help="Process all of today's script JSONs",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all brands (use with --today)",
    )
    parser.add_argument(
        "--formats",
        default="blog,email,social,pin",
        help="Comma-separated list of formats to generate (default: all)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]

    # Determine which files to process
    files_to_process: list[Path] = []

    if args.json_path:
        p = Path(args.json_path)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        if not p.exists():
            logger.error(f"File not found: {p}")
            sys.exit(1)
        files_to_process = [p]

    elif args.today or args.all:
        brand_filter = None if args.all else args.brand
        files_to_process = _find_todays_jsons(brand=brand_filter)
        if not files_to_process:
            logger.warning("No script JSONs found for today.")
            sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)

    # Initialize Gemini once for all files
    client = _init_gemini()

    logger.info(f"{'=' * 60}")
    logger.info(f"Content Repurposer — {len(files_to_process)} file(s) to process")
    logger.info(f"Formats: {formats}")
    logger.info(f"{'=' * 60}")

    all_results = []

    for i, json_path in enumerate(files_to_process, 1):
        logger.info(f"\n[{i}/{len(files_to_process)}] Processing: {json_path.name}")
        try:
            result = repurpose_script(json_path, client=client, formats=formats)
            all_results.append(result)
            logger.info(f"  → Output: {result['output_dir']}")
        except Exception as e:
            logger.error(f"  → FAILED: {e}", exc_info=True)
            all_results.append({"source": str(json_path), "status": "failed", "error": str(e)})

    # Summary
    succeeded = sum(1 for r in all_results if "error" not in r)
    failed = len(all_results) - succeeded

    print(f"\n{'=' * 60}")
    print(f"Content Repurposer Complete: {succeeded}/{len(all_results)} succeeded, {failed} failed")
    for r in all_results:
        if "error" in r:
            print(f"  ✗ {r.get('source', 'unknown')} — {r['error']}")
        else:
            print(f"  ✓ [{r['brand']}] {r['title']}")
            for fmt, path in r.get("files", {}).items():
                status = "✓" if not str(path).startswith("ERROR") else "✗"
                print(f"      {status} {fmt}: {Path(path).name if status == '✓' else path}")
    print(f"{'=' * 60}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
