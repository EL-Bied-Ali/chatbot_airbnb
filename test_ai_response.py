import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TOGETHER_AI_KEY")

API_URL = "https://api.together.xyz/v1/completions"

# 🔹 Database of apartment details
APPARTEMENTS = {
    "Bayside Luxe 2BR | Marina Dubai": {
        "transport": "5-minute walk to the metro station and multiple bus lines.",
        "soundproofing": "Enhanced insulation with double-glazed windows.",
        "view": "Panoramic sea view from the living room and balcony.",
        "amenities": "Swimming pool, gym, high-speed Wi-Fi, fully equipped kitchen.",
        "rules": "No smoking, no pets, check-in between 3 PM and 10 PM.",
        "security": "24/7 concierge and secure access with code."
    }
}

def generate_response(client_message, appartement_nom):
    """ Generates an AI response considering the apartment's details if relevant """
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    # 🔹 Fetch apartment details
    appartement_info = APPARTEMENTS.get(appartement_nom, {})
    details = "\n".join([f"{key}: {value}" for key, value in appartement_info.items()])

    # 📝 Optimized Prompt in English
    prompt = f"""You are a professional Airbnb host. 
    Respond in a polite and friendly manner to guest inquiries.

    📍 Apartment: {appartement_nom}

    ✅ If the guest's question is related to the apartment, use the following information:
    {details}

    ❌ If the question is unrelated to the apartment, ignore the above details and provide a general response.

    Guest: "{client_message}"
    Host:"""

    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.5,
        "top_p": 0.9,
        "stop": ["Guest:"]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response_data = response.json()

    if "choices" in response_data and len(response_data["choices"]) > 0:
        return response_data["choices"][0]["text"].strip()
    else:
        return f"❌ Error: {response_data}"

# 🔹 Test with different guest questions
if __name__ == "__main__":
    questions = [
        "Is the apartment close to public transport?",  # Should respond with relevant details
        "What do you think about the weather in Dubai?",  # Should ignore apartment details
        "What amenities does the apartment offer?",  # Should list apartment features
        "Can you recommend any good restaurants nearby?"  # Should ignore apartment details
    ]

    appartement_nom = "Bayside Luxe 2BR | Marina Dubai"

    for question in questions:
        print(f"\n📩 **Guest Question:** {question}")
        response = generate_response(question, appartement_nom)
        print(f"🤖 **AI Response:** {response}")
