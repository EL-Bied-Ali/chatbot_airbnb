from flask import Flask, request, jsonify
from chatbot.database import add_faq, get_answer_by_keyword, init_db

# Initialize Flask app
app = Flask(__name__)

# Initialize the database within the app context
with app.app_context():
    init_db()

# Route to check if the API is running
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Chatbot API is running!"}), 200

# Endpoint to add a new FAQ entry
@app.route('/add_faq', methods=['POST'])
def add_faq_entry():
    data = request.get_json()

    if not data or 'question' not in data or 'answer' not in data or 'keywords' not in data:
        return jsonify({"error": "Invalid input. Provide 'question', 'answer', and 'keywords'."}), 400

    add_faq(data['question'], data['answer'], data['keywords'])
    return jsonify({"message": "FAQ added successfully!"}), 201

# Endpoint to get an answer based on a keyword
@app.route('/ask', methods=['GET'])
def ask_question():
    keyword = request.args.get('keyword')
    
    if not keyword:
        return jsonify({"error": "Keyword is required."}), 400
    
    answer = get_answer_by_keyword(keyword)
    return jsonify({"answer": answer})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
