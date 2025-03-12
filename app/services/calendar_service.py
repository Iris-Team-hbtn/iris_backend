import pickle
import datetime as dt
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarService:
    def __init__(self):
        self.clinic_email = "yuntxwillover@gmail.com"
        self._auth()

    def _auth(self):
        with open("token.pickle", "rb") as token_file:
            self.creds = pickle.load(token_file)

        self.service = build("calendar", "v3", credentials=self.creds)

    def listEvents(self):
        try:
            now = dt.datetime.now().isoformat() + "Z"
            time_max = (dt.datetime.now() + dt.timedelta(weeks=2)).isoformat() + "Z"

            event_result = self.service.events().list(
                calendarId="primary",
                timeMin=now,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = event_result.get("items", [])
            return [{"date": e["start"].get("dateTime", e["start"].get("date"))} for e in events]

        except Exception as error:
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
