from django.urls import path
from . import views

app_name = 'league'

urlpatterns = [
    path('request/new_league', views.request_new_league, name='request_new_league'),
    path('manager/league_i_manage', views.get_league_i_manage, name='league_i_manage'),
    path('manager/league_detail/<int:league_id>', views.get_league_detail, name='league_detail'),
    path('manager/league_user_detail/<int:league_id>', views.get_league_user_detail, name='league_user_detail'),
    path('manager/season_detail/<int:season_id>', views.get_season_detail, name='season_detail'),
    path('manager/season_user_detail/<int:season_id>', views.get_season_user_detail, name='season_user_detail'),
    path('manager/tournament_detail/<int:tournament_id>', views.get_tournament_detail, name='tournament_detail'),
    path('manager/tournament_user_detail/<int:tournament_id>', views.get_tournament_user_detail, name='tournament_user_detail'),
    path('manager/create_season/<int:league_id>', views.create_season, name='create_season'),
    path('manager/create_tournament/<int:season_id>', views.create_tournament, name='create_tournament'),
    path('manager/add_team_to_season/<int:season_id>', views.add_team_to_season, name='add_team_to_season'),
    path('manager/add_team_to_tournament/<int:tournament_id>', views.add_team_to_tournament, name='add_team_to_tournament'),
    path('list', views.get_all_leagues, name='get_all_leagues'),
    path('joined_list', views.get_all_joined_leagues, name='get_all_joined_leagues'),
    path('seasons_joined_list', views.get_all_joined_seasons, name='get_all_joined_seasons'),
    path('tournaments_joined_list', views.get_all_joined_tournaments, name='get_all_joined_tournaments'),
    path('calendar', views.calendar, name='calendar')
]