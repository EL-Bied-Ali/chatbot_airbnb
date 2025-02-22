from flask import Blueprint, request, jsonify
import os
import requests
import urllib.parse
from utils.storage import load_conversations, save_conversations
from datetime import datetime

push_blueprint = Blueprint('push', __name__)

PUSHBULLET_API_KEY = os.getenv("PUSHBULLET_API_KEY")

def send_push_notification(guest, message, ai_response, airbnb_link, test_mode=False):
    """Sends a Pushbullet notification with AI-generated response and saves it only when sent."""
    if not PUSHBULLET_API_KEY and not test_mode:
        print("❌ Pushbullet API Key is missing. Skipping notification.")
        return

    encoded_ai_response = urllib.parse.quote(ai_response)
    encoded_airbnb_link = urllib.parse.quote(airbnb_link, safe=":/?=&")

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

@push_blueprint.route("/prefill_message", methods=["GET"])
def prefill_message():
    """Opens Airbnb chat and saves the AI response when the user actively sends it."""
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request: Missing parameters.", 400

    # ✅ Extract thread_id from link
    thread_match = re.search(r'thread/(\d+)', airbnb_link)
    if thread_match:
        thread_id = thread_match.group(1)
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    # ✅ Store AI response in conversation history when approved
    conversations = load_conversations()
    if thread_id not in conversations:
        conversations[thread_id] = []

    conversations[thread_id].append({
        "role": "host",
        "sender": "AI Approved Response",
        "message": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    })

    save_conversations(conversations)

    # ✅ Redirect user to Airbnb messaging
    airbnb_redirect_url = f"https://fr.airbnb.be/messaging/thread/{thread_id}"
    return redirect(airbnb_redirect_url, code=302)
