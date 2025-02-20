from flask import Blueprint, request, render_template_string
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

    # Copy the AI-generated response to clipboard (for desktop)
    try:
        pyperclip.copy(ai_response)
    except Exception as e:
        print(f"❌ Clipboard copy failed: {e}")

    # Extract the Airbnb thread ID from the provided URL
    match = re.search(r'thread/(\d+)', airbnb_link)
    if match:
        thread_id = match.group(1)
        airbnb_app_link = f"airbnb://messaging/thread/{thread_id}"  # iOS & General Deep Link
        android_intent_link = f"intent://messaging/thread/{thread_id}#Intent;scheme=airbnb;package=com.airbnb.android;end;"  # Android Intent
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to Airbnb App: {airbnb_app_link}")

    # Return HTML & JavaScript to force the app open
    return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Opening Airbnb...</title>
            <script type="text/javascript">
                function openAirbnb() {{
                    var isAndroid = /Android/i.test(navigator.userAgent);
                    var isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);

                    if (isAndroid) {{
                        window.location.href = "{android_intent_link}";
                    }} else if (isIOS) {{
                        window.location.href = "{airbnb_app_link}";
                    }} else {{
                        alert("❌ Unable to open Airbnb app on this device.");
                    }}
                }}

                window.onload = openAirbnb;
            </script>
        </head>
        <body>
            <h2>Redirecting to Airbnb App...</h2>
        </body>
        </html>
    """)
