from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from match.models import Match
from django.shortcuts import render, redirect, get_object_or_404
from teams.team_helper import update_team_value
from .match_util import CloseMatchDataReader, reset_missing_next_game, is_conceded
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class AllMatchesToPlayListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/all_matches.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.filter(played=False).order_by('-match_date_from')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllMatchesToPlayListView, self).dispatch(request, args, kwargs)


class AllMatchesPlayedListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/all_matches_played.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.filter(played=True).order_by('-match_date_from')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllMatchesPlayedListView, self).dispatch(request, args, kwargs)


class MyMatchesToPlayListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/my_matches.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.filter(
            (Q(first_team__coach=self.request.user) | Q(second_team__coach=self.request.user)) & Q(played=False)
        ).order_by('-match_date_from')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyMatchesToPlayListView, self).dispatch(request, args, kwargs)


class MyMatchesPlayedListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/my_matches_played.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.filter(
            (Q(first_team__coach=self.request.user) | Q(second_team__coach=self.request.user)) & Q(played=True)
        ).order_by('-match_date_from')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyMatchesPlayedListView, self).dispatch(request, args, kwargs)


@login_required
def close_match(request, match_id):
    logger.debug('User ' + str(request.user) + ' Try to close match ')
    if not request.user.is_superuser:
        logger.warning('User ' + str(request.user) + ' is not an admin ')
        return HttpResponse(status=403)  # HTTP 403 Forbidden

    match = get_object_or_404(Match, id=match_id)

    logger.debug('User ' + str(request.user) + ' close match ' + match.debug())

    if request.method == 'POST':
        data = request.POST
        logger.debug('User ' + str(request.user) + ' form data ' + str(data))

        # FIRST CHECK IF THERE IS CONCEDED. TODO: Rewrite all concede code
        conceded, conceded_error, conceded_data = is_conceded(data)
        if conceded_error:
            messages.error(request, conceded_data)
            first_team_players = match.first_team.players.all()
            second_team_players = match.second_team.players.all()
            first_team_dedicated_fan = match.first_team.extra_dedicated_fan + 1
            second_team_dedicated_fan = match.second_team.extra_dedicated_fan + 1
            return render(request, 'matches/close_match.html',
                          {'match': match, 'first_team_players': first_team_players,
                           'second_team_players': second_team_players,
                           'first_team_dedicated_fan': first_team_dedicated_fan,
                           'second_team_dedicated_fan': second_team_dedicated_fan})

        try:
            with transaction.atomic():

                # Conceded check is OK. Reset next missing game
                reset_missing_next_game(match.first_team)
                reset_missing_next_game(match.second_team)

                first_team_data = CloseMatchDataReader(data, match.first_team, 'FIRST', match, conceded_data)
                second_team_data = CloseMatchDataReader(data, match.second_team, 'SECOND', match, conceded_data)

                first_team_data.prepare()
                second_team_data.prepare()

                total_fan = first_team_data.get_fan_factor() + second_team_data.get_fan_factor()

                logger.debug('For match ' + str(match.id) + ' first team fan factor '
                             + str(first_team_data.get_fan_factor()) + ' second team fan factor '
                             + str(second_team_data.get_fan_factor()) + ' total fan ' + str(total_fan))

                match.first_team.treasury += ((total_fan / 2) + first_team_data.get_number_of_td()) * 10000
                logger.debug('For match ' + str(match.id) + ' first team total fan / 2 '
                             + str((total_fan / 2)) + ' - After add first team TD '
                             + str((total_fan / 2) + first_team_data.get_number_of_td())
                             + ' - total =>  ' + str(((total_fan / 2) + first_team_data.get_number_of_td()) * 10000)
                             + ' - New treasury -> ' + str(match.first_team.treasury))

                match.second_team.treasury += ((total_fan / 2) + second_team_data.get_number_of_td()) * 10000
                logger.debug('For match ' + str(match.id) + ' second team total fan / 2 '
                             + str((total_fan / 2)) + ' - After add second team TD '
                             + str((total_fan / 2) + second_team_data.get_number_of_td())
                             + ' - total =>  ' + str(((total_fan / 2) + second_team_data.get_number_of_td()) * 10000)
                             + ' - New treasury -> ' + str(match.second_team.treasury))

                first_team_fan_update = data.get("first_team_update_fan")
                if first_team_fan_update:
                    match.first_team.extra_dedicated_fan += int(first_team_fan_update)
                    logger.debug('For match ' + str(match) + ' first team update team fan ' + first_team_fan_update)
                    if match.first_team.extra_dedicated_fan < 0:
                        match.first_team.extra_dedicated_fan = 0

                second_team_fan_update = data.get("second_team_update_fan")
                if second_team_fan_update:
                    match.second_team.extra_dedicated_fan += int(second_team_fan_update)
                    logger.debug('For match ' + str(match) + ' second team update team fan ' + second_team_fan_update)
                    if match.second_team.extra_dedicated_fan < 0:
                        match.second_team.extra_dedicated_fan = 0

                match.first_team.value = update_team_value(match.first_team, True)
                match.first_team.current_team_value = update_team_value(match.first_team)
                logger.debug('For match ' + str(match) + ' first team TV ' + str(match.first_team.value)
                             + ' current value ' + str(match.first_team.current_team_value))

                match.second_team.value = update_team_value(match.second_team, True)
                match.second_team.current_team_value = update_team_value(match.second_team)
                logger.debug('For match ' + str(match) + ' second team TV ' + str(match.second_team.value)
                             + ' current value ' + str(match.second_team.current_team_value))

                # first_team_extra_td = data["first_team_extra_td"]
                # second_team_extra_td = data["second_team_extra_td"]

                # if first_team_extra_td:
                #    first_team_extra_td_int = int(first_team_extra_td)
                #    match.first_team_td += first_team_extra_td_int
                #    match.first_team.total_touchdown += first_team_extra_td_int

                # if second_team_extra_td:
                #    second_team_extra_td_int = int(second_team_extra_td)
                #    match.second_team_td += second_team_extra_td_int
                #    match.second_team.total_touchdown += second_team_extra_td_int

                first_team_td = first_team_data.get_number_of_td()
                second_team_td = second_team_data.get_number_of_td()
                if first_team_td > second_team_td:
                    match.first_team.win += 1
                    match.first_team.league_points += 3
                    match.second_team.loss += 1
                    logger.debug('For match ' + str(match) + ' team ' + str(match.first_team) + ' win')
                elif first_team_td < second_team_td:
                    match.first_team.loss += 1
                    match.second_team.win += 1
                    match.second_team.league_points += 3
                    logger.debug('For match ' + str(match) + ' team ' + str(match.second_team) + ' win')
                elif first_team_td == second_team_td:
                    match.first_team.tie += 1
                    match.second_team.tie += 1
                    match.first_team.league_points += 1
                    match.second_team.league_points += 1
                    logger.debug('For match ' + str(match) + ' team ' + str(match.first_team) + ' and team '
                                 + str(match.second_team) + ' tie')

                # More league points for team 1
                if first_team_td > 2:
                    match.first_team.league_points += 1
                    logger.debug('For match ' + str(match) + ' team ' + str(match.first_team)
                                 + ' gain 1 league point for TD ' + str(first_team_td))
                if match.first_team_cas > 2:
                    match.first_team.league_points += 1
                    logger.debug('For match ' + str(match) + ' team ' + str(match.first_team)
                                 + ' gain 1 league point for CAS ' + str(match.first_team_cas))
                if second_team_td == 0:
                    match.first_team.league_points += 1
                    logger.debug('For match ' + str(match) + ' team ' + str(match.first_team)
                                 + ' gain 1 league point for 0 TD received ' + str(second_team_td))

                # More league points for team 2
                if second_team_td > 2:
                    match.second_team.league_points += 1
                    logger.debug('For match ' + str(match) + ' team ' + str(match.second_team)
                                 + ' gain 1 league point for TD ' + str(first_team_td))
                if match.second_team_cas > 2:
                    match.second_team.league_points += 1
                    logger.debug('For match ' + str(match) + ' team ' + str(match.second_team)
                                 + ' gain 1 league point for CAS ' + str(match.second_team_cas))
                if first_team_td == 0:
                    match.second_team.league_points += 1
                    logger.debug('For match ' + str(match) + ' team ' + str(match.second_team)
                                 + ' gain 1 league point for 0 TD received ' + str(first_team_td))

                first_team_gold = data.get('first_team_gold')
                second_team_gold = data.get('second_team_gold')

                if first_team_gold:
                    first_team_gold_int = int(first_team_gold)
                    match.first_team_gold = first_team_gold_int
                    logger.debug('For match ' + str(match) + ' team ' + str(match.first_team)
                                 + ' add gold ' + first_team_gold)
                    match.first_team.treasury += first_team_gold_int

                if second_team_gold:
                    second_team_gold_int = int(second_team_gold)
                    match.second_team_gold = second_team_gold_int
                    logger.debug('For match ' + str(match) + ' team ' + str(match.second_team)
                                 + ' add gold ' + second_team_gold)
                    match.second_team.treasury += second_team_gold_int

                match.first_team.save()
                match.second_team.save()
                match.played = True
                match.save()

                logger.debug('User ' + str(request.user) + ' closed match ' + match.debug())

        except Exception as e:
            logger.error('User ' + str(request.user) + ' close match Exception ' + str(e))
            messages.error(request, 'Internal error in close match Player')

        return redirect('match:all_matches')
    else:
        first_team_players = match.first_team.players.all()
        second_team_players = match.second_team.players.all()
        first_team_dedicated_fan = match.first_team.extra_dedicated_fan + 1
        second_team_dedicated_fan = match.second_team.extra_dedicated_fan + 1
        return render(request, 'matches/close_match.html', {'match': match, 'first_team_players': first_team_players,
                                                            'second_team_players': second_team_players,
                                                            'first_team_dedicated_fan': first_team_dedicated_fan,
                                                            'second_team_dedicated_fan': second_team_dedicated_fan})
