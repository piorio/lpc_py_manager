class MatchContainer:
    def __init__(self, match):
        self.match = match
        self.match_id = match.id
        self.first_team = MatchContainer(match.first_team)
        self.second_team = MatchContainer(match.second_team)

    def debug(self):
        return 'MatchContainer {' \
               + '"match": ' + self.match.debug() \
               + '"match_id": ' + str(self.match_id) \
               + '"first_team": ' + self.first_team.debug() \
               + '"second_team": ' + self.second_team.debug() \
               + '}'


class MatchTeamContainer:
    def __init__(self, team):
        self.team = team
        self.team_id = team.id
        self.touchdown = 0
        self.cas = 0
        self.badly_hurt = 0
        self.serious_injury = 0
        self.kill = 0
        self.extra_fan = 0
        self.fan_factor = 0
        self.gold = 0

    def debug(self):
        return 'MatchTeamContainer {' \
               + '"team": ' + str(self.team) \
               + '"team_id": ' + str(self.team_id) \
               + '"touchdown": ' + str(self.touchdown) \
               + '"cas": ' + str(self.cas) \
               + '"badly_hurt": ' + str(self.badly_hurt) \
               + '"serious_injury": ' + str(self.serious_injury) \
               + '"kill": ' + str(self.kill) \
               + '"extra_fan": ' + str(self.extra_fan) \
               + '"fan_factor": ' + str(self.fan_factor) \
               + '"gold": ' + str(self.gold) \
               + '}'
