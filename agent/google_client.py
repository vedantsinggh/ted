import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleClient:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
        self.creds = None
        self._authenticate()
    
    def _authenticate(self):
        """Handle OAuth2 authentication"""
        token_file = 'credentials/token.json'
        
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/client_secret.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())
    
    def get_calendar_service(self):
        return build('calendar', 'v3', credentials=self.creds)
    
    def get_gmail_service(self):
        return build('gmail', 'v1', credentials=self.creds)
