from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from flask import current_app
from app.data.prompts import system_prompt
from typing import List, Dict, Any

def get_vs() -> Any:
    with current_app.app_context():
        return current_app.config["vs"]

class IrisAI:
    def __init__(self) -> None:
        load_dotenv()
        self._google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
        self.llm: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0.7,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.chat_history: List[Dict[str, str]] = []

    def call_iris(self, user_input: str) -> str:
        """
        Procesa la entrada del usuario a través del modelo Gemini manteniendo el historial del chat.
        Este método toma la entrada del usuario, la combina con el prompt del sistema y el historial del chat,
        y genera una respuesta usando el modelo Gemini. El historial de la conversación se actualiza
        después de cada interacción.

        Args:
            user_input (str): El mensaje de texto del usuario para ser procesado por el modelo.

        Returns:
            str: La respuesta generada por el modelo Gemini.

        Notas:
            - Mantiene el contexto de la conversación a través del chat_history
            - Cada interacción se almacena como un par usuario-asistente
            - Incluye el prompt del sistema en cada llamada
        """
        system_message_content: str = system_prompt()
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_message_content}]
        
        # Añadir el historial de chat a los mensajes
        for entry in self.chat_history:
            messages.append({"role": "assistant", "content": entry["assistant"]})
            messages.append({"role": "user", "content": entry["user"]})
        
        # Añadir el nuevo mensaje del usuario
        messages.append({"role": "user", "content": user_input})
        
        # Generar la respuesta utilizando gemini
        response = self.llm.invoke(messages)
        
        # Actualizar el historial de chat
        self.chat_history.append({"user": user_input, "assistant": response.content})
        
        return response.content

    def send_message(self, user_message: str) -> str:
        return self.call_iris(user_message)
