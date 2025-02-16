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
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json")
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def listEvents(self):
        try:
            service = build("calendar", "v3", credentials=self.creds)
            now = dt.datetime.now().isoformat() + "Z"
            
            event_result = service.events().list(calendarId="primary", timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime").execute()
            events = event_result.get("items", [])

            if not events:
                print("No upcoming events found")
                return
            
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])
        except HttpError as error:
            print("An error occurred:", error)

    def createEvent(self, month, day, startTime, email, year=2025):
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


def main():
    calendar = CalendarService()
    calendar.listEvents()
    calendar.createEvent(2, 18, 9, "santi29ramos@gmail.com")
    calendar.listEvents()


if __name__ == "__main__":
    main()