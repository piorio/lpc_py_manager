from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from xhtml2pdf import pisa

from league.models import Tournament, TournamentTeamResult
from lpc_py_manager.security_util import is_team_belong_to_logged_user, is_roster_player_belongs_to_roster, \
    is_player_belongs_to_team, is_team_in_league_i_manage
from .buy_fire_helpers.buy_journeyman import BuyJourneyman
from .models import Team, TeamPlayer
from .forms import CreateMyTeamForm, RandomSkill
from roster.models import RosterTeam, RosterPlayer, Skill, Trait
from django.contrib import messages
from .team_helper import update_team_value, perform_dismiss_team, perform_ready_team, is_players_count_to_prepare_team, \
    can_you_buy_player, add_re_roll_during_team_prepare, remove_re_roll_during_team_prepare, \
    add_assistant_coach_during_team_prepare, remove_assistant_coach_during_team_prepare, \
    add_cheerleader_during_team_prepare, remove_cheerleader_during_team_prepare, add_extra_fan_during_team_prepare, \
    remove_extra_fan_during_team_prepare, add_apothecary_during_team_prepare, remove_apothecary_during_team_prepare, \
    change_player_name_number_by_request, buy_team_re_roll, remove_team_re_roll, buy_team_assistant_coach, \
    remove_team_assistant_coach, buy_team_cheerleader, remove_team_cheerleader, buy_team_apothecary, \
    remove_team_apothecary, get_random_skill_search_string, update_team_freeze, fire_player_helper
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
        self.request = request
        return super(AllTeamDetail, self).dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllTeamDetail, self).get_context_data(**kwargs)
        team = context['team']
        dedicated_fan = getattr(team, 'extra_dedicated_fan')
        enable_edit = is_team_in_league_i_manage(team, self.request)

        logger.debug(f"All team details for team {team} - Dedicated fan => {dedicated_fan} - Enable edit {enable_edit}")

        context['dedicated_fan'] = dedicated_fan + 1
        context['enable_edit'] = enable_edit
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
            messages.error(request, form.errors)
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
def dismiss_team(request, *args, **kwargs):
    pk = kwargs.get('pk')
    team = get_object_or_404(Team, id=pk)
    logger.debug('User ' + str(request.user) + ' try to dismiss team ' + str(team))
    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot retire a team not belongs to you')
    else:
        perform_dismiss_team(team, request)
        messages.success(request, 'You retire ' + str(team))
    return redirect('teams:my_teams')


@login_required
def prepare_team(request, *args, **kwargs):
    pk = kwargs.get('pk')
    team = get_object_or_404(Team, id=pk)
    logger.debug('User ' + str(request.user) + ' try to prepare team ' + str(team))
    roster_players = team.roster_team.roster_players.filter(is_journeyman=False).all()

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot prepare a team not belongs to you')
        return redirect('teams:my_teams')

    return render(request,
                  'teams/prepare_team.html', {'team': team, 'roster_players': roster_players})


@login_required
def ready_team(request, *args, **kwargs):
    pk = kwargs.get('pk')
    team = get_object_or_404(Team, id=pk)

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot ready a team not belongs to you')
    elif not is_players_count_to_prepare_team(team, request):
        messages.error(request, 'A team must have 11 to 16 players. You cannot ready a not complete team')
    else:
        perform_ready_team(team, request)
    return redirect('teams:my_teams')


