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

    def stream_response(self, user_input, user_id):
        """Genera respuestas en streaming con Gemini, con formato Markdown."""
        chat_history = self.toolkit.get_chat_history(user_id)

        vs = self.toolkit.get_vs()
        text = vs.search(user_input) or "No encontré información relevante en la base de datos."
        print(text)

        system_message_content = system_prompt() + "\nFuente: protocolo2.pdf\n" + "\n" + text
        messages = [SystemMessage(content=system_message_content)]

        for entry in chat_history:
            messages.append(HumanMessage(content=entry["user"]))
            messages.append(AIMessage(content=entry["assistant"]))

        messages.append(HumanMessage(content=user_input))

        def generate_stream():
            streamed_text = ""
            for chunk in self.llm.stream(messages):
                content = chunk.content if chunk.content else ""
                
                # 🔹 Ajustamos el formato para que se vea como Gemini
                if "**" in content or "*" in content or "-" in content:
                    formatted_chunk = content  # Ya tiene formato
                else:
                    formatted_chunk = f"\n{content}"  # Agregamos saltos de línea
                
                streamed_text += formatted_chunk
                yield formatted_chunk

            self.toolkit.save_message(user_id, user_input, streamed_text)

        return generate_stream()  # Devuelve el generador
