from flask import Blueprint, request, redirect, render_template, jsonify
from utils.storage import load_conversations, save_conversations
import re
from test_ai_response import generate_response  # ✅ Import AI response function
from datetime import datetime

# ✅ Define Blueprint first before using it
responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route("/generate_ai_response", methods=["GET"])
def generate_ai_response():
    """ Generate AI response dynamically if not provided in the URL """
    thread_id = request.args.get("thread")

    # ✅ Load conversation history and find last guest message
    conversations = load_conversations()
    if thread_id in conversations:
        guest_messages = [msg for msg in conversations[thread_id] if msg["role"] == "guest"]
        if guest_messages:
            last_guest_message = guest_messages[-1]["message"]
            ai_response = generate_response(last_guest_message, "Bayside Luxe 2BR")  # Customize with the listing name
            print(f"🤖 Generated AI Response: {ai_response}")
            return jsonify({"response": ai_response})

    # ✅ If no guest message exists, generate a generic response
    ai_response = generate_response("Hello! How can I assist you?", "Bayside Luxe 2BR")
    print(f"🤖 Generated Default AI Response: {ai_response}")
    return jsonify({"response": ai_response})

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Opens Airbnb chat directly in the app """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    print(f"🔗 Received Airbnb Link in prefill_message: {airbnb_link}")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request: Missing parameters.", 400

    match = re.search(r'thread/(\d+)', airbnb_link)
    if match:
        thread_id = match.group(1)
        airbnb_app_link = f"https://fr.airbnb.be/messaging/thread/{thread_id}?thread_type=home_booking&c=.pi80.pkaG9tZXNfbWVzc2FnaW5nL25ld19tZXNzYWdl&euid=819f8882-a06d-f4a6-da35-6b3b6f87be81"
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to Airbnb: {airbnb_app_link}")

    return redirect(airbnb_app_link, code=302)

@responses_blueprint.route('/edit_response', methods=['GET', 'POST'])
def edit_response():
    """ Allows user to edit AI-generated response and view full conversation """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    print(f"🔍 Debug: Received AI Response = {ai_response}")
    print(f"🔍 Debug: Received Airbnb Link = {airbnb_link}")

    match = re.search(r'thread/(\d+)', airbnb_link)
    thread_id = match.group(1) if match else None

    print(f"🔍 Debug: Extracted Thread ID = {thread_id}")

    conversations = load_conversations()
    conversation_history = conversations.get(thread_id, [])

    print(f"🔍 Debug: Loaded Conversation History = {conversation_history}")

    # ✅ If an AI response was already generated via Pushbullet, use it
    if not ai_response:
        ai_messages = [msg for msg in conversation_history if msg["role"] == "ai_generated"]
        if ai_messages:
            ai_response = ai_messages[-1]["message"]
            print(f"♻️ Reusing Previously Generated AI Response: {ai_response}")
        else:
            guest_messages = [msg for msg in conversation_history if msg["role"] == "guest"]
            if guest_messages:
                last_guest_message = guest_messages[-1]["message"]
                ai_response = generate_response(last_guest_message, "Bayside Luxe 2BR")
                print(f"🤖 Generated New AI Response: {ai_response}")

                # ✅ Store it in conversation history but NOT as "approved" yet
                conversations[thread_id].append({
                    "role": "ai_generated",
                    "sender": "AI Pending Approval",
                    "message": ai_response,
                    "timestamp": datetime.utcnow().isoformat()
                })
                save_conversations(conversations)

    return render_template("edit_response.html", ai_response=ai_response, airbnb_link=airbnb_link, conversation_history=conversation_history)
