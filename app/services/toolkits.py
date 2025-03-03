import uuid
import os
import json
from flask import request, current_app, make_response
from collections import deque

# Maximum number of messages to keep in chat history
MAX_HISTORY = 5

class ToolkitService:
    # Set up base directory and history file path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HISTORY_FILE = os.path.join(BASE_DIR, "..", "data", "chat_history.json")

    def __init__(self):
        # Initialize dictionaries to store chat history, message counts, and sent queries
        self.chat_history = {}
        self.message_counter = {}
        self.sent_queries = {}

    def get_vs(self):
        # Get vector store from Flask app context
        with current_app.app_context():
            return current_app.config["vs"]

    def _load_chat_history(self, user_id):
        # Load chat history for a specific user from JSON file
        if not os.path.exists(self.HISTORY_FILE):
            return deque(maxlen=MAX_HISTORY)
        try:
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return deque(data.get(str(user_id), []), maxlen=MAX_HISTORY)
        except (json.JSONDecodeError, FileNotFoundError):
            return deque(maxlen=MAX_HISTORY)

    def _save_chat_history(self, user_id, chat_history):
        # Save chat history for a specific user to JSON file
        data = {}
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    pass
        # Update data with new chat history and increment message counter
        data[str(user_id)] = list(deque(chat_history, maxlen=MAX_HISTORY))
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.message_counter[user_id] = self.message_counter.get(user_id, 0) + 1

    def should_summarize(self, user_id):
        # Check if chat history should be summarized (every 3 messages)
        count = self.message_counter.get(user_id, 0)
        return count >= 3 and count % 3 == 0

    def _has_query_been_sent(self, user_id, query):
        # Check if a query has already been sent by this user
        if user_id not in self.sent_queries:
            return False
        return query in self.sent_queries[user_id]

    def _mark_query_as_sent(self, user_id, query):
        # Mark a query as sent for a specific user
        if user_id not in self.sent_queries:
            self.sent_queries[user_id] = set()
        self.sent_queries[user_id].add(query)

def get_or_create_user_id():
    # Get existing user ID from cookies or create a new one
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        resp = make_response()
        resp.set_cookie("user_id", user_id, max_age=24*60*60)  # Cookie expires in 24 hours
        return user_id, resp
    return user_id, None
