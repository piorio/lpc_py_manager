import logging

from django.db.models import Q

from match.close_helpers.match_player import MatchPlayer
from match.models import TeamPlayerMatchRecord

logger = logging.getLogger(__name__)

mvp_team = {'FIRST': 'first_team_mvp', 'SECOND': 'second_team_mvp'}
extra_fan_team = {'FIRST': 'first_team_extra_fan', 'SECOND': 'second_team_extra_fan'}


class MatchTeam:
    def __init__(self, team, selected_team, form_data, match):

        if selected_team not in extra_fan_team or selected_team not in mvp_team:
            logger.warning('For team ' + str(team) + ' and matchId ' + str(match.id)
                           + '. Unable to find index into mvp_team or extra_fan_team')
            raise Exception('Unable to find ' + str(selected_team) + ' Into dicts')

        self.team = team
        self.selected_team = selected_team
        self.mvp_data_key = mvp_team[selected_team]
        self.extra_fan_data_key = extra_fan_team[selected_team]
        self.form_data = form_data
        self.match = match

        self.extra_fan = 0
        self.touchdown = 0
        self.cas = 0
        self.badly_hurt = 0
        self.serious_injury = 0
        self.kill = 0
        self.fan_factor = 0

    def calculate_extra_fan(self):
        extra_fan = self.form_data[self.extra_fan_data_key]
        if extra_fan:
            self.extra_fan = int(extra_fan)
            # A team has extra dedicated fan + 1
            self.fan_factor = self.extra_fan + self.team.extra_dedicated_fan + 1

        logger.debug('For team ' + str(self.team) + ' and matchId ' + str(self.match.id)
                     + '. match_extra_fan ' + str(self.extra_fan) + ' final fan factor ' + str(self.fan_factor))

    def calculate_for_all_players(self):
        logger.debug('For team ' + str(self.team) + ' and matchId ' + str(self.match.id)
                     + ' Start the players calculation')

        # Get only valid players
        for player in self.team.players.filter(Q(dead=False) & Q(fired=False) & Q(missing_next_game=False)).all():
            match_player = MatchPlayer(player, self.team.id, self.form_data, mvp_team[self.selected_team])
            match_player.calculate_all_from_form_data()
            match_player.apply_cas(self.match)
            if match_player.is_valid():
                match_player.apply()
            else:
                logger.debug('For team ' + str(self.team) + ' and matchId ' + str(self.match.id)
                             + '. player ' + player.debug() + ' close match invalid')
                raise Exception('Invalid close match for ' + str(player) + ' belong to team ' + str(self.team))

            match_played = TeamPlayerMatchRecord()
            match_played.match = self.match
            match_played.player = player

            self.touchdown += match_player.touchdown
            self.badly_hurt += match_player.badly_hurt
            self.serious_injury += match_player.serious_injury
            self.kill += match_player.kill

            match_played.touchdown = match_player.touchdown
            match_played.badly_hart = match_player.badly_hurt
            match_played.seriously_injury = match_player.serious_injury
            match_played.kill = match_player.kill
            match_played.intercept = match_player.intercept
            match_played.deflection = match_player.deflection
            match_played.complete = match_player.complete

            # if self.conceded_team is True and self.conceded_team != self.select_team:
            #    if self.is_second_mvp(player):
            #        total_spp += 4

            self.cas += match_player.total_cas

            # Save match and played match...must be in other place
            match_played.ssp = match_player.spp
            match_played.total_cas = match_player.total_cas

            logger.debug('For team ' + str(self.team) + ' and matchId ' + str(self.match.id)
                         + ' Player total spp ' + str(match_player.spp) + ' total cas ' + str(match_player.total_cas))

            # INJURY RECEIVED????
            match_played.save()
            match_player.save()

    def is_valid(self):
        # TODO. For now always valid data
        return True

    def apply(self):
        if self.selected_team == 'FIRST':
            self.match.first_team_td = self.touchdown
            self.match.first_team_cas = self.cas
            self.match.first_team_kill = self.kill
            self.match.first_team_badly_hurt = self.badly_hurt
            self.match.first_team_serious_injury = self.serious_injury
            self.match.first_team_extra_fan = self.extra_fan
            self.match.first_team_fan_factor = self.fan_factor
            self.match.first_team.total_touchdown += self.touchdown
            self.match.first_team.total_cas += self.cas

        elif self.selected_team == 'SECOND':
            self.match.second_team_td = self.touchdown
            self.match.second_team_cas = self.cas
            self.match.second_team_kill = self.kill
            self.match.second_team_badly_hurt = self.badly_hurt
            self.match.second_team_serious_injury = self.serious_injury
            self.match.second_team_extra_fan = self.extra_fan
            self.match.second_team_fan_factor = self.fan_factor
            self.match.second_team.total_touchdown += self.touchdown
            self.match.second_team.total_cas += self.cas

        logger.debug('For team ' + str(self.team) + ' and matchId ' + str(self.match.id)
                     + ' Total Touchdown ' + str(self.touchdown))

    def __str__(self):
        return str(self.team)


