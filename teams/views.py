from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Team
from .forms import CreateMyTeamForm
from roster.models import RosterTeam


# Create your views here.
class AllTeamListView(ListView):
    model = Team
    template_name = 'teams/all_teams.html'
    context_object_name = 'teams'
    paginate_by = 20


class AllTeamDetail(DetailView):
    model = Team
    template_name = 'teams/all_team_detail.html'
    context_object_name = 'team'


class MyTeamsListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/my_teams.html'
    context_object_name = 'teams'
    paginate_by = 20

    def get_queryset(self):
        return Team.objects.filter(
            coach=self.request.user
        ).order_by('name')


def get_create_my_team(request):
    roster_teams = RosterTeam.objects.all()
    team = tuple((t.id, t.name) for t in roster_teams)
    if request.method == 'POST':
        form = CreateMyTeamForm()
        form.fields['roster'].choices = team
        return render(request, 'teams/createMyTeam.html', {'form': form})
    else:
        form = CreateMyTeamForm(request.POST)
        form.fields['roster'].choices = team
        if form.is_valid():
            name = form.cleaned_data['name']
            treasury = form.cleaned_data['treasury']
            roster = form.cleaned_data['roster']
            team = Team(name=name, treasury=treasury, roster_team_id=roster, coach=request.user, status='CREATED')
            team.save()
            return redirect('teams:my_teams')
        else:
            form = CreateMyTeamForm()
            form.fields['roster'].choices = team
            return render(request, 'teams/createMyTeam.html', {'form': form})


def dismiss_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    team.status = 'DISMISS'
    team.save()
    return redirect('teams:my_teams')


def prepare_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    if request.method == 'POST':
        return render(request, 'teams/prepare_team.html', {'team': team})
    else:
        return render(request, 'teams/prepare_team.html', {'team': team})


def ready_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    team.status = 'READY'
    team.save()
    return redirect('teams:my_teams')
