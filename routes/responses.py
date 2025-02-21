from flask import Blueprint, request, redirect
import pyperclip
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Ouvre directement l'application Airbnb en utilisant un Intent Android """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request.", 400

    # Copier la réponse dans le presse-papier (si possible)
    try:
        pyperclip.copy(ai_response)
    except Exception as e:
        print(f"❌ Clipboard copy failed: {e}")

    # Extraire l'ID du thread Airbnb
    match = re.search(r'thread/(\d+)', airbnb_link)
    if match:
        thread_id = match.group(1)
        airbnb_intent_link = f"intent://messaging/thread/{thread_id}#Intent;scheme=airbnb;package=com.airbnb.android;end;"  # ✅ Intent Android
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirection vers: {airbnb_intent_link}")

    # Rediriger directement vers l'Intent Android
    return redirect(airbnb_intent_link, code=302)
