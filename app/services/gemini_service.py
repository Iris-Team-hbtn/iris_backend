from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from flask import current_app
from app.data.prompts import system_prompt
from collections import deque

# Límite de mensajes en el historial por usuario
MAX_HISTORY = 5  

class IrisAI:
    def __init__(self):
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=1,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.chat_history = {}  # Diccionario con historial limitado por usuario

    def get_vs(self):
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

    def call_iris(self, user_input, user_id):
        # Obtener historial de chat limitado
        chat_history = self.get_chat_history(user_id)

        # Obtener vector store y resultados de búsqueda
        vs = self.get_vs()
        text = vs.search(user_input)

        # Construir mensajes
        system_message_content = system_prompt() + "\n" + text + "\nResponde en formato Markdown"
        messages = [SystemMessage(content=system_message_content)]

        # Añadir historial de chat
        for entry in chat_history:
            messages.append(HumanMessage(content=entry["user"]))
            messages.append(AIMessage(content=entry["assistant"]))

        # Añadir mensaje actual
        messages.append(HumanMessage(content=user_input))

        # Generar respuesta
        response = self.llm.invoke(messages)

        # Guardar en historial
        self.save_message(user_id, user_input, response.content)

        return response.content

    def send_message(self, user_message, user_id):
        return self.call_iris(user_message, user_id)
