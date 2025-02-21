from flask import Blueprint, request, render_template_string
import pyperclip
import re

responses_blueprint = Blueprint('responses', __name__)

@responses_blueprint.route('/prefill_message', methods=['GET'])
def prefill_message():
    """ Forces Airbnb app to open using JavaScript for deep linking """
    ai_response = request.args.get("response", "")
    airbnb_link = request.args.get("thread", "#")

    if not ai_response or not airbnb_link:
        return "❌ Invalid request.", 400

    # Copy the AI-generated response to clipboard (for desktop users)
    try:
        pyperclip.copy(ai_response)
    except Exception as e:
        print(f"❌ Clipboard copy failed: {e}")

    # Extract the Airbnb thread ID
    match = re.search(r'thread/(\d+)', airbnb_link)
    if match:
        thread_id = match.group(1)
        airbnb_intent_link = f"intent://messaging/thread/{thread_id}#Intent;scheme=airbnb;package=com.airbnb.android;end;"  # ✅ Correct Intent Deep Link
    else:
        return "❌ Unable to extract Airbnb thread ID.", 400

    print(f"🔗 Redirecting to: {airbnb_intent_link}")

    # Return an HTML page with JavaScript to force the redirect
    return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Opening Airbnb...</title>
            <script type="text/javascript">
                function openAirbnb() {{
                    window.location.href = "{airbnb_intent_link}";
                }}
                window.onload = openAirbnb;
            </script>
        </head>
        <body>
            <h2>Redirecting to Airbnb App...</h2>
        </body>
        </html>
    """)
