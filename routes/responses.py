from flask import Blueprint, request, redirect, render_template
import pyperclip
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/edit_response', methods=['GET', 'POST'])
def edit_response():
    """ Allows the user to edit the AI response before sending """
    if request.method == 'GET':
        ai_response = request.args.get("response", "")
        airbnb_link = request.args.get("thread", "#")
        return render_template("edit_form.html", ai_response=ai_response, airbnb_link=airbnb_link)

    if request.method == 'POST':
        edited_response = request.form["edited_response"]
        new_info = request.form.get("new_info", "")
        airbnb_link = request.form["airbnb_link"]

        if new_info:
            with open("apartment_updates.txt", "a") as file:
                file.write(f"{new_info}\n")

        print(f"✅ Sending edited response: {edited_response}")
        print(f"🔗 Airbnb Thread: {airbnb_link}")

        return "✅ Message sent with edits!", 200

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

    # Extract thread ID from the URL and create a deep link for the Airbnb app
    match = re.search(r'(\d{9,})', airbnb_link)  # Extracts the thread ID (at least 9 digits)
    if match:
        thread_id = match.group(1)
        airbnb_deep_link = f"airbnb://messaging/thread/{thread_id}"
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to Airbnb App: {airbnb_deep_link}")

    # Redirect directly to the Airbnb app
    return redirect(airbnb_deep_link, code=302)
