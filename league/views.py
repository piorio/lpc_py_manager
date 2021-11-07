from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect

from league.forms import RequireNewLeagueForm, RequireNewSeasonForm, RequireNewTournamentForm, AddTeamForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from teams.models import Team
from .mail_utils import send_league_creation_request
from django.contrib import messages
from .league_utils import create_new_season, get_number_of_teams_for_season, get_number_of_teams_for_seasons, \
    create_new_tournament, get_all_teams_for_season, get_all_ready_teams_without_season, get_all_teams_for_tournament
from .models import League, Season, Tournament, TournamentTeamResult
import logging

logger = logging.getLogger(__name__)


@login_required()
def request_new_league(request, *args, **kwargs):
    logger.debug('User ' + str(request.user) + ' require a new league')
    if request.method == 'POST':
        form = RequireNewLeagueForm(request.POST)
        if form.is_valid():
            logger.debug('User ' + str(request.user) + ' require a new league with name '
                         + str(form.cleaned_data['name']) + ' and author email '
                         + str(form.cleaned_data['author_email']))
            messages.success(request, 'Your request is send to admin. You will be contacted')
            send_league_creation_request(request.user, form.cleaned_data['name'], form.cleaned_data['author_email'])
            return HttpResponseRedirect('/')
        else:
            logger.debug('User ' + str(request.user) + ' require a new league with invalid form ' + str(form))
            messages.warning(request, 'You provide invalid information: ' + str(form.errors))
            form = RequireNewLeagueForm()
            return render(request, 'league/require_new_league.html', {'form': form})
    else:
        form = RequireNewLeagueForm()
        # form.author = request.user.get_username
        return render(request, 'league/require_new_league.html', {'form': form})


@login_required()
def get_league_i_manage(request):
    logged_user = request.user
    leagues = League.objects.filter(managers__in=[logged_user])
    return render(request, 'league/league_i_manage.html', {'leagues': leagues})


@login_required()
def get_league_detail(request, *args, **kwargs):
    league_id = kwargs.get('league_id')
    league = League.objects.filter(managers__in=[request.user]).filter(id=league_id).first()
    if league is not None:
        logger.debug('User ' + str(request.user) + ' request detail for league ' + league.debug())
        league_seasons = Season.objects.filter(league_id=league.id).all()
        number_of_teams = get_number_of_teams_for_seasons(league_seasons)
        return render(request, 'league/league_detail.html', {'league': league, 'league_seasons': league_seasons,
                                                             'number_of_teams': number_of_teams})
    else:
        logger.warning('User ' + str(request.user) + ' request detail for league ' + str(league_id)
                       + ' but return empty result')
        messages.warning(request, 'You are not a manager for leagueId ' + str(league_id))
        return redirect('league:league_i_manage')


@login_required()
def create_season(request, *args, **kwargs):
    league_id = kwargs.get('league_id')
    league = League.objects.filter(managers__in=[request.user]).filter(id=league_id).first()

    if league is None:
        logger.warning('User ' + str(request.user) + ' wants create season for league ' + str(league_id)
                       + ' but return empty result')
        messages.warning(request, 'You are not a manager for leagueId ' + str(league_id))
        return redirect('league:league_i_manage')

    if request.method == "POST":
        form = RequireNewSeasonForm(request.POST)
        if form.is_valid():
            logger.debug('User ' + str(request.user) + ' require a new season with name '
                         + str(form.cleaned_data['name']) + ' for league ' + league.name)
            flag = create_new_season(league, form.cleaned_data['name'])
            if flag:
                messages.success(request, 'Your create successfully a new season')
                return redirect('league:league_detail', **kwargs)
            else:
                messages.error(request, 'Error in create season')
                return redirect('league:league_i_manage')
        else:
            logger.debug('User ' + str(request.user) + ' require a new season with invalid form ' + str(form))
            messages.warning(request, 'You provide invalid information: ' + str(form.errors))
            form = RequireNewLeagueForm()
            return render(request, 'league/create_new_season.html', {'form': form, 'league': league})
    else:
        form = RequireNewSeasonForm()
        return render(request, 'league/create_new_season.html', {'form': form, 'league': league})


