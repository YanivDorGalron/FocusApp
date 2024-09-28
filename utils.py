import datetime
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def authenticate_google_calendar():
    creds = None
    token_path = get_resource_path('token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(get_resource_path('cred.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:  # Use updated token path
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def add_focus_session_to_calendar(start_time, focus_duration, task, cc_email=None):
    service = authenticate_google_calendar()
    event = {
        'summary': f'Focus Session: {task}',
        'description': f'Focus time on task: {task}',
        'start': {
            'dateTime': start_time.isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (start_time + datetime.timedelta(minutes=focus_duration)).isoformat() + 'Z',
            'timeZone': 'UTC',
        }
    }
    if cc_email:
        event['attendees'] = [{'email': cc_email}]
    service.events().insert(calendarId='primary', body=event).execute()


def get_resource_path(relative_path):
    """ Get absolute path to a resource, works for both frozen and non-frozen applications """
    if getattr(sys, 'frozen', False):
        # The application is running as a frozen executable
        base_path = sys._MEIPASS
    else:
        # The application is running as a normal Python script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)