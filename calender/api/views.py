from django.shortcuts import render

# Create your views here.
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.conf import settings

class GoogleCalendarInitView(View):
    def get(self, request):
        flow = Flow.from_client_config(
            settings.GOOGLE_OAUTH2_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar.events']
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        request.session['google_auth_state'] = state
        return HttpResponseRedirect(authorization_url)

class GoogleCalendarRedirectView(View):
    def get(self, request):
        state = request.session.get('google_auth_state')
        flow = Flow.from_client_config(
            settings.GOOGLE_OAUTH2_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar.events'],
            state=state
        )
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials

        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary', timeMin='2023-04-21T00:00:00Z',
                                              timeMax='2023-04-22T00:00:00Z', singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        return JsonResponse({'events': events})
