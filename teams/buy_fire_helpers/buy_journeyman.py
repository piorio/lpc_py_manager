from roster.models import Skill
import logging

from teams.models import TeamPlayer

logger = logging.getLogger(__name__)


class BuyJourneyman:
    def __init__(self, team, roster_player, user):
        self.team = team
        self.roster_player = roster_player
        self.user = user
        self.message_for_flash = None
        self.buy_player_state = False

    def buy_journeyman(self):
        buy_flag = self.check_max_team_player()
        if not buy_flag:
            return False

        self.buy_player_state = buy_flag
        return buy_flag

    def check_max_team_player(self):
        if self.team.number_of_players > 10:
            logger.warning('User ' + str(self.user) + ' try to hire journeyman ' + str(self.roster_player)
                           + ' for team ' + str(self.team) + ' but can\'t buy if you have more than 16 players. '
                           + ' Players counter -> ' + str(self.team.number_of_players))
            self.message_for_flash = 'You can\'t buy a journeyman if you have more  than 11 players'
            return False

        return True

    def generate_player_to_buy(self):
        logger.debug('User ' + str(self.user) + ' hire Journeyman ' + str(self.roster_player) + ' for team '
                     + str(self.team) + ' Flag status ' + str(self.buy_player_state))

        if self.buy_journeyman():
            player = TeamPlayer()
            player.init_with_roster_player(self.roster_player, self.team)
            self.team.number_of_players += 1

            logger.debug('User ' + str(self.user) + ' hire ' + str(self.roster_player) + ' for team '
                         + str(self.team) + ' New Treasury ' + str(self.team.treasury))

            return player

        logger.debug('User ' + str(self.user) + ' can\'t hire ' + str(self.roster_player) + ' for team '
                     + str(self.team) + ' for invalid flag status ' + str(self.buy_player_state))
        return None

    def add_more_skill(self, player):
        skill = self.find_loner_skill()
        logger.debug('User ' + str(self.user) + ' hire journeyman ' + str(self.roster_player) + ' for team '
                     + str(self.team) + ' Add skill ' + str(skill))

        if skill is not None:
            player.extra_skills.add(skill)

    def find_loner_skill(self):
        return Skill.objects.filter(name='Loner (4+)').get()

