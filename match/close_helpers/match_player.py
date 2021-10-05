import logging

from match.casualty_util import PlayerCasualtyFactory

logger = logging.getLogger(__name__)


class MatchPlayer:
    def __init__(self, player, team_id, form_data, mvp_data_key):
        self.player = player
        self.team_id = team_id
        self.form_data = form_data
        self.spp = 0
        self.touchdown = 0
        self.total_cas = 0
        self.badly_hurt = 0
        self.serious_injury = 0
        self.kill = 0
        self.intercept = 0
        self.deflection = 0
        self.complete = 0
        self.mvp = 0
        self.mvp_data_key = mvp_data_key

    def calculate_all_from_form_data(self):
        self.calculate_player_touchdown()
        self.calculate_player_badly_hurt()
        self.calculate_player_serious_injury()
        self.calculate_player_kill()
        self.calculate_intercept()
        self.calculate_deflection()
        self.calculate_complete()
        self.calculate_mvp()

    def apply(self):
        self.player.touchdown += self.touchdown
        self.player.total_cas += self.total_cas
        self.player.badly_hurt += self.badly_hurt
        self.player.serious_injury += self.serious_injury
        self.player.kill += self.kill
        self.player.spp += self.spp
        self.player.intercept += self.intercept
        self.player.deflection += self.deflection
        self.player.complete += self.complete
        self.player.total_mvp += self.mvp

    def is_valid(self):
        # TODO. For now always valid data
        return True

    def save(self):
        self.player.save()

    def calculate_player_touchdown(self):
        data_key = str(self.team_id) + '_td_' + str(self.player.id)
        player_td = self.form_data.get(data_key)
        if player_td:
            self.touchdown = int(player_td)
            self.spp += (self.touchdown * 3)
            logger.debug('Player ' + self.player.debug() + ' done ' + str(self.touchdown)
                         + ' touchdown for a total SPP ' + str(self.touchdown * 3))
        else:
            logger.debug('Player ' + self.player.debug() + ' 0 TD ')

    def calculate_player_badly_hurt(self):
        data_key = str(self.team_id) + '_bh_' + str(self.player.id)
        player_badly_hurt = self.form_data.get(data_key)
        if player_badly_hurt:
            self.badly_hurt = int(player_badly_hurt)
            self.spp += (self.badly_hurt * 2)
            self.total_cas += self.badly_hurt
            logger.debug('Player ' + self.player.debug() + ' done ' + str(self.badly_hurt)
                         + ' badly hurt for a total SPP ' + str(self.badly_hurt * 2)
                         + '. Total cas ' + str(self.total_cas))
        else:
            logger.debug('Player ' + self.player.debug() + ' 0 BADLY HURT ')

    def calculate_player_serious_injury(self):
        data_key = str(self.team_id) + '_si_' + str(self.player.id)
        player_serious_injury = self.form_data.get(data_key)
        if player_serious_injury:
            self.serious_injury = int(player_serious_injury)
            self.spp += (self.serious_injury * 2)
            self.total_cas += self.serious_injury
            logger.debug('Player ' + self.player.debug() + ' done ' + str(self.serious_injury)
                         + ' serious injury for a total SPP ' + str(self.serious_injury * 2)
                         + '. Total cas ' + str(self.total_cas))
        else:
            logger.debug('Player ' + self.player.debug() + ' 0 SERIOUS INJURY ')

    def calculate_player_kill(self):
        data_key = str(self.team_id) + '_ki_' + str(self.player.id)
        player_kill = self.form_data.get(data_key)
        if player_kill:
            self.kill = int(player_kill)
            self.spp += (self.kill * 2)
            self.total_cas += self.kill
            logger.debug('Player ' + self.player.debug() + ' done ' + str(self.kill)
                         + ' kill for a total SPP ' + str(self.kill * 2)
                         + '. Total cas ' + str(self.total_cas))
        else:
            logger.debug('Player ' + self.player.debug() + ' 0 KILL ')

    def calculate_intercept(self):
        data_key = str(self.team_id) + '_int_' + str(self.player.id)
        player_intercept = self.form_data.get(data_key)
        if player_intercept:
            self.intercept = int(player_intercept)
            # Intercept value one because we didn't transform a deflection into a intercept, but "save" separately
            self.spp += (self.intercept * 1)
            logger.debug('Player ' + self.player.debug() + ' done ' + str(self.intercept)
                         + ' intercept for a total SPP ' + str(self.intercept * 1))
        else:
            logger.debug('Player ' + self.player.debug() + ' 0 INTERCEPT ')

    def calculate_deflection(self):
        data_key = str(self.team_id) + '_def_' + str(self.player.id)
        player_deflection = self.form_data.get(data_key)
        if player_deflection:
            self.deflection = int(player_deflection)
            self.spp += (self.deflection * 1)
            logger.debug('Player ' + self.player.debug() + ' done ' + str(self.deflection)
                         + ' deflection for a total SPP ' + str(self.deflection * 1))
        else:
            logger.debug('Player ' + self.player.debug() + ' 0 DEFLECTION ')

    def calculate_complete(self):
        data_key = str(self.team_id) + '_comp_' + str(self.player.id)
        player_complete = self.form_data.get(data_key)
        if player_complete:
            self.complete = int(player_complete)
            self.spp += (self.complete * 1)
            logger.debug('Player ' + self.player.debug() + ' done ' + str(self.complete)
                         + ' complete for a total SPP ' + str(self.complete * 1))
        else:
            logger.debug('Player ' + self.player.debug() + ' 0 COMPLETE ')

    def calculate_mvp(self):
        player_mvp = self.form_data.get(self.mvp_data_key)
        if player_mvp and player_mvp != '--' and int(player_mvp) == self.player.id:
            self.mvp += 1
            self.spp += 4
            logger.debug('Player ' + self.player.debug() + ' is MVP ' + ' for a total SPP 4 ')
        else:
            logger.debug('Player ' + self.player.debug() + ' is not MVP ')

    def apply_cas(self, match):
        factory = PlayerCasualtyFactory()
        engine = factory.get_casualty_engine(self.form_data, self.team_id, self.player.id)
        logger.debug('For team ' + str(self.team_id) + ' and match_played ' + self.player.debug()
                     + ' CAS engine ' + str(engine))
        if engine is not None:
            engine.apply_to_player(self.player, match)
