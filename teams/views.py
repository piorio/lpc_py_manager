from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Team


# Create your views here.
class AllTeamListView(ListView):
    model = Team
    template_name = 'teams/all_teams.html'
    context_object_name = 'teams'


class AllTeamDetail(DetailView):
    model = Team
    template_name = 'teams/all_team_detail.html'
    context_object_name = 'team'
