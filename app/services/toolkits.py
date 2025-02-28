import uuid
import os
import json
from flask import request, current_app
from flask import make_response
from collections import deque

MAX_HISTORY = 5

class ToolkitService:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HISTORY_FILE = os.path.join(BASE_DIR, "..", "data", "chat_history.json")

    def __init__(self):
        self.chat_history = {}  # Historial de usuarios
        self.message_counter = {}  # Contador de mensajes por usuario
        self.sent_queries = {}

    def get_vs(self):
        """Obtiene la instancia del vector store desde Flask."""
        with current_app.app_context():
            return current_app.config["vs"]

    def _load_chat_history(self, user_id):
        """Carga el historial desde un archivo JSON."""
        if not os.path.exists(self.HISTORY_FILE):
            return []
        try:
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get(str(user_id), [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_chat_history(self, user_id, chat_history):
        """Guarda el historial en un archivo JSON."""
        data = {}
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    pass
        data[str(user_id)] = deque(chat_history, maxlen=MAX_HISTORY)
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.message_counter[user_id] = self.message_counter.get(user_id, 0) + 1

    def should_summarize(self, user_id):
        """Determina si se debe resumir el historial."""
        count = self.message_counter.get(user_id, 0)
        return count >= 3 and count % 3 == 0

    def _has_query_been_sent(self, user_id, query):
        """Verifica si la consulta ya fue enviada por el usuario."""
        if user_id not in self.sent_queries:
            return False
        return query in self.sent_queries[user_id]

    def _mark_query_as_sent(self, user_id, query):
        """Marca una consulta como enviada."""
        if user_id not in self.sent_queries:
            self.sent_queries[user_id] = set()
        self.sent_queries[user_id].add(query)

def get_or_create_user_id():
    """Gestiona la creación/obtención de user_id mediante cookies."""
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        resp = make_response()
        resp.set_cookie("user_id", user_id, max_age=24*60*60)
        return user_id
    return user_id