#!/usr/bin/env python3
"""Interactive script to add credentials to .env file.

Run this after obtaining credentials from Make.com and Google Cloud Console.
"""

import os
import re
from pathlib import Path

def main():
    env_path = Path(__file__).parent.parent / '.env'

    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        return

    print("=" * 60)
    print("CREDENTIAL SETUP HELPER")
    print("=" * 60)
    print()
    print("This script will help you add credentials to your .env file.")
    print("Press Enter to skip any credential you don't have yet.")
    print()

    # Read current .env
    with open(env_path, 'r') as f:
        content = f.read()

    credentials = {}

    # Make.com webhook
    print("-" * 40)
    print("MAKE.COM WEBHOOK (for Pinterest)")
    print("-" * 40)
    print("Get this from your Make.com scenario's webhook module.")
    print("Format: https://hook.us2.make.com/...")
    webhook = input("MAKE_WEBHOOK_URL: ").strip()
    if webhook:
        credentials['MAKE_WEBHOOK_URL'] = webhook

    print()

    # YouTube credentials
    print("-" * 40)
    print("YOUTUBE OAUTH CREDENTIALS")
    print("-" * 40)
    print("Get these from Google Cloud Console → APIs & Services → Credentials")

    client_id = input("YOUTUBE_CLIENT_ID: ").strip()
    if client_id:
        credentials['YOUTUBE_CLIENT_ID'] = client_id

    client_secret = input("YOUTUBE_CLIENT_SECRET: ").strip()
    if client_secret:
        credentials['YOUTUBE_CLIENT_SECRET'] = client_secret

    print()
    print("Get refresh token from OAuth Playground or by running:")
    print("  python scripts/get_youtube_oauth.py")
    refresh_token = input("YOUTUBE_REFRESH_TOKEN: ").strip()
    if refresh_token:
        credentials['YOUTUBE_REFRESH_TOKEN'] = refresh_token

    if not credentials:
        print()
        print("No credentials entered. Exiting.")
        return

    print()
    print("=" * 60)
    print("UPDATING .env FILE")
    print("=" * 60)

    # Update .env content
    for key, value in credentials.items():
        # Check if key exists (commented or not)
        pattern = rf'^#?\s*{key}=.*$'
        if re.search(pattern, content, re.MULTILINE):
            # Replace existing line
            content = re.sub(pattern, f'{key}={value}', content, flags=re.MULTILINE)
            print(f"Updated: {key}")
        else:
            # Add new line
            content += f'\n{key}={value}'
            print(f"Added: {key}")

    # Write updated content
    with open(env_path, 'w') as f:
        f.write(content)

    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print()
    print("Credentials saved to .env")
    print()
    print("Next steps:")
    print("1. Test Pinterest: python cli.py --brand menopause-planner --count 1 --post-pinterest")
    print("2. Test YouTube: python cli.py --brand menopause-planner --count 1 --post-youtube")
    print("3. Add same credentials to GitHub Secrets for automated workflows")


if __name__ == '__main__':
    main()
