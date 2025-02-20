import uuid
import os
import json
from flask import request, current_app
from flask import make_response
from collections import deque
from typing import List, Dict, Any

MAX_HISTORY = 5

class ToolkitService:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HISTORY_FILE = os.path.join(BASE_DIR, "..", "data", "chat_history.json")

    def __init__(self) -> None:
        self.chat_history: Dict[str, List[Dict[str, Any]]] = {}  # Historial de usuarios con límite
        self.message_counter: Dict[str, int] = {}  # Object by user_id, contains counter for summarize chat history

    def get_vs(self) -> Any:
        """Obtiene la instancia del vector store desde la configuración de Flask."""
        with current_app.app_context():
            return current_app.config["vs"]

    def _load_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Loads history chat from json file"""
        if not os.path.exists(self.HISTORY_FILE):
            return []

        with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return data.get(user_id, [])
            except json.JSONDecodeError:
                return []
            
    def _save_chat_history(self, user_id: str, chat_history: List[Dict[str, Any]]) -> None:
        """Saves modified chat history"""
        data: Dict[str, List[Dict[str, Any]]] = {}
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    pass

        data[user_id] = chat_history

        self.message_counter[user_id] = self.message_counter.get(user_id, 0) + 1

        with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def should_summarize(self, user_id: str) -> bool:
        """If counter its multiple of 3, it should summarize"""
        count = self.message_counter.get(user_id, 0)
        return count >= 3 and count % 3 == 0

def get_or_create_user_id() -> str:
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        resp = make_response()
        resp.set_cookie("user_id", user_id, max_age=24*60*60)  # Cookie por 1 día
        return user_id
    return user_id