@login_required()
def get_season_detail(request, *args, **kwargs):
    season_id = kwargs.get('season_id')
    season = get_object_or_404(Season, id=season_id)
    league = League.objects.filter(managers__in=[request.user]).filter(id=season.league.id).first()
    if league is not None:
        logger.debug('User ' + str(request.user) + ' request detail for season ' + season.debug())
        season_tournaments = Tournament.objects.filter(season_id=season.id).all()
        number_of_teams = get_number_of_teams_for_season(season)
        all_teams = get_all_teams_for_season(season)
        return render(request, 'league/season_detail.html', {'league': league, 'season': season,
                                                             'season_tournaments': season_tournaments,
                                                             'number_of_teams': number_of_teams,
                                                             'all_teams': all_teams})
    else:
        logger.warning('User ' + str(request.user) + ' request detail for season ' + str(season_id)
                       + ' but return empty result')
        messages.warning(request, 'You are not a manager for seasonId ' + str(season_id))
        return redirect('league:league_i_manage')


@login_required()
def create_tournament(request, *args, **kwargs):
    season_id = kwargs.get('season_id')
    season = get_object_or_404(Season, id=season_id)
    league = League.objects.filter(managers__in=[request.user]).filter(id=season.league.id).first()

    if league is None:
        logger.warning('User ' + str(request.user) + ' wants create new tournament for seasonId ' + str(season_id)
                       + ' but return empty result')
        messages.warning(request, 'You are not a manager for leagueId ' + str(season.league.id))
        return redirect('league:league_i_manage')

    if request.method == "POST":
        form = RequireNewTournamentForm(request.POST)
        if form.is_valid():
            logger.debug('User ' + str(request.user) + ' require a new tournament with name '
                         + str(form.cleaned_data['name']) + ' for league ' + league.name
                         + ' and season ' + season.debug())
            flag = create_new_tournament(season, form.cleaned_data['name'])
            if flag:
                messages.success(request, 'Your create successfully a new tournament')
                return redirect('league:season_detail', **kwargs)
            else:
                messages.error(request, 'Error in create tournament')
                return redirect('league:league_i_manage')
        else:
            logger.debug('User ' + str(request.user) + ' require a new tournament with invalid form ' + str(form))
            messages.warning(request, 'You provide invalid information: ' + str(form.errors))
            form = RequireNewLeagueForm()
            return render(request, 'league/create_new_tournament.html', {'form': form, 'league': league,
                                                                         'season': season})
    else:
        form = RequireNewTournamentForm()
        return render(request, 'league/create_new_tournament.html', {'form': form, 'league': league, 'season': season})


@login_required()
def add_team_to_season(request, *args, **kwargs):
    season_id = kwargs.get('season_id')
    season = get_object_or_404(Season, id=season_id)
    league = League.objects.filter(managers__in=[request.user]).filter(id=season.league.id).first()

    if league is None:
        logger.warning('User ' + str(request.user) + ' wants add a team to seasonId ' + str(season_id)
                       + ' but return empty result')
        messages.warning(request, 'You are not a manager for leagueId ' + str(season.league.id))
        return redirect('league:season_detail', **kwargs)

    if request.method == "POST":
        form = AddTeamForm(request.POST)
        teams = get_all_ready_teams_without_season()
        teams_id = [team.id for team in teams]
        chosen_team = form.data['team']
        if chosen_team is not None:
            chosen_team_id = int(chosen_team)
            if chosen_team_id in teams_id:
                team = Team.objects.filter(id=chosen_team).get()
                team.season = season
                team.save()
                messages.success(request, 'Add team ' + str(team.name) + ' successfully')
                return redirect('league:season_detail', **kwargs)
            else:
                logger.warning('User ' + str(request.user) + ' wants add a team to seasonId ' + str(season_id)
                               + ' but the teamId ' + str(chosen_team) + ' is not a valid id. List is ' + str(teams_id))
                form = AddTeamForm()
                messages.warning(request, 'You chosen an invalid team')
                return render(request, 'league/add_team_to_season.html', {'form': form, 'league': league,
                                                                          'season': season, 'teams': teams})
        else:
            logger.warning('User ' + str(request.user) + ' wants add a team to seasonId ' + str(season_id)
                           + ' but chosen no team')
            form = AddTeamForm()
            messages.error(request, 'You must choose a team')
            return render(request, 'league/add_team_to_season.html', {'form': form, 'league': league,
                                                                      'season': season, 'teams': teams})
    else:
        teams = get_all_ready_teams_without_season()
        form = AddTeamForm()
        return render(request, 'league/add_team_to_season.html', {'form': form, 'league': league,
                                                                  'season': season, 'teams': teams})


