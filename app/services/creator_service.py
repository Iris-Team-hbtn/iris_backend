# Import necessary libraries
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv
from app.services.toolkits import ToolkitService

class ObjectCreator:
    """A class that creates JSON objects from chat history using Google's Generative AI."""
    
    def __init__(self):
        # Load environment variables and initialize the AI model
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0,  # No randomness in responses
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.toolkit = ToolkitService()

    def date_object(self, user_id):
        """
        Creates a JSON object containing user's scheduling information.
        
        Args:
            user_id: The ID of the user whose chat history to process
            
        Returns:
            str: JSON object with scheduling details or None if data is insufficient
        """
        # Load the user's chat history
        chat_history = self.toolkit._load_chat_history(user_id) or "No hay historial de chat"
        
        # Define the system prompt that specifies the JSON structure
        system_prompt = """
        Tu tarea es generar SOLO un objeto JSON con la información del usuario, sin ningún texto adicional.
        Si faltan datos para generar el objeto, no lo generes.
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

        A continuación se te proporcionará el historial de chat del usuario. Utiliza esta información para completar los campos del objeto JSON.
        """
        
        # Get response from the AI model
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=chat_history)
        ])
        
        # Return the response content if it's not empty
        if response.content != "{}":
            return response.content
        return

    def email_object(self, user_id):
        """
        Creates a JSON object containing user's email information.
        
        Args:
            user_id: The ID of the user whose chat history to process
            
        Returns:
            str: JSON object with email details or None if data is insufficient
        """
        # Load the user's chat history
        chat_history = self.toolkit._load_chat_history(user_id) or "No hay historial de chat"
        
        # Define the system prompt that specifies the JSON structure
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
        
        # Get response from the AI model
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=chat_history)
        ])
        
        # Return the response content if it's not empty
        if response.content != "{}":
            return response.content
        return
