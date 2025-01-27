import sqlite3  # Importing SQLite library to handle database operations
from fuzzywuzzy import process


# Function to initialize the database and create the 'faq' table if it doesn't exist
def init_db():
    # Connect to the SQLite database (creates a new file if it doesn't exist)
    conn = sqlite3.connect('chatbot_airbnb.db')
    cursor = conn.cursor()

    # SQL query to create the FAQ table with necessary columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for each entry
            question TEXT NOT NULL,                -- The question asked by the user
            answer TEXT NOT NULL,                  -- The predefined response
            keywords TEXT NOT NULL,                -- Keywords for quick search
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of entry creation
        )
    ''')
    
    # Save changes and close the connection
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Function to add a new question-answer pair to the database
def add_faq(question, answer, keywords):
    # Connect to the database
    conn = sqlite3.connect('chatbot_airbnb.db')
    cursor = conn.cursor()

    # SQL query to insert the provided question, answer, and keywords
    cursor.execute('''
        INSERT INTO faq (question, answer, keywords) VALUES (?, ?, ?)
    ''', (question, answer, keywords))

    # Save changes and close the connection
    conn.commit()
    conn.close()
    print("FAQ entry added successfully.")

# Function to fetch an answer based on keywords provided by the user with fallback mechanism
def get_answer_by_keyword(keyword):
    conn = sqlite3.connect('chatbot_airbnb.db')
    cursor = conn.cursor()

    # Search for exact keyword match
    cursor.execute("SELECT answer FROM faq WHERE keywords LIKE ?", ('%' + keyword.lower() + '%',))
    result = cursor.fetchone()

    if result:
        conn.close()
        return result[0]

    # If no exact match, look for similar keywords
    cursor.execute("SELECT keywords FROM faq")
    keywords_list = [row[0] for row in cursor.fetchall()]
    
    if keywords_list:
        closest_match, score = process.extractOne(keyword, keywords_list)

        # If similarity is above threshold, suggest similar question
        if score > 60:
            conn.close()
            return f"Did you mean: {closest_match}? Please try again."

    conn.close()
    return "Sorry, I don't have an answer to that. Please contact support for more details."

# Entry point to initialize the database when this script is run directly
if __name__ == "__main__":
    init_db()  # Call the function to create the database and table
