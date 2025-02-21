from flask import Blueprint
import os
import requests
import urllib.parse
import re

push_blueprint = Blueprint('push', __name__)

PUSHBULLET_API_KEY = os.getenv("PUSHBULLET_API_KEY")

def send_push_notification(guest, message, ai_response, airbnb_link):
    """ Sends a Pushbullet notification with AI-generated response and interactive options """
    if not PUSHBULLET_API_KEY:
        print("❌ Pushbullet API Key is missing. Skipping notification.")
        return

    encoded_ai_response = urllib.parse.quote(ai_response)

    # 🔹 Extract the Airbnb thread ID properly
    thread_match = re.search(r"thread/(\d+)", airbnb_link)
    if thread_match:
        thread_id = thread_match.group(1)
        # ✅ Restore the old URL format that worked before
        airbnb_app_link = f"https://fr.airbnb.be/messaging/thread/{thread_id}?thread_type=home_booking&c=.pi80.pkaG9tZXNfbWVzc2FnaW5nL25ld19tZXNzYWdl&euid=819f8882-a06d-f4a6-da35-6b3b6f87be81"
    else:
        airbnb_app_link = airbnb_link  # Fallback if extraction fails

    approve_url = f"https://airbnb-bot.onrender.com/prefill_message?response={encoded_ai_response}&thread={airbnb_app_link}"
    edit_url = f"https://airbnb-bot.onrender.com/edit_response?response={encoded_ai_response}&thread={airbnb_app_link}"

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
