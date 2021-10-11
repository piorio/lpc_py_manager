from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from xhtml2pdf import pisa

from .buy_fire_helpers.buy_journeyman import BuyJourneyman
from .models import Team, TeamPlayer
from .forms import CreateMyTeamForm, RandomSkill
from roster.models import RosterTeam, RosterPlayer, Skill
from django.contrib import messages
from .team_helper import update_team_value
from django.db.models import Q
from .levelup_helper import get_levelup_cost_by_level, get_levelup_cost_all_levels, get_first_skills_category, \
    get_new_level, get_second_skills_category, get_first_skills_select_option, get_second_skills_select_option
import logging
from .buy_fire_helpers.buy_player import BuyPlayer

logger = logging.getLogger(__name__)


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
        team = context['team']
        dedicated_fan = getattr(team, 'extra_dedicated_fan')

        logger.debug('All team details for team ' + str(team) + ' - Dedicated fan => ' + str(dedicated_fan))

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
    logger.debug('User ' + str(request.user) + ' made a create team request with method ' + request.method)

    roster_teams = RosterTeam.objects.all()
    team = tuple((t.id, t.name) for t in roster_teams)
    if request.method == 'POST':
        form = CreateMyTeamForm(request.POST)
        form.fields['roster'].choices = team

        logger.debug('Create team POST. Roster choice ' + str(team))
        logger.debug('Create team POST. Data sent ' + str(request.POST))

        if form.is_valid():
            name = form.cleaned_data['name']
            treasury = form.cleaned_data['treasury']
            roster = form.cleaned_data['roster']
            created_team = Team(name=name, treasury=treasury, roster_team_id=roster, coach=request.user,
                                status='CREATED')
            logger.debug('Create team POST. Form valid. Create team ' + str(created_team))
            created_team.save()
            return redirect('teams:my_teams')
        else:
            form = CreateMyTeamForm()
            form.fields['roster'].choices = team
            logger.warning('Create team POST. Form invalid ' + str(form.errors))
            return render(request, 'teams/createMyTeam.html', {'form': form})
    else:
        form = CreateMyTeamForm()
        form.fields['roster'].choices = team
        logger.debug('Create team GET. Return form with this roster choice ' + str(team))
        return render(request, 'teams/createMyTeam.html', {'form': form})


@login_required
def dismiss_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    logger.debug('User ' + str(request.user) + ' try to dismiss team ' + str(team))
    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot retire a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' try to dismiss not owned team ' + str(team))
    else:
        team.status = 'RETIRED'
        team.save()
        messages.success(request, 'You retire ' + str(team))
        logger.debug('User ' + str(request.user) + ' dismiss successfully team ' + str(team))
    return redirect('teams:my_teams')


@login_required
def prepare_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    logger.debug('User ' + str(request.user) + ' try to prepare team ' + str(team))
    roster_players = team.roster_team.roster_players.filter(is_journeyman=False).all()

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot prepare a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' try to prepare not owned team ' + str(team))
        return redirect('teams:my_teams')

    return render(request,
                  'teams/prepare_team.html', {'team': team, 'roster_players': roster_players})


@login_required
def ready_team(request, pk):
    team = get_object_or_404(Team, id=pk)
    players_count = team.players.all().count()
    logger.debug('User ' + str(request.user) + ' try to ready team ' + str(team) + '. Players count '
                 + str(players_count))

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot ready a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' try to ready a not owned team ' + str(team))
    elif players_count < 11 or players_count > 16:
        messages.error(request, 'A team must have 11 to 16 players. You cannot ready a not complete team')
        logger.warning('User ' + str(request.user) + ' try to ready team ' + str(team)
                       + ' with invalid player count ' + players_count)
    else:
        team_value = update_team_value(team)
        team.value = team_value
        team.current_team_value = team_value
        team.status = 'READY'
        team.save()
        logger.warning('User ' + str(request.user) + ' ready team ' + str(team))
    return redirect('teams:my_teams')


