from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from app.data.prompts import system_prompt
from app.services.toolkits import ToolkitService
from datetime import datetime

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

    def call_iris(self, user_input, user_id):
        # Obtener historial de chat limitado
        chat_history = self.toolkit._load_chat_history(user_id)

        vs = self.toolkit.get_vs()
        text = vs.search(user_input) or "No encontré información relevante en la base de datos."

        system_message_content = system_prompt() + "\nFuente: protocoloIris.pdf\n" + "\n" + text + f". La fecha de hoy es {datetime.today().date()}"

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

        return response.content
