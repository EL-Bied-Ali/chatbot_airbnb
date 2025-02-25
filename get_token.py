from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import json

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)  # This will open a browser for authentication

# Save the token to a file
with open("token_web.json", "w") as token_file:
    token_file.write(creds.to_json())

print("✅ Token saved as token_web.json")
