from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from match.models import Match
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CloseMatchForm
from django.contrib import messages


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
        match_form = CloseMatchForm(request.POST)
        if match_form.is_valid():
            match.first_team_td = match_form.cleaned_data['first_team_td']
            match.second_team_td = match_form.cleaned_data['second_team_td']
            match.first_team_badly_hurt = match_form.cleaned_data['first_team_badly_hurt']
            match.second_team_badly_hurt = match_form.cleaned_data['second_team_badly_hurt']
            match.first_team_serious_injury = match_form.cleaned_data['first_team_serious_injury']
            match.second_team_serious_injury = match_form.cleaned_data['second_team_serious_injury']
            match.first_team_kill = match_form.cleaned_data['first_team_kill']
            match.second_team_kill = match_form.cleaned_data['second_team_kill']

            first_team_cas = 0
            second_team_cas = 0

            if match.first_team_badly_hurt is not None:
                first_team_cas += match.first_team_badly_hurt
            if match.first_team_serious_injury is not None:
                first_team_cas += match.first_team_serious_injury
            if match.first_team_kill is not None:
                first_team_cas += match.first_team_kill
            match.first_team_cas = first_team_cas

            if match.second_team_badly_hurt is not None:
                second_team_cas += match.second_team_badly_hurt
            if match.second_team_serious_injury is not None:
                second_team_cas += match.second_team_serious_injury
            if match.second_team_kill is not None:
                second_team_cas += match.second_team_kill
            match.second_team_cas = second_team_cas

            match.save()
            return redirect('match:all_matches')
        else:
            messages.error(request, 'Close error ' + str(match_form.errors))
            match_form = CloseMatchForm(initial={
                'first_team_td': match.first_team_td, 'second_team_td': match.second_team_td,
                'first_team_badly_hurt': match.first_team_badly_hurt,
                'first_team_serious_injury': match.second_team_serious_injury,
                'first_team_kill': match.first_team_kill, 'second_team_badly_hurt': match.second_team_badly_hurt,
                'second_team_serious_injury': match.second_team_serious_injury,
                'second_team_kill': match.second_team_kill
            })
            return render(request, 'matches/close_match.html', {'match': match, 'form': match_form})
    else:
        match_form = CloseMatchForm(initial={
            'first_team_td': match.first_team_td, 'second_team_td': match.second_team_td,
            'first_team_badly_hurt': match.first_team_badly_hurt,
            'first_team_serious_injury': match.first_team_serious_injury,
            'first_team_kill': match.first_team_kill, 'second_team_badly_hurt': match.second_team_badly_hurt,
            'second_team_serious_injury': match.second_team_serious_injury, 'second_team_kill': match.second_team_kill
        })
        return render(request, 'matches/close_match.html', {'match': match, 'form': match_form})
