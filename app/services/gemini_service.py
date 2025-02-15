from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from app.data.prompts import system_prompt
from app.services.toolkits import ToolkitService

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
        self.toolkit = ToolkitService()  # Instancia de ToolkitService

    def call_iris(self, user_input, user_id):
        # Obtener historial de chat limitado
        chat_history = self.toolkit._load_chat_history(user_id)
        print(user_input)
        if not chat_history:
            welcome_message = {
                "user": "Hola Iris!",
                "assistant": "Hola! Soy Iris, una asistente virtual dedicada a ayudar a liberar tus consultas sobre Holberton Clinic!"
            }
            chat_history.append(welcome_message)
            self.toolkit.save_message(user_id, welcome_message["user"], welcome_message["assistant"])

        print(F"Chat history es: {chat_history}")
        print(self.toolkit.should_summarize(user_id))
        if self.toolkit.should_summarize(user_id):
            summary_prompt = "Resume brevemente el siguiente historial de conversación:"
            history_text = "\n".join(
                [f"Usuario: {e['user']}\nAsistente: {e['assistant']}" for e in chat_history]
            )
            print(f"history text es: {history_text}")
            summary_response = self.llm.invoke([SystemMessage(content=summary_prompt), HumanMessage(content=history_text)])
            print(summary_response)
            chat_history = summary_response.content

        # Obtener vector store y resultados de búsqueda
        vs = self.toolkit.get_vs()
        text = vs.search(user_input)

        # Construir mensajes
        system_message_content = system_prompt() + "\n" + text
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
        chat_history.append({"user": user_input, "assistant": response.content})
        self.toolkit._save_chat_history(user_id, chat_history)

        return response.content

    def send_message(self, user_message, user_id):
        return self.call_iris(user_message, user_id)
