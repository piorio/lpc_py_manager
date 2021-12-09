class AllLeaguesDTO:
    def __init__(self, **kwargs):
        self.league = kwargs.get('league')
        self.seasons_count = kwargs.get('seasons_count')
        self.teams_count = kwargs.get('teams_count')
        self.tournaments_count = kwargs.get('tournaments_count')
        self.league_status = kwargs.get('league_status')


class AllSeasonsDTO:
    def __init__(self, **kwargs):
        self.season = kwargs.get('season')
        self.teams_count = kwargs.get('teams_count')
        self.tournaments_count = kwargs.get('tournaments_count')


class AllTournamentsDTO:
    def __init__(self, **kwargs):
        self.season = kwargs.get('season')
        self.teams_count = kwargs.get('teams_count')
        self.tournament = kwargs.get('tournament')
