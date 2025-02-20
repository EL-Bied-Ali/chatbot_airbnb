from flask import Blueprint, request, render_template, redirect, render_template_string
import pyperclip

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

    # Ensure Airbnb link uses deep linking format for mobile
    if "airbnb.com/messaging/thread" in airbnb_link:
        airbnb_link = airbnb_link.replace("https://www.airbnb.com", "airbnb://")
        airbnb_link = airbnb_link.replace("https://fr.airbnb.com", "airbnb://")
        airbnb_link = airbnb_link.replace("https://airbnb.com", "airbnb://")

    # Return a page with a clickable link
    return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Open Airbnb Chat</title>
        </head>
        <body>
            <h2>Message Copied! Open Airbnb to Send</h2>
            <p>Your AI-generated message has been copied. Click below to open the Airbnb chat:</p>
            <a href="{airbnb_link}" style="font-size:20px; padding:10px; background-color:#007AFF; color:white; text-decoration:none;">Open Airbnb Chat</a>
        </body>
        </html>
    """)
