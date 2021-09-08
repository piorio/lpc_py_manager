# teamid_cas_playerId -> BH
class BadlyHurt:
    def apply_to_player(self, player):
        # Nothing just logging in the future
        pass

    def set_last_injury(self, last_injury):
        pass


class SeriouslyHurt:
    def apply_to_player(self, player):
        player.missing_next_game = True

    def set_last_injury(self, last_injury):
        pass


class SeriouslyInjury:
    def apply_to_player(self, player):
        player.missing_next_game = True
        player.niggling_injury += 1

    def set_last_injury(self, last_injury):
        pass


class LastingInjury:
    def __init__(self):
        self.injury_type = None

    def apply_to_player(self, player):
        if self.injury_type is None:
            raise Exception('Last Injury without which type')

        player.missing_next_game = True
        if self.injury_type == 'JI':
            player.armor_value -= 1
        elif self.injury_type == 'SK':
            player.movement_allowance -= 1
        elif self.injury_type == 'BA':
            player.passing -= 1
        elif self.injury_type == 'NI':
            player.agility -= 1
        elif self.injury_type == 'DS':
            player.strength -= 1


    def set_last_injury(self, last_injury):
        self.injury_type = last_injury


class Dead:
    def apply_to_player(self, player):
        player.dead = True

    def set_last_injury(self, last_injury):
        pass


class PlayerCasualtyFactory:
    instance_to_return = {'BH': BadlyHurt(), 'SH': SeriouslyHurt(), 'SI': SeriouslyInjury,
                          'LI': LastingInjury(), 'DE': Dead(), 'NA': None}

    def get_casualty_engine(self, data, team_id, player_id):
        data_cas_string = str(team_id) + '_cas_' + str(player_id)
        data_last_injury_string = str(team_id) + '_lasti_' + str(player_id)
        cas_type = data[data_cas_string]
        if cas_type:
            engine = PlayerCasualtyFactory.instance_to_return[cas_type]
            injury_type = data[data_last_injury_string]
            if injury_type and injury_type != 'NA':
                engine.set_last_injury(injury_type)
            return engine
        else:
            return None