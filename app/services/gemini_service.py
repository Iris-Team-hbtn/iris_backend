from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from flask import Response, stream_with_context
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
            stream=True
        )
        self.toolkit = ToolkitService()  # Instancia de ToolkitService

    def call_iris(self, user_input, user_id):
        # Obtener historial de chat limitado
        chat_history = self.toolkit.get_chat_history(user_id)

        # Obtener vector store y resultados de búsqueda
        vs = self.toolkit.get_vs()
        text = vs.search(user_input) or "No encontré información relevante en la base de datos."

        # Construir mensajes
        system_message_content = system_prompt() + "\n" + text
        messages = [SystemMessage(content=system_message_content)]

        # Añadir historial de chat
        for entry in chat_history:
            messages.append(HumanMessage(content=entry["user"]))
            messages.append(AIMessage(content=entry["assistant"]))

        # Añadir mensaje actual
        messages.append(HumanMessage(content=user_input))

        # Generar streaming de respuesta
        def generate():
            response = self.llm.stream(messages)
            streamed_text = ""
            for chunk in response:
                content = chunk.content if chunk.content else ""
                streamed_text += content
                yield content  # Enviar fragmento al cliente
            
            # Guardar respuesta completa en historial
            self.toolkit.save_message(user_id, user_input, streamed_text)

        return Response(stream_with_context(generate()), content_type="text/plain")

    #     # Generar respuesta
    #     response = self.llm.invoke(messages)

    #     # Guardar en historial
    #     self.toolkit.save_message(user_id, user_input, response.content)

    #     return response.content

    # def send_message(self, user_message, user_id):
    #     return self.call_iris(user_message, user_id)