@login_required
def buy_player(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    # You can buy only player not journeyman. The J didn't show into the list of players. But add a check
    roster_player_id = request.GET.get('roster_player', None)
    team = get_object_or_404(Team, id=team_id)
    roster_player_to_buy = get_object_or_404(RosterPlayer, id=roster_player_id)
    kwargs = {'pk': team.id}

    logger.debug('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                 + str(team))

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot buy a player for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    if roster_player_to_buy.is_journeyman:
        messages.error(request, 'You cannot buy a Journeyman player during team preparation')
        logger.warning('User ' + str(request.user) + ' try to buy a journeyman ' + str(roster_player_to_buy)
                       + ' for team ' + str(team))
        return redirect('teams:prepare_team', **kwargs)

    is_buy_valid = True

    # Check if roster_player_id belongs to roster team
    if not is_roster_player_belongs_to_roster(team, roster_player_id, request.user):
        messages.error(request, 'You cannot buy that player because it is not belong with the chosen roster')
        return redirect('teams:my_teams')

    is_buy_valid = can_you_buy_player(team, request, roster_player_to_buy)

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
            return redirect('teams:prepare_team', **kwargs)

        messages.success(request, 'You bought ' + str(player.position))
        logger.debug('User ' + str(request.user) + ' bought ' + str(player) + ' for team ' + str(team))

    return redirect('teams:prepare_team', **kwargs)


@login_required
def fire_player(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    # You can fire only player not journeyman. The J didn't show into the list of players. But add a check
    player_id = request.GET.get('player', None)
    team = get_object_or_404(Team, id=team_id)
    player = get_object_or_404(TeamPlayer, id=player_id)
    kwargs = {'pk': team.id}

    logger.debug('User ' + str(request.user) + ' try to fire ' + str(player) + ' for team '
                 + str(team))

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot fire a player for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    if player.roster_player.is_journeyman:
        messages.error(request, 'You cannot fire a Journeyman player during team preparation')
        logger.warning('User ' + str(request.user) + ' try to fire a journeyman ' + str(player)
                       + ' for team ' + str(team))
        return redirect('teams:prepare_team', **kwargs)

    # Check if player_id belongs to team
    if not is_player_belongs_to_team(team, player_id, request.user):
        messages.error(request, 'You cannot fire that player because it is not belong with team you are working on')
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
    return redirect('teams:prepare_team', **kwargs)


@login_required
def my_team_detail(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    team = update_team_freeze(team)
    logger.debug(f"User {request.user} request detail for {team}")

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'Team did not belongs to you')
        return redirect('teams:my_teams')

    roster_players = team.roster_team.roster_players.all()
    dedicated_fan = team.extra_dedicated_fan + 1

    valid_player_counter = team.players.filter(Q(dead=False) & Q(fired=False) & Q(missing_next_game=False)).count()

    enable_journeyman = False
    if valid_player_counter < 11:
        enable_journeyman = True

    tournaments = Tournament.objects.filter(team=team).all()
    tournaments_results = TournamentTeamResult.objects.filter(team=team).filter(tournament__in=tournaments).all()

    logger.debug('User ' + str(request.user) + ' request detail for ' + str(team) + ' Enable JourneyMan '
                 + str(enable_journeyman))
    return render(request,
                  'teams/my_team_detail.html', {'team': team, 'roster_players': roster_players,
                                                'dedicated_fan': dedicated_fan, 'enable_journeyman': enable_journeyman,
                                                'tournaments': tournaments, 'tournaments_results': tournaments_results})


@login_required
def buy_re_roll(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs_for_redirect = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot buy a re roll for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs_for_redirect)

    # check money spent and max number
    if team.roster_team.re_roll_cost > team.treasury or team.re_roll > team.roster_team.re_roll_max:
        messages.error(request,
                       'You don\'t have money for another re roll or you reached the max number of re roll permitted')
    else:
        add_re_roll_during_team_prepare(team)

    return redirect('teams:prepare_team', **kwargs_for_redirect)


@login_required
def remove_re_roll(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot remove a re roll for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    # check money spent and max number
    if team.re_roll <= 0:
        messages.error(request, 'You don\'t have re roll to remove')
    else:
        remove_re_roll_during_team_prepare(team)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def buy_assistant_coach(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot buy an assistant coach for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    add_assistant_coach_during_team_prepare(team, request)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def remove_assistant_coach(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot remove an assistant coach for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    remove_assistant_coach_during_team_prepare(team, request)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def buy_cheerleader(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot buy an cheerleader for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    add_cheerleader_during_team_prepare(team, request)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def remove_cheerleader(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot remove a cheerleader for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    remove_cheerleader_during_team_prepare(team, request)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def buy_extra_fan(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot buy an extra fan for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    add_extra_fan_during_team_prepare(team, request)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def remove_extra_fan(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot remove an extra fan for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    remove_extra_fan_during_team_prepare(team, request)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def buy_apothecary(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot buy an apothecary for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    add_apothecary_during_team_prepare(team, request)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def remove_apothecary(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    kwargs = {'pk': team.id}

    if not is_team_belong_to_logged_user(team, request):
        messages.error(request, 'You cannot remove an apothecary for a team not belongs to you')
        return redirect('teams:prepare_team', **kwargs)

    remove_apothecary_during_team_prepare(team, request)

    return redirect('teams:prepare_team', **kwargs)


@login_required
def manage_player(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    player_id = request.GET.get('player', None)
    logger.debug(f"Manage {player_id} for teamId {team_id})")
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot manage a player of a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    # Check if player_id belongs to team
    if not is_player_belongs_to_team(team, player_id, request.user):
        messages.error(request, 'You cannot manage that player because it is not belong with team you are working on')
        return redirect('teams:my_teams')

    player = get_object_or_404(TeamPlayer, id=player_id)
    team_detail_url = reverse('teams:my_team_detail', args=[str(team.id)])
    return render(request,
                  'teams/manage_player.html', {'player': player, 'team': team, 'range': range(1, 101),
                                               'team_detail': team_detail_url})


@login_required
def change_player_name_number(request):
    if request.method == 'POST':
        print(request.POST)
        player_id = request.POST['playerId']
        team_id = request.POST['teamId']
        player = get_object_or_404(TeamPlayer, id=player_id)
        team = get_object_or_404(Team, id=team_id)

        if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
            messages.error(request, 'You cannot change player name of a team not belongs to you')
            return redirect('teams:my_teams')

        if not is_player_belongs_to_team(team, player_id, request.user):
            messages.error(request, 'You cannot change the name of that player because it is not belong with team '
                                    'you are working on')
            return redirect('teams:my_teams')

        change_player_name_number_by_request(player, request)

        url_to_redirect = reverse('teams:manage_player', args=[str(team.id)]) + '?player=' + player_id
        return redirect(url_to_redirect)
    else:
        return redirect('teams:my_teams')


@login_required
def manage_fire_player(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    # If a coach fire a Journeyman, change the TV, but not the Treasury. TODO
    player_id = request.GET.get('player', None)
    team = get_object_or_404(Team, id=team_id)
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug(f"User {request.user} try to fire {player} for team {team}")

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot fire a player for a team not belongs to you')
        return redirect('teams:my_teams')

    # Check if player_id belongs to team
    if not is_player_belongs_to_team(team, player_id, request.user):
        messages.error(request, 'You cannot fire that player because it is not belong with team you are working on')
        return redirect('teams:my_teams')

    if fire_player_helper(player, team, request):
        return redirect('teams:my_team_detail', **kwargs)
    else:
        return redirect('teams:my_teams')


@login_required
def manage_buy_re_roll(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot buy a re roll for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    buy_team_re_roll(team, request)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def manage_remove_re_roll(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot remove a re roll for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    remove_team_re_roll(team, request)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def manage_buy_assistant_coach(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot buy an assistant coach for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    buy_team_assistant_coach(team, request)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def manage_remove_assistant_coach(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot remove an assistant coach for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    remove_team_assistant_coach(team, request)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def manage_buy_cheerleader(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot buy an cheerleader for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    buy_team_cheerleader(team, request)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def manage_remove_cheerleader(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot remove a cheerleader for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    remove_team_cheerleader(team, request)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def manage_buy_apothecary(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot buy an apothecary for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    buy_team_apothecary(team, request)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def manage_remove_apothecary(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot remove an apothecary for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    remove_team_apothecary(team, request)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def manage_buy_player(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    roster_player_id = request.GET.get('roster_player', None)
    team = get_object_or_404(Team, id=team_id)
    roster_player_to_buy = get_object_or_404(RosterPlayer, id=roster_player_id)

    logger.debug(f"User {request.user} try to hire {roster_player_to_buy} for team {team}")

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot buy a player for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

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
            logger.error(f"User {request.user} try to hire {player} - Exception {e}")
            messages.error(request, 'Internal error during hire Player')
            return redirect('teams:my_teams')

        messages.success(request, 'You bought ' + str(player.position))
    else:
        messages.error(request, buy_engine.message_for_flash)

    return redirect('teams:my_team_detail', **kwargs)


@login_required
def player_level_up(request, player_id):
    player = get_object_or_404(TeamPlayer, id=player_id)

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        kwargs = {'team_id': player.team.id}
        return redirect('teams:my_team_detail', **kwargs)

    level_cost = get_levelup_cost_all_levels(player)
    return render(request, 'teams/levelup.html', {'player': player, 'level_cost': level_cost})


@login_required
def random_first_skill(request, *args, **kwargs):
    player_id = kwargs.get('player_id')
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' random first skill for player ' + str(player))
    kwargs = {'team_id': player.team.id}

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    level_cost = get_levelup_cost_by_level(player, 0)
    if player.spp < level_cost:
        messages.error(request, 'You cannot level up a this player: too few SPP')
        logger.warning('User ' + str(request.user) + ' random first skill for player ' + str(player)
                       + ' not enough SPP. SPP -> ' + str(player.spp) + ' - Level cost ' + str(level_cost))
        return redirect('teams:my_team_detail', **kwargs)

    if request.method == "POST":
        form = RandomSkill(request.POST)
        if form.is_valid():
            search_string = get_random_skill_search_string(form, request, player)
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

                    kwargs = {'team_id': player.team.id}
                    return redirect('teams:my_team_detail', **kwargs)
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
def random_second_skill(request, *args, **kwargs):
    player_id = kwargs.get('player_id')
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' random second skill for player ' + str(player))
    kwargs_team = {'team_id': player.team.id}

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs_team)

    level_cost = get_levelup_cost_by_level(player, 1)
    if player.spp < level_cost:
        messages.error(request, 'You cannot level up a this player: too few SPP')
        logger.warning('User ' + str(request.user) + ' random second skill for player ' + str(player)
                       + ' not enough SPP. SPP -> ' + str(player.spp) + ' - Level cost ' + str(level_cost))
        return redirect('teams:my_team_detail', **kwargs_team)

    if request.method == "POST":
        form = RandomSkill(request.POST)
        if form.is_valid():
            search_string = get_random_skill_search_string(form, request, player)
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

                    return redirect('teams:my_team_detail', **kwargs_team)
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
def select_first_skill(request, *args, **kwargs):
    player_id = kwargs.get('player_id')
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' first skill for player ' + str(player))
    kwargs_team = {'team_id': player.team.id}

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs_team)

    level_cost = get_levelup_cost_by_level(player, 1)
    if player.spp < level_cost:
        messages.error(request, 'You cannot level up a this player: too few SPP')
        logger.warning('User ' + str(request.user) + ' first skill for player ' + str(player)
                       + ' not enough SPP. SPP -> ' + str(player.spp) + ' - Level cost ' + str(level_cost))
        return redirect('teams:my_team_detail', **kwargs_team)

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
        return redirect('teams:my_team_detail', **kwargs_team)

    first_skills = get_first_skills_select_option(player)
    return render(request, 'teams/select_first_skill.html', {'player': player, 'first_skills': first_skills})


@login_required
def select_second_skill(request, *args, **kwargs):
    player_id = kwargs.get('player_id')
    player = get_object_or_404(TeamPlayer, id=player_id)

    logger.debug('User ' + str(request.user) + ' second skill for player ' + str(player))
    kwargs_team = {'team_id': player.team.id}

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot level up a player for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs_team)

    level_cost = get_levelup_cost_by_level(player, 2)
    if player.spp < level_cost:
        messages.error(request, 'You cannot level up a this player: too few SPP')
        logger.warning('User ' + str(request.user) + ' second skill for player ' + str(player)
                       + ' not enough SPP. SPP -> ' + str(player.spp) + ' - Level cost ' + str(level_cost))
        return redirect('teams:my_team_detail', **kwargs_team)

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
        return redirect('teams:my_team_detail', **kwargs_team)

    second_skills = get_second_skills_select_option(player)
    return render(request, 'teams/select_second_skill.html', {'player': player, 'second_skills': second_skills})


def index_test(request):
    return render(request, 'index.html')


@login_required
def render_pdf_view(request, *args, **kwargs):
    team_id = kwargs.get('team_id')
    team = get_object_or_404(Team, id=team_id)
    logger.debug('User ' + str(request.user) + ' try to create pdf for team' + str(team))

    players = team.players.order_by('player_number').all()

    template_path = 'teams/team_pdf.html'
    dedicated_fan = team.extra_dedicated_fan + 1
    context = {'team': team, 'dedicated_fan': dedicated_fan, 'players': players}
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
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
def confirm_journeyman(request, *args, **kwargs):
    team_id = kwargs.get("team_id")
    player_id = request.GET.get('player', None)
    team = get_object_or_404(Team, id=team_id)

    logger.debug('User ' + str(request.user) + ' try to confirm journeymanId ' + str(player_id) + ' for team '
                 + str(team))

    if not (is_team_belong_to_logged_user(team, request) or is_team_in_league_i_manage(team, request)):
        messages.error(request, 'You cannot confirm a journeyman for a team not belongs to you')
        return redirect('teams:my_team_detail', **kwargs)

    player = get_object_or_404(TeamPlayer, id=player_id)
    logger.debug('User ' + str(request.user) + ' try to confirm journeymanId ' + player.debug() + ' for team '
                 + str(team))

    loner = get_object_or_404(Trait, name='Loner (4+)*')
    logger.debug('User ' + str(request.user) + ' try to confirm journeymanId ' + player.debug() + ' for team '
                 + str(team) + ' Found Loner TRAITS ' + str(loner))

    roster_player = team.roster_team.roster_players.all().filter(is_journeyman=False) \
        .order_by('-max_quantity')[0]

    logger.debug('User ' + str(request.user) + ' try to confirm journeymanId ' + player.debug() + ' for team '
                 + str(team) + ' Found New Roster player to use ' + str(roster_player))

    # Check if it's a valid buy
    player_check = BuyPlayer(team, roster_player, request.user)
    flag = player_check.buy_player(player.value)
    if not flag:
        messages.error(request, player_check.message_for_flash)
        return redirect('teams:my_teams')

    # The confirm a Journeyman we must remove Loner
    try:
        with transaction.atomic():
            # Update value: the value start from 0, so the best way is calculate again
            team.value = update_team_value(team, True)
            team.current_team_value = update_team_value(team)

            # Update Money: remove value instead of roster cost, so if J has more value, we update correctly
            team.treasury = team.treasury - player.value

            # Update player
            player.traits.remove(loner)
            player.is_journeyman = False
            player.roster_player = roster_player
            player.position = roster_player.position
            player.save()
            team.save()
    except Exception as e:
        logger.error('User ' + str(request.user) + ' try to hire ' + str(player) +
                     ' Exception ' + str(e))
        messages.error(request, 'Internal error during hire Player')
        return redirect('teams:my_teams')

    messages.success(request, 'You bought ' + str(player.position))
    return redirect('teams:my_team_detail', **kwargs)
