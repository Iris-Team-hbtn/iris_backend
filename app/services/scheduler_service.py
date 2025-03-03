from datetime import datetime
from dateutil import parser  # dateutil is used for robust date parsing
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv
from app.services.calendar_service import CalendarService

class EventScheduler:
    def __init__(self):
        load_dotenv()  # Load environment variables from a .env file
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")  # Get Google API key from environment variables
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",  # Specify the model to use
            temperature=0,  # Set the temperature for response generation
            max_tokens=None,  # No limit on the number of tokens
            timeout=None,  # No timeout
            max_retries=2  # Number of retries in case of failure
        )

    def check(self, day, month, starttime):
        calendar = CalendarService()  # Initialize the CalendarService
        event_list = calendar.listEvents()  # Get the list of events

        # Service hours from 11 AM to 7 PM
        available_hours = [f"{hour}:00" for hour in range(11, 20)]

        # Filter occupied events for the given day
        occupied_hours = set()
        for event in event_list:
            event_date = event['date']
            try:
                # Using parser.parse to handle different ISO formats
                event_datetime = parser.parse(event_date)
            except Exception as e:
                # Skip event if parsing fails
                continue
            if event_datetime.day == day and event_datetime.month == month:
                occupied_hours.add(event_datetime.strftime("%H:%M"))

        # Determine available time slots for that day
        free_hours = [hour for hour in available_hours if hour not in occupied_hours]
        free_hours_str = "\n".join([f"- {hour}" for hour in free_hours])

        # Build the prompt with available time slots
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
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Dia: {day} - Mes: {month}, Hora: {starttime}:00")
        ])
        return response.content  # Return the response content