@login_required
def buy_player(request, team_id):
    # You can buy only player not journeyman. The J didn't show into the list of players. But add a check
    roster_player_id = request.GET.get('roster_player', None)
    team = get_object_or_404(Team, id=team_id)
    roster_player_to_buy = get_object_or_404(RosterPlayer, id=roster_player_id)

    logger.debug('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                 + str(team))

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy a player for a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                       + str(team) + ' but the team not belong to the user')
        return redirect(team.get_prepare_absolute_url())

    if roster_player_to_buy.is_journeyman:
        messages.error(request, 'You cannot buy a Journeyman player during team preparation')
        logger.warning('User ' + str(request.user) + ' try to buy a journeyman ' + str(roster_player_to_buy)
                       + ' for team ' + str(team))
        return redirect(team.get_prepare_absolute_url())

    is_buy_valid = True

    # Check if roster_player_id belongs to roster team
    roster_players_id = list(team.roster_team.roster_players.values_list('id', flat=True))
    if int(roster_player_id) not in roster_players_id:
        messages.error(request, 'You cannot buy that player because it is not belong with the chosen roster')
        logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                       + str(team) + ' but the player not belong to the roster')
        return redirect('teams:my_teams')

    # Check max team players
    if team.number_of_players > 15:
        is_buy_valid = False
        messages.error(request, 'You can\'t buy more than 16 players')
        logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                       + str(team) + ' but can\'t buy more than 16 players. Players ' + str(team.number_of_players))

    # check money spent
    if is_buy_valid and roster_player_to_buy.cost > team.treasury:
        is_buy_valid = False
        messages.error(request, 'You don\'t have money for this player ' + roster_player_to_buy.position)
        logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                       + str(team) + ' but can\'t have money. Treasury ' + str(team.treasury)
                       + ' player cost ' + str(roster_player_to_buy.cost))

    # Check big guy: a roster team must have a max number of big guy
    if is_buy_valid and roster_player_to_buy.big_guy:
        if team.big_guy_numbers >= team.roster_team.big_guy_max:
            is_buy_valid = False
            messages.error(request, 'You cant\'t have more big guy')
            logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                           + str(team) + ' but can\'t have more big guy. Big Guy ' + str(team.big_guy_numbers)
                           + ' permitted big guy ' + str(team.roster_team.big_guy_max))

    # Check max position quantity
    if is_buy_valid:
        number_of_roster_player_hired = team.players.filter(roster_player=roster_player_to_buy.id).count()
        if number_of_roster_player_hired >= roster_player_to_buy.max_quantity:
            is_buy_valid = False
            messages.error(request, 'You cant\'t buy ' + roster_player_to_buy.position + '! Max quantity is ' +
                           str(roster_player_to_buy.max_quantity))
            logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                           + str(team) + ' but can\'t have player for this position. Positional Hired '
                           + str(number_of_roster_player_hired)
                           + ' permitted player max quantity ' + str(roster_player_to_buy.max_quantity))

    if is_buy_valid:
        player = TeamPlayer()
        player.init_with_roster_player(roster_player_to_buy, team)
        team.treasury = team.treasury - roster_player_to_buy.cost
        if roster_player_to_buy.big_guy:
            team.big_guy_numbers += 1
        team.number_of_players += 1

        try:
            with transaction.atomic():
                team.save()
                player.save()
                player.set_initial_skills_and_traits(roster_player_to_buy)
        except Exception as e:
            logger.error('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) +
                         ' Exception ' + str(e))
            messages.error(request, 'Internal error during buy Player')
            return redirect(team.get_prepare_absolute_url())

        messages.success(request, 'You bought ' + str(player.position))
        logger.debug('User ' + str(request.user) + ' bought ' + str(player) + ' for team ' + str(team))

    return redirect(team.get_prepare_absolute_url())


