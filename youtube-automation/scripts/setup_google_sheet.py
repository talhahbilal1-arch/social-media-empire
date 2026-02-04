"""
Google Sheets Setup Script
Creates the required sheet structure for the automation pipeline
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from pathlib import Path

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    """Get or refresh Google API credentials"""
    creds = None
    token_path = Path(__file__).parent / 'token.pickle'
    creds_path = Path(__file__).parent / 'credentials.json'

    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                print("❌ credentials.json not found!")
                print("\nTo set up Google Sheets API:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a project or select existing")
                print("3. Enable Google Sheets API")
                print("4. Create OAuth 2.0 credentials (Desktop app)")
                print("5. Download and save as 'scripts/credentials.json'")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def create_scripts_sheet(spreadsheet_id: str = None):
    """
    Create or update the Scripts sheet with required columns

    Args:
        spreadsheet_id: Existing spreadsheet ID, or None to create new
    """
    creds = get_credentials()
    if not creds:
        return None

    try:
        service = build('sheets', 'v4', credentials=creds)

        if spreadsheet_id:
            # Update existing spreadsheet
            print(f"Updating spreadsheet: {spreadsheet_id}")
        else:
            # Create new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': 'YouTube Shorts - Scripts'
                },
                'sheets': [
                    {'properties': {'title': 'Scripts'}},
                    {'properties': {'title': 'Errors'}}
                ]
            }
            spreadsheet = service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            print(f"✅ Created new spreadsheet: {spreadsheet_id}")

        # Define headers for Scripts sheet
        scripts_headers = [
            ['row_id', 'title', 'script_text', 'description', 'hashtags',
             'thumbnail_text', 'status', 'created_date', 'published_date',
             'youtube_post_id', 'video_url']
        ]

        # Define headers for Errors sheet
        errors_headers = [
            ['timestamp', 'workflow', 'node', 'error', 'execution_id']
        ]

        # Update Scripts sheet headers
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Scripts!A1:K1',
            valueInputOption='RAW',
            body={'values': scripts_headers}
        ).execute()

        # Update Errors sheet headers
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Errors!A1:E1',
            valueInputOption='RAW',
            body={'values': errors_headers}
        ).execute()

        # Add sample script row
        sample_script = [[
            '1',  # row_id
            'Stop Taking Zinc for Testosterone',  # title
            'Stop taking zinc for testosterone unless you\'re actually deficient.\n\nA 2023 study found that zinc supplementation only raised testosterone in men who were already low to begin with.\n\nIf your zinc levels are normal, you\'re wasting your money.\n\nHere\'s what to do instead:\n\nFirst, get a blood test. Check your zinc AND testosterone levels.\n\nSecond, if you\'re deficient, 15 to 30 milligrams daily is enough. More isn\'t better.\n\nThird, focus on what actually works: sleep, strength training, and managing stress.\n\nFollow for more evidence-based fitness tips.',  # script_text
            'Learn why zinc supplementation might not boost your testosterone, and what actually works. Based on 2023 research.\n\n🔔 Subscribe for daily fitness tips for men 35+',  # description
            '#testosterone #fitness #menover40 #health #workout #supplements',  # hashtags
            'ZINC MYTH',  # thumbnail_text
            'pending',  # status
            '=TODAY()',  # created_date
            '',  # published_date
            '',  # youtube_post_id
            ''  # video_url
        ]]

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Scripts!A2:K2',
            valueInputOption='USER_ENTERED',
            body={'values': sample_script}
        ).execute()

        # Format header row (bold)
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,  # Scripts sheet
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            },
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 1,  # Errors sheet
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            },
            # Freeze header row
            {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': 0,
                        'gridProperties': {'frozenRowCount': 1}
                    },
                    'fields': 'gridProperties.frozenRowCount'
                }
            },
            {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': 1,
                        'gridProperties': {'frozenRowCount': 1}
                    },
                    'fields': 'gridProperties.frozenRowCount'
                }
            }
        ]

        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()

        print("✅ Sheet structure created successfully!")
        print(f"\nSpreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print(f"\nAdd this to your .env:")
        print(f"GOOGLE_SHEETS_ID={spreadsheet_id}")

        return spreadsheet_id

    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return None

def add_script(
    spreadsheet_id: str,
    title: str,
    script_text: str,
    description: str,
    hashtags: str,
    thumbnail_text: str = ""
):
    """Add a new script to the sheet"""
    creds = get_credentials()
    if not creds:
        return None

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Get current row count to determine next row_id
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Scripts!A:A'
        ).execute()
        values = result.get('values', [])
        next_id = len(values)  # Includes header, so this is correct

        new_row = [[
            str(next_id),  # row_id
            title,
            script_text,
            description,
            hashtags,
            thumbnail_text,
            'pending',
            '=TODAY()',
            '', '', ''
        ]]

        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Scripts!A:K',
            valueInputOption='USER_ENTERED',
            body={'values': new_row}
        ).execute()

        print(f"✅ Added script: {title}")
        return next_id

    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Set up Google Sheets for automation")
    parser.add_argument("--sheet-id", help="Existing spreadsheet ID to update")
    parser.add_argument("--create", action="store_true", help="Create new spreadsheet")
    args = parser.parse_args()

    print("=" * 60)
    print("Google Sheets Setup for YouTube Automation")
    print("=" * 60)

    if args.create or not args.sheet_id:
        create_scripts_sheet(args.sheet_id)
    else:
        print("Specify --create to create a new sheet or --sheet-id to update existing")
