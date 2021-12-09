from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from league.forms import RequireNewLeagueForm, RequireNewSeasonForm, RequireNewTournamentForm, AddTeamForm
from django.shortcuts import render, get_object_or_404, redirect

from .mail_utils import send_league_creation_request
from django.contrib import messages
from .league_utils import create_new_season, get_number_of_teams_for_season, get_number_of_teams_for_seasons, \
    create_new_tournament, get_all_teams_for_season, get_all_ready_teams_without_season, get_all_teams_for_tournament, \
    get_all_matches_for_tournament, get_all_results_for_tournament, \
    get_joined_leagues_contained_info, get_joined_seasons_contained_info, get_joined_tournaments_contained_info, \
    get_managed_leagues_by_league_id, get_all_leagues_contained_info
from .models import League, Season, Tournament
import logging

logger = logging.getLogger(__name__)


@login_required()
def request_new_league(request, *args, **kwargs):
    logger.debug('User ' + str(request.user) + ' require a new league')
    if request.method == 'POST':
        form = RequireNewLeagueForm(request.POST)
        if form.is_valid():
            logger.debug(f"User {str(request.user)} require a new league with name {str(form.cleaned_data['name'])} "
                         f"and author email {str(form.cleaned_data['author_email'])}")

            messages.success(request, 'Your request is send to admin. You will be contacted')
            send_league_creation_request(request.user, form.cleaned_data['name'], form.cleaned_data['author_email'])
            return HttpResponseRedirect('/')
        else:
            logger.debug(f"User {str(request.user)} require a new league with invalid form {str(form)}")
            messages.warning(request, f"You provide invalid information: {str(form.errors)}")
            form = RequireNewLeagueForm()
            return render(request, 'league/require_new_league.html', {'form': form})
    else:
        form = RequireNewLeagueForm()
        # form.author = request.user.get_username
        return render(request, 'league/require_new_league.html', {'form': form})


@login_required()
def get_league_i_manage(request):
    leagues = League.objects.filter(managers__in=[request.user])
    return render(request, 'league/league_i_manage.html', {'leagues': leagues})


@login_required()
def get_all_leagues(request):
    leagues_dto = get_all_leagues_contained_info()
    return render(request, 'league/all_leagues.html', {'leagues_dto': leagues_dto,
                                                       'leagues_list_title': 'Leagues list'})


@login_required()
def get_all_joined_leagues(request):
    leagues_dto = get_joined_leagues_contained_info(request.user)
    return render(request, 'league/all_leagues.html', {'leagues_dto': leagues_dto,
                                                       'leagues_list_title': 'All Leagues you have  joined'})


@login_required()
def get_all_joined_seasons(request):
    season_dto = get_joined_seasons_contained_info(request.user)
    return render(request, 'league/all_seasons.html', {'season_dto': season_dto})


@login_required()
def get_all_joined_tournaments(request):
    tournament_dto = get_joined_tournaments_contained_info(request.user)
    return render(request, 'league/all_tournaments.html', {'tournament_dto': tournament_dto})


@login_required()
def get_league_detail(request, *args, **kwargs):
    league_id = kwargs.get('league_id')
    league = get_managed_leagues_by_league_id(request, league_id)
    if league is not None:
        logger.debug(f"User {str(request.user)} request detail for league {league.debug()}")
        league_seasons = Season.objects.filter(league_id=league.id).all()
        number_of_teams = get_number_of_teams_for_seasons(league_seasons)
        return render(request, 'league/league_detail.html', {'league': league, 'league_seasons': league_seasons,
                                                             'number_of_teams': number_of_teams})

    return redirect('league:league_i_manage')


