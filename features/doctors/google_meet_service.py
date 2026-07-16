import os
import uuid
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


def get_calendar_service():

    creds = None


    # Load saved token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )


    # First time authorization only
    if not creds or not creds.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )

        creds = flow.run_local_server(
            port=8080
        )


        with open("token.json", "w") as token:
            token.write(creds.to_json())


    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    return service



def create_google_meet(date, start_time, end_time):

    service = get_calendar_service()

    event = {
        "summary": "Doctor Patient Consultation",
        "description": "Online medical appointment",

        "start": {
            "dateTime": f"{date}T{start_time}",
            "timeZone": "Asia/Karachi"
        },

        "end": {
            "dateTime": f"{date}T{end_time}",
            "timeZone": "Asia/Karachi"
        },

        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {
                    "type": "hangoutsMeet"
                }
            }
        }
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1
    ).execute()

    return created_event["hangoutLink"]