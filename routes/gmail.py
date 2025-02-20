from flask import Blueprint, request, jsonify
from parse_airbnb_email import get_latest_airbnb_messages
from test_ai_response import generate_response
from routes.push_notifications import send_push_notification

gmail_blueprint = Blueprint('gmail', __name__)

@gmail_blueprint.route('/gmail_trigger', methods=['POST'])
def gmail_trigger():
    """ Fetches new Airbnb messages and sends Push Notification """
    print("🔔 Checking for new Airbnb messages...")

    messages = get_latest_airbnb_messages()
    
    if not messages:
        return jsonify({"status": "Aucun nouvel email trouvé"}), 200

    latest_message = messages[0]
    guest_name = latest_message["guest_name"]
    client_message = latest_message["message"]
    listing_name = latest_message["listing_name"]
    airbnb_link = latest_message.get("airbnb_link", "#")

    print(f"\n📩 **New Airbnb Message from {guest_name}**")
    print(f"💬 Message: {client_message}")

    ai_response = generate_response(client_message, listing_name)
    send_push_notification(guest_name, client_message, ai_response, airbnb_link)

    return jsonify({
        "status": "Réponse générée",
        "guest": guest_name,
        "client_message": client_message,
        "apartment": listing_name,
        "ai_response": ai_response
    }), 200
