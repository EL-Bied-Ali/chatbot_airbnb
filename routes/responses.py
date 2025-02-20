from flask import Blueprint, request, redirect
import pyperclip
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Opens Airbnb chat and copies the AI response to clipboard for easy pasting in the app """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request.", 400

    # Copy the response to clipboard (works on desktop)
    try:
        pyperclip.copy(ai_response)
    except Exception as e:
        print(f"❌ Clipboard copy failed: {e}")

    # Extract thread ID from the URL and create the universal deep link
    match = re.search(r'(\d{9,})', airbnb_link)  # Extracts the thread ID (at least 9 digits)
    if match:
        thread_id = match.group(1)
        airbnb_deep_link = f"https://www.airbnb.com/messaging/thread/{thread_id}"
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to Airbnb Chat: {airbnb_deep_link}")

    # Redirect to the universal Airbnb chat link
    return redirect(airbnb_deep_link, code=302)
