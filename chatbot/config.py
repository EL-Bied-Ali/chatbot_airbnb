import os

# Path to Chrome user profile (replace with your actual path)
CHROME_PROFILE_PATH = r"C:\Users\casse\AppData\Local\Google\Chrome\User Data"

# Airbnb URLs
AIRBNB_INBOX_URL = "https://www.airbnb.com/guest/messages/"

# Hugging Face API Token (retrieved from environment variables)
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "your-placeholder-token")

# Other settings
WAIT_TIME = 5  # Time to wait for elements to load (seconds)