@login_required()
def get_tournament_detail(request, *args, **kwargs):
    tournament_id = kwargs.get('tournament_id')
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    league = League.objects.filter(managers__in=[request.user]).filter(id=season.league.id).first()
    if league is not None:
        logger.debug('User ' + str(request.user) + ' request detail for tournament ' + tournament.debug())
        all_teams = get_all_teams_for_tournament(tournament)
        return render(request, 'league/tournament_detail.html', {'league': league, 'season': season,
                                                                 'all_teams': all_teams, 'tournament': tournament})
    else:
        logger.warning('User ' + str(request.user) + ' request detail for tournament ' + str(tournament_id)
                       + ' but return empty result')
        messages.warning(request, 'You are not a manager for tournamentId ' + str(tournament_id))
        return redirect('league:league_i_manage')


@login_required()
def add_team_to_tournament(request, *args, **kwargs):
    # TODO: Devo evitare di far mettere 2 volta la astessa squadra, altrimenti mi crea due volte il result. Add transactional
    tournament_id = kwargs.get('tournament_id')
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    league = League.objects.filter(managers__in=[request.user]).filter(id=season.league.id).first()

    if league is None:
        logger.warning('User ' + str(request.user) + ' wants add a team to tournamentId ' + str(tournament_id)
                       + ' but return empty result')
        messages.warning(request, 'You are not a manager for leagueId ' + str(season.league.id))
        return redirect('league:season_detail', **kwargs)

    if request.method == "POST":
        form = AddTeamForm(request.POST)
        teams = get_all_teams_for_season(season)
        teams_id = [team.id for team in teams]
        chosen_team = form.data['team']
        if chosen_team is not None:
            chosen_team_id = int(chosen_team)
            if chosen_team_id in teams_id:
                try:
                    with transaction.atomic():
                        team = Team.objects.filter(id=chosen_team).get()
                        if team not in tournament.team.all():
                            tournament_result = TournamentTeamResult()
                            tournament_result.team = team
                            tournament_result.tournament = tournament
                            tournament_result.save()
                            tournament.team.add(team)

                        messages.success(request, 'Add team ' + str(team.name) + ' successfully')
                        return redirect('league:tournament_detail', **kwargs)
                except Exception as e:
                    logger.error(
                        'User ' + str(request.user) + ' wants add a team to tournamentId ' + str(tournament_id)
                        + ' but there is exception ' + str(e))
                    form = AddTeamForm()
                    messages.error(request, 'Internal error')
                    return render(request, 'league/add_team_to_tournament.html', {'form': form, 'league': league,
                                                                                  'season': season, 'teams': teams})
            else:
                logger.warning('User ' + str(request.user) + ' wants add a team to tournamentId ' + str(tournament_id)
                               + ' but the teamId ' + str(chosen_team) + ' is not a valid id. List is ' + str(teams_id))
                form = AddTeamForm()
                messages.warning(request, 'You chosen an invalid team')
                return render(request, 'league/add_team_to_tournament.html', {'form': form, 'league': league,
                                                                              'season': season, 'teams': teams})
        else:
            logger.warning('User ' + str(request.user) + ' wants add a team to tournamentId ' + str(tournament_id)
                           + ' but chosen no team')
            form = AddTeamForm()
            messages.error(request, 'You must choose a team')
            return render(request, 'league/add_team_to_tournament.html', {'form': form, 'league': league,
                                                                          'season': season, 'teams': teams})
    else:
        teams = get_all_teams_for_season(season)
        form = AddTeamForm()
        return render(request, 'league/add_team_to_tournament.html', {'form': form, 'league': league,
                                                                      'season': season, 'teams': teams,
                                                                      'tournament': tournament})


def calendar(request):
    return render(request, 'league/calendar.html')
