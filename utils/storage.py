import json
import os

CONVO_FILE = "conversations.json"

def load_conversations():
    if not os.path.exists(CONVO_FILE):
        return {}
    with open(CONVO_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_conversations(conversations):
    with open(CONVO_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, indent=4)

def sort_conversation(conversation):
    return sorted(conversation, key=lambda x: x["timestamp"])
