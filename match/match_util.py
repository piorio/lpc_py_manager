from .close_helpers.match_player import MatchPlayer
from .close_helpers.match_team import MatchTeam
from .models import TeamPlayerMatchRecord
import logging

logger = logging.getLogger(__name__)


class CloseMatchDataReader:
    def __init__(self, data, team, selected_team, match, conceded_team):
        self.select_team = {'FIRST': 'first_team_extra_fan', 'SECOND': 'second_team_extra_fan'}
        self.mvp_team = {'FIRST': 'first_team_mvp', 'SECOND': 'second_team_mvp'}
        self.selected_team = selected_team
        self.data = data
        self.team = team
        self.players = team.players.all()
        self.team_id = team.id
        self.match = match
        self.fan_factor = 0
        self.number_of_td = 0
        self.conceded_team = conceded_team

    def get_fan_factor(self):
        return self.fan_factor

    def get_number_of_td(self):
        return self.number_of_td

    def prepare(self):
        logger.debug("Match util prepare DATA FORM " + str(self.data))
        logger.debug("Match util prepare selected team " + str(self.selected_team) + ' TEAM ' + str(self.team))

        if self.selected_team not in self.select_team:
            logger.warning('For team ' + str(self.team) + ' and matchId ' + str(self.match.id)
                           + '. Unable to find index into select_team ')
            return

        first_team_match = MatchTeam(self.match.first_team, "FIRST", self.data, self.match)
        second_team_match = MatchTeam(self.match.second_team, "SECOND", self.data, self.match)

        first_team_match.calculate_extra_fan()
        second_team_match.calculate_extra_fan()

        first_team_match.calculate_for_all_players()
        second_team_match.calculate_for_all_players()

        if first_team_match.is_valid() and second_team_match.is_valid():
            first_team_match.apply()
            second_team_match.apply()
        else:
            logger.debug('For team ' + str(self.team) + ' and matchId ' + str(self.match.id)
                         + '. Team close match invalid')
            raise Exception('Invalid close match for team ' + str(self.team))

        if self.selected_team == 'FIRST':
            self.number_of_td = first_team_match.touchdown
            self.fan_factor = first_team_match.fan_factor
        elif self.selected_team == 'SECOND':
            self.number_of_td = second_team_match.touchdown
            self.fan_factor = second_team_match.fan_factor

        self.match.save()

    def is_second_mvp(self, player):
        data_key = self.mvp_team[self.selected_team] + "_"
        player_mvp = self.data[data_key]
        if player_mvp != '--' and int(player_mvp) == player.id:
            return True
        else:
            return False


def reset_missing_next_game(team):
    for player in team.players.all():
        if player.missing_next_game:
            player.missing_next_game = False
            player.save()


def is_conceded(data):
    first_team_conceded = False
    second_team_conceded = False
    team_conceded = None

    if 'first_team_conceded' in data and data['first_team_conceded'] == 'on':
        first_team_conceded = True
        team_conceded = 'FIRST'

    if 'second_team_conceded' in data and data['first_team_conceded'] == 'on':
        second_team_conceded = True
        team_conceded = 'SECOND'

    if first_team_conceded and second_team_conceded:
        return False, True, "Only one team can conceded"

    return_flag = first_team_conceded or second_team_conceded
    if not return_flag:
        team_conceded = False

    return return_flag, False, team_conceded
