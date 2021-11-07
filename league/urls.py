from django.urls import path

from league.views import (
    request_new_league,
    get_league_i_manage,
    get_league_detail,
    create_season,
    get_season_detail,
    create_tournament,
    add_team_to_season,
    get_tournament_detail,
    add_team_to_tournament,
    calendar
)

app_name = 'league'

urlpatterns = [
    path('request/new_league', request_new_league, name='request_new_league'),
    path('manager/league_i_manage', get_league_i_manage, name='league_i_manage'),
    path('manager/league_detail/<int:league_id>', get_league_detail, name='league_detail'),
    path('manager/season_detail/<int:season_id>', get_season_detail, name='season_detail'),
    path('manager/tournament_detail/<int:tournament_id>', get_tournament_detail, name='tournament_detail'),
    path('manager/create_season/<int:league_id>', create_season, name='create_season'),
    path('manager/create_tournament/<int:season_id>', create_tournament, name='create_tournament'),
    path('manager/add_team_to_season/<int:season_id>', add_team_to_season, name='add_team_to_season'),
    path('manager/add_team_to_tournament/<int:tournament_id>', add_team_to_tournament, name='add_team_to_tournament'),
    path('calendar', calendar, name='calendar')
]