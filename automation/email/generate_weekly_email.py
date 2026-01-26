"""
Weekly Deals Email Generator

Generates HTML email content for the weekly Tuesday deals newsletter.
Compatible with ConvertKit, Mailchimp, and other email services.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Brand colors
PRIMARY_COLOR = "#E85A4F"
SECONDARY_COLOR = "#2C3E50"
AMAZON_ORANGE = "#FF9900"
BACKGROUND = "#FDFCFB"


def generate_deal_card_html(deal: dict, index: int) -> str:
    """Generate HTML for a single deal card."""

    discount_badge_color = "#E74C3C" if deal['discount_percent'] >= 30 else "#E67E22"

    return f'''
    <tr>
      <td style="padding: 20px 0; border-bottom: 1px solid #eee;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td width="120" style="vertical-align: top; padding-right: 15px;">
              <a href="{deal['affiliate_url']}" style="text-decoration: none;">
                <img src="{deal['image_url']}" alt="{deal['title']}" width="120" height="120" style="border-radius: 8px; object-fit: contain; background: #f8f8f8;">
              </a>
            </td>
            <td style="vertical-align: top;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td>
                    <span style="display: inline-block; background: {discount_badge_color}; color: white; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 4px; margin-bottom: 8px;">
                      {deal['discount_percent']:.0f}% OFF
                    </span>
                    <span style="display: inline-block; background: #f0f0f0; color: #666; font-size: 11px; padding: 4px 8px; border-radius: 4px; margin-left: 5px;">
                      {deal['category']}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 8px 0;">
                    <a href="{deal['affiliate_url']}" style="color: {SECONDARY_COLOR}; text-decoration: none; font-weight: 600; font-size: 15px; line-height: 1.4;">
                      {deal['title'][:60]}{'...' if len(deal['title']) > 60 else ''}
                    </a>
                  </td>
                </tr>
                <tr>
                  <td>
                    <span style="color: {PRIMARY_COLOR}; font-size: 18px; font-weight: bold;">${deal['current_price']:.2f}</span>
                    <span style="color: #999; text-decoration: line-through; font-size: 14px; margin-left: 8px;">${deal['original_price']:.2f}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding-top: 6px;">
                    <span style="color: #666; font-size: 13px; font-style: italic;">💡 {deal['why_buy']}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding-top: 12px;">
                    <a href="{deal['affiliate_url']}" style="display: inline-block; background: {AMAZON_ORANGE}; color: white; text-decoration: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px;">
                      Shop on Amazon →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
'''


def generate_email_html(deals_data: dict) -> str:
    """
    Generate the complete HTML email from deals data.

    Args:
        deals_data: Output from weekly_deals_finder.py

    Returns:
        Complete HTML email string
    """
    deals = deals_data.get('deals', [])
    email_date = deals_data.get('email_date', datetime.now().strftime('%Y-%m-%d'))

    # Format date for display
    try:
        date_obj = datetime.fromisoformat(email_date.replace('Z', '+00:00'))
        date_display = date_obj.strftime('%B %d, %Y')
    except:
        date_display = email_date

    # Group deals by category for sections
    beauty_deals = [d for d in deals if 'beauty' in d['category'].lower() or 'skincare' in d['category'].lower()]
    home_deals = [d for d in deals if 'organization' in d['category'].lower() or 'storage' in d['category'].lower()]
    decor_deals = [d for d in deals if 'decor' in d['category'].lower()]

    # Generate deal cards HTML
    all_deals_html = ""
    for i, deal in enumerate(deals):
        all_deals_html += generate_deal_card_html(deal, i)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>This Week's Best Deals | Daily Deal Darling</title>
  <!--[if mso]>
  <style type="text/css">
    table {{border-collapse: collapse; border-spacing: 0; margin: 0;}}
    div, td {{padding: 0;}}
    div {{margin: 0 !important;}}
  </style>
  <noscript>
    <xml>
      <o:OfficeDocumentSettings>
        <o:PixelsPerInch>96</o:PixelsPerInch>
      </o:OfficeDocumentSettings>
    </xml>
  </noscript>
  <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">

  <!-- Email Container -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f4f4f4;">
    <tr>
      <td align="center" style="padding: 20px;">

        <!-- Main Content -->
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #D4A574 100%); padding: 30px; text-align: center;">
              <a href="https://dailydealdarling.com" style="text-decoration: none;">
                <span style="font-size: 28px;">💝</span>
                <span style="color: white; font-size: 24px; font-weight: 700; vertical-align: middle; margin-left: 8px;">Daily Deal Darling</span>
              </a>
            </td>
          </tr>

          <!-- Hero Section -->
          <tr>
            <td style="padding: 40px 30px 30px; text-align: center; background: {BACKGROUND};">
              <h1 style="margin: 0 0 10px; color: {SECONDARY_COLOR}; font-size: 28px; font-weight: 700;">
                This Week's Best Deals 🎉
              </h1>
              <p style="margin: 0; color: #666; font-size: 16px;">
                {len(deals)} hand-picked deals on beauty, home & decor
              </p>
              <p style="margin: 10px 0 0; color: #999; font-size: 13px;">
                {date_display}
              </p>
            </td>
          </tr>

          <!-- Deals Section -->
          <tr>
            <td style="padding: 0 30px 30px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {all_deals_html}
              </table>
            </td>
          </tr>

          <!-- CTA Section -->
          <tr>
            <td style="padding: 30px; background: #f8f8f8; text-align: center;">
              <p style="margin: 0 0 15px; color: {SECONDARY_COLOR}; font-size: 18px; font-weight: 600;">
                Want more deals?
              </p>
              <a href="https://dailydealdarling.com/#deals" style="display: inline-block; background: {PRIMARY_COLOR}; color: white; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                See All Deals on Our Site →
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 30px; background: {SECONDARY_COLOR}; text-align: center;">
              <p style="margin: 0 0 15px; color: rgba(255,255,255,0.9); font-size: 14px;">
                💝 Daily Deal Darling
              </p>
              <p style="margin: 0 0 15px; color: rgba(255,255,255,0.7); font-size: 12px; line-height: 1.6;">
                You're receiving this because you signed up for weekly deals.<br>
                <a href="{{{{unsubscribe_url}}}}" style="color: rgba(255,255,255,0.9); text-decoration: underline;">Unsubscribe</a> |
                <a href="https://dailydealdarling.com" style="color: rgba(255,255,255,0.9); text-decoration: underline;">Visit Website</a>
              </p>
              <p style="margin: 0; color: rgba(255,255,255,0.5); font-size: 11px;">
                <strong>Affiliate Disclosure:</strong> We may earn a commission when you click our links and make purchases. This helps support our free content.
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>'''

    return html


def generate_plain_text(deals_data: dict) -> str:
    """Generate plain text version of the email."""

    deals = deals_data.get('deals', [])

    lines = [
        "💝 DAILY DEAL DARLING",
        "=" * 40,
        "",
        f"This Week's Best Deals ({len(deals)} finds!)",
        "",
    ]

    for i, deal in enumerate(deals, 1):
        lines.append(f"{i}. {deal['title'][:50]}...")
        lines.append(f"   ${deal['current_price']:.2f} (was ${deal['original_price']:.2f}) - {deal['discount_percent']:.0f}% OFF")
        lines.append(f"   {deal['why_buy']}")
        lines.append(f"   Shop: {deal['affiliate_url']}")
        lines.append("")

    lines.extend([
        "-" * 40,
        "See all deals: https://dailydealdarling.com/#deals",
        "",
        "You're receiving this because you signed up for weekly deals.",
        "Unsubscribe: {{unsubscribe_url}}",
        "",
        "Affiliate Disclosure: We may earn a commission when you click our links.",
    ])

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate weekly deals email')
    parser.add_argument(
        '--input',
        default='weekly_deals.json',
        help='Input deals JSON file'
    )
    parser.add_argument(
        '--output-html',
        default='weekly_email.html',
        help='Output HTML file path'
    )
    parser.add_argument(
        '--output-text',
        default='weekly_email.txt',
        help='Output plain text file path'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Open HTML in browser for preview'
    )

    args = parser.parse_args()

    # Load deals data
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {args.input}")
        logger.info("Run weekly_deals_finder.py first")
        return 1

    deals_data = json.loads(input_path.read_text())
    logger.info(f"Loaded {len(deals_data.get('deals', []))} deals")

    # Generate HTML email
    html = generate_email_html(deals_data)
    Path(args.output_html).write_text(html)
    logger.info(f"HTML email saved to {args.output_html}")

    # Generate plain text version
    text = generate_plain_text(deals_data)
    Path(args.output_text).write_text(text)
    logger.info(f"Plain text email saved to {args.output_text}")

    # Preview in browser
    if args.preview:
        import webbrowser
        webbrowser.open(f"file://{Path(args.output_html).absolute()}")

    print(f"\n{'='*60}")
    print("EMAIL GENERATED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"HTML: {args.output_html}")
    print(f"Text: {args.output_text}")
    print(f"Deals: {len(deals_data.get('deals', []))}")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    exit(main())
