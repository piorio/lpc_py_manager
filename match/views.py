from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from match.models import Match
from django.shortcuts import render, redirect, get_object_or_404
from teams.team_helper import update_team_value
from .match_util import CloseMatchDataReader, reset_missing_next_game


# Create your views here.
class AllMatchesToPlayListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/all_matches.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.filter(played=False).order_by('-match_date')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllMatchesToPlayListView, self).dispatch(request, args, kwargs)


class AllMatchesPlayedListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/all_matches_played.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.filter(played=True).order_by('-match_date')

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
        ).order_by('-match_date')

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
        ).order_by('-match_date')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyMatchesPlayedListView, self).dispatch(request, args, kwargs)


@login_required
def close_match(request, match_id):
    if not request.user.is_superuser:
        return HttpResponse(status=403)  # HTTP 403 Forbidden

    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        data = request.POST
        print(data)

        reset_missing_next_game(match.first_team)
        reset_missing_next_game(match.second_team)

        first_team_data = CloseMatchDataReader(data, match.first_team, 'FIRST', match)
        second_team_data = CloseMatchDataReader(data, match.second_team, 'SECOND', match)

        first_team_data.prepare()
        second_team_data.prepare()

        total_fan = first_team_data.get_fan_factor() + second_team_data.get_fan_factor()
        match.first_team.treasury += ((total_fan / 2) + first_team_data.get_number_of_td()) * 10000
        match.second_team.treasury += ((total_fan / 2) + second_team_data.get_number_of_td()) * 10000

        first_team_fan_update = data["first_team_update_fan"]
        if first_team_fan_update:
            match.first_team.extra_dedicated_fan += int(first_team_fan_update)
            if match.first_team.extra_dedicated_fan < 0:
                match.first_team.extra_dedicated_fan = 0

        second_team_fan_update = data["second_team_update_fan"]
        if second_team_fan_update:
            match.second_team.extra_dedicated_fan += int(second_team_fan_update)
            if match.second_team.extra_dedicated_fan < 0:
                match.second_team.extra_dedicated_fan = 0

        match.first_team.value = update_team_value(match.first_team, True)
        match.first_team.current_team_value = update_team_value(match.first_team)

        match.second_team.value = update_team_value(match.second_team, True)
        match.second_team.current_team_value = update_team_value(match.second_team)

        first_team_td = first_team_data.get_number_of_td()
        second_team_td = second_team_data.get_number_of_td()
        if first_team_td > second_team_td:
            match.first_team.win += 1
            match.second_team.loss += 1
        elif first_team_td < second_team_td:
            match.first_team.loss += 1
            match.second_team.win += 1
        elif first_team_td == second_team_td:
            match.first_team.tie += 1
            match.second_team.tie += 1

        match.first_team.save()
        match.second_team.save()
        match.played = True
        match.save()

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
