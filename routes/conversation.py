from flask import Blueprint, request, jsonify, render_template
from utils.storage import load_conversations, save_conversations, sort_conversation
from datetime import datetime

conversation_bp = Blueprint("conversation", __name__)

@conversation_bp.route("/", methods=["GET"])
def get_conversation():
    """Retrieve conversation history sorted by timestamp."""
    thread_id = request.args.get("thread")
    conversations = load_conversations()
    return jsonify(sort_conversation(conversations.get(thread_id, [])))

@conversation_bp.route("/add", methods=["POST"])
def add_message():
    """Add a new message to the conversation."""
    data = request.json
    thread_id = data.get("thread_id")
    message = data.get("message")
    role = data.get("role", "guest")
    sender = data.get("sender", "Anonymous")
    airbnb_link = data.get("airbnb_link", None)  # ✅ Ensure Airbnb link is retrieved

    if not thread_id or not message:
        return jsonify({"error": "Missing data"}), 400

    conversations = load_conversations()
    if thread_id not in conversations:
        conversations[thread_id] = []

    new_message = {
        "role": role,
        "sender": sender,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

    if airbnb_link:  # ✅ Store the Airbnb link only if it exists
        new_message["airbnb_link"] = airbnb_link

    conversations[thread_id].append(new_message)

    # ✅ Keep only the last 100,000 messages
    if len(conversations[thread_id]) > 100000:
        conversations[thread_id] = conversations[thread_id][-100000:]

    save_conversations(conversations)  # ✅ Save the updated conversation
    return jsonify({"status": "Message added"})

@conversation_bp.route("/delete", methods=["POST"])
def delete_message():
    """Delete a specific message by timestamp."""
    data = request.json
    thread_id = data.get("thread_id")
    timestamp = data.get("timestamp")

    if not thread_id or not timestamp:
        return jsonify({"error": "Missing data"}), 400

    conversations = load_conversations()
    if thread_id in conversations:
        updated_conversation = [msg for msg in conversations[thread_id] if msg["timestamp"] != timestamp]

        if len(updated_conversation) < len(conversations[thread_id]):  # ✅ Message was found & deleted
            conversations[thread_id] = updated_conversation
            save_conversations(conversations)
            return jsonify({"status": "Message deleted"})
    
    return jsonify({"error": "Message not found"}), 404

@conversation_bp.route("/undo", methods=["POST"])
def undo_last_edit():
    """Undo the last message added."""
    data = request.json
    thread_id = data.get("thread_id")

    if not thread_id:
        return jsonify({"error": "Missing thread ID"}), 400

    conversations = load_conversations()
    if thread_id in conversations and conversations[thread_id]:
        last_message = conversations[thread_id].pop()  # ✅ Remove last message
        save_conversations(conversations)
        return jsonify({"status": "Undo successful", "removed": last_message})
    
    return jsonify({"error": "No messages to undo"}), 400

# ✅ Serve the edit response page
@conversation_bp.route("/edit_response", methods=["GET"])
def edit_response():
    return render_template("edit_response.html")

# ✅ Save edited AI response and return the Airbnb link dynamically
@conversation_bp.route("/edit_response/save", methods=["POST"])
def save_edited_response():
    """Edit AI response and retrieve Airbnb link dynamically from the latest message."""
    data = request.json
    thread_id = data.get("thread_id")
    new_message = data.get("message")

    if not thread_id or not new_message:
        return jsonify({"error": "Missing data"}), 400

    conversations = load_conversations()
    if thread_id in conversations and conversations[thread_id]:
        last_message = conversations[thread_id][-1]  # ✅ Get the last message
        last_message["message"] = new_message  # ✅ Update AI response

        # ✅ Retrieve the latest Airbnb link by checking all messages in the thread
        airbnb_link = None
        for msg in reversed(conversations[thread_id]):  # Loop from newest to oldest
            if "airbnb_link" in msg:
                airbnb_link = msg["airbnb_link"]
                break  # Stop when the first link is found

        save_conversations(conversations)

        return jsonify({
            "status": "Response edited",
            "airbnb_link": airbnb_link  # ✅ Send link back to frontend
        })

    return jsonify({"error": "Thread not found"}), 404


@conversation_bp.route("/extra_info", methods=["POST"])
def add_extra_info():
    """Receive additional apartment details."""
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
