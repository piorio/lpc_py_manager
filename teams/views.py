from django.contrib.auth.mixins import LoginRequiredMixin
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


class MyTeamsListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/my_teams.html'
    context_object_name = 'teams'

    def get_queryset(self):
        return Team.objects.filter(
            coach=self.request.user
        ).order_by('name')


def get_create_my_team(request):
    return render(request, 'teams/createMyTeam.html', {})

