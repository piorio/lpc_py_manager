from league.models import TournamentTeamResult
import logging

logger = logging.getLogger(__name__)


def update_tournament_result(match, match_data):
    logger.debug('Try to Update the tournament match entry for match ' + str(match))
    tournament = match.tournament

    tournament_first_team = TournamentTeamResult.objects \
        .filter(tournament=tournament).filter(team=match.first_team).first()

    tournament_second_team = TournamentTeamResult.objects \
        .filter(tournament=tournament).filter(team=match.second_team).first()

    # For now only if both have tournament, we update that entry
    if tournament_first_team is not None and tournament_second_team is not None:
        match_data.update_tournament_team_data(tournament_first_team, tournament_second_team)
        tournament_first_team.save()
        tournament_second_team.save()
    else:
        logger.error('Unable to find tournament match for match ' + str(match) + ' for first team  '
                     + str(match.first_team) + ' or second team ' + str(match.second_team))




