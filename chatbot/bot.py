from chatbot.database import get_answer_by_keyword
from chatbot.nlp import get_ai_response

def chatbot_response(user_input):
    answer = get_answer_by_keyword(user_input)
    if "Sorry" in answer:
        answer = get_ai_response(user_input)
    return answer
