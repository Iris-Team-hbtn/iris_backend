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

    def validate_input(self, day, month, starttime):
        """Validates date."""
        if not (1 <= month <= 12):
            raise ValueError("El mes debe estar entre 1 y 12.")
        if not (1 <= day <= 31):
            raise ValueError("El día debe estar entre 1 y 31.")
        if not (11 <= starttime <= 19):
            raise ValueError("La hora debe estar entre 11 y 19.")
        return True

    def check(self, day, month, starttime):
        """Checks availability"""

        # Validate input
        try:
            self.validate_input(day, month, starttime)
        except ValueError as e:
            return str(e)

        calendar = CalendarService()
        event_list = calendar.listEvents()

        # Attention hours from 11 to 18
        available_hours = {f"{hour}:00" for hour in range(11, 19)}

        # Grouping up day-month
        events_by_date = {}
        for event in event_list:
            event_date = event.get('date')
            if event_date:
                event_datetime = datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S")
                event_key = f"{event_datetime.day}-{event_datetime.month}"  # Agrupamos por día y mes
                event_hour = event_datetime.strftime("%H:%M")  # Extraemos solo la hora

                if event_key not in events_by_date:
                    events_by_date[event_key] = set()
                events_by_date[event_key].add(event_hour)

        # Creates a key for that day
        requested_date_key = f"{day}-{month}"

        # Getting occupied hours for that date
        occupied_hours = events_by_date.get(requested_date_key, set())

        # Starttime format -> "HH:00"
        requested_time = f"{starttime:02d}:00" if isinstance(starttime, int) else starttime

        # Checks if requestes time its occupied
        if requested_time in occupied_hours:
            # If not available, we show available hours
            free_hours = available_hours - occupied_hours
            free_hours_str = "\n".join([f"- {hour}" for hour in free_hours])
            return f"Hora ocupada. Los siguientes horarios están disponibles:\n{free_hours_str}"
        elif requested_time in available_hours:
            return "Disponible"
        return "Hora inválida"
