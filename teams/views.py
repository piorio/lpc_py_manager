from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from .models import Team, TeamPlayer
from .forms import CreateMyTeamForm
from roster.models import RosterTeam, RosterPlayer
from django.contrib import messages
from .team_helper import update_team_value
from django.db.models import Q


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


class AllReadyTeamListView(ListView):
    model = Team
    template_name = 'teams/all_teams.html'
    context_object_name = 'teams'
    paginate_by = 20
    ordering = ['-name']

    def get_queryset(self):
        return Team.objects.filter(
            Q(status='READY')
        ).order_by('name')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllReadyTeamListView, self).dispatch(request, args, kwargs)


class AllTeamDetail(DetailView):
    model = Team
    template_name = 'teams/all_team_detail.html'
    context_object_name = 'team'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllTeamDetail, self).dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllTeamDetail, self).get_context_data(**kwargs)
        team = self.model.objects.first()
        dedicated_fan = getattr(team, 'extra_dedicated_fan')
        context['dedicated_fan'] = dedicated_fan + 1
        return context


class MyTeamsListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/my_teams.html'
    context_object_name = 'teams'
    paginate_by = 20

    def get_queryset(self):
        return Team.objects.filter(
            (Q(coach=self.request.user) & ~Q(status='RETIRED'))
        ).order_by('name')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyTeamsListView, self).dispatch(request, args, kwargs)


class MyRetiredTeamsListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/my_teams.html'
    context_object_name = 'teams'
    paginate_by = 20

    def get_queryset(self):
        return Team.objects.filter(
            (Q(coach=self.request.user) & Q(status='RETIRED'))
        ).order_by('name')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyRetiredTeamsListView, self).dispatch(request, args, kwargs)


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
        messages.error(request, 'You cannot retire a team not belongs to you')
    else:
        team.status = 'RETIRED'
        team.save()
        messages.success(request, 'You retire ' + str(team))
    return redirect('teams:my_teams')


@login_required
def prepare_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    roster_players = team.roster_team.roster_players.all()

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot prepare a team not belongs to you')
        return redirect('teams:my_teams')

    return render(request,
                  'teams/prepare_team.html', {'team': team, 'roster_players': roster_players})


@login_required
def ready_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    players_count = team.players.all().count()
    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot ready a team not belongs to you')
    elif players_count < 11 or players_count > 16:
        messages.error(request, 'A team must have 11 to 16 players. You cannot ready a not complete team')
    else:
        team_value = update_team_value(team)
        team.value = team_value
        team.current_team_value = team_value
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

    # Check max team players
    if team.number_of_players > 15:
        is_buy_valid = False
        messages.error(request, 'You can\'t buy more than 16 players')

    # check money spent
    if is_buy_valid and roster_player_to_buy.cost > team.treasury:
        is_buy_valid = False
        messages.error(request, 'You don\'t have money for this player ' + roster_player_to_buy.position)

    # Check big guy: a roster team must have a max number of big guy
    if is_buy_valid and roster_player_to_buy.big_guy:
        if team.big_guy_numbers >= team.roster_team.big_guy_max:
            is_buy_valid = False
            messages.error(request, 'You cant\'t have more big guy')

    # Check max position quantity
    if is_buy_valid:
        number_of_roster_player_hired = team.players.filter(roster_player=roster_player_to_buy.id).count()
        if number_of_roster_player_hired >= roster_player_to_buy.max_quantity:
            is_buy_valid = False
            messages.error(request, 'You cant\'t buy ' + roster_player_to_buy.position + '! Max quantity is ' +
                           str(roster_player_to_buy.max_quantity))

    # add Team player -> Create session for rollback
    if is_buy_valid:
        player = TeamPlayer()
        player.init_with_roster_player(roster_player_to_buy, team)
        team.treasury = team.treasury - roster_player_to_buy.cost
        if roster_player_to_buy.big_guy:
            team.big_guy_numbers += 1
        team.number_of_players += 1
        team.save()
        player.save()
        player.set_initial_skills_and_traits(roster_player_to_buy)
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
    if player.big_guy:
        team.big_guy_numbers -= 1
    team.number_of_players -= 1
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

    roster_players = team.roster_team.roster_players.all()
    dedicated_fan = team.extra_dedicated_fan + 1
    return render(request,
                  'teams/my_team_detail.html', {'team': team, 'roster_players': roster_players,
                                                'dedicated_fan': dedicated_fan})


