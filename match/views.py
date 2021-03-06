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
from .close_helpers.tournament_helper import update_tournament_result
from .match_container import MatchContainer
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
def close_match(request, *args, **kwargs):
    match_id = kwargs.get('match_id')
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

                # Reset the MNG flag. First things otherwise we reset the MNG due close match
                reset_missing_next_game(match.first_team)
                reset_missing_next_game(match.second_team)

                match_data = CloseMatchDataReader(data, match, conceded_data)

                match_data.prepare()
                match_data.post_match()
                match_data.winning_points()

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

                # Reset freeze status
                logger.debug(f"Reset freeze status for {str(match.first_team)} and {str(match.second_team)}")
                match.first_team.freeze = False
                match.second_team.freeze = False

                match.first_team.save()
                match.second_team.save()
                match.played = True
                match.save()

                # match_container = MatchContainer(match)

                # UPDATE TOURNAMENT RESULT
                if match.tournament is not None:
                    update_tournament_result(match, match_data)

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
