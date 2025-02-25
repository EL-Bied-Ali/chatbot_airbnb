import base64
import json
from flask import Blueprint, request, jsonify
from routes.gmail import gmail_trigger  # Import de la fonction qui traite les emails Gmail
import traceback

gmail_push_bp = Blueprint('gmail_push', __name__)

@gmail_push_bp.route('/gmail_push_notification', methods=['POST'])
def gmail_push_notification():
    """
    Endpoint pour gérer les notifications push de Gmail via Cloud Pub/Sub.
    Il décode le message reçu et déclenche le traitement des emails.
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
            
            # Déclenche le traitement complet des emails (simulateur de réception d'email)
            gmail_trigger()
        except Exception as e:
            print("Error decoding Pub/Sub message:", e)
            traceback.print_exc()
            return "Error processing message", 500
    else:
        print("No data found in message.")
    
    return jsonify(status="ok"), 200