@login_required
def buy_re_roll(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy a re roll for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent and max number
    if team.roster_team.re_roll_cost > team.treasury or team.re_roll > team.roster_team.re_roll_max:
        messages.error(request,
                       'You don\'t have money for another re roll or you reached the max number of re roll permitted')
    else:
        team.re_roll += 1
        team.treasury -= team.roster_team.re_roll_cost
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def remove_re_roll(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove a re roll for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent and max number
    if team.re_roll <= 0:
        messages.error(request, 'You don\'t have re roll to remove')
    else:
        team.re_roll -= 1
        team.treasury += team.roster_team.re_roll_cost
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def buy_assistant_coach(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy an assistant coach for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent
    if team.treasury - 10000 < 0 or team.assistant_coach > 5:
        messages.error(request, 'You don\'t have money for another assistant coach')
    else:
        team.assistant_coach += 1
        team.treasury -= 10000
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def remove_assistant_coach(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove an assistant coach for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent and max number
    if team.assistant_coach <= 0:
        messages.error(request, 'You don\'t have assistant coach to remove or too many assistant coach')
    else:
        team.assistant_coach -= 1
        team.treasury += 10000
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def buy_cheerleader(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy an cheerleader for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent
    if team.treasury - 10000 < 0 or team.cheerleader > 11:
        messages.error(request, 'You don\'t have money for another cheerleader or too many cheerleaders')
    else:
        team.cheerleader += 1
        team.treasury -= 10000
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def remove_cheerleader(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove a cheerleader for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent and max number
    if team.cheerleader <= 0:
        messages.error(request, 'You don\'t have cheerleader to remove')
    else:
        team.cheerleader -= 1
        team.treasury += 10000
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def buy_extra_fan(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy an extra fan for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent
    if team.treasury - 10000 < 0 or team.extra_dedicated_fan > 4:
        messages.error(request, 'You don\'t have money for another extra fan or too many extra fan')
    else:
        team.extra_dedicated_fan += 1
        team.treasury -= 10000
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def remove_extra_fan(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove an extra fan for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent and max number
    if team.extra_dedicated_fan <= 0:
        messages.error(request, 'You don\'t have extra fan to remove')
    else:
        team.extra_dedicated_fan -= 1
        team.treasury += 10000
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def buy_apothecary(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy an apothecary for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    if team.roster_team.apothecary is False:
        messages.error(request, 'Your team cannot have an apothecary')
        return redirect(team.get_prepare_absolute_url())

    # check money spent
    if team.treasury - 50000 < 0 or team.apothecary is True:
        messages.error(request,
                       'You don\'t have money for the apothecary or too many apothecary (You can buy only one)')
    else:
        team.apothecary = True
        team.treasury -= 50000
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def remove_apothecary(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove an apothecary for a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # check money spent and max number
    if team.apothecary is False:
        messages.error(request, 'You don\'t have apothecary to remove')
    else:
        team.apothecary = False
        team.treasury += 50000
        team.save()

    return redirect(team.get_prepare_absolute_url())


@login_required
def manage_player(request, team_id):
    player_id = request.GET.get('player', None)
    print('Manage ' + str(player_id) + ' for teamId ' + str(team_id))
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot manage a player of a team not belongs to you')
        return redirect(team.get_prepare_absolute_url())

    # Check if player_id belongs to team
    team_players_id = list(team.players.values_list('id', flat=True))
    if int(player_id) not in team_players_id:
        messages.error(request, 'You cannot manage that player because it is not belong with team you are working on')
        return redirect('teams:my_teams')

    player = get_object_or_404(TeamPlayer, id=player_id)
    return render(request,
                  'teams/manage_player.html', {'player': player, 'range': range(1, 101),
                                               'team_detail': team.get_my_team_detail_absolute_url()})


@login_required
def change_player_name_number(request):
    if request.method == 'POST':
        print(request.POST)
        player_id = request.POST['playerId']
        team_id = request.POST['teamId']
        player = get_object_or_404(TeamPlayer, id=player_id)
        team = get_object_or_404(Team, id=team_id)

        if team.coach.id != request.user.id:
            messages.error(request, 'You cannot change player name of a team not belongs to you')
            return redirect('teams:my_teams')

        team_players_id = list(team.players.values_list('id', flat=True))
        if int(player_id) not in team_players_id:
            messages.error(request, 'You cannot change the name of that player because it is not belong with team '
                                    'you are working on')
            return redirect('teams:my_teams')

        player_name = request.POST['new_name']
        player_number = request.POST['new_number']

        if player_name:
            player.name = player_name

        if player_number and player_number != '--':
            player.player_number = int(player_number)

        player.save()

        return redirect(team.get_manage_player_absolute_url() + '?player=' + player_id)

    else:
        return redirect('teams:my_teams')


@login_required
def manage_fire_player(request, team_id):
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
    if player.big_guy:
        team.big_guy_numbers -= 1
    team.number_of_players -= 1
    player.fired = True
    player.missing_next_game = False
    player.save()

    team.value = update_team_value(team, True)
    team.current_team_value = update_team_value(team)
    team.save()

    messages.success(request, 'You fire a ' + str(player.position))
    return redirect(team.get_my_team_detail_absolute_url())


####

@login_required
def manage_buy_re_roll(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy a re roll for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    # check money spent and max number
    if team.roster_team.re_roll_cost > team.treasury or team.re_roll > team.roster_team.re_roll_max:
        messages.error(request,
                       'You don\'t have money for another re roll or you reached the max number of re roll permitted')
    else:
        team.re_roll += 1
        team.treasury -= team.roster_team.re_roll_cost
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def manage_remove_re_roll(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove a re roll for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    # check money spent and max number
    if team.re_roll <= 0:
        messages.error(request, 'You don\'t have re roll to remove')
    else:
        team.re_roll -= 1
        team.treasury += team.roster_team.re_roll_cost
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def manage_buy_assistant_coach(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy an assistant coach for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    # check money spent
    if team.treasury - 10000 < 0 or team.assistant_coach > 5:
        messages.error(request, 'You don\'t have money for another assistant coach')
    else:
        team.assistant_coach += 1
        team.treasury -= 10000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def manage_remove_assistant_coach(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove an assistant coach for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    # check money spent and max number
    if team.assistant_coach <= 0:
        messages.error(request, 'You don\'t have assistant coach to remove or too many assistant coach')
    else:
        team.assistant_coach -= 1
        team.treasury += 10000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def manage_buy_cheerleader(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy an cheerleader for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    # check money spent
    if team.treasury - 10000 < 0 or team.cheerleader > 11:
        messages.error(request, 'You don\'t have money for another cheerleader or too many cheerleaders')
    else:
        team.cheerleader += 1
        team.treasury -= 10000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def manage_remove_cheerleader(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove a cheerleader for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    # check money spent and max number
    if team.cheerleader <= 0:
        messages.error(request, 'You don\'t have cheerleader to remove')
    else:
        team.cheerleader -= 1
        team.treasury += 10000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def manage_buy_apothecary(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy an apothecary for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    if team.roster_team.apothecary is False:
        messages.error(request, 'Your team cannot have an apothecary')
        return redirect(team.get_my_team_detail_absolute_url())

    # check money spent
    if team.treasury - 50000 < 0 or team.apothecary is True:
        messages.error(request,
                       'You don\'t have money for the apothecary or too many apothecary (You can buy only one)')
    else:
        team.apothecary = True
        team.treasury -= 50000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def manage_remove_apothecary(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot remove an apothecary for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    # check money spent and max number
    if team.apothecary is False:
        messages.error(request, 'You don\'t have apothecary to remove')
    else:
        team.apothecary = False
        team.treasury += 50000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def manage_buy_player(request, team_id):
    roster_player_id = request.GET.get('roster_player', None)
    team = get_object_or_404(Team, id=team_id)
    roster_player_to_buy = get_object_or_404(RosterPlayer, id=roster_player_id)

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy a player for a team not belongs to you')
        return redirect(team.get_my_team_detail_absolute_url())

    is_buy_valid = True

    # Check if roster_player_id belongs to roster team
    roster_players_id = list(team.roster_team.roster_players.values_list('id', flat=True))
    if int(roster_player_id) not in roster_players_id:
        messages.error(request, 'You cannot buy that player because it is not belong with the chosen roster')
        return redirect('teams:my_teams')

    # Check max team players
    if team.number_of_players > 15:
        is_buy_valid = False
        messages.error(request, 'You can\'t buy more than 16 players')

    # check money spent
    if is_buy_valid and roster_player_to_buy.cost > team.treasury:
        is_buy_valid = False
        messages.error(request, 'You don\'t have money for this player ' + roster_player_to_buy.position)

    # Check big guy: a roster team must have a max number of big guy
    if is_buy_valid and roster_player_to_buy.big_guy:
        if team.big_guy_numbers >= team.roster_team.big_guy_max:
            is_buy_valid = False
            messages.error(request, 'You cant\'t have more big guy')

    # Check max position quantity
    if is_buy_valid:
        number_of_roster_player_hired = team.players.filter(roster_player=roster_player_to_buy.id).count()
        if number_of_roster_player_hired >= roster_player_to_buy.max_quantity:
            is_buy_valid = False
            messages.error(request, 'You cant\'t buy ' + roster_player_to_buy.position + '! Max quantity is ' +
                           str(roster_player_to_buy.max_quantity))

    # add Team player -> Create session for rollback
    if is_buy_valid:
        player = TeamPlayer()
        player.init_with_roster_player(roster_player_to_buy, team)
        team.treasury = team.treasury - roster_player_to_buy.cost
        if roster_player_to_buy.big_guy:
            team.big_guy_numbers += 1
        team.number_of_players += 1
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()
        player.save()
        player.set_initial_skills_and_traits(roster_player_to_buy)
        messages.success(request, 'You bought ' + str(player.position))

    return redirect(team.get_my_team_detail_absolute_url())


def index_test(request):
    return render(request, 'index.html')
