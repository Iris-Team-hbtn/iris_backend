# Import necessary libraries
import datetime as dt
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarService:
    # Define the scope for Google Calendar API access
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None

    def __init__(self):
        # Initialize service by authenticating
        self._auth()

    def _auth(self):
        """Handle Google Calendar API authentication"""
        # Get the directory path and credentials file location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(base_dir, "credentials.json")
        
        # Load existing token if available
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        
        # Handle credential validation and refresh
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Create new token if none exists
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for future use
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def listEvents(self):
        """Retrieve list of events for next 2 weeks"""
        try:
            service = build("calendar", "v3", credentials=self.creds)
            now = dt.datetime.now()
            # Set time range for events (now to 2 weeks ahead)
            time_min = now.isoformat() + "Z"
            time_max = (now + dt.timedelta(weeks=2)).isoformat() + "Z"

            # Query calendar API for events
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
            
            # Process and format events
            event_list = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                # Trim timezone information if present
                if len(start) > 19:
                    start = start[:19]
                event_list.append({'date': start})
            return event_list

        except HttpError as error:
            print("An error occurred:", error)
            return []

    def createEvent(self, month, day, startTime, email, year=2025):
        """Create a new calendar event"""
        print(month, day, startTime, email, year)
        service = build("calendar", "v3", credentials=self.creds)
        
        # Calculate event start and end times (1 hour duration)
        start_datetime = dt.datetime(year, month, day, startTime, 0, 0).isoformat()
        end_datetime = dt.datetime(year, month, day, startTime + 1, 0, 0).isoformat()
        
        # Define event details
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
        # Create the event and return the result
        event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Event created {event.get('htmlLink')}")
        return event
