from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
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

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllTeamListView, self).dispatch(request, args, kwargs)


class AllTeamDetail(DetailView):
    model = Team
    template_name = 'teams/all_team_detail.html'
    context_object_name = 'team'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllTeamDetail, self).dispatch(request, args, kwargs)


class MyTeamsListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/my_teams.html'
    context_object_name = 'teams'
    paginate_by = 20

    def get_queryset(self):
        return Team.objects.filter(
            coach=self.request.user
        ).order_by('name')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyTeamsListView, self).dispatch(request, args, kwargs)


@login_required
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


@login_required
def dismiss_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot dismiss a team not belongs to you')
    else:
        team.status = 'DISMISS'
        team.save()
        messages.success(request, 'You dismiss ' + str(team))
    return redirect('teams:my_teams')


@login_required
def prepare_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    roster_players = team.roster_team.roster_players.all()

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot prepare a team not belongs to you')
        return redirect('teams:my_teams')

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


@login_required
def ready_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot ready a team not belongs to you')
    else:
        team.status = 'READY'
        team.save()
    return redirect('teams:my_teams')


@login_required
def buy_player(request, team_id):
    roster_player_id = request.GET.get('roster_player', None)
    team = get_object_or_404(Team, id=team_id)
    roster_player_to_buy = get_object_or_404(RosterPlayer, id=roster_player_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy a player for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    is_buy_valid = True

    # Check if roster_player_id belongs to roster team
    roster_players_id = list(team.roster_team.roster_players.values_list('id', flat=True))
    if int(roster_player_id) not in roster_players_id:
        messages.error(request, 'You cannot buy that player because it is not belong with the chosen roster')
        return redirect('teams:my_teams')

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

    return redirect(team.get_prepare_absolute_url())


@login_required
def fire_player(request, team_id):
    player_id = request.GET.get('player', None)
    print('Fire ' + str(player_id) + ' for teamId ' + str(team_id))
    team = get_object_or_404(Team, id=team_id)
    player = get_object_or_404(TeamPlayer, id=player_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot fire a player for a team not belongs to you')
        return redirect('teams:my_teams')

    # Check if player_id belongs to team
    team_players_id = list(team.players.values_list('id', flat=True))
    if int(player_id) not in team_players_id:
        messages.error(request, 'You cannot fire that player because it is not belong with team you are working on')
        return redirect('teams:my_teams')

    # Delete player and add again the cost
    team.treasury = team.treasury + player.cost
    player.delete()
    team.save()

    messages.success(request, 'You fire a ' + str(player.position))
    return redirect(team.get_prepare_absolute_url())


@login_required
def my_team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'Team did not belongs to you')
        return redirect('teams:my_teams')

    return render(request,
                  'teams/my_team_detail.html', {'team': team})
