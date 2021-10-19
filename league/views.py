from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from league.forms import RequireNewLeagueForm
from match.models import Match
from django.shortcuts import render, redirect, get_object_or_404
from teams.team_helper import update_team_value
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


@login_required()
def request_new_league(request, *args, **kwargs):
    logger.debug('User ' + str(request.user) + ' require a new league')
    if request.method == 'POST':
        form = RequireNewLeagueForm(request.POST)
        if form.is_valid():
            logger.debug('User ' + str(request.user) + ' require a new league with author '
                         + str(form.cleaned_data['author']) + ' and author email '
                         + str(form.cleaned_data['author_email']))
            messages.success(request, 'Your request is send to admin. You will be contacted')
            return HttpResponseRedirect('/')
        else:
            logger.debug('User ' + str(request.user) + ' require a new league with invalid form ' + str(form))
            messages.warning(request, 'You provide invalid information')
            form = RequireNewLeagueForm()
            return render(request, 'league/require_new_league.html', {'form': form})
    else:
        form = RequireNewLeagueForm()
        return render(request, 'league/require_new_league.html', {'form': form})


