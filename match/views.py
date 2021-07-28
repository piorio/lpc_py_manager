from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from match.models import Match


# Create your views here.
class AllMatchesListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/all_matches.html'
    context_object_name = 'matches'
    paginate_by = 20
    ordering = ['-match_date']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllMatchesListView, self).dispatch(request, args, kwargs)


class MyMatchesListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/my_matches.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.filter(
            Q(first_team__coach=self.request.user) | Q(second_team__coach=self.request.user)
        ).order_by('-match_date')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyMatchesListView, self).dispatch(request, args, kwargs)


@login_required
def close_match(request, match_id):
    if not request.user.is_superuser:
        return HttpResponse(status=403)  # HTTP 403 Forbidden
    if request.method == 'POST':
        pass
    else:
        return render(request, 'matches/close_match.html', {})
