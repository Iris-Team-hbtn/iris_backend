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
            stream=True  # Streaming activado
        )
        self.toolkit = ToolkitService()

    def call_iris(self, user_input, user_id):
        # Obtener historial de chat limitado
        chat_history = self.toolkit._load_chat_history(user_id)

        if not chat_history:
            welcome_message = {
                "user": "Hola Iris!",
                "assistant": "Hola! Soy Iris, una asistente virtual dedicada a ayudar a liberar tus consultas sobre Holberton Clinic!"
            }
            chat_history.append(welcome_message)

        if self.toolkit.should_summarize(user_id):
            summary_prompt = "Resume brevemente el siguiente historial de conversación, guardando información clave:"
            history_text = "\n".join(
                [f"Usuario: {e['user']}\nAsistente: {e['assistant']}" for e in chat_history]
            )
            print(f"history text es: {history_text}")
            summary_response = self.llm.invoke([SystemMessage(content=summary_prompt), HumanMessage(content=history_text)])
            print(summary_response)
            chat_history = [{"user": "Resumen", "assistant": summary_response.content}]

        vs = self.toolkit.get_vs()
        text = vs.search(user_input) or "No encontré información relevante en la base de datos."
        print(text)

        system_message_content = system_prompt() + "\nFuente: protocolo2.pdf\n" + "\n" + text
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

        return response.content  # Devuelve el generador
