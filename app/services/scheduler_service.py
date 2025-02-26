from datetime import datetime
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


    def check(self, day, month, starttime):
        calendar = CalendarService()
        event_list = calendar.listEvents()

        # Horarios de atención de 11 a 19hs
        available_hours = [f"{hour}:00" for hour in range(11, 20)]

        # Filtrar eventos ocupados según el día proporcionado
        occupied_hours = set()
        for event in event_list:
            # Asegurarse de que la fecha esté en un formato adecuado (asegúrate de que 'date' esté en formato ISO)
            event_date = event['date']  # Suponiendo que la fecha es una cadena ISO 8601 (YYYY-MM-DDTHH:MM:SS)
            event_datetime = datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S")
            
            # Verificar si el evento es para el mismo día que el solicitado
            if event_datetime.day == day and event_datetime.month == month:
                occupied_hours.add(event_datetime.strftime("%H:%M"))  # Agregar hora ocupada

        # Determinar los horarios libres para ese día
        free_hours = [hour for hour in available_hours if hour not in occupied_hours]
        free_hours_str = "\n".join([f"- {hour}" for hour in free_hours])

        # System prompt con los horarios disponibles para ese día específico
        system_prompt = f"""
        Tu tarea es verificar la disponibilidad para consultas de la clínica, basándote en los horarios disponibles de 11:00 a 19:00 hs, con una duración de una hora para cada consulta.

        El usuario te proporcionará un día, mes y hora de inicio.

        Reglas:
        - Si el horario solicitado está disponible, responde solamente con "Disponible".
        - Si el horario solicitado no está disponible, responde con los horarios libres para ese día.
        - Si el usuario no proporciona una hora exacta, responde con los horarios disponibles para ese día.

        Los siguientes son los horarios disponibles para el día solicitado:
        {free_hours_str}
        """

        # Clasificar el mensaje del usuario
        response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=f"Dia: {day} - Mes: {month}, Hora: {starttime}:00")])
        return response.content
