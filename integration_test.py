import os
from server import app

# --- 1. Préparation du test : remplacer la fonction de récupération d'emails par une version factice ---
# Importer le module contenant la fonction originale
import routes.gmail as gmail_module

def fake_get_latest_airbnb_messages():
    """
    Retourne un faux email Airbnb pour simuler le flux complet.
    """
    return [{
        "airbnb_thread_id": "123456",
        "guest_name": "Test Guest",
        "message": "Est-ce que l'appartement est proche des transports en commun ?",
        "listing_name": "Bayside Luxe 2BR | Marina Dubai",
        "airbnb_link": "https://fr.airbnb.be/messaging/thread/123456",
        "message_timestamp": "2025-02-25 12:00:00 UTC"
    }]

# Remplacer la fonction de récupération d'emails par la version factice
gmail_module.get_latest_airbnb_messages = fake_get_latest_airbnb_messages

# --- 2. Exécution des tests via le client Flask ---
with app.test_client() as client:
    print("\n--- Test de l'endpoint /gmail_trigger ---")
    # Appeler l'endpoint qui simule la réception d'un email, la génération d'une réponse IA et l'envoi d'une notification
    response = client.post("/gmail_trigger")
    print("Statut :", response.status_code)
    print("Réponse :", response.get_data(as_text=True))

    print("\n--- Test de l'endpoint /prefill_message ---")
    # Simuler la validation de la réponse générée
    # On passe un faux paramètre 'response' (la réponse IA) et 'thread' (lien vers la conversation Airbnb)
    fake_ai_response = "Voici une réponse test générée par l'IA."
    fake_airbnb_link = "https://fr.airbnb.be/messaging/thread/123456"
    response = client.get("/prefill_message", query_string={"response": fake_ai_response, "thread": fake_airbnb_link})
    print("Statut :", response.status_code)
    print("Contenu :", response.get_data(as_text=True))
