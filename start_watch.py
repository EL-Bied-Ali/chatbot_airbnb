from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """Authenticate using the stored token_web.json or credentials.json."""
    creds = None

    # Load token from environment variable
    token_json = os.getenv("GMAIL_TOKEN_WEB")  # Changed variable name

    if token_json:
        creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
    else:
        raise ValueError("❌ GMAIL_TOKEN_WEB environment variable is missing! Please upload your token.")

    # Refresh token if needed
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds

def start_gmail_watch():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)
    
    request_body = {
        "labelIds": ["INBOX"],
        "topicName": "projects/airbnb-gmail-bot/topics/gmail-notifications"
    }
    
    response = service.users().watch(userId="me", body=request_body).execute()
    print("Watch registered:", response)

if __name__ == "__main__":
    start_gmail_watch()
