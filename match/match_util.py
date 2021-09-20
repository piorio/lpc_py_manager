from .casualty_util import PlayerCasualtyFactory
from .models import TeamPlayerMatchRecord


class CloseMatchDataReader:
    def __init__(self, data, team, selected_team, match):
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

    def get_fan_factor(self):
        return self.fan_factor

    def get_number_of_td(self):
        return self.number_of_td

    def prepare(self):
        print("Match util prepare DATA FORM " + str(self.data))
        if self.selected_team not in self.select_team:
            return

        extra_fan_string = self.select_team[self.selected_team]
        extra_fan = self.data[extra_fan_string]
        match_extra_fan = 0
        if extra_fan:
            match_extra_fan = int(extra_fan)

        team_touchdown = 0
        team_cas = 0
        team_badly_hurt = 0
        team_serious_injury = 0
        team_kill = 0

        print("Match util prepare players " + str(self.players))
        for player in self.players:
            print("Match util prepare -> Prepare player " + str(player))
            total_spp = 0
            total_cas = 0

            match_played = TeamPlayerMatchRecord()
            match_played.match = self.match
            match_played.player = player

            touchdown, touchdown_spp = self.get_td(player)
            total_spp += touchdown_spp
            player.touchdown += touchdown
            team_touchdown += touchdown
            match_played.touchdown = touchdown

            badly_hurt, badly_hurt_spp = self.get_bh(player)
            total_spp += badly_hurt_spp
            total_cas += badly_hurt
            player.badly_hurt += badly_hurt
            team_badly_hurt += badly_hurt
            match_played.badly_hart = badly_hurt

            serious_injury, serious_injury_spp = self.get_si(player)
            total_spp += serious_injury_spp
            total_cas += serious_injury
            player.serious_injury += serious_injury
            team_serious_injury += serious_injury
            match_played.seriously_injury = serious_injury

            kill, kill_spp = self.get_ki(player)
            total_spp += kill_spp
            total_cas += kill
            player.kill += kill
            team_kill += kill
            match_played.kill = kill

            intercept, intercept_spp = self.get_intercept(player)
            total_spp += intercept_spp
            player.intercept += intercept
            match_played.intercept = intercept

            deflection, deflection_spp = self.get_deflection(player)
            total_spp += deflection_spp
            player.deflection += deflection
            match_played.deflection = deflection

            complete, complete_spp = self.get_complete(player)
            total_spp += complete_spp
            player.complete += complete

            if self.is_mvp(player):
                total_spp += 4

            player.total_cas += total_cas
            player.spp += total_spp
            team_cas += total_cas

            print("Match util prepare -> Prepare player before CAS " + str(player))
            self.apply_cas(player, match_played)

            player.save()

            # Save match and played match...must be in other place
            match_played.ssp = total_spp
            match_played.total_cas = total_cas
            # INJURY RECEIVED????
            match_played.save()

        self.fan_factor = match_extra_fan + self.team.extra_dedicated_fan
        if self.selected_team == 'FIRST':
            self.match.first_team_td = team_touchdown
            self.match.first_team_cas = team_cas
            self.match.first_team_kill = team_kill
            self.match.first_team_badly_hurt = team_badly_hurt
            self.match.first_team_serious_injury = team_serious_injury
            self.match.first_team_extra_fan = match_extra_fan
            self.match.first_team_fan_factor = self.fan_factor
            self.match.first_team.total_touchdown = team_touchdown
            self.match.first_team.total_cas = team_cas

        elif self.selected_team == 'SECOND':
            self.match.second_team_td = team_touchdown
            self.match.second_team_cas = team_cas
            self.match.second_team_kill = team_kill
            self.match.second_team_badly_hurt = team_badly_hurt
            self.match.second_team_serious_injury = team_serious_injury
            self.match.second_team_extra_fan = match_extra_fan
            self.match.second_team_fan_factor = self.fan_factor
            self.match.second_team.total_touchdown = team_touchdown
            self.match.second_team.total_cas = team_cas

        self.number_of_td = team_touchdown
        self.match.save()

    def get_td(self, player):
        players_td = str(self.team_id) + '_td_'
        player_td = self.data[players_td + str(player.id)]
        if player_td:
            player_td_int = int(player_td)
            return player_td_int, player_td_int * 3
        else:
            return 0, 0

    def get_bh(self, player):
        players_bh = str(self.team_id) + '_bh_'
        player_bh = self.data[players_bh + str(player.id)]
        if player_bh:
            player_bh_int = int(player_bh)
            return player_bh_int, player_bh_int * 2
        else:
            return 0, 0

    def get_si(self, player):
        players_si = str(self.team_id) + '_si_'
        player_si = self.data[players_si + str(player.id)]
        if player_si:
            player_si_int = int(player_si)
            return player_si_int, player_si_int * 2
        else:
            return 0, 0

    def get_ki(self, player):
        players_ki = str(self.team_id) + '_ki_'
        player_ki = self.data[players_ki + str(player.id)]
        if player_ki:
            player_ki_int = int(player_ki)
            return player_ki_int, player_ki_int * 2
        else:
            return 0, 0

    def get_intercept(self, player):
        players_int = str(self.team_id) + '_int_'
        player_int = self.data[players_int + str(player.id)]
        if player_int:
            player_int_int = int(player_int)
            return player_int_int, player_int_int * 2
        else:
            return 0, 0

    def get_deflection(self, player):
        players_def = str(self.team_id) + '_def_'
        player_def = self.data[players_def + str(player.id)]
        if player_def:
            player_def_int = int(player_def)
            return player_def_int, player_def_int * 1
        else:
            return 0, 0

    def get_complete(self, player):
        players_complete = str(self.team_id) + '_comp_'
        player_complete = self.data[players_complete + str(player.id)]
        if player_complete:
            player_complete_int = int(player_complete)
            return player_complete_int, player_complete_int * 1
        else:
            return 0, 0

    def is_mvp(self, player):
        player_mvp = self.data[self.mvp_team[self.selected_team]]
        if int(player_mvp) == player.id:
            return True
        else:
            return False

    def apply_cas(self, player, match_played):
        factory = PlayerCasualtyFactory()
        print("Match util prepare -> CAS Factory " + str(factory) + " - player " + str(player))
        engine = factory.get_casualty_engine(self.data, self.team_id, player.id)
        if engine is not None:
            engine.apply_to_player(player, match_played)


def reset_missing_next_game(team):
    for player in team.players.all():
        if player.missing_next_game:
            player.missing_next_game = False
            player.save()
