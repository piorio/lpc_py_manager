import logging

logger = logging.getLogger(__name__)

# teamid_cas_playerId -> BH
class BadlyHurt:
    def apply_to_player(self, player, match_played):
        # Nothing just logging in the future
        match_played.badly_hart = 1
        pass

    def set_last_injury(self, last_injury):
        pass

    def __str__(self):
        return "BadlyHurt"


class SeriouslyHurt:
    def apply_to_player(self, player, match_played):
        player.missing_next_game = True
        match_played.seriously_injury = 1
        match_played.seriously_hurt = 1

    def set_last_injury(self, last_injury):
        pass

    def __str__(self):
        return "SeriouslyHurt"


class SeriouslyInjury:
    def apply_to_player(self, player, match_played):
        player.missing_next_game = True
        player.niggling_injury += 1
        match_played.seriously_injury = 1

    def set_last_injury(self, last_injury):
        pass

    def __str__(self):
        return "SeriouslyInjury"


class LastingInjury:
    def __init__(self):
        self.injury_type = None

    def apply_to_player(self, player, match_played):
        if self.injury_type is None:
            raise Exception('Last Injury without which type')
        match_played.last_injury = 1

        player.missing_next_game = True
        if self.injury_type == 'JI':
            player.armor_value += 1
            match_played.received_cas = 'Head Injury'
        elif self.injury_type == 'SK':
            if player.movement_allowance > 0:
                player.movement_allowance -= 1
            match_played.received_cas = 'Smashed Knee'
        elif self.injury_type == 'BA':
            if player.passing != 0:
                player.passing += 1
            match_played.received_cas = 'Broken Arm'
        elif self.injury_type == 'NI':
            player.agility += 1
            match_played.received_cas = 'Neck Injury'
        elif self.injury_type == 'DS':
            if player.strength > 0:
                player.strength -= 1
            match_played.received_cas = 'Dislocated Shoulder'

    def set_last_injury(self, last_injury):
        self.injury_type = last_injury

    def __str__(self):
        return "LastingInjury"


class Dead:
    def apply_to_player(self, player, match_played):
        player.dead = True
        match_played.died = True

    def set_last_injury(self, last_injury):
        pass

    def __str__(self):
        return "DEAD!!!"


class PlayerCasualtyFactory:
    instance_to_return = {'BH': BadlyHurt(), 'SH': SeriouslyHurt(), 'SI': SeriouslyInjury(),
                          'LI': LastingInjury(), 'DE': Dead(), 'NA': None}

    def get_casualty_engine(self, data, team_id, player_id):
        data_cas_string = str(team_id) + '_cas_' + str(player_id)
        data_last_injury_string = str(team_id) + '_lasti_' + str(player_id)
        cas_type = data.get(data_cas_string)
        if cas_type:
            logger.debug('CAS UTIL for playerId ' + str(player_id) + ' of team ' + str(team_id)
                         + ' cas type ' + cas_type)

            engine = PlayerCasualtyFactory.instance_to_return[cas_type]
            injury_type = data.get(data_last_injury_string)
            if injury_type and injury_type != 'NA':
                engine.set_last_injury(injury_type)
            return engine
        else:
            logger.debug('CAS UTIL for playerId ' + str(player_id) + ' of team ' + str(team_id)
                         + ' No cas type ')
            return None
