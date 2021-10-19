from .close_helpers.match_player import MatchPlayer
from .close_helpers.match_team import MatchTeam
from .models import TeamPlayerMatchRecord
import logging

logger = logging.getLogger(__name__)


class CloseMatchDataReader:
    def __init__(self, data, match, conceded_team):
        self.select_team = {'FIRST': 'first_team_extra_fan', 'SECOND': 'second_team_extra_fan'}
        self.mvp_team = {'FIRST': 'first_team_mvp', 'SECOND': 'second_team_mvp'}
        self.data = data
        self.match = match
        self.fan_factor = 0
        self.number_of_td = 0
        self.conceded_team = conceded_team
        self.first_team_match = None
        self.second_team_match = None

    def get_fan_factor(self):
        return self.fan_factor

    def get_number_of_td(self):
        return self.number_of_td

    def prepare(self):
        logger.debug("Match util prepare DATA FORM " + str(self.data))

        self.first_team_match = MatchTeam(self.match.first_team, "FIRST", self.data, self.match)
        self.second_team_match = MatchTeam(self.match.second_team, "SECOND", self.data, self.match)

        self.first_team_match.calculate_extra_fan()
        self.second_team_match.calculate_extra_fan()

        self.first_team_match.calculate_for_all_players()
        self.second_team_match.calculate_for_all_players()

        if self.first_team_match.is_valid() and self.second_team_match.is_valid():
            self.first_team_match.apply()
            self.second_team_match.apply()
        else:
            logger.debug('For team ' + str(self.first_team_match) + ' and ' + str(self.second_team_match)
                         + ' and matchId ' + str(self.match.id) + '. Team close match invalid')
            raise Exception('Invalid close match for match ' + str(self.match))

        self.number_of_td = self.first_team_match.touchdown + self.second_team_match.touchdown
        self.fan_factor = self.first_team_match.fan_factor + self.second_team_match.fan_factor

        self.match.save()

    # def is_second_mvp(self, player):
    #    data_key = self.mvp_team[self.selected_team] + "_"
    #    player_mvp = self.data[data_key]
    #    if player_mvp != '--' and int(player_mvp) == player.id:
    #        return True
    #    else:
    #        return False

    def post_match(self):
        total_fan = self.fan_factor

        logger.debug('For match ' + str(self.match.id) + ' first team fan factor '
                     + str(self.first_team_match.fan_factor) + ' second team fan factor '
                     + str(self.second_team_match.fan_factor) + ' total fan ' + str(total_fan))

        self.match.first_team.treasury += ((total_fan / 2) + self.first_team_match.touchdown) * 10000
        logger.debug('For match ' + str(self.match.id) + ' first team total fan / 2 '
                     + str((total_fan / 2)) + ' - After add first team TD '
                     + str((total_fan / 2) + self.first_team_match.touchdown)
                     + ' - total =>  ' + str(((total_fan / 2) + self.first_team_match.touchdown) * 10000)
                     + ' - New treasury -> ' + str(self.match.first_team.treasury))

        self.match.second_team.treasury += ((total_fan / 2) + self.second_team_match.touchdown) * 10000
        logger.debug('For match ' + str(self.match.id) + ' second team total fan / 2 '
                     + str((total_fan / 2)) + ' - After add second team TD '
                     + str((total_fan / 2) + self.second_team_match.touchdown)
                     + ' - total =>  ' + str(((total_fan / 2) + self.second_team_match.touchdown) * 10000)
                     + ' - New treasury -> ' + str(self.match.second_team.treasury))

    def winning_points(self):
        first_team_td = self.first_team_match.touchdown
        second_team_td = self.second_team_match.touchdown
        if first_team_td > second_team_td:
            self.match.first_team.win += 1
            self.match.first_team.league_points += 3
            self.match.second_team.loss += 1
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.first_team) + ' win')
        elif first_team_td < second_team_td:
            self.match.first_team.loss += 1
            self.match.second_team.win += 1
            self.match.second_team.league_points += 3
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.second_team) + ' win')
        elif first_team_td == second_team_td:
            self.match.first_team.tie += 1
            self.match.second_team.tie += 1
            self.match.first_team.league_points += 1
            self.match.second_team.league_points += 1
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.first_team) + ' and team '
                         + str(self.match.second_team) + ' tie')

        # More league points for team 1
        if first_team_td > 2:
            self.match.first_team.league_points += 1
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.first_team)
                         + ' gain 1 league point for TD ' + str(first_team_td))
        if self.match.first_team_cas > 2:
            self.match.first_team.league_points += 1
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.first_team)
                         + ' gain 1 league point for CAS ' + str(self.match.first_team_cas))
        if second_team_td == 0:
            self.match.first_team.league_points += 1
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.first_team)
                         + ' gain 1 league point for 0 TD received ' + str(second_team_td))

        # More league points for team 2
        if second_team_td > 2:
            self.match.second_team.league_points += 1
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.second_team)
                         + ' gain 1 league point for TD ' + str(first_team_td))
        if self.match.second_team_cas > 2:
            self.match.second_team.league_points += 1
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.second_team)
                         + ' gain 1 league point for CAS ' + str(self.match.second_team_cas))
        if first_team_td == 0:
            self.match.second_team.league_points += 1
            logger.debug('For match ' + str(self.match) + ' team ' + str(self.match.second_team)
                         + ' gain 1 league point for 0 TD received ' + str(first_team_td))


def reset_missing_next_game(team):
    for player in team.players.all():
        logger.debug('Close match for team ' + str(team) + ' check MNG for player ' + str(player))
        if player.missing_next_game:
            logger.debug('Close match for team ' + str(team) + ' player ' + str(player) + ' Reset MNG')
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
