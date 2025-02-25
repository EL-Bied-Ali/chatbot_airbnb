from flask import Flask
from routes.gmail import gmail_blueprint
from routes.push_notifications import push_blueprint
from routes.responses import responses_blueprint
from routes.conversation import conversation_bp  
from routes.gmail_push import gmail_push_bp
from apscheduler.schedulers.background import BackgroundScheduler
from start_watch import start_gmail_watch


app = Flask(__name__)

# Register Blueprints (Modular Routes)
app.register_blueprint(gmail_blueprint)
app.register_blueprint(push_blueprint)
app.register_blueprint(responses_blueprint)
app.register_blueprint(conversation_bp, url_prefix="/conversation")  # Register new conversation routes
app.register_blueprint(gmail_push_bp)


def schedule_watch():
    try:
        print("Renewing Gmail watch...")
        start_gmail_watch()
        print("Gmail watch renewed successfully.")
    except Exception as e:
        print("Error renewing Gmail watch:", e)

# Set up the APScheduler
scheduler = BackgroundScheduler(daemon=True)
# Schedule the job to run every 6 days (Gmail watch typically expires in ~7 days)
scheduler.add_job(schedule_watch, 'interval', days=6)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)