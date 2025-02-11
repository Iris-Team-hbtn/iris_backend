from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from flask import current_app
from app.data.prompts import system_prompt

def get_vs():
    with current_app.app_context():
        return current_app.config["vs"]


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
        # Usar un diccionario para almacenar el historial de chat por usuario
        self.chat_history = {" Hola, mi nombre es Iris, estoy aqui para ayudarte con tus consultas acerca de la estética capilar"}

    def call_iris(self, user_input, user_id):
        """
        Procesa la entrada del usuario a través del modelo Gemini manteniendo el historial del chat.

        Args:
            user_input (str): El mensaje de texto del usuario para ser procesado por el modelo.
            user_id (str): El identificador único del usuario.

        Returns:
            str: La respuesta generada por el modelo Gemini.

        Notas:
            - Mantiene el contexto de la conversación a través del chat_history
            - Cada interacción se almacena como un par usuario-asistente
            - Incluye el prompt del sistema en cada llamada
        """
        # Si el usuario no tiene historial de chat, inicializarlo
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []

        chat_history = self.chat_history[user_id]

        vs = get_vs()
        text = vs.search(user_input)
        print(vs)
        print(text)

        # Combina el prompt del sistema con el resultado de la búsqueda
        system_message_content = system_prompt() + "\n" + text
        print(system_message_content)
        system_message_content += "'\n Responde en formato Markdown"
        print("\n")
        print(system_message_content)
        messages = [{"role": "system", "content": system_message_content}]
        print('\n', messages)

        # Añadir el historial de chat a los mensajes
        for entry in chat_history:
            messages.append({"role": "assistant", "content": entry["assistant"]})
            messages.append({"role": "user", "content": entry["user"]})

        # Añadir el nuevo mensaje del usuario
        messages.append({"role": "user", "content": user_input})

        # Generar la respuesta utilizando gemini
        response = self.llm.invoke(messages)

        # Actualizar el historial de chat
        chat_history.append({"user": user_input, "assistant": response.content})
        self.chat_history[user_id] = chat_history

        return response.content

    def send_message(self, user_message, user_id):
        return self.call_iris(user_message, user_id)
