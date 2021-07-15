from django.urls import path
from .views import (
    AllTeamListView,
    AllTeamDetail,
    MyTeamsListView,
    get_create_my_team,
    dismiss_team,
)

app_name = 'teams'

urlpatterns = [
    path('', AllTeamListView.as_view(), name='all_teams'),
    path('<int:pk>/', AllTeamDetail.as_view(), name='all_team_detail'),
    path('my_teams/', MyTeamsListView.as_view(), name='my_teams'),
    path('my_teams/create', get_create_my_team, name='create_my_team'),
    path('my_teams/dismiss/<int:pk>/', dismiss_team, name='dismiss_team'),
]
