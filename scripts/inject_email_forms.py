"""Inject ConvertKit email capture forms into existing brand articles.

Adds two forms per article:
1. After the first product card or first <h2> (mid-article)
2. Before the footer (bottom of article)
"""

import os
import re
import glob

BRAND_FORMS = {
    "fitness": {
        "dir": "outputs/fitover35-website/articles",
        "form_id": "8946984",
        "lead_magnet": "FREE 7-Day Fat Burn Kickstart Plan",
        "button_text": "Get Free Program",
        "accent": "#d4a843",
        "bg": "#1a181e",
        "border": "#2e2c33",
        "text_color": "#FFFFFF",
        "muted": "#8a8894",
        "btn_text": "#111",
        "input_bg": "#1A1A1A",
    },
    "deals": {
        "dir": "outputs/dailydealdarling-website/articles",
        "form_id": "9144859",
        "lead_magnet": "FREE Weekly Deals Digest",
        "button_text": "Join Free",
        "accent": "#E91E63",
        "bg": "#FFFFFF",
        "border": "#F0E6EB",
        "text_color": "#1a1a2e",
        "muted": "#6b7280",
        "btn_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
    },
    "menopause": {
        "dir": "outputs/menopause-planner-website/articles",
        "form_id": "9144926",
        "lead_magnet": "FREE Menopause Symptom Tracker & Relief Guide",
        "button_text": "Get Free Guide",
        "accent": "#7B1FA2",
        "bg": "#FFFFFF",
        "border": "#E8DEF8",
        "text_color": "#1a1a2e",
        "muted": "#6b7280",
        "btn_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
    },
}


def _build_form_html(cfg):
    return (
        f'<div style="background:{cfg["bg"]};border:1px solid {cfg["border"]};border-radius:12px;'
        f'padding:24px;margin:32px 0;text-align:center">'
        f'<h3 style="margin:0 0 8px;color:{cfg["text_color"]}">{cfg["lead_magnet"]}</h3>'
        f'<p style="margin:0 0 16px;color:{cfg["muted"]};font-size:0.95em">'
        f'Join our community for weekly tips and guides.</p>'
        f'<script src="https://f.convertkit.com/ckjs/ck.5.js"></script>'
        f'<form action="https://app.kit.com/forms/{cfg["form_id"]}/subscriptions" method="post" '
        f'data-sv-form="{cfg["form_id"]}" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center">'
        f'<input type="email" name="email_address" placeholder="Enter your email" required '
        f'style="padding:12px 16px;border:1px solid {cfg["border"]};border-radius:8px;'
        f'width:100%;max-width:300px;font-size:1em;background:{cfg["input_bg"]};color:{cfg["text_color"]}">'
        f'<button type="submit" style="padding:12px 24px;background:{cfg["accent"]};color:{cfg["btn_text"]};'
        f'border:none;border-radius:8px;cursor:pointer;font-weight:700;font-size:1em">'
        f'{cfg["button_text"]}</button></form></div>'
    )


def inject_forms(brand_key, cfg):
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), cfg["dir"])
    files = glob.glob(os.path.join(base, "*.html"))
    form_html = _build_form_html(cfg)
    injected = 0

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip if form already present
        if f'data-sv-form="{cfg["form_id"]}"' in content:
            continue

        modified = False

        # 1. Inject mid-article form after first product div or after first <h2> section
        # Find first </div> that closes a product card
        product_end = content.find('class="product"')
        if product_end != -1:
            # Find the end of the first product div (look for the next product or a major section)
            next_product = content.find('class="product"', product_end + 15)
            if next_product != -1:
                # Insert between first and second product
                content = content[:next_product] + form_html + '\n' + content[next_product:]
                modified = True

        if not modified:
            # Fallback: insert after first </h2> + next </p>
            h2_match = re.search(r'</h2>', content)
            if h2_match:
                # Find the next </p> after the h2
                p_end = content.find('</p>', h2_match.end())
                if p_end != -1:
                    insert_pos = p_end + 4
                    content = content[:insert_pos] + '\n' + form_html + '\n' + content[insert_pos:]
                    modified = True

        # 2. Inject bottom form before footer
        footer_pos = content.find('class="footer"')
        if footer_pos != -1:
            # Find the opening <div before class="footer"
            div_start = content.rfind('<div', 0, footer_pos)
            if div_start != -1:
                content = content[:div_start] + form_html + '\n' + content[div_start:]
                modified = True

        if modified:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            injected += 1

    return injected, len(files)


if __name__ == "__main__":
    total_injected = 0
    total_files = 0
    for brand, cfg in BRAND_FORMS.items():
        count, total = inject_forms(brand, cfg)
        total_injected += count
        total_files += total
        print(f"{brand}: {count}/{total} articles updated")
    print(f"\nTotal: {total_injected}/{total_files} articles updated with email capture forms")
