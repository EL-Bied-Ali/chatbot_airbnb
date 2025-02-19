from flask import Flask, request, jsonify, render_template
import os
import requests
from parse_airbnb_email import get_latest_airbnb_messages
from test_ai_response import generate_response

# Load Pushbullet API key from Render environment variables
PUSHBULLET_API_KEY = os.getenv("PUSHBULLET_API_KEY")

app = Flask(__name__)

def send_push_notification(guest, message, ai_response, airbnb_link):
    """ Sends a Pushbullet notification with AI-generated response and interactive options """
    if not PUSHBULLET_API_KEY:
        print("❌ Pushbullet API Key is missing. Skipping notification.")
        return

    # Generate encoded AI response for URL-safe transfer
    import urllib.parse
    encoded_ai_response = urllib.parse.quote(ai_response)

    # URLs for direct approval and manual edit
    approve_url = f"https://airbnb-bot.onrender.com/send_message?response={encoded_ai_response}&thread={airbnb_link}"
    edit_url = f"https://airbnb-bot.onrender.com/edit_response?response={encoded_ai_response}&thread={airbnb_link}"

    push_data = {
        "type": "note",
        "title": f"New Airbnb Message from {guest}!",
        "body": (
            f"📩 Message: {message}\n"
            f"🤖 AI Response: {ai_response}\n\n"
            f"✅ Approve & Send: {approve_url}\n"
            f"📝 Edit & Send: {edit_url}"
        )
    }


    headers = {"Access-Token": PUSHBULLET_API_KEY, "Content-Type": "application/json"}
    
    response = requests.post("https://api.pushbullet.com/v2/pushes", json=push_data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Push notification sent successfully!")
    else:
        print(f"❌ Failed to send notification: {response.text}")


@app.route('/gmail_trigger', methods=['POST'])
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

    # 🔹 Generate AI Response
    ai_response = generate_response(client_message, listing_name)

    # 🔹 Send Push Notification
    send_push_notification(guest_name, client_message, ai_response, airbnb_link)

    return jsonify({
        "status": "Réponse générée",
        "guest": guest_name,
        "client_message": client_message,
        "apartment": listing_name,
        "ai_response": ai_response
    }), 200
    
@app.route('/send_message', methods=['GET'])
def send_message():
    """ Sends the AI response directly to Airbnb """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request.", 400

    # Simulating sending the message to Airbnb (you'll replace this with actual automation)
    print(f"✅ Sending approved response: {ai_response}")
    print(f"🔗 Airbnb Thread: {airbnb_link}")

    return "✅ Message sent successfully!", 200


@app.route('/messages', methods=['GET'])
def fetch_messages():
    """Fetches Airbnb messages (For testing API)"""
    messages = get_latest_airbnb_messages()
    
    if not messages:
        return jsonify({"status": "No new Airbnb messages found"}), 200

    return jsonify(messages), 200
    
@app.route('/edit_response', methods=['GET', 'POST'])
def edit_response():
    """ Allows the user to edit the AI response before sending """
    if request.method == 'GET':
        ai_response = request.args.get("response", "")
        airbnb_link = request.args.get("thread", "#")

        return render_template("edit_form.html", ai_response=ai_response, airbnb_link=airbnb_link)

    if request.method == 'POST':
        edited_response = request.form["edited_response"]
        new_info = request.form.get("new_info", "")
        airbnb_link = request.form["airbnb_link"]

        # Store new info in the database (for AI training)
        if new_info:
            with open("apartment_updates.txt", "a") as file:
                file.write(f"{new_info}\n")

        print(f"✅ Sending edited response: {edited_response}")
        print(f"🔗 Airbnb Thread: {airbnb_link}")

        return "✅ Message sent with edits!", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
