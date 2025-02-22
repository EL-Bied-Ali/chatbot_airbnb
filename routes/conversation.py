from flask import Blueprint, request, jsonify, render_template
from utils.storage import load_conversations, save_conversations, sort_conversation
from datetime import datetime

conversation_bp = Blueprint("conversation", __name__)

@conversation_bp.route("/", methods=["GET"])
def get_conversation():
    """Retrieve conversation history for a specific thread ID."""
    thread_id = request.args.get("thread")
    conversations = load_conversations()
    return jsonify(sort_conversation(conversations.get(thread_id, []))) if thread_id in conversations else jsonify([])

@conversation_bp.route("/add", methods=["POST"])
def add_message():
    """Add a new message to a specific thread's conversation."""
    data = request.json
    thread_id = data.get("thread_id")
    message = data.get("message")
    role = data.get("role", "guest")
    sender = data.get("sender", "Anonymous")
    airbnb_link = data.get("airbnb_link", None)

    if not thread_id or not message:
        return jsonify({"error": "Missing data"}), 400

    conversations = load_conversations()
    if thread_id not in conversations:
        conversations[thread_id] = []

    new_message = {
        "role": role,
        "sender": sender,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if airbnb_link:
        new_message["airbnb_link"] = airbnb_link

    conversations[thread_id].append(new_message)

    # Keep only the last 100,000 messages per thread
    if len(conversations[thread_id]) > 100000:
        conversations[thread_id] = conversations[thread_id][-100000:]

    save_conversations(conversations)
    return jsonify({"status": "Message added"})

@conversation_bp.route("/approve", methods=["POST"])
def approve_response():
    """Save an approved AI response into the conversation history."""
    data = request.json
    thread_id = data.get("thread_id")
    approved_message = data.get("message")

    if not thread_id or not approved_message:
        return jsonify({"error": "Missing data"}), 400

    conversations = load_conversations()
    if thread_id not in conversations:
        conversations[thread_id] = []

    new_message = {
        "role": "host",
        "sender": "AI Approved Response",
        "message": approved_message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    conversations[thread_id].append(new_message)
    save_conversations(conversations)

    return jsonify({"status": "AI response approved and saved"})

@conversation_bp.route("/edit_response", methods=["GET"])
def edit_response():
    """Serve the edit response page."""
    return render_template("edit_response.html")

@conversation_bp.route("/edit_response/save", methods=["POST"])
def save_edited_response():
    """Edit AI response and store it in conversation history, retrieving the Airbnb link dynamically."""
    data = request.json
    thread_id = data.get("thread_id")
    new_message = data.get("message")

    if not thread_id or not new_message:
        return jsonify({"error": "Missing data"}), 400

    conversations = load_conversations()
    if thread_id in conversations and conversations[thread_id]:
        last_message = conversations[thread_id][-1]
        last_message["message"] = new_message

        # Retrieve the latest Airbnb link from the thread's history
        airbnb_link = None
        for msg in reversed(conversations[thread_id]):
            if "airbnb_link" in msg:
                airbnb_link = msg["airbnb_link"]
                break

        save_conversations(conversations)

        return jsonify({
            "status": "Response edited",
            "airbnb_link": airbnb_link
        })

    return jsonify({"error": "Thread not found"}), 404

@conversation_bp.route("/extra_info", methods=["POST"])
def add_extra_info():
    """Receive and store additional apartment details in the conversation."""
    data = request.json
    thread_id = data.get("thread_id")
    extra_info = data.get("extra_info")

    if not thread_id or not extra_info:
        return jsonify({"error": "Missing data"}), 400

    conversations = load_conversations()
    if thread_id not in conversations:
        conversations[thread_id] = []

    conversations[thread_id].append({
        "role": "host",
        "sender": "Host",
        "message": f"Extra Info: {extra_info}",
        "timestamp": datetime.utcnow().isoformat()
    })

    save_conversations(conversations)
    return jsonify({"status": "Extra info added"})
