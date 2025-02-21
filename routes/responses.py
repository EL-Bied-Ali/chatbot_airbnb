from flask import Blueprint, request, redirect, render_template
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Opens Airbnb chat directly in the app """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    print(f"🔗 Received Airbnb Link in prefill_message: {airbnb_link}")

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


@responses_blueprint.route('/edit_response', methods=['GET', 'POST'])
def edit_response():
    """ Allows user to edit AI-generated response and view full conversation """
    if request.method == "POST":
        edited_response = request.form.get("edited_response", "").strip()
        additional_notes = request.form.get("additional_notes", "").strip()
        airbnb_link = request.form.get("thread", "#")

        print(f"📥 Received Edited Response: {edited_response}")
        print(f"📝 Additional Notes: {additional_notes}")
        print(f"🔗 Received Airbnb Link in edit_response: {airbnb_link}")

        try:
            pyperclip.copy(edited_response)
        except Exception as e:
            print(f"❌ Clipboard copy failed: {e}")

        return "✅ Response updated successfully. Notes saved.", 200

    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    print(f"🔗 Received Airbnb Link in edit_response: {airbnb_link}")

    return render_template("edit_response.html", ai_response=ai_response, airbnb_link=airbnb_link)
