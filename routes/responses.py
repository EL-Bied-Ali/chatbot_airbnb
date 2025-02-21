from flask import Blueprint, request, redirect
import pyperclip
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Redirects to the old Airbnb URL format to force the app to open """
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
        # ✅ Restore the old working Airbnb URL format
        airbnb_web_link = f"https://fr.airbnb.be/messaging/thread/{thread_id}?thread_type=home_booking&c=.pi80.pkaG9tZXNfbWVzc2FnaW5nL25ld19tZXNzYWdl&euid=819f8882-a06d-f4a6-da35-6b3b6f87be81"
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to: {airbnb_web_link}")

    # Redirect directly to the Airbnb web link (which should open the app)
    return redirect(airbnb_web_link, code=302)
