from django.db import transaction

from league.dtos import AllLeaguesDTO, AllSeasonsDTO, AllTournamentsDTO
from league.models import Season, Tournament, TournamentTeamResult, League
import logging

from match.models import Match
from teams.models import Team
from django.contrib import messages

logger = logging.getLogger(__name__)


def get_managed_leagues_by_league_id(request, league_id):
    league = League.objects.filter(managers__in=[request.user]).filter(id=league_id).first()
    if league is None:
        logger.warning(f"User {str(request.user)} request detail for league {str(league_id)} but return empty result")
        messages.warning(request, f"You are not a manager for leagueId {str(league_id)}")
    return league


def create_new_season(league, season_name):
    try:
        with transaction.atomic():
            season = Season()
            season.name = season_name
            season.status = 'OPEN'
            season.league = league
            season.save()
            logger.debug('Create successfully the season ' + season_name + ' for league ' + league.debug())
            return True
    except Exception as e:
        logger.error('Error in create the season ' + season_name + ' for league ' + league.debug()
                     + ' with exception ' + str(e))
    return False


def create_new_tournament(season, tournament_name):
    try:
        with transaction.atomic():
            tournament = Tournament()
            tournament.name = tournament_name
            tournament.status = 'OPEN'
            tournament.season = season
            tournament.save()
            logger.debug('Create successfully the tournament ' + tournament_name + ' for season ' + season.debug())
            return True
    except Exception as e:
        logger.error('Error in create the tournament ' + tournament_name + ' for season ' + season.debug()
                     + ' with exception ' + str(e))
    return False


def get_number_of_teams_for_seasons(seasons):
    teams = get_all_teams_for_seasons(seasons)
    if teams is not None:
        return teams.count()

    return 0


def get_number_of_teams_for_season(season):
    return Team.objects.filter(season=season).count()


def get_all_teams_for_season(season):
    return Team.objects.filter(season=season).all()


def get_all_teams_for_seasons(seasons):
    return Team.objects.filter(season__in=seasons).all()


def get_all_tournaments_for_seasons(seasons):
    return Tournament.objects.filter(season__in=seasons).all()


def get_all_tournaments_for_season(season):
    return Tournament.objects.filter(season=season).all()


def get_number_of_tournaments_for_season(season):
    return Tournament.objects.filter(season=season).count()


def get_number_of_tournaments_for_seasons(seasons):
    tournaments = get_all_tournaments_for_seasons(seasons)
    if tournaments is not None:
        return tournaments.count()

    return 0


def get_distinct_joined_seasons(user):
    all_seasons_joined = Season.objects.filter(team__coach=user).all()
    if all_seasons_joined is not None:
        all_seasons_joined_distinct = list(set(all_seasons_joined))
        return all_seasons_joined_distinct
    return None


def get_all_ready_teams_without_season():
    return Team.objects \
        .filter(season=None) \
        .filter(status='READY') \
        .all()


def get_all_teams_for_tournament(tournament):
    return tournament.team.all()


def get_all_results_for_tournament(tournament):
    return TournamentTeamResult.objects.filter(tournament=tournament).all()


def get_all_matches_for_tournament(tournament):
    return Match.objects.filter(tournament=tournament).all()


def add_team_to_season(chosen_team, teams_id, season, request):
    chosen_team_id = int(chosen_team)
    if chosen_team_id in teams_id:
        team = Team.objects.filter(id=chosen_team).get()
        team.season = season
        team.save()
        messages.success(request, f"Add team {str(team.name)} successfully")
        return True
    else:
        logger.warning(f"User {str(request.user)} wants add a team to seasonId {str(season.id)} "
                       f"but the teamId {str(chosen_team)} is not a valid id. List is {str(teams_id)}")
        messages.warning(request, 'You chosen an invalid team')
        return False


def add_team_to_tournament(chosen_team, teams_id, tournament, request):
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

                messages.success(request, f"Add team {str(team.name)} successfully")
                return True
        except Exception as e:
            logger.error(f"User {str(request.user)} wants add a team to tournamentId {str(tournament.id)} "
                         f"but there is exception {str(e)}")
            messages.error(request, 'Internal error')
            return False
    else:
        logger.warning(f"User {str(request.user)} wants add a team to tournamentId {str(tournament.id)} "
                       f"but the teamId {str(chosen_team)} is not a valid id. List is {str(teams_id)}")
        messages.warning(request, 'You chosen an invalid team')
        return False


def get_all_leagues_contained_info():
    leagues = League.objects.all()
    leagues_dto = []

    for league in leagues:
        dto = get_all_league_contained_info(league)
        leagues_dto.append(dto)

    return leagues_dto


def get_all_league_contained_info(league):
    seasons = Season.objects.filter(league=league).all()
    seasons_count = 0
    teams_count = 0
    tournaments_count = 0
    if seasons is not None:
        seasons_count = seasons.count()
        teams_count = get_number_of_teams_for_seasons(seasons)
        tournaments_count = get_number_of_tournaments_for_seasons(seasons)

    kwargs = {'league': league, 'seasons_count': seasons_count, 'teams_count': teams_count,
              'tournaments_count': tournaments_count, 'league_status': league.status}
    dto = AllLeaguesDTO(**kwargs)
    return dto


def get_joined_leagues_contained_info(user):
    # The queries must be optimized
    leagues_dto = []
    all_seasons_joined = Season.objects.filter(team__coach=user).all()
    if all_seasons_joined is not None:
        all_distinct_leagues = all_seasons_joined.values('league').distinct()
        leagues = League.objects.filter(pk__in=all_distinct_leagues)
        for league in leagues:
            dto = get_all_league_contained_info(league)
            leagues_dto.append(dto)

    return leagues_dto


def get_joined_seasons_contained_info(user):
    seasons_dto = []
    all_seasons_joined_distinct = get_distinct_joined_seasons(user)
    if all_seasons_joined_distinct is not None:
        for season in all_seasons_joined_distinct:
            teams_count = get_number_of_teams_for_season(season)
            tournaments_count = get_number_of_tournaments_for_season(season)

            kwargs = {'season': season, 'teams_count': teams_count, 'tournaments_count': tournaments_count}
            dto = AllSeasonsDTO(**kwargs)
            seasons_dto.append(dto)

    return seasons_dto


def get_joined_tournaments_contained_info(user):
    tournaments_dto = []
    user_tournaments = Tournament.objects.filter(team__coach=user)
    if user_tournaments is not None:
        # make distinct
        user_tournaments = list(set(user_tournaments))
        for tournament in user_tournaments:
            teams_count = get_number_of_teams_for_season(tournament.season)
            kwargs = {'season': tournament.season, 'teams_count': teams_count, 'tournament': tournament}
            dto = AllTournamentsDTO(**kwargs)
            tournaments_dto.append(dto)
    return tournaments_dto


def user_manage_at_least_a_league(user):
    leagues = League.objects.filter(managers__in=[user])
    if leagues is None or len(leagues) == 0:
        return False
    return True

