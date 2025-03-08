from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv
from app.services.toolkits import ToolkitService
from datetime import datetime

class ObjectCreator:

    def __init__(self):
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.toolkit = ToolkitService()

    def date_object(self, user_input, user_id):
        chat_history = self.toolkit._load_chat_history(user_id) or "No hay historial de chat"
        
        # We get data from user input and create a JSON object
        system_prompt = """
        Tu tarea es generar SOLO un objeto JSON con la información del usuario, sin ningún texto adicional.
        No supongas datos, si no los tienes no generes el objeto.
        El formato estricto del objeto debe ser:

        {
            "fullname": string,
            "email": string,
            "day": int,
            "month": int,
            "year": int,
            "starttime": int
        }

        Fullname es el nombre del usuario
        Email es el email del usuario
        Day es el día del mes en número
        Month es el mes del año en número
        Year es el año en que estemos, por default es 2025 si no especifica
        Starttime es la hora, sin especificar los minutos

        No añadas comillas, ni ningún otro texto o símbolo fuera del JSON. Si falta algún dato, devuelve exactamente lo siguiente:

        {}
        
        A continuación se te proporcionará el historial de chat del usuario. Utiliza la información más reciente para completar los campos del objeto JSON.
        """
        system_prompt += f". La fecha de hoy es {datetime.today().date()}"

        if isinstance(chat_history, list):
            # Add user's input to chat history
            chat_history.append({"user": user_input, "assistant": ""})

        history_text = "\n".join(
            [f"Usuario: {e['user']}\nAsistente: {e.get('assistant', '')}" for e in chat_history]
        ) if isinstance(chat_history, list) else chat_history

        response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=history_text)])


        if response.content != "{}":
            return response.content
        return


    def email_object(self, user_input, user_id):
        chat_history = self.toolkit._load_chat_history(user_id) or "No hay historial de chat"
        # Get user data to create a JSON Object
        system_prompt = """
        Tu tarea es generar SOLO un objeto JSON con la información del usuario, sin ningún texto adicional.

        El formato estricto del objeto debe ser:

        {
            "fullname": string,
            "email": string,
            "user_question": string
        }

        No añadas comillas, ni ningún otro texto o símbolo fuera del JSON. Si falta algún dato, devuelve exactamente lo siguiente:

        {}

        A continuación, se te proporcionará el historial de chat del usuario. Utiliza esta información para completar los campos del objeto JSON. 
        """



        if isinstance(chat_history, list):
            # Add user input to chat history
            chat_history.append({"user": user_input, "assistant": ""})

        history_text = "\n".join(
            [f"Usuario: {e['user']}\nAsistente: {e.get('assistant', '')}" for e in chat_history]
        ) if isinstance(chat_history, list) else chat_history

        response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=history_text)])


        if response.content != "{}":
            return response.content
        return