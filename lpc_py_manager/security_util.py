import logging

logger = logging.getLogger(__name__)


def is_team_belong_to_logged_user(team, request):
    if team.coach.id != request.user.id:
        logger.warning(f"User {request.user} try to operate on not owned team {team}")
        return False
    return True


def is_roster_player_belongs_to_roster(team, roster_player_id, user):
    all_roster_players = list(team.roster_team.roster_players.values_list('id', flat=True))
    if int(roster_player_id) not in all_roster_players:
        logger.warning('User ' + str(user) + ' try to buy ' + str(roster_player_id) + ' for team '
                       + str(team) + ' but the player not belong to the roster')
        return False
    return True


def is_player_belongs_to_team(team, player_id, user):
    all_team_players_id = list(team.players.values_list('id', flat=True))
    if int(player_id) not in all_team_players_id:
        logger.warning('User ' + str(user) + ' try to fire ' + str(player_id) + ' but not play for team '
                       + str(team))
        return False
    return True


def is_team_in_league_i_manage(team, request):
    # If the team is not in a league, False for sure
    if team.season is None:
        return False

    managers_of_league = team.season.league.managers.all()
    if managers_of_league is not None and len(managers_of_league) > 0:
        managers_of_league_id = [manager.id for manager in managers_of_league]
        if request.user.id in managers_of_league_id:
            return True

    # If the request user is not admin return False
    return False
