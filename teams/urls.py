from django.urls import path
from .views import (
    AllTeamListView,
    AllTeamDetail,
    MyTeamsListView,
    get_create_my_team,
    dismiss_team,
    prepare_team,
    ready_team,
    buy_player,
    fire_player
)

app_name = 'teams'

urlpatterns = [
    path('', AllTeamListView.as_view(), name='all_teams'),
    path('<int:pk>/', AllTeamDetail.as_view(), name='all_team_detail'),
    path('my_teams/', MyTeamsListView.as_view(), name='my_teams'),
    path('my_teams/create', get_create_my_team, name='create_my_team'),
    path('my_teams/dismiss/<int:pk>/', dismiss_team, name='dismiss_team'),
    path('my_teams/preapre/<int:pk>/', prepare_team, name='prepare_team'),
    path('my_teams/ready/<int:pk>/', ready_team, name='ready_team'),
    path('my_teams/buy_player/<int:team_id>', buy_player, name='buy_player'),
    path('my_teams/fire_player/<int:team_id>', fire_player, name='fire_player'),
]
