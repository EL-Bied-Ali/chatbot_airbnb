from chatbot.database import add_faq, get_answer_by_keyword

# Adding an entry to the FAQ database
add_faq("What time is check-in?", "Check-in starts at 3 PM.", "check-in, arrival, timing")

# Searching for an answer using a keyword
response = get_answer_by_keyword("check-in")
print(response)  # Expected output: "Check-in starts at 3 PM."
