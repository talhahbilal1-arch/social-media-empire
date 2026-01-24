#!/usr/bin/env python3
"""Helper script to obtain YouTube OAuth refresh token.

Run this script locally with your client credentials to get a refresh token.

Prerequisites:
1. Go to Google Cloud Console (console.cloud.google.com)
2. Create/select a project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download client_secret.json or note the Client ID and Secret

Usage:
    python scripts/get_youtube_oauth.py

Or with arguments:
    python scripts/get_youtube_oauth.py --client-id YOUR_ID --client-secret YOUR_SECRET
"""

import argparse
import json
import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse
import requests


# YouTube upload scope
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
REDIRECT_URI = 'http://localhost:8080'


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback."""

    def do_GET(self):
        """Handle GET request with authorization code."""
        query = parse_qs(urlparse(self.path).query)

        if 'code' in query:
            self.server.auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            ''')
        else:
            error = query.get('error', ['Unknown error'])[0]
            self.server.auth_code = None
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'''
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>Authorization Failed</h1>
                    <p>Error: {error}</p>
                </body>
                </html>
            '''.encode())

    def log_message(self, format, *args):
        """Suppress logging."""
        pass


def get_authorization_url(client_id: str) -> str:
    """Build Google OAuth authorization URL."""
    params = {
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'  # Force consent to get refresh token
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def exchange_code_for_tokens(code: str, client_id: str, client_secret: str) -> dict:
    """Exchange authorization code for tokens."""
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description='Obtain YouTube OAuth refresh token for video uploads'
    )
    parser.add_argument('--client-id', help='OAuth Client ID')
    parser.add_argument('--client-secret', help='OAuth Client Secret')
    parser.add_argument('--client-secrets-file', help='Path to client_secret.json')
    args = parser.parse_args()

    client_id = args.client_id or os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = args.client_secret or os.getenv('YOUTUBE_CLIENT_SECRET')

    # Try loading from client_secrets.json
    if args.client_secrets_file and os.path.exists(args.client_secrets_file):
        with open(args.client_secrets_file) as f:
            secrets = json.load(f)
            if 'installed' in secrets:
                client_id = secrets['installed']['client_id']
                client_secret = secrets['installed']['client_secret']
            elif 'web' in secrets:
                client_id = secrets['web']['client_id']
                client_secret = secrets['web']['client_secret']

    if not client_id or not client_secret:
        print("Error: Client ID and Client Secret required.")
        print()
        print("Options:")
        print("  1. Pass --client-id and --client-secret arguments")
        print("  2. Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET environment variables")
        print("  3. Pass --client-secrets-file with path to client_secret.json")
        print()
        print("To get credentials:")
        print("  1. Go to https://console.cloud.google.com")
        print("  2. Create/select a project")
        print("  3. Enable YouTube Data API v3")
        print("  4. Go to Credentials > Create Credentials > OAuth client ID")
        print("  5. Select 'Desktop app' as application type")
        print("  6. Copy the Client ID and Client Secret")
        sys.exit(1)

    print("=" * 60)
    print("YouTube OAuth Token Generator")
    print("=" * 60)
    print()
    print(f"Client ID: {client_id[:20]}...")
    print()

    # Build authorization URL
    auth_url = get_authorization_url(client_id)

    print("Opening browser for Google authorization...")
    print()
    print("If browser doesn't open, visit this URL:")
    print(auth_url)
    print()

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to receive callback
    print("Waiting for authorization callback on http://localhost:8080...")
    print()

    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    server.auth_code = None
    server.handle_request()  # Handle single request

    if not server.auth_code:
        print("Error: Authorization failed or was cancelled")
        sys.exit(1)

    print("Authorization code received. Exchanging for tokens...")

    # Exchange code for tokens
    try:
        tokens = exchange_code_for_tokens(
            server.auth_code, client_id, client_secret
        )
    except Exception as e:
        print(f"Error exchanging code: {e}")
        sys.exit(1)

    refresh_token = tokens.get('refresh_token')
    access_token = tokens.get('access_token')

    if not refresh_token:
        print("Warning: No refresh token received.")
        print("This may happen if you've already authorized this app.")
        print("Try revoking access at https://myaccount.google.com/permissions")
        print("Then run this script again.")
        sys.exit(1)

    print()
    print("=" * 60)
    print("SUCCESS! Here are your credentials:")
    print("=" * 60)
    print()
    print("Add these to your .env file:")
    print()
    print(f"YOUTUBE_CLIENT_ID={client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
    print()
    print("=" * 60)
    print()
    print("Also add these as GitHub Secrets for automated workflows:")
    print("  - YOUTUBE_CLIENT_ID")
    print("  - YOUTUBE_CLIENT_SECRET")
    print("  - YOUTUBE_REFRESH_TOKEN")
    print()

    # Optionally update .env file
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        response = input("Would you like to update .env file automatically? [y/N] ")
        if response.lower() == 'y':
            with open(env_file, 'r') as f:
                content = f.read()

            # Update or add credentials
            updates = {
                'YOUTUBE_CLIENT_ID': client_id,
                'YOUTUBE_CLIENT_SECRET': client_secret,
                'YOUTUBE_REFRESH_TOKEN': refresh_token
            }

            for key, value in updates.items():
                if f'{key}=' in content:
                    # Replace existing (including commented)
                    import re
                    content = re.sub(
                        rf'^#?\s*{key}=.*$',
                        f'{key}={value}',
                        content,
                        flags=re.MULTILINE
                    )
                else:
                    content += f'\n{key}={value}'

            with open(env_file, 'w') as f:
                f.write(content)

            print(f"Updated {env_file}")


if __name__ == '__main__':
    main()
