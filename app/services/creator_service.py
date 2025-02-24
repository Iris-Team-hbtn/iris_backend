from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv
from app.services.toolkits import ToolkitService

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
            stream=True  # Streaming activado
        )
        self.toolkit = ToolkitService()

    def date_object(self, user_id):
        chat_history = self.toolkit._load_chat_history(user_id)
        
        # Según el user_input, define a que servicio se deriva lo siguiente
        system_prompt = """
        Tu tarea es generar SOLO un objeto JSON con la información del usuario, sin ningún texto adicional.

        El formato estricto del objeto debe ser:

        {
            "fullname": "string",
            "email": "string",
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
        
        A continuación se te proporcionará el historial de chat del usuario. Utiliza esta información para completar los campos del objeto JSON.
        """

        # Clasifica el mensaje del usuario
        response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=chat_history)])
        if response.content != '0':
            return response.content
        return


    def email_object(self, user_id):
        chat_history = self.toolkit._load_chat_history(user_id)
        # Según el user_input, define a que servicio se deriva lo siguiente
        system_prompt = """
        Tu tarea es generar SOLO un objeto JSON con la información del usuario, sin ningún texto adicional.

        El formato estricto del objeto debe ser:

        {
            "fullname": "string",
            "email": "string"
        }

        No añadas comillas, ni ningún otro texto o símbolo fuera del JSON. Si falta algún dato, devuelve exactamente lo siguiente:

        {}

        A continuación, se te proporcionará el historial de chat del usuario. Utiliza esta información para completar los campos del objeto JSON. 
        """



        # Clasifica el mensaje del usuario
        response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=chat_history)])
        if response.content != '0':
            return response.content
        return