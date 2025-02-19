from flask import Flask, request, jsonify
import json
from parse_airbnb_email import get_latest_airbnb_messages
from test_ai_response import generate_response

app = Flask(__name__)

@app.route('/gmail_trigger', methods=['POST'])
def gmail_trigger():
    """ Traite le dernier email reçu et génère une réponse IA """
    print("🔔 Nouvelle notification Gmail reçue...")

    messages = get_latest_airbnb_messages()
    
    if not messages:
        return jsonify({"status": "Aucun nouvel email trouvé"}), 200

    latest_message = messages[0]
    client_message = latest_message["message"]
    guest_name = latest_message["guest_name"]
    listing_name = latest_message["listing_name"]

    print("\n📩 **Nouveau message Airbnb**")
    print(f"👤 De : {guest_name}")
    print(f"🏡 Appartement : {listing_name}")
    print(f"💬 Message : {client_message}")

    # Générer une réponse IA basée sur l'appartement
    response_text = generate_response(client_message, listing_name)
    
    print("\n🤖 **Réponse générée par l'IA**")
    print(response_text)

    return jsonify({
        "status": "Réponse générée",
        "guest": guest_name,
        "client_message": client_message,
        "apartment": listing_name,
        "ai_response": response_text
    }), 200

@app.route('/messages', methods=['GET'])
def fetch_messages():
    """Fetches Airbnb messages (For testing API)"""
    messages = get_latest_airbnb_messages()
    
    if not messages:
        return jsonify({"status": "No new Airbnb messages found"}), 200

    return jsonify(messages), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