@login_required
def fire_player(request, team_id):
    # You can fire only player not journeyman. The J didn't show into the list of players. But add a check
    player_id = request.GET.get('player', None)
    team = get_object_or_404(Team, id=team_id)
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' try to fire ' + str(player) + ' for team '
                 + str(team))

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot fire a player for a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' try to fire ' + str(player) + ' for not owned team '
                       + str(team))
        return redirect(team.get_prepare_absolute_url())

    if player.roster_player.is_journeyman:
        messages.error(request, 'You cannot fire a Journeyman player during team preparation')
        logger.warning('User ' + str(request.user) + ' try to fire a journeyman ' + str(player)
                       + ' for team ' + str(team))
        return redirect(team.get_prepare_absolute_url())

    # Check if player_id belongs to team
    team_players_id = list(team.players.values_list('id', flat=True))
    if int(player_id) not in team_players_id:
        messages.error(request, 'You cannot fire that player because it is not belong with team you are working on')
        logger.warning('User ' + str(request.user) + ' try to fire ' + str(player) + ' but not play for team '
                       + str(team))
        return redirect('teams:my_teams')

    # Delete player and add again the cost
    team.treasury = team.treasury + player.cost
    if player.big_guy:
        team.big_guy_numbers -= 1
    team.number_of_players -= 1
    try:
        with transaction.atomic():
            player.delete()
            team.save()
    except Exception as e:
        logger.error('User ' + str(request.user) + ' try to fire ' + str(player) +
                     ' Exception ' + str(e))
        messages.error(request, 'Internal error during buy Player')
        return redirect('teams:my_teams')

    messages.success(request, 'You fire a ' + str(player.position))
    logger.debug('User ' + str(request.user) + ' fired ' + str(player) + ' for team ' + str(team))
    return redirect(team.get_prepare_absolute_url())


@login_required
def my_team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    logger.debug('User ' + str(request.user) + ' request detail for ' + str(team))

    if team.coach.id != request.user.id:
        messages.error(request, 'Team did not belongs to you')
        logger.warning('User ' + str(request.user) + ' request detail for ' + str(team) + ' but don\'t own team')
        return redirect('teams:my_teams')

    roster_players = team.roster_team.roster_players.all()
    dedicated_fan = team.extra_dedicated_fan + 1

    valid_player_counter = team.players.filter(Q(dead=False) & Q(fired=False) & Q(missing_next_game=False)).count()

    enable_journeyman = False
    if valid_player_counter < 11:
        enable_journeyman = True

    logger.debug('User ' + str(request.user) + ' request detail for ' + str(team) + ' Enable JourneyMan '
                 + str(enable_journeyman))
    return render(request,
                  'teams/my_team_detail.html', {'team': team, 'roster_players': roster_players,
                                                'dedicated_fan': dedicated_fan, 'enable_journeyman': enable_journeyman})


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
    # If a coach fire a Journeyman, change the TV, but not the Treasury. TODO
    player_id = request.GET.get('player', None)
    team = get_object_or_404(Team, id=team_id)
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' try to fire ' + str(player) + ' for team '
                 + str(team))

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot fire a player for a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' try to fire ' + str(player) + ' for not owned team '
                       + str(team))
        return redirect('teams:my_teams')

    # Check if player_id belongs to team
    team_players_id = list(team.players.values_list('id', flat=True))
    if int(player_id) not in team_players_id:
        messages.error(request, 'You cannot fire that player because it is not belong with team you are working on')
        logger.warning('User ' + str(request.user) + ' try to fire ' + str(player) + ' but not play for team '
                       + str(team))
        return redirect('teams:my_teams')

    # Fired player and add again the cost
    if not player.roster_player.is_journeyman:
        logger.debug('User ' + str(request.user) + ' fire ' + str(player) + ' for team '
                     + str(team) + ' and is not a journeyman so update treasury')
        team.treasury = team.treasury + player.cost

    if player.big_guy:
        team.big_guy_numbers -= 1
    team.number_of_players -= 1
    player.fired = True
    player.missing_next_game = False

    try:
        with transaction.atomic():
            player.save()
            team.value = update_team_value(team, True)
            team.current_team_value = update_team_value(team)
            team.save()
    except Exception as e:
        logger.error('User ' + str(request.user) + ' try to fire ' + str(player) +
                     ' Exception ' + str(e))
        messages.error(request, 'Internal error during fire Player')
        return redirect('teams:my_teams')

    messages.success(request, 'You fire a ' + str(player.position))
    return redirect(team.get_my_team_detail_absolute_url())


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

    logger.debug('User ' + str(request.user) + ' try to hire ' + str(roster_player_to_buy) + ' for team '
                 + str(team))

    if team.coach.id != request.user.id:
        messages.error(request, 'You cannot buy a player for a team not belongs to you')
        logger.warning(
            'User ' + str(request.user) + ' try to hire ' + str(roster_player_to_buy) + ' for not owned team '
            + str(team))
        return redirect(team.get_my_team_detail_absolute_url())

    buy_engine = None
    if roster_player_to_buy.is_journeyman:
        buy_engine = BuyJourneyman(team, roster_player_to_buy, request.user)
    else:
        buy_engine = BuyPlayer(team, roster_player_to_buy, request.user)

    player = buy_engine.generate_player_to_buy()

    # add Team player -> Create session for rollback
    if player is not None:
        try:
            with transaction.atomic():
                player.save()
                # Journeyman doesn't change the TV but only current value
                if not roster_player_to_buy.is_journeyman:
                    team.value = update_team_value(team, True)
                team.current_team_value = update_team_value(team)
                team.save()
                player.set_initial_skills_and_traits(roster_player_to_buy)
        except Exception as e:
            logger.error('User ' + str(request.user) + ' try to hire ' + str(player) +
                         ' Exception ' + str(e))
            messages.error(request, 'Internal error during hire Player')
            return redirect('teams:my_teams')

        messages.success(request, 'You bought ' + str(player.position))
    else:
        messages.error(request, buy_engine.message_for_flash)

    return redirect(team.get_my_team_detail_absolute_url())


