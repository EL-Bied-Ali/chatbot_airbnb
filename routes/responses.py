from flask import Blueprint, request, render_template, redirect, render_template_string
import pyperclip
import re  # Import regex for extracting thread ID

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
    """ Opens Airbnb chat and copies the AI response to clipboard for easy pasting """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request.", 400

    # Copy the response to clipboard (works on desktop)
    try:
        pyperclip.copy(ai_response)
    except Exception as e:
        print(f"❌ Clipboard copy failed: {e}")

    # Ensure Airbnb link uses the correct messaging format
    match = re.search(r'(\d{9,})', airbnb_link)  # Extracts the thread ID (at least 9 digits)
    if match:
        thread_id = match.group(1)
        airbnb_link = f"https://www.airbnb.com/messaging/thread/{thread_id}"

    return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Open Airbnb Chat</title>
        </head>
        <body>
            <h2>Message Copied! Open Airbnb to Send</h2>
            <p>Your AI-generated message has been copied. Click below to open the Airbnb chat:</p>
            <a href="{airbnb_link}" target="_blank" style="font-size:20px; padding:10px; background-color:#007AFF; color:white; text-decoration:none;">Open in Browser</a>
            <br><br>
            <a href="airbnb://messaging/thread/{thread_id}" style="font-size:20px; padding:10px; background-color:#34A853; color:white; text-decoration:none;">Open in App (Mobile Only)</a>
        </body>
        </html>
    """)
