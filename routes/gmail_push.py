import base64
import json
from flask import Blueprint, request, jsonify
from routes.gmail import gmail_trigger  # Optionally, import your trigger function
from utils.storage import load_conversations, save_conversations

gmail_push_bp = Blueprint('gmail_push', __name__)

@gmail_push_bp.route('/gmail_push_notification', methods=['POST'])
def gmail_push_notification():
    """
    Endpoint for handling push notifications from Gmail via Cloud Pub/Sub.
    """
    envelope = request.get_json()
    if not envelope:
        return "Bad Request: No JSON received", 400

    if 'message' not in envelope:
        return "Bad Request: No message field", 400

    pubsub_message = envelope['message']
    data_encoded = pubsub_message.get('data')
    if data_encoded:
        try:
            data_decoded = base64.b64decode(data_encoded).decode('utf-8')
            message_data = json.loads(data_decoded)
            print("Received Gmail push notification:", message_data)
            history_id = message_data.get('historyId')
            # Optionally, call your gmail_trigger() function here to process new emails.
            # For example, uncomment the following line:
            # gmail_trigger()
        except Exception as e:
            print("Error decoding Pub/Sub message:", e)
            return "Error processing message", 500
    else:
        print("No data found in message.")
    
    # Return a successful response to Pub/Sub
    return jsonify(status="ok"), 200
