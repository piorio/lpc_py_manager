from django.urls import path
from .views import (
    AllTeamListView,
    AllTeamDetail
)

urlpatterns = [
    path('teams/', AllTeamListView.as_view(), name='all_teams'),
    path('teams/<pk>/', AllTeamDetail.as_view(), name='all_team_detail'),
]