from datetime import datetime, timedelta
from agent.google_client import GoogleClient

class CalendarTools:
    def __init__(self):
        self.client = GoogleClient()
        self.service = self.client.get_calendar_service()
    
    def get_events(self, max_results=10):
        """Get upcoming events"""
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    
    def create_event(self, summary, start_time, end_time, description=""):
        """Create a new calendar event"""
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/New_York',
            },
        }
        
        event = self.service.events().insert(
            calendarId='primary', 
            body=event
        ).execute()
        return event
