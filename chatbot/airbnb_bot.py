from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chatbot.config as config  # Import global config variables
from chatbot.database import get_answer_by_keyword  # Import the response function from database.py

def open_airbnb_inbox():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-data-dir={config.CHROME_PROFILE_PATH}")
    chrome_options.add_argument("--profile-directory=Default")

    # Suppress unnecessary logs
    chrome_options.add_argument("--log-level=3")  # Reduces logging to warnings/errors only
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppresses DevTools warnings
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Hides automation flag

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(config.AIRBNB_INBOX_URL)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-name="message-content-wrapper"]'))
        )
        print("Inbox page loaded successfully!")
    except TimeoutException:
        print("Failed to verify inbox page.")
        driver.save_screenshot("debug_screenshot.png")

    return driver


def read_last_client_message(driver):
    """
    Extract the last client message from the Airbnb inbox.
    """
    try:
        # Locate all message wrappers
        messages = driver.find_elements(By.CSS_SELECTOR, '[data-name="message-content-wrapper"]')

        last_client_message = None

        for wrapper in messages:
            # Check the speaker using attributes or text patterns
            if "Read by Youssef" in wrapper.text:  # Replace "Youssef" with your actual name or indicator
                continue  # Skip messages sent by you (host)

            # Save the last client's message
            last_client_message = wrapper.text

        if last_client_message:
            print(f"Last client message: {last_client_message}")
            return last_client_message
        else:
            print("No client messages found.")
            return None

    except Exception as e:
        print(f"Error occurred while reading messages: {e}")
        return None

def type_response(driver, response):
    """
    Type the response into the text input box on Airbnb.
    """
    try:
        # Locate the text input box
        input_box = driver.find_element(By.TAG_NAME, "textarea")  # Adjust selector if necessary
        
        # Type the response into the textbox
        input_box.clear()
        input_box.send_keys(response)
        print(f"Typed response: {response}")
    except Exception as e:
        print(f"Error occurred while typing response: {e}")

def handle_last_message(driver):
    """
    Process the last client message and type an appropriate response.
    """
    # Get the last client message
    last_message = read_last_client_message(driver)

    if not last_message:
        print("No client message to respond to.")
        return

    # Use the imported get_answer_by_keyword function to determine the response
    response = get_answer_by_keyword(last_message)
    if not response:
        response = "Thank you for your message! I'll get back to you shortly."

    # Type the response into the text box
    type_response(driver, response)

if __name__ == "__main__":
    driver = open_airbnb_inbox()

    # Handle only the last client message
    handle_last_message(driver)

    input("Press Enter to close the browser...")
    driver.quit()
