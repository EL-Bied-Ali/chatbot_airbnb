from push_notifications import send_push_notification

# Test Data
guest_name = "Youssef"
client_message = "How are you?"
ai_response = "Hello! I'm doing well, thank you for asking. How can I assist you today?"
airbnb_link = "https://fr.airbnb.be/messaging/thread/2055967410?thread_type=home_booking&c=.pi80.pkaG9tZXNfbWVzc2FnaW5nL25ld19tZXNzYWdl&euid=819f8882-a06d-f4a6-da35-6b3b6f87be81"

# Run test WITHOUT sending to PushBullet
send_push_notification(guest_name, client_message, ai_response, airbnb_link, test_mode=True)
