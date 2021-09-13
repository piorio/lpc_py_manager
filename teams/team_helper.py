def update_team_value(team, team_value=False):
    value = 0
    for player in team.players.all():
        if not player.dead and not player.fired and (not player.missing_next_game or team_value):
            value += player.value

    if team.apothecary:
        value += 50000

    if team.assistant_coach > 0:
        value += (team.assistant_coach * 10000)

    if team.cheerleader > 0:
        value += (team.cheerleader * 10000)

    if team.re_roll > 0:
        value += (team.re_roll * team.roster_team.re_roll_cost)

    return value
