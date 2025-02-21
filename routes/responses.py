from flask import Blueprint, request, redirect
import pyperclip
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Redirects to Airbnb's official web link, which automatically opens the app """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request.", 400

    # Copy AI response to clipboard
    try:
        pyperclip.copy(ai_response)
    except Exception as e:
        print(f"❌ Clipboard copy failed: {e}")

    # Extract Airbnb thread ID
    match = re.search(r'thread/(\d+)', airbnb_link)
    if match:
        thread_id = match.group(1)
        airbnb_web_link = f"https://www.airbnb.com/messaging/thread/{thread_id}"  # ✅ Official Airbnb Link
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to: {airbnb_web_link}")

    # Redirect to Airbnb's official web link, which should open the app automatically
    return redirect(airbnb_web_link, code=302)
