import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.generativeai as genai
key = 'AIzaSyD7uZs_czeXMEbP64JFFXWcy2choY9NW7o'
genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-pro')

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

template = """
{
    "summary": "Name for the Meeting",
    "location": "location of the meeting",
    "description": "Description of the meeting",
    "start": {
        "dateTime": "start date time in UTC format",
        "timeZone": "America/Chicago"
        }
   "end": {
        "dateTime": "start date time in UTC format",
        "timeZone": "America/Chicago",
        }
    "attendees": [
       {"email": "emails of the attendees"}
    ]
}
"""

def fetchCreds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def createEvent(details):
    creds = fetchCreds()

    try:
        service = build("calendar", "v3", credentials=creds)

        event = details

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return event


    except HttpError as error:
        print(f"An error occurred: {error}")


def getEventDetails(transcript):
    query= f"Trascript: {transcript} Based on the transcript provided, Is anything discussed about the next meeting? If yes,  fill in the meeting data in json template: {template}."
    try:
        response = model.generate_content(query)
        buffer = response.text.replace("\n", "")
        if(buffer):
            eventDetails = eval(buffer)
            return eventDetails
        else:
            return {}
    except HttpError as error:
        print(f"An error occurred: {error}")
        

def getMeetingSummary(transcript):
    query = f"Trascript: {transcript} Based on the transcript provided, summarize the meeting in 100 words."
    response = model.generate_content(query)
    return response.text

def getactionItems(transcript):
    query = f"Trascript: {transcript} Based on the transcript provided, what are the action items for me?"
    response = model.generate_content(query)
    return response.text