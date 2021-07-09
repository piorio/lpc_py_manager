from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from .models import Team
from .forms import CreateMyTeamForm
from roster.models import RosterTeam


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
    roster_teams = RosterTeam.objects.all()
    team = tuple((t.id, t.name) for t in roster_teams)
    if request.method == 'GET':
        form = CreateMyTeamForm()
        form.fields['roster'].choices = team
        return render(request, 'teams/createMyTeam.html', {'form': form})
    else:
        print(request.body)
        form = CreateMyTeamForm(request.POST)
        form.fields['roster'].choices = team
        if form.is_valid():
            name = form.cleaned_data['name']
            treasury = form.cleaned_data['treasury']
            roster = form.cleaned_data['roster']
            team = Team(name=name, treasury=treasury, roster_team_id=roster, coach=request.user, status='CREATED')
            team.save()
        else:
            form = CreateMyTeamForm()
            form.fields['roster'].choices = team
            return render(request, 'teams/createMyTeam.html', {'form': form})

        return redirect('my_teams')

