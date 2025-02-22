from flask import Blueprint, request, jsonify
from parse_airbnb_email import get_latest_airbnb_messages
from utils.storage import load_conversations, save_conversations
from datetime import datetime
from routes.push_notifications import send_push_notification
from test_ai_response import generate_response

gmail_blueprint = Blueprint("gmail", __name__)

@gmail_blueprint.route('/gmail_trigger', methods=['POST'])
def gmail_trigger():
    """Fetches new Airbnb messages, generates AI responses, and saves the conversation."""
    print("🔔 Checking for new Airbnb messages...")

    messages = get_latest_airbnb_messages()
    if not messages:
        return jsonify({"status": "No new emails found"}), 200

    conversations = load_conversations()

    for latest_message in messages:
        thread_id = latest_message.get("airbnb_thread_id")
        guest_name = latest_message.get("guest_name")
        client_message = latest_message.get("message")
        listing_name = latest_message.get("listing_name")
        airbnb_link = latest_message.get("airbnb_link")

        print(f"\n📩 **New Airbnb Message from {guest_name}**")
        print(f"💬 Message: {client_message}")

        # ✅ Store guest's question in conversation history
        if thread_id not in conversations:
            conversations[thread_id] = []

        conversations[thread_id].append({
            "role": "guest",
            "sender": guest_name,
            "message": client_message,
            "timestamp": datetime.utcnow().isoformat(),
            "airbnb_link": airbnb_link
        })

        save_conversations(conversations)  # ✅ Save guest's message

        # ✅ Generate AI response
        ai_response = generate_response(client_message, listing_name)

        # ✅ Send Pushbullet notification (but don't save AI response yet)
        send_push_notification(guest_name, client_message, ai_response, airbnb_link)

    return jsonify({"status": "Guest message stored, AI response generated & Pushbullet notification sent"}), 200