@login_required()
def get_league_user_detail(request, *args, **kwargs):
    league_id = kwargs.get('league_id')
    league = League.objects.filter(id=league_id).first()
    if league is not None:
        logger.debug(f"User {str(request.user)} request user detail for league {league.debug()}")
        league_seasons = Season.objects.filter(league_id=league.id).all()
        number_of_teams = get_number_of_teams_for_seasons(league_seasons)
        return render(request, 'league/league_user_detail.html', {'league': league, 'league_seasons': league_seasons,
                                                                  'number_of_teams': number_of_teams})
    else:
        logger.warning(f"User {str(request.user)} request detail for league {str(league_id)} but return empty result")
        messages.warning(request, 'Invalid leagueId ' + str(league_id))
        return redirect('teams:my_teams')


@login_required()
def create_season(request, *args, **kwargs):
    league_id = kwargs.get('league_id')
    league = get_managed_leagues_by_league_id(request, league_id)

    if league is None:
        return redirect('league:league_i_manage')

    if request.method == "POST":
        form = RequireNewSeasonForm(request.POST)
        if form.is_valid():
            logger.debug(f"User {str(request.user)} require a new season with name {str(form.cleaned_data['name'])} "
                         f"for league {league.name}")
            flag = create_new_season(league, form.cleaned_data['name'])
            if flag:
                messages.success(request, 'Your create successfully a new season')
                return redirect('league:league_detail', **kwargs)
            else:
                messages.error(request, 'Error in create season')
                return redirect('league:league_i_manage')
        else:
            logger.debug(f"User {str(request.user)} require a new season with invalid form {str(form)}")
            messages.warning(request, f"You provide invalid information: {str(form.errors)}")
            form = RequireNewLeagueForm()
            return render(request, 'league/create_new_season.html', {'form': form, 'league': league})
    else:
        form = RequireNewSeasonForm()
        return render(request, 'league/create_new_season.html', {'form': form, 'league': league})


@login_required()
def get_season_detail(request, *args, **kwargs):
    season_id = kwargs.get('season_id')
    season = get_object_or_404(Season, id=season_id)
    league = get_managed_leagues_by_league_id(request, season.league.id)

    if league is not None:
        logger.debug(f"User {str(request.user)} request detail for season {season.debug()}")
        season_tournaments = Tournament.objects.filter(season_id=season.id).all()
        number_of_teams = get_number_of_teams_for_season(season)
        all_teams = get_all_teams_for_season(season)
        return render(request, 'league/season_detail.html', {'league': league, 'season': season,
                                                             'season_tournaments': season_tournaments,
                                                             'number_of_teams': number_of_teams,
                                                             'all_teams': all_teams})

    return redirect('league:league_i_manage')


@login_required()
def get_season_user_detail(request, *args, **kwargs):
    season_id = kwargs.get('season_id')
    season = get_object_or_404(Season, id=season_id)
    league = League.objects.filter(id=season.league.id).first()
    if league is not None:
        logger.debug(f"User {str(request.user)} request detail for user season {season.debug()}")
        season_tournaments = Tournament.objects.filter(season_id=season.id).all()
        number_of_teams = get_number_of_teams_for_season(season)
        all_teams = get_all_teams_for_season(season)
        return render(request, 'league/season_user_detail.html', {'league': league, 'season': season,
                                                                  'season_tournaments': season_tournaments,
                                                                  'number_of_teams': number_of_teams,
                                                                  'all_teams': all_teams})
    else:
        logger.warning(f"User {str(request.user)} request detail for user season {str(season_id)} "
                       f"but return empty result")
        messages.warning(request, f"Invalid seasonId {str(season_id)}")
        return redirect('teams:my_teams')


