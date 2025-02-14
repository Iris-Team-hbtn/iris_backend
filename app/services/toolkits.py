import uuid
from flask import request, current_app
from collections import deque

MAX_HISTORY = 100

class ToolkitService:
    def __init__(self):
        self.chat_history = {}  # Historial de usuarios con límite

    def get_vs(self):
        """Obtiene la instancia del vector store desde la configuración de Flask."""
        with current_app.app_context():
            return current_app.config["vs"]

    def save_message(self, user_id, user_message, assistant_message):
        """Guarda un mensaje en el historial del usuario con un límite."""
        if user_id not in self.chat_history:
            self.chat_history[user_id] = deque(maxlen=MAX_HISTORY)  # Cola con tamaño máximo
        
        self.chat_history[user_id].append({"user": user_message, "assistant": assistant_message})

    def get_chat_history(self, user_id):
        """Obtiene el historial del usuario si existe."""
        return list(self.chat_history.get(user_id, []))

# Función para obtener o crear un ID único para el usuario
def get_or_create_user_id():
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id
