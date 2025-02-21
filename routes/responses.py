from flask import Blueprint, request, redirect
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Opens Airbnb chat directly in the app """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    # ✅ Debugging: Print received link
    print(f"🔗 Received Airbnb Link: {airbnb_link}")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request: Missing parameters.", 400

    # ✅ Ensure thread ID is extracted correctly
    match = re.search(r'thread/(\d+)', airbnb_link)
    if match:
        thread_id = match.group(1)
        # ✅ Keep the full Airbnb web link format with referral parameters
        airbnb_app_link = f"https://fr.airbnb.be/messaging/thread/{thread_id}?thread_type=home_booking&c=.pi80.pkaG9tZXNfbWVzc2FnaW5nL25ld19tZXNzYWdl&euid=819f8882-a06d-f4a6-da35-6b3b6f87be81"
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to Airbnb: {airbnb_app_link}")

    return redirect(airbnb_app_link, code=302)