@login_required()
def create_tournament(request, *args, **kwargs):
    season_id = kwargs.get('season_id')
    season = get_object_or_404(Season, id=season_id)
    league = get_managed_leagues_by_league_id(request, season.league.id)

    if league is None:
        return redirect('league:league_i_manage')

    if request.method == "POST":
        form = RequireNewTournamentForm(request.POST)
        if form.is_valid():
            logger.debug(f"User {str(request.user)} require a new tournament with name {str(form.cleaned_data['name'])}"
                         f" for league {league.name} and season {season.debug()}")
            flag = create_new_tournament(season, form.cleaned_data['name'])
            if flag:
                messages.success(request, 'Your create successfully a new tournament')
                return redirect('league:season_detail', **kwargs)
            else:
                messages.error(request, 'Error in create tournament')
                return redirect('league:league_i_manage')
        else:
            logger.debug(f"User {str(request.user)} require a new tournament with invalid form {str(form)}")
            messages.warning(request, f"You provide invalid information: {str(form.errors)}")
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
    league = get_managed_leagues_by_league_id(request, season.league.id)

    if league is None:
        return redirect('league:season_detail', **kwargs)

    if request.method == "POST":
        form = AddTeamForm(request.POST)
        teams = get_all_ready_teams_without_season()
        teams_id = [team.id for team in teams]
        chosen_team = form.data['team']
        if chosen_team is not None:
            result = add_team_to_season(chosen_team, teams_id, season, request)
            if result:
                return redirect('league:season_detail', **kwargs)
            else:
                form = AddTeamForm()
                return render(request, 'league/add_team_to_season.html', {'form': form, 'league': league,
                                                                          'season': season, 'teams': teams})
        else:
            logger.warning(f"User {str(request.user)} wants add a team to seasonId {str(season_id)} but chosen no team")
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
    league = get_managed_leagues_by_league_id(request, season.league.id)
    if league is not None:
        logger.debug(f"User {str(request.user)} request detail for tournament {tournament.debug()}")
        all_teams = get_all_teams_for_tournament(tournament)
        all_matches = get_all_matches_for_tournament(tournament)
        all_results = get_all_results_for_tournament(tournament)
        return render(request, 'league/tournament_detail.html', {'league': league, 'season': season,
                                                                 'all_teams': all_teams, 'tournament': tournament,
                                                                 'all_matches': all_matches,
                                                                 'all_results': all_results})
    return redirect('league:league_i_manage')


@login_required()
def get_tournament_user_detail(request, *args, **kwargs):
    tournament_id = kwargs.get('tournament_id')
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    league = League.objects.filter(id=season.league.id).first()
    if league is not None:
        logger.debug(f"User {str(request.user)} request detail for tournament {tournament.debug()}")
        all_teams = get_all_teams_for_tournament(tournament)
        all_matches = get_all_matches_for_tournament(tournament)
        all_results = get_all_results_for_tournament(tournament)
        return render(request, 'league/tournament_user_detail.html', {'league': league, 'season': season,
                                                                      'all_teams': all_teams, 'tournament': tournament,
                                                                      'all_matches': all_matches,
                                                                      'all_results': all_results})
    else:
        logger.warning(f"User {str(request.user)} request detail for tournament {str(tournament_id)} "
                       f"but return empty result")
        messages.warning(request, 'Invalid tournamentId ' + str(tournament_id))
        return redirect('teams:my_teams')


@login_required()
def add_team_to_tournament(request, *args, **kwargs):
    # TODO: Devo evitare di far mettere 2 volta la astessa squadra, altrimenti mi crea due volte il result. Add transactional
    tournament_id = kwargs.get('tournament_id')
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    league = get_managed_leagues_by_league_id(request, season.league.id)

    if league is None:
        return redirect('league:season_detail', **kwargs)

    if request.method == "POST":
        form = AddTeamForm(request.POST)
        teams = get_all_teams_for_season(season)
        teams_id = [team.id for team in teams]
        chosen_team = form.data['team']
        if chosen_team is not None:
            result = add_team_to_tournament(chosen_team, teams_id, tournament, request)
            if result:
                return redirect('league:tournament_detail', **kwargs)
            else:
                form = AddTeamForm()
                return render(request, 'league/add_team_to_tournament.html', {'form': form, 'league': league,
                                                                              'season': season, 'teams': teams})
        else:
            logger.warning(f"User {str(request.user)} wants add a team to tournamentId {str(tournament_id)} "
                           f"but chosen no team")
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
