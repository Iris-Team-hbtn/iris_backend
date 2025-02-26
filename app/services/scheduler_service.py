from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv
from app.services.calendar_service import CalendarService
class EventScheduler:

    def __init__(self):
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )

    def check(self, user_input):
        calendar = CalendarService()
        event_list = calendar.listEvents()
        event_str = "\n".join([f"- {event['date']}" for event in event_list])
        # Según el user_input, define a que servicio se deriva lo siguiente
        system_prompt = f"""
        Tu rol es verificar la agenda de la clínica y conocer con certeza la disponibilidad para consultas.
        El usuario te entregará un objeto JSON con su horario deseado.

        Reglas: 
        Si la consulta está disponible, responde solamente con "Disponible".
        Si la consulta NO se encuentra disponible en ese horario, responde con los horarios disponibles dentro de ese día que consulta el usuario.

        Estas son las consultas agendadas para las siguientes dos semanas, los horarios de atención son de 11 a 19hs:

        {event_str}
        """

        # Clasifica el mensaje del usuario
        response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_input)])
        if response.content != "{}":
            return response.content
        return
