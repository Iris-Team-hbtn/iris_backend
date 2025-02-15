import uuid
import os
import json
from flask import request, current_app
from collections import deque

MAX_HISTORY = 5

class ToolkitService:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HISTORY_FILE = os.path.join(BASE_DIR, "..", "data", "chat_history.json")

    def __init__(self):
        self.chat_history = {}  # Historial de usuarios con límite
        self.message_counter = {} #Object by user_id, contains counter for summarize chat history

    def get_vs(self):
        """Obtiene la instancia del vector store desde la configuración de Flask."""
        with current_app.app_context():
            return current_app.config["vs"]

    def _load_chat_history(self, user_id):
        """Loads history chat from json file"""
        if not os.path.exists(self.HISTORY_FILE):
            return []

        with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return data.get(str(user_id), [])
            except json.JSONDecodeError:
                return []
            
    def _save_chat_history(self, user_id, chat_history):
        """Saves modified chat history"""
        data = {}
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    pass

        data[str(user_id)] = chat_history

        self.message_counter[user_id] = self.message_counter.get(user_id, 0) + 1

        with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    
    def should_summarize(self, user_id):
        """If counter its multiple of 3, it should summarize"""
        count = self.message_counter.get(user_id, 0)
        return count >= 3 and count % 3 == 0

# Función para obtener o crear un ID único para el usuario
def get_or_create_user_id():
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id
