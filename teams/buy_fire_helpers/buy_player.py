import logging

from django.db.models import Q
from teams.models import TeamPlayer

logger = logging.getLogger(__name__)


class BuyPlayer:
    def __init__(self, team, roster_player, user):
        self.team = team
        self.roster_player = roster_player
        self.user = user
        self.message_for_flash = None
        self.buy_player_state = False

    def buy_player(self):
        buy_flag = self.check_max_team_player()
        if not buy_flag:
            return False

        buy_flag = self.check_money_to_spend()
        if not buy_flag:
            return False

        buy_flag = self.check_big_guy()
        if not buy_flag:
            return False

        buy_flag = self.check_max_quantity()
        if not buy_flag:
            return False

        self.buy_player_state = buy_flag
        return buy_flag

    def check_max_team_player(self):
        if self.team.number_of_players > 15:
            logger.warning('User ' + str(self.user) + ' try to hire ' + str(self.roster_player) + ' for team '
                           + str(self.team) + ' but can\'t buy more than 16 players. Players counter -> '
                           + str(self.team.number_of_players))
            self.message_for_flash = 'You can\'t buy more than 16 players'
            return False

        return True

    def check_money_to_spend(self):
        if self.roster_player.cost > self.team.treasury:
            logger.warning('User ' + str(self.user) + ' try to hire ' + str(self.roster_player) + ' for team '
                           + str(self.team) + ' but don\'t have money. Treasury -> ' + str(self.team.treasury)
                           + ' Player cost -> ' + str(self.roster_player.cost))
            self.message_for_flash = 'You don\'t have money for this player ' + self.roster_player.position
            return False

        return True

    def check_big_guy(self):
        if self.roster_player.big_guy and self.team.big_guy_numbers >= self.team.roster_team.big_guy_max:
            logger.warning('User ' + str(self.user) + ' try to hire ' + str(self.roster_player) + ' for team '
                           + str(self.team) + ' but can\'t have more big guy. Big Guy -> '
                           + str(self.team.big_guy_numbers)
                           + ' Max number of big guy -> ' + str(self.team.roster_team.big_guy_max))
            self.message_for_flash = 'You cant\'t have more big guy'
            return False

        return True

    def check_max_quantity(self):
        number_of_roster_player_hired = self.team.players \
            .filter(Q(roster_player=self.roster_player.id) & Q(dead=False) & Q(fired=False)) \
            .count()
        if number_of_roster_player_hired >= self.roster_player.max_quantity:
            logger.warning('User ' + str(self.user) + ' try to hire ' + str(self.roster_player) + ' for team '
                           + str(self.team) + ' but can\'t have more positional of this kind. has -> '
                           + str(number_of_roster_player_hired)
                           + ' Max quantity -> ' + str(self.roster_player.max_quantity))
            self.message_for_flash = 'You cant\'t buy ' + self.roster_player.position + '! Max quantity is ' \
                                     + str(self.roster_player.max_quantity)
            return False

        return True

    def generate_player_to_buy(self):
        logger.debug('User ' + str(self.user) + ' hire ' + str(self.roster_player) + ' for team '
                     + str(self.team) + ' OLD Treasury ' + str(self.team.treasury)
                     + ' Flag status ' + str(self.buy_player_state))

        if self.buy_player():
            player = TeamPlayer()
            player.init_with_roster_player(self.roster_player, self.team)
            self.team.treasury = self.team.treasury - self.roster_player.cost
            if self.roster_player.big_guy:
                self.team.big_guy_numbers += 1
            self.team.number_of_players += 1

            logger.debug('User ' + str(self.user) + ' hire ' + str(self.roster_player) + ' for team '
                         + str(self.team) + ' New Treasury ' + str(self.team.treasury))

            return player

        logger.debug('User ' + str(self.user) + ' can\'t hire ' + str(self.roster_player) + ' for team '
                     + str(self.team) + ' for invalid flag status ' + str(self.buy_player_state))
        return None

    def add_more_skill(self, player):
        logger.debug('User ' + str(self.user) + ' hire ' + str(self.roster_player) + ' for team '
                     + str(self.team) + ' No more skill required')
