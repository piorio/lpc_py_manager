from django.urls import path

from league.views import (
    request_new_league,
    calendar
)

app_name = 'league'

urlpatterns = [
    path('request/new_league', request_new_league, name='request_new_league'),
    path('calendar', calendar, name='calendar')
]