from flask import Blueprint, request, jsonify, redirect
import os
import re
import requests
import urllib.parse

from utils.storage import load_conversations, save_conversations
from datetime import datetime

push_blueprint = Blueprint('push', __name__)

PUSHBULLET_API_KEY = os.getenv("PUSHBULLET_API_KEY")

def send_push_notification(guest, message, ai_response, airbnb_link, test_mode=False):
    """Sends a Pushbullet notification with the AI-generated response."""
    if not PUSHBULLET_API_KEY and not test_mode:
        print("❌ Pushbullet API Key is missing. Skipping notification.")
        return

    encoded_ai_response = urllib.parse.quote(ai_response)
    encoded_airbnb_link = urllib.parse.quote(airbnb_link, safe=":/?=&")

    # Use the /prefill_message route from responses.py for approval
    approve_url = f"https://airbnb-bot.onrender.com/prefill_message?response={encoded_ai_response}&thread={encoded_airbnb_link}"
    edit_url = f"https://airbnb-bot.onrender.com/edit_response?response={encoded_ai_response}&thread={encoded_airbnb_link}"

    print(f"\n🔍 **PushBullet Links:**")
    print(f"🔗 Airbnb Link: {airbnb_link}")
    print(f"✅ Approve & Send: {approve_url}")
    print(f"📝 Edit & Send: {edit_url}\n")

    if test_mode:
        return

    push_data = {
        "type": "note",
        "title": f"📩 New Airbnb Message from {guest}!",
        "body": (
            f"💬 **Message:** {message}\n"
            f"🤖 **AI Suggested Reply:** {ai_response}\n\n"
            f"✅ **Approve & Send:**\n{approve_url}\n\n"
            f"📝 **Edit & Send:**\n{edit_url}"
        )
    }

    headers = {"Access-Token": PUSHBULLET_API_KEY, "Content-Type": "application/json"}
    response = requests.post("https://api.pushbullet.com/v2/pushes", json=push_data, headers=headers)

    if response.status_code == 200:
        print("✅ Push notification sent successfully!")
    else:
        print(f"❌ Failed to send notification: {response.text}")
