from flask import Blueprint, request, render_template
import pyperclip
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/edit_response', methods=['GET', 'POST'])
def edit_response():
    """ Allows user to edit AI-generated response and add extra apartment notes before sending """
    if request.method == "POST":
        edited_response = request.form.get("edited_response", "").strip()
        additional_notes = request.form.get("additional_notes", "").strip()
        airbnb_link = request.form.get("thread", "#")

        # Save additional notes somewhere (To-Do: Implement storage mechanism)
        print(f"📥 Received Edited Response: {edited_response}")
        print(f"📝 Additional Notes: {additional_notes}")
        print(f"🔗 Airbnb Link: {airbnb_link}")

        # Copy edited response to clipboard for convenience
        try:
            pyperclip.copy(edited_response)
        except Exception as e:
            print(f"❌ Clipboard copy failed: {e}")

        return "✅ Response updated successfully. Notes saved.", 200

    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    return render_template("edit_response.html", ai_response=ai_response, airbnb_link=airbnb_link)
