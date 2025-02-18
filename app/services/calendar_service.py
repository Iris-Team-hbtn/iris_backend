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
                event_list.append({'date': start})
                print(start, event["summary"])
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
            "colorId": 6,
            "start": {
                "dateTime": start_datetime,
                "timeZone": "America/Montevideo"
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": "America/Montevideo"
            },
            "attendees": [
                {"email": "axel.palombo.ap@gmail.com"},
                {"email": email}
            ]
        }

        event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Event created {event.get('htmlLink')}")
        return event
