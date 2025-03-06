import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarService:
    
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    
    def __init__(self):
        self._auth()
        self.clinic_email = "yuntxwillover@gmail.com"

    def _auth(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(base_dir, "credentials.json") 

        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json")
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def listEvents(self):
        try:
            service = build("calendar", "v3", credentials=self.creds)
            now = dt.datetime.now()
            time_min = now.isoformat() + "Z"
            time_max = (now + dt.timedelta(weeks=2)).isoformat() + "Z"

            event_result = service.events().list(
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
                start = start[:-6]

                attendees = event.get("attendees", [])
                attendee_emails = {a["email"] for a in attendees if a["email"] != self.clinic_email}

                event_list.append({'date': start, 'attendees': list(attendee_emails)})
            return event_list

        except HttpError as error:
            print("An error occurred:", error)

    def createEvent(self, month, day, startTime, email, year=2025):
        print(month, day, startTime, email, year)
        service = build("calendar", "v3", credentials=self.creds)

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

        event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Event created {event.get('htmlLink')}")
        return event
    
    def getUniqueAttendees(self):
        """Obtiene un conjunto de correos únicos de los asistentes a los eventos, excluyendo el de la clínica."""
        events = self.listEvents()
        unique_attendees = set()
        
        for event in events:
            unique_attendees.update(event["attendees"])

        return unique_attendees