@login_required
def player_level_up(request, player_id):
    player = get_object_or_404(TeamPlayer, id=player_id)

    if player.team.coach.id != request.user.id:
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        return redirect(player.team.get_my_team_detail_absolute_url())

    level_cost = get_levelup_cost_all_levels(player)
    return render(request, 'teams/levelup.html', {'player': player, 'level_cost': level_cost})


@login_required
def random_first_skill(request, player_id):
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' random first skill for player ' + str(player))

    if player.team.coach.id != request.user.id:
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' random first skill for player ' + str(player)
                       + ' for not owned team')
        return redirect(player.team.get_my_team_detail_absolute_url())

    level_cost = get_levelup_cost_by_level(player, 0)
    if player.spp < level_cost:
        messages.error(request, 'You cannot level up a this player: too few SPP')
        logger.warning('User ' + str(request.user) + ' random first skill for player ' + str(player)
                       + ' not enough SPP. SPP -> ' + str(player.spp) + ' - Level cost ' + str(level_cost))
        return redirect(player.team.get_my_team_detail_absolute_url())

    if request.method == "POST":
        form = RandomSkill(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            first_dice = form.cleaned_data['first_dice']
            second_dice = form.cleaned_data['second_dice']

            if first_dice <= 3:
                first_dice = 1
            if first_dice >= 4:
                first_dice = 4

            search_string = category + str(first_dice) + str(second_dice)
            logger.debug('User ' + str(request.user) + ' random first skill for player ' + str(player)
                         + ' First dice set ' + str(form.cleaned_data['first_dice'])
                         + ' Second dice set ' + str(second_dice)
                         + ' First dice ' + str(first_dice) + ' search string ' + search_string)

            try:
                with transaction.atomic():
                    skill = Skill.objects.filter(random_identifier=search_string).get()
                    if skill is not None:
                        logger.debug('User ' + str(request.user) + ' random first skill for player ' + str(player)
                                     + ' Skill -> ' + str(skill))
                        player.extra_skills.add(skill)
                        player.level = get_new_level(player)
                        player.value += 10000
                        player.spp -= level_cost
                        player.spent_spp += level_cost
                        player.save()
                        player.team.value = update_team_value(player.team, True)
                        player.team.current_team_value = update_team_value(player.team)
                        player.team.save()
                    else:
                        messages.error(request, 'Skill with random identifier ' + str(search_string) + ' not found!!!')
                        logger.warning('User ' + str(request.user) + ' random first skill for player ' + str(player)
                                       + ' Skill not found ' + str(search_string))

                    return redirect(player.team.get_my_team_detail_absolute_url())
            except Exception as e:
                logger.error('User ' + str(request.user) + ' random skill error ' + str(player) +
                             ' Exception ' + str(e))
                messages.error(request, 'Internal error random first skill Player')
                return redirect('teams:my_teams')
        else:
            err = form.errors
            messages.error(request, 'Some error ' + err)
            logger.warning('User ' + str(request.user) + ' random first kill error ' + str(player) +
                           ' Form errors ' + str(err))
        return
    else:
        form = RandomSkill()
        combo_box = get_first_skills_category(player)

    return render(request, 'teams/random_first_skill.html', {'player': player, 'form': form, 'combo_box': combo_box})


@login_required
def random_second_skill(request, player_id):
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' random second skill for player ' + str(player))

    if player.team.coach.id != request.user.id:
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' random second skill for player ' + str(player)
                       + ' for not owned team')
        return redirect(player.team.get_my_team_detail_absolute_url())

    level_cost = get_levelup_cost_by_level(player, 1)
    if player.spp < level_cost:
        messages.error(request, 'You cannot level up a this player: too few SPP')
        logger.warning('User ' + str(request.user) + ' random second skill for player ' + str(player)
                       + ' not enough SPP. SPP -> ' + str(player.spp) + ' - Level cost ' + str(level_cost))
        return redirect(player.team.get_my_team_detail_absolute_url())

    if request.method == "POST":
        form = RandomSkill(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            first_dice = form.cleaned_data['first_dice']
            second_dice = form.cleaned_data['second_dice']

            if first_dice <= 3:
                first_dice = 1
            if first_dice >= 4:
                first_dice = 4
            search_string = category + str(first_dice) + str(second_dice)

            logger.debug('User ' + str(request.user) + ' random second skill for player ' + str(player)
                         + ' First dice set ' + str(form.cleaned_data['first_dice'])
                         + ' Second dice set ' + str(second_dice)
                         + ' First dice ' + str(first_dice) + ' search string ' + search_string)

            try:
                with transaction.atomic():
                    skill = Skill.objects.filter(random_identifier=search_string).get()
                    if skill is not None:
                        logger.debug('User ' + str(request.user) + ' random second skill for player ' + str(player)
                                     + ' Skill -> ' + str(skill))
                        player.extra_skills.add(skill)
                        player.level = get_new_level(player)
                        player.value += 20000
                        player.spp -= level_cost
                        player.spent_spp += level_cost
                        player.save()
                        player.team.value = update_team_value(player.team, True)
                        player.team.current_team_value = update_team_value(player.team)
                        player.team.save()
                    else:
                        messages.error(request, 'Skill with random identifier ' + str(search_string) + ' not found!!!')
                        logger.warning('User ' + str(request.user) + ' random second skill for player ' + str(player)
                                       + ' Skill not found ' + str(search_string))

                    return redirect(player.team.get_my_team_detail_absolute_url())
            except Exception as e:
                logger.error('User ' + str(request.user) + ' random second skill error ' + str(player) +
                             ' Exception ' + str(e))
                messages.error(request, 'Internal error random second skill Player')
                return redirect('teams:my_teams')
        else:
            err = form.errors
            messages.error(request, 'Some error ' + err)
            logger.warning('User ' + str(request.user) + ' random second kill error ' + str(player) +
                           ' Form errors ' + str(err))
        return
    else:
        form = RandomSkill()
        combo_box = get_second_skills_category(player)

    return render(request, 'teams/random_second_skill.html', {'player': player, 'form': form, 'combo_box': combo_box})


@login_required
def select_first_skill(request, player_id):
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' first skill for player ' + str(player))

    if player.team.coach.id != request.user.id:
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' first skill for player ' + str(player)
                       + ' for not owned team')
        return redirect(player.team.get_my_team_detail_absolute_url())

    level_cost = get_levelup_cost_by_level(player, 1)
    if player.spp < level_cost:
        messages.error(request, 'You cannot level up a this player: too few SPP')
        logger.warning('User ' + str(request.user) + ' first skill for player ' + str(player)
                       + ' not enough SPP. SPP -> ' + str(player.spp) + ' - Level cost ' + str(level_cost))
        return redirect(player.team.get_my_team_detail_absolute_url())

    if request.method == "POST":
        # TODO: Check if the skill could be chosen: input validation
        skill_id = request.POST['skill']
        skill = Skill.objects.filter(id=skill_id).get()
        if skill is not None:
            logger.debug('User ' + str(request.user) + ' first skill for player ' + str(player)
                         + ' Skill -> ' + str(skill))
            try:
                with transaction.atomic():
                    player.extra_skills.add(skill)
                    player.level = get_new_level(player)
                    player.value += 20000
                    player.spp -= level_cost
                    player.spent_spp += level_cost
                    player.save()
                    player.team.value = update_team_value(player.team, True)
                    player.team.current_team_value = update_team_value(player.team)
                    player.team.save()
            except Exception as e:
                logger.error('User ' + str(request.user) + ' first skill error ' + str(player) +
                             ' Exception ' + str(e))
                messages.error(request, 'Internal error first skill Player')
                return redirect('teams:my_teams')

        else:
            messages.error(request, "Skill with id " + skill_id + " not found!!!")
            logger.warning('User ' + str(request.user) + ' first skill for player ' + str(player)
                           + ' Skill not found ' + str(skill_id))
        return redirect(player.team.get_my_team_detail_absolute_url())

    first_skills = get_first_skills_select_option(player)
    return render(request, 'teams/select_first_skill.html', {'player': player, 'first_skills': first_skills})


