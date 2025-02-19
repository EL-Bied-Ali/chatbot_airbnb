import base64
import re
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# 🔹 Gmail API scope (read-only)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """ Authenticate with Gmail API """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_latest_airbnb_messages():
    """ Fetch latest email from Airbnb Express in Gmail """
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    # 🔍 Recherche des emails de express@airbnb.com
    query = 'from:express@airbnb.com'
    results = service.users().messages().list(userId="me", q=query, maxResults=1).execute()
    messages = results.get("messages", [])

    if not messages:
        print("📭 Aucun email trouvé de express@airbnb.com.")
        return []

    airbnb_messages = []
    
    for msg in messages:
        message = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = message.get("payload", {})

        # Décodage du contenu de l'email
        msg_body = None
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/html":
                    msg_body = part["body"].get("data")
                    break
        else:
            msg_body = payload.get("body", {}).get("data")

        if msg_body:
            try:
                decoded_msg = base64.urlsafe_b64decode(msg_body).decode("utf-8", errors="ignore")
            except Exception as e:
                print(f"❌ Erreur de décodage: {e}")
                decoded_msg = ""

            extracted_data = extract_airbnb_details(decoded_msg)
            if extracted_data:
                airbnb_messages.append(extracted_data)

    return airbnb_messages

def extract_airbnb_details(email_html):
    """ Extract key information from an Airbnb email using BeautifulSoup """
    soup = BeautifulSoup(email_html, "html.parser")
    email_text = soup.get_text()

    print("\n🔎 EMAIL BRUT :\n", email_text[:1000])  # Affiche les 1000 premiers caractères pour analyser

    # 🔹 Extraction du nom de l'invité (éviter l'hôte)
    guest_name = None
    guest_match = re.search(r"Voyageurs\d*\s*personne", email_text)
    if guest_match:
        prev_text = email_text[:guest_match.start()]
        last_name_match = re.findall(r"\b[A-Z][a-z]+\b", prev_text)
        if last_name_match:
            guest_name = last_name_match[-1]  # Dernier mot trouvé

    # 🔹 Extraction du message du client
    message = None
    if guest_name:
        message_match = re.search(rf"{guest_name}\s*(.*?)\s*Réserver", email_text, re.DOTALL)
        if message_match:
            message = message_match.group(1).strip()

    # 🔹 Extraction du logement
    listing_name = None
    listing_match = re.search(r"Détails de la réservation\s*(.*?)\s*(Appartement|Voyageurs)", email_text, re.DOTALL)
    if listing_match:
        listing_name = listing_match.group(1).strip()

    # 🔹 Extraction des dates de réservation
    dates_match = re.search(r"Arrivée.*?(\d{1,2} \w+ \d{4}).*?Départ.*?(\d{1,2} \w+ \d{4})", email_text, re.DOTALL)
    reservation_dates = None
    if dates_match:
        reservation_dates = f"{dates_match.group(1)} to {dates_match.group(2)}"

    # Vérification des données
    guest_name = guest_name if guest_name else "Inconnu"
    listing_name = listing_name if listing_name else "Non spécifié"
    reservation_dates = reservation_dates if reservation_dates else "Non spécifié"
    message = message if message else "Aucun message trouvé"
    
    # 🔹 Extraction du lien contenu dans "Répondre"
    airbnb_link = None
    reply_button = soup.find("a", string=re.compile(r"Répondre", re.IGNORECASE))  # Trouver le bouton Répondre
    if reply_button and reply_button.has_attr("href"):
        airbnb_link = reply_button["href"]

    # 🔹 Extraction de l'ID de la conversation Airbnb
    airbnb_thread_id = None
    if airbnb_link:
        thread_match = re.search(r"thread/(\d+)", airbnb_link)
        if thread_match:
            airbnb_thread_id = thread_match.group(1)

    return {
        "guest_name": guest_name,
        "listing_name": listing_name,
        "reservation_dates": reservation_dates,
        "message": message,
        "airbnb_link": airbnb_link,  # 🔹 Lien direct vers la conversation
        "airbnb_thread_id": airbnb_thread_id  # 🔹 ID unique de la discussion Airbnb
    }



if __name__ == "__main__":
    messages = get_latest_airbnb_messages()
    for msg in messages:
        print("\n📩 **New Airbnb Message**")
        print(f"👤 Guest: {msg['guest_name']}")
        print(f"🏡 Listing: {msg['listing_name']}")
        print(f"📅 Dates: {msg['reservation_dates']}")
        print(f"💬 Message: {msg['message']}")
        print(f"🔗 Lien vers la conversation Airbnb: {msg.get('airbnb_link', '❌ Aucun lien trouvé')}")
        print(f"🆔 ID de la discussion Airbnb: {msg.get('airbnb_thread_id', '❌ Aucun ID trouvé')}")


