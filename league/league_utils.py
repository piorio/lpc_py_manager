from django.db import transaction
from league.models import Season, Tournament, TournamentTeamResult
import logging

from match.models import Match
from teams.models import Team

logger = logging.getLogger(__name__)


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
    number_of_teams = 0
    for season in seasons:
        number_of_teams += Team.objects.filter(season=season).count()
    return number_of_teams


def get_number_of_teams_for_season(season):
    return Team.objects.filter(season=season).count()


def get_all_teams_for_season(season):
    return Team.objects.filter(season=season).all()


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
