from flask import Blueprint, request, redirect, render_template, jsonify
from utils.storage import load_conversations, save_conversations
import re
from test_ai_response import generate_response  # Import AI response function
from datetime import datetime
import time

# Define Blueprint
responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route("/generate_ai_response", methods=["GET"])
def generate_ai_response():
    """Generate AI response dynamically if not provided in the URL."""
    thread_id = request.args.get("thread")

    # Load conversation history and find the last guest message
    conversations = load_conversations()
    if thread_id in conversations:
        guest_messages = [msg for msg in conversations[thread_id] if msg["role"] == "guest"]
        if guest_messages:
            last_guest_message = guest_messages[-1]["message"]
            ai_response = generate_response(last_guest_message, "Bayside Luxe 2BR")  # Customize with your listing name
            print(f"🤖 Generated AI Response: {ai_response}")
            return jsonify({"response": ai_response})

    # If no guest message exists, generate a generic response
    ai_response = generate_response("Hello! How can I assist you?", "Bayside Luxe 2BR")
    print(f"🤖 Generated Default AI Response: {ai_response}")
    return jsonify({"response": ai_response})


@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """
    Copies AI response, prevents duplicate approvals by checking that the latest message is from the guest,
    and renders a page that copies the response to the clipboard before redirecting to Airbnb.
    """
    ai_response = request.args.get("response", "").strip()
    airbnb_link = request.args.get("thread", "#")

    print(f"🔗 Debug: Received Airbnb Link in prefill_message: {airbnb_link}")
    print(f"📝 Debug: AI Response to Copy: {ai_response}")

    if not airbnb_link:
        return "❌ Invalid request: Missing parameters.", 400

    # Extract thread ID from the Airbnb link
    match = re.search(r'thread/(\d+)', airbnb_link)
    if match:
        thread_id = match.group(1)
        airbnb_app_link = f"https://fr.airbnb.be/messaging/thread/{thread_id}"
        print(f"🔀 Redirecting to Airbnb: {airbnb_app_link}")
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    # Load conversation history
    conversations = load_conversations()

    # Retrieve guest messages
    guest_messages = [msg for msg in conversations.get(thread_id, []) if msg["role"] == "guest"]
    if not guest_messages:
        print(f"🚫 No guest messages found for thread {thread_id}. Skipping save.")
        return render_template("copy_redirect.html", ai_response=ai_response, airbnb_link=airbnb_app_link)

    last_guest_message = guest_messages[-1]["message"]

    # If no AI response exists, generate one using the latest guest message
    if not ai_response:
        ai_response = generate_response(last_guest_message, "Bayside Luxe 2BR")
        print(f"🤖 Generated new AI response: {ai_response}")

    # Prevent duplicate approval by checking if the latest message is still from the guest
    thread_convo = conversations.get(thread_id, [])
    if thread_convo and thread_convo[-1]["role"] != "guest":
        print(f"🚫 Latest message is already approved. Skipping duplicate host response.")
    else:
        conversations[thread_id].append({
            "role": "host",
            "sender": "AI Approved Response",
            "message": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        save_conversations(conversations)
        print(f"✅ AI Response Approved and Saved for Message: {last_guest_message}")

    return render_template("copy_redirect.html", ai_response=ai_response, airbnb_link=airbnb_app_link)


@responses_blueprint.route('/edit_response', methods=['GET'])
def edit_response():
    """Allows the user to edit the AI-generated response and view the full conversation."""
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

    # If no AI response was provided, attempt to reuse or generate one
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

                # Store it in conversation history (but not as "approved" yet)
                conversations[thread_id].append({
                    "role": "ai_generated",
                    "sender": "AI Pending Approval",
                    "message": ai_response,
                    "timestamp": datetime.utcnow().isoformat()
                })
                save_conversations(conversations)

    return render_template("edit_response.html", ai_response=ai_response, airbnb_link=airbnb_link, conversation_history=conversation_history)
