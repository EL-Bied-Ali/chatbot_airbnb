from flask import Blueprint, request, redirect
import pyperclip
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Opens Airbnb chat directly in the app without passing through a browser """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request.", 400

    # Copy the AI-generated response to clipboard
    try:
        pyperclip.copy(ai_response)
    except Exception as e:
        print(f"❌ Clipboard copy failed: {e}")

    # Extract the Airbnb thread ID from the provided URL
    match = re.search(r'thread/(\d+)', airbnb_link)  # Extracts the numeric thread ID
    if match:
        thread_id = match.group(1)
        airbnb_app_link = f"airbnb://messaging/thread/{thread_id}"  # The correct deep link
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting directly to Airbnb App: {airbnb_app_link}")

    # Directly redirect to Airbnb app
    return redirect(airbnb_app_link, code=302)
