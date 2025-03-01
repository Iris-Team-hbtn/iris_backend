from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
import markdown
from dotenv import load_dotenv
from collections import deque
from app.data.prompts import system_prompt
from app.services.toolkits import ToolkitService
from app.services.mail_service import MailService


class IrisAI:
    def __init__(self):
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0.7,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.toolkit = ToolkitService()
        self.mail_service = MailService()

    def _handle_email_request(self, user_input, user_id):
        """Maneja solicitudes de correo electrónico."""
        if not self.mail_service.validate_email(user_input):
            return "Formato de correo inválido. Por favor, ingresa uno válido."
        
        # Si el email es válido, procesar el envío (esto es solo un ejemplo)
        self.mail_service.send_email(user_id, user_input)
        return "Correo enviado con éxito."

    def format_response(self, text):
        """Convierte el texto de la IA a Markdown para mejor presentación."""
        return markdown.markdown(text)

    def call_iris(self, user_input, user_id):
        # Verificar si la consulta ya fue enviada
        if self.toolkit._has_query_been_sent(user_id, user_input):
            return "Ya hemos procesado esta consulta anteriormente. ¿Necesitas más información?"

        # Marcar la consulta como enviada
        self.toolkit._mark_query_as_sent(user_id, user_input)

        # Obtener historial de chat limitado
        chat_history = self.toolkit._load_chat_history(user_id)

        # Convertir a lista si es deque para evitar errores de serialización
        if isinstance(chat_history, deque):
            chat_history = list(chat_history)

        vs = self.toolkit.get_vs()
        text = vs.search(user_input) or "No encontré información relevante en la base de datos."

        system_message_content = system_prompt() + "\nFuente: protocoloIris.pdf\n" + "\n" + text

        messages = [SystemMessage(content=system_message_content)]

        for entry in chat_history:
            messages.append(HumanMessage(content=entry["user"]))
            messages.append(AIMessage(content=entry["assistant"]))

        messages.append(HumanMessage(content=user_input))

        # Generar respuesta
        response = self.llm.invoke(messages)

        # Convertir respuesta a Markdown
        formatted_response = self.format_response(response.content)

        # Guardar en historial
        chat_history.append({"user": user_input, "assistant": formatted_response})
        self.toolkit._save_chat_history(user_id, list(chat_history))

        return {"text": formatted_response}