from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Team, TeamPlayer
from .forms import CreateMyTeamForm, PrepareTeamForm
from roster.models import RosterTeam, RosterPlayer
from django.contrib import messages
from .form_helpers import PrepareTeamValidator


# Create your views here.
class AllTeamListView(ListView):
    model = Team
    template_name = 'teams/all_teams.html'
    context_object_name = 'teams'
    paginate_by = 20
    ordering = ['-name']


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
    roster_players = team.roster_team.roster_players.all()
    if request.method == 'POST':
        form = PrepareTeamForm(request.POST)
        if form.is_valid():
            treasury = team.treasury
            prepare_team_validator = PrepareTeamValidator(treasury, form.cleaned_data, team.roster_team)
            (is_valid, treasury, message) = prepare_team_validator.validate_form()
            if not is_valid:
                messages.error(request, message)
                return render(request, 'teams/prepare_team.html', {'team': team, 'form': form,
                                                                   'roster_players': roster_players})

            team.apothecary = form.cleaned_data['apothecary']
            team.re_roll = form.cleaned_data['re_roll']
            team.assistant_coach = form.cleaned_data['assistant_coach']
            team.cheerleader = form.cleaned_data['cheerleader']
            team.extra_dedicated_fan = form.cleaned_data['extra_dedicated_fan']

            team.treasury = treasury
            team.save()

            return redirect(team.get_prepare_absolute_url())
        else:
            return render(request, 'teams/prepare_team.html', {'team': team, 'form': form})
    else:
        form = PrepareTeamForm(initial={
            're_roll': team.re_roll, 'cheerleader': team.cheerleader, 'assistant_coach': team.assistant_coach,
            'apothecary': team.apothecary, 'extra_dedicated_fan': team.extra_dedicated_fan
        })

        return render(request,
                      'teams/prepare_team.html', {'team': team, 'form': form, 'roster_players': roster_players})


def ready_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    team.status = 'READY'
    team.save()
    return redirect('teams:my_teams')


def buy_player(request, team_id):
    roster_player_id = request.GET.get('roster_player', None)
    print('Buy ' + str(roster_player_id) + ' for teamId ' + str(team_id))
    team = get_object_or_404(Team, id=team_id)
    roster_player_to_buy = get_object_or_404(RosterPlayer, id=roster_player_id)

    is_buy_valid = True

    # Check if roster_player_id belongs to roster team

    # check money spent
    if is_buy_valid and roster_player_to_buy.cost > team.treasury:
        is_buy_valid = False
        messages.error(request, 'You don\'t have money for this player ' + roster_player_to_buy.position)

    # add Team player -> Create session for rollback
    if is_buy_valid:
        player = TeamPlayer()
        player.init_with_roster_player(roster_player_to_buy, team)
        team.treasury = team.treasury - roster_player_to_buy.cost
        team.save()
        player.save()
        messages.success(request, 'You bought ' + str(player.position))

    form = PrepareTeamForm(initial={
        're_roll': team.re_roll, 'cheerleader': team.cheerleader, 'assistant_coach': team.assistant_coach,
        'apothecary': team.apothecary
    })

    roster_players = team.roster_team.roster_players.all()

    return redirect(team.get_prepare_absolute_url())


def fire_player(request, team_id):
    player_id = request.GET.get('player', None)
    print('Fire ' + str(player_id) + ' for teamId ' + str(team_id))
    team = get_object_or_404(Team, id=team_id)
    player = get_object_or_404(TeamPlayer, id=player_id)

    # Check if roster_player_id belongs to team

    # Delete player and add again the cost
    team.treasury = team.treasury + player.cost
    player.delete()
    team.save()

    messages.success(request, 'You fire a ' + str(player.position))

    form = PrepareTeamForm(initial={
        're_roll': team.re_roll, 'cheerleader': team.cheerleader, 'assistant_coach': team.assistant_coach,
        'apothecary': team.apothecary
    })

    roster_players = team.roster_team.roster_players.all()

    return redirect(team.get_prepare_absolute_url())


def my_team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    return render(request,
                  'teams/my_team_detail.html', {'team': team})
