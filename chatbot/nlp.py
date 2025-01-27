from transformers import pipeline

# Load a lightweight question-answering model from Hugging Face
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

def get_ai_response(question):
    context = """
    Welcome to our Airbnb. We offer free WiFi, check-in starts at 3 PM, and check-out is before 11 AM.
    Pets are not allowed, and our customer support is available 24/7.
    """
    result = qa_pipeline(question=question, context=context)
    return result['answer']
