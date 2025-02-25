from flask import Blueprint, request, jsonify
from datetime import datetime
from routes.push_notifications import send_push_notification
from test_ai_response import generate_response
from parse_airbnb_email import get_latest_airbnb_messages
from utils.storage import load_conversations, save_conversations
from google_auth_oauthlib.flow import InstalledAppFlow

import pickle

import os

gmail_blueprint = Blueprint("gmail", __name__)

@gmail_blueprint.route('/gmail_trigger', methods=['POST'])
def gmail_trigger():
    """Fetches new Airbnb messages, generates AI responses, and saves the conversation."""
    print("🔔 Checking for new Airbnb messages...")

    messages = get_latest_airbnb_messages()
    if not messages:
        print("🚫 No new emails found.")
        return jsonify({"status": "No new emails found"}), 200

    conversations = load_conversations()

    for latest_message in messages:
        thread_id = latest_message.get("airbnb_thread_id")
        guest_name = latest_message.get("guest_name")
        client_message = latest_message.get("message")
        listing_name = latest_message.get("listing_name")
        airbnb_link = latest_message.get("airbnb_link")
        email_timestamp = latest_message.get("message_timestamp")  # ✅ Get correct timestamp

        print(f"\n📩 **New Airbnb Message from {guest_name}**")
        print(f"💬 Message: {client_message}")
        print(f"⏳ Received At: {email_timestamp}")

        # ✅ Store guest's question only if it's not a duplicate
        if thread_id not in conversations:
            conversations[thread_id] = []

        # Check if the same message already exists
        existing_messages = [msg["message"] for msg in conversations[thread_id] if msg["role"] == "guest"]
        if client_message not in existing_messages:
            conversations[thread_id].append({
                "role": "guest",
                "sender": guest_name,
                "message": client_message,
                "timestamp": email_timestamp,
                "airbnb_link": airbnb_link
            })
            print(f"✅ Message from {guest_name} stored successfully.")

        save_conversations(conversations)  # ✅ Save guest's message

        # ✅ Generate AI response
        ai_response = generate_response(client_message, listing_name)
        print(f"🤖 AI Response Generated: {ai_response}")

        # ✅ Send Pushbullet notification
        send_push_notification(guest_name, client_message, ai_response, airbnb_link)
        print(f"📩 Pushbullet notification sent for {guest_name}.")

    return jsonify({"status": "Guest message stored, AI response generated & Pushbullet notification sent"}), 200

def authorize_gmail():
    """Starts the OAuth2 authorization flow for Gmail API."""
    print("🔑 Opening Gmail OAuth authentication...")

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    client_secret_path = os.path.join(os.path.dirname(__file__), "..", "credentials.json")

    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES, redirect_uri="http://localhost:8080/")
    creds = flow.run_local_server(port=8080)  # ✅ Ensure this matches Google Console

    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

    print("✅ Gmail authorization complete.")
    
def start_gmail_watch():
    """Starts the Gmail push notification watch."""
    print("🔔 Starting Gmail Watch...")
    
    # ✅ Import and call the correct function from `start_watch.py`
    from start_watch import start_gmail_watch as start_watch_function
    start_watch_function()

    print("✅ Gmail Watch started successfully.")



    
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize", action="store_true", help="Authorize Gmail API")
    parser.add_argument("--trigger-watch", action="store_true", help="Start Gmail Watch for push notifications")
    args = parser.parse_args()

    if args.authorize:
        print("🔑 Starting Gmail authorization flow...")
        authorize_gmail()  # ✅ Call the function here

    if args.trigger_watch:
        print("🔔 Triggering Gmail Watch...")
        start_gmail_watch()  # ✅ Call the function here

