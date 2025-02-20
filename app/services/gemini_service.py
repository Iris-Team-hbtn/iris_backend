from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from app.data.prompts import system_prompt
from app.services.toolkits import ToolkitService
from app.services.mail_service import MailService  # Importamos MailService

class IrisAI:

    def __init__(self):
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0.5,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # stream=True  # Si quieres agregar Streaming descomenta esta linea
        )
        self.toolkit = ToolkitService()
        self.mail_service = MailService()  # Instanciamos MailService

    def call_iris(self, user_input, user_id, user_email=None):
        """Genera una respuesta estructurada y, si es necesario, envía un correo con más información."""

        # Obtener historial de chat
        chat_history = self.toolkit._load_chat_history(user_id)

        if not chat_history:
            welcome_message = {
                "user": "Hola Iris!",
                "assistant": "¡Hola! Soy Iris, tu asistente virtual. ¿En qué puedo ayudarte hoy?"
            }
            chat_history.append(welcome_message)

        # Resumen del historial si es necesario
        if self.toolkit.should_summarize(user_id):
            summary_prompt = "Resume brevemente el siguiente historial de conversación, manteniendo los puntos clave:"
            history_text = "\n\n".join(
                [f"Usuario: {e['user']}\nAsistente: {e['assistant']}" for e in chat_history]
            )
            summary_response = self.llm.invoke([
                SystemMessage(content=summary_prompt),
                HumanMessage(content=history_text)
            ])
            chat_history = [{"user": "Resumen", "assistant": summary_response.content}]

        # Obtener información relevante desde FAISS
        vs = self.toolkit.get_vs()
        text = vs.search(user_input)

        # Asegurar formato legible de la información recuperada
        if text:
            formatted_text = "\n\n🔹 Información relacionada:\n" + text.replace(".", ".\n")
        else:
            formatted_text = "No encontré información relevante en la base de datos."

        # Mensaje del sistema con contexto
        system_message_content = f"{system_prompt()}\n\nFuente: protocolo2.pdf\n{formatted_text}"

        # Construcción del mensaje para la IA
        messages = [SystemMessage(content=system_message_content)]

        for entry in chat_history:
            messages.append(HumanMessage(content=entry["user"]))
            messages.append(AIMessage(content=entry["assistant"]))

        messages.append(HumanMessage(content=user_input))

        # Generar respuesta
        response = self.llm.invoke(messages)

        # Guardar en historial
        chat_history.append({"user": user_input, "assistant": response.content})
        self.toolkit._save_chat_history(user_id, chat_history)

        # Si la respuesta menciona "más información" y hay un correo, enviamos un email
        if ("más información" or "contactar humano") in response.content.lower() and user_email:
            subject = "Más información sobre tu consulta"
            email_body = f"Hola, aquí tienes más detalles sobre tu consulta:\n\n{response.content}"
            self.mail_service.send_email("info_request",subject, email_body, user_email)

        return response.content  # Respuesta en formato legible
