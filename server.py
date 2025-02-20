from flask import Flask
from routes.gmail import gmail_blueprint
from routes.push_notifications import push_blueprint
from routes.responses import responses_blueprint

app = Flask(__name__)

# Register Blueprints (Modular Routes)
app.register_blueprint(gmail_blueprint)
app.register_blueprint(push_blueprint)
app.register_blueprint(responses_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
