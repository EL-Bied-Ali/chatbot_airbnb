import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TOGETHER_AI_KEY")

API_URL = "https://api.together.xyz/v1/completions"

# 🔹 Base de données des appartements
APPARTEMENTS = {
    "Bayside Luxe 2BR | Marina Dubai": {
        "transport": "À 5 minutes à pied de la station de métro et de plusieurs lignes de bus.",
        "insonorisation": "Isolation renforcée avec double vitrage.",
        "vue": "Vue panoramique sur la mer depuis le salon et le balcon.",
        "équipements": "Piscine, salle de sport, Wi-Fi rapide, cuisine équipée.",
        "règlement": "Interdiction de fumer, pas d'animaux, check-in entre 15h et 22h.",
        "sécurité": "Concierge 24h/24 et accès sécurisé avec code."
    }
}

def generate_response(client_message, appartement_nom):
    """ Génère une réponse IA en tenant compte des infos spécifiques de l'appartement si c'est pertinent """
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    # 🔹 On récupère les infos de l'appartement
    appartement_info = APPARTEMENTS.get(appartement_nom, {})
    details = "\n".join([f"{key}: {value}" for key, value in appartement_info.items()])

    # 📝 Prompt optimisé
    prompt = f"""Tu es un hôte Airbnb expérimenté.
    Réponds de manière professionnelle et amicale aux questions des clients.
    
    📍 Appartement : {appartement_nom}

    ✅ Si la question du client concerne les détails de l'appartement, utilise ces informations :
    {details}

    ❌ Si la question n'a rien à voir avec l'appartement, ignore les informations ci-dessus et réponds normalement.

    Client : "{client_message}"
    Hôte : """

    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.5,
        "top_p": 0.9,
        "stop": ["Client :"]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response_data = response.json()

    if "choices" in response_data and len(response_data["choices"]) > 0:
        return response_data["choices"][0]["text"].strip()
    else:
        return f"❌ Erreur: {response_data}"

# 🔹 Test avec un exemple de question hors sujet
if __name__ == "__main__":
    questions = [
        "L'appartement est-il proche des transports en commun ?",  # Doit répondre avec les infos du logement
        "Que penses-tu du climat à Dubaï ?",  # Doit ignorer les infos et répondre normalement
        "Quels sont les équipements de l'appartement ?",  # Doit utiliser les infos
        "As-tu des recommandations de restaurants ?"  # Doit ignorer les infos et répondre normalement
    ]

    appartement_nom = "Bayside Luxe 2BR | Marina Dubai"

    for question in questions:
        print(f"\n📩 **Question du client :** {question}")
        response = generate_response(question, appartement_nom)
        print(f"🤖 **Réponse de l'IA :** {response}")
