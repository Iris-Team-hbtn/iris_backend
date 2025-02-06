from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from flask import current_app

def get_vs():
    with current_app.app_context():
        return current_app.config["vs"]

class IrisAI:
    def __init__(self):
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=1,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.chat_history = "Iris: ¡Hola! Mi nombre es Iris, estoy aquí para responder cualquier duda que tengas sobre nuestros tratamientos en Holberton.\n"

    def send_message(self, user_message):
        vs = get_vs()
        text = vs.search(user_message)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Tu eres Iris, una asistente virtual que asiste a una clínica de estética real llamada Holberton, usuarios te harán preguntas sobre los tratamientos de la clínica, debes responder desarrollando con la siguiente información: {text}. Debes seguir el hilo de la conversación, el historial de la conversación es: {chat_history}",
                ),
                ("human", "{input}"),
            ]
        )
        chain = prompt | self.llm
        response = chain.invoke(
            {
                "chat_history": self.chat_history,
                "text": text,
                "input": user_message,
            }
        )
        self.chat_history += f"Human: {user_message}\n"
        self.chat_history += f"Iris: {response.content}\n"
        return response.content
