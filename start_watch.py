from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def start_gmail_watch():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)
    
    request_body = {
        "labelIds": ["INBOX"],
        "topicName": "projects/airbnb-gmail-push/topics/gmail-notifications"
    }
    
    response = service.users().watch(userId="me", body=request_body).execute()
    print("Watch registered:", response)

if __name__ == "__main__":
    start_gmail_watch()