@login_required
def select_second_skill(request, player_id):
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' second skill for player ' + str(player))

    if player.team.coach.id != request.user.id:
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        logger.warning('User ' + str(request.user) + ' second skill for player ' + str(player)
                       + ' for not owned team')
        return redirect(player.team.get_my_team_detail_absolute_url())

    level_cost = get_levelup_cost_by_level(player, 2)
    if player.spp < level_cost:
        messages.error(request, 'You cannot level up a this player: too few SPP')
        logger.warning('User ' + str(request.user) + ' second skill for player ' + str(player)
                       + ' not enough SPP. SPP -> ' + str(player.spp) + ' - Level cost ' + str(level_cost))
        return redirect(player.team.get_my_team_detail_absolute_url())

    if request.method == "POST":
        # TODO: Check if the skill could be chosen: input validation
        skill_id = request.POST['skill']
        skill = Skill.objects.filter(id=skill_id).get()
        if skill is not None:
            logger.debug('User ' + str(request.user) + ' first skill for player ' + str(player)
                         + ' Skill -> ' + str(skill))
            try:
                with transaction.atomic():
                    player.extra_skills.add(skill)
                    player.level = get_new_level(player)
                    player.value += 40000
                    player.spp -= level_cost
                    player.spent_spp += level_cost
                    player.save()
                    player.team.value = update_team_value(player.team, True)
                    player.team.current_team_value = update_team_value(player.team)
                    player.team.save()
            except Exception as e:
                logger.error('User ' + str(request.user) + ' second skill error ' + str(player) +
                             ' Exception ' + str(e))
                messages.error(request, 'Internal error second skill Player')
                return redirect('teams:my_teams')
        else:
            messages.error(request, "Skill with id " + skill_id + " not found!!!")
            logger.warning('User ' + str(request.user) + ' second skill for player ' + str(player)
                           + ' Skill not found ' + str(skill_id))
        return redirect(player.team.get_my_team_detail_absolute_url())

    second_skills = get_second_skills_select_option(player)
    return render(request, 'teams/select_second_skill.html', {'player': player, 'second_skills': second_skills})


def index_test(request):
    return render(request, 'index.html')


@login_required
def render_pdf_view(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    logger.debug('User ' + str(request.user) + ' try to create pdf for team' + str(team))

    template_path = 'teams/team_pdf.html'
    dedicated_fan = team.extra_dedicated_fan + 1
    context = {'team': team, 'dedicated_fan': dedicated_fan}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')

    # To download the file
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # To view the file
    response['Content-Disposition'] = 'filename="' + team.name + '.pdf"'

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
