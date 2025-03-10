import datetime as dt
import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarService:
    
    API_KEY = os.getenv("CALENDAR_API_KEY")
    service = None
    
    def __init__(self):
        self._auth()
        self.clinic_email = "yuntxwillover@gmail.com"

    def _auth(self):
        try:
            self.service = build("calendar", "v3", developerKey=self.API_KEY)
            print("Autenticación exitosa con API Key.")
        except HttpError as err:
            print(f"Ocurrió un error al autenticar con la API: {err}")
            self.service = None

    def listEvents(self):
        try:
            now = dt.datetime.now()
            time_min = now.isoformat() + "Z"
            time_max = (now + dt.timedelta(weeks=2)).isoformat() + "Z"

            event_result = self.service.events().list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = event_result.get("items", [])
            if not events:
                print("No upcoming events found")
                return []

            event_list = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))

                attendees = event.get("attendees", [])
                attendee_emails = {a["email"] for a in attendees if a["email"] != self.clinic_email}

                event_list.append({'date': start, 'attendees': list(attendee_emails)})
            return event_list

        except HttpError as error:
            print("An error occurred:", error)
            return []

    def createEvent(self, month, day, startTime, email, year=2025):
        if not self.service:
            print("Error: No se pudo autenticar con la API.")
            return None

        start_datetime = dt.datetime(year, month, day, startTime, 0, 0).isoformat()
        end_datetime = dt.datetime(year, month, day, startTime + 1, 0, 0).isoformat()

        event = {
            "summary": "Consulta Holberton Clinic",
            "location": "Holberton", 
            "description": "Holberton Clinic consultation service at display",
            "colorId": 3,
            "start": {
                "dateTime": start_datetime,
                "timeZone": "America/Montevideo"
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": "America/Montevideo"
            },
            "attendees": [
                {"email": "yuntxwillover@gmail.com"},
                {"email": email}
            ]
        }

        try:
            event = self.service.events().insert(calendarId="primary", body=event).execute()
            print(f"Event created {event.get('htmlLink')}")
            return event
        except HttpError as error:
            print("An error occurred:", error)
            return None
    
    def getUniqueAttendees(self):
        """Get attendees from medic consultations already scheduled"""
        events = self.listEvents()
        unique_attendees = set()
        
        for event in events:
            unique_attendees.update(event["attendees"])

        return unique_attendees
