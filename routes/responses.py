from flask import Blueprint, request, render_template_string
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

    # Extract thread ID from the URL
    match = re.search(r'(\d{9,})', airbnb_link)  # Extracts the thread ID (at least 9 digits)
    if match:
        thread_id = match.group(1)
        airbnb_app_link = f"airbnb://messaging/thread/{thread_id}"  # App Deep Link
        airbnb_web_link = f"https://www.airbnb.com/messaging/thread/{thread_id}"  # Web Fallback
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to Airbnb Chat: {airbnb_app_link}")

    # Return JavaScript that first tries to open the app, then falls back to web
    return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Opening Airbnb...</title>
            <script type="text/javascript">
                function openAirbnb() {{
                    var appLink = "{airbnb_app_link}";
                    var webLink = "{airbnb_web_link}";

                    // Try to open Airbnb app
                    window.location.href = appLink;

                    // If it fails, open the web version after 2 seconds
                    setTimeout(function() {{
                        window.location.href = webLink;
                    }}, 2000);
                }}

                window.onload = openAirbnb;
            </script>
        </head>
        <body>
            <h2>Redirecting to Airbnb...</h2>
            <p>If the app doesn't open, <a href="{airbnb_web_link}">click here</a> to open Airbnb in your browser.</p>
        </body>
        </html>
    """)
