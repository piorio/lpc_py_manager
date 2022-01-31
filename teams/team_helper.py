import logging
from datetime import datetime

from django.contrib import messages
from django.db import transaction
from django.db.models import Q

from league.models import LeagueConfiguration
from match.models import Match

logger = logging.getLogger(__name__)


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


def player_has_changed_level(player):
    if player.level == 'EXPERIENCED' and player.spp <= 3:
        return True
    elif player.level == 'VETERAN' and player.spp <= 4:
        return True
    elif player.level == 'EMERGING STAR' and player.spp <= 6:
        return True
    elif player.level == 'STAR' and player.spp <= 8:
        return True
    elif player.level == 'SUPER STAR' and player.spp <= 10:
        return True
    elif player.level == 'LEGEND' and player.spp <= 15:
        return True


def perform_dismiss_team(team, request):
    team.status = 'RETIRED'
    team.save()
    logger.debug('User ' + str(request.user) + ' dismiss successfully team ' + str(team))


def perform_ready_team(team, request):
    team_value = update_team_value(team)
    team.value = team_value
    team.current_team_value = team_value
    team.status = 'READY'
    team.save()
    logger.warning('User ' + str(request.user) + ' ready team ' + str(team))


def is_players_count_to_prepare_team(team, request):
    players_count = team.players.all().count()
    logger.debug('User ' + str(request.user) + ' try to ready team ' + str(team) + '. Players count '
                 + str(players_count))
    if players_count < 11 or players_count > 16:
        logger.warning('User ' + str(request.user) + ' try to ready team ' + str(team)
                       + ' with invalid player count ' + str(players_count))
        return False
    return True


def can_you_buy_player(team, request, roster_player_to_buy):
    # Check max team players
    if team.number_of_players > 15:
        messages.error(request, 'You can\'t buy more than 16 players')
        logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                       + str(team) + ' but can\'t buy more than 16 players. Players ' + str(team.number_of_players))
        return False

    # check money spent
    if roster_player_to_buy.cost > team.treasury:
        messages.error(request, 'You don\'t have money for this player ' + roster_player_to_buy.position)
        logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                       + str(team) + ' but can\'t have money. Treasury ' + str(team.treasury)
                       + ' player cost ' + str(roster_player_to_buy.cost))
        return False

    # Check big guy: a roster team must have a max number of big guy
    if roster_player_to_buy.big_guy:
        if team.big_guy_numbers >= team.roster_team.big_guy_max:
            messages.error(request, 'You cant\'t have more big guy')
            logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                           + str(team) + ' but can\'t have more big guy. Big Guy ' + str(team.big_guy_numbers)
                           + ' permitted big guy ' + str(team.roster_team.big_guy_max))
            return False

    # Check max position quantity
    number_of_roster_player_hired = team.players.filter(roster_player=roster_player_to_buy.id).count()
    if number_of_roster_player_hired >= roster_player_to_buy.max_quantity:
        messages.error(request, 'You cant\'t buy ' + roster_player_to_buy.position + '! Max quantity is ' +
                       str(roster_player_to_buy.max_quantity))
        logger.warning('User ' + str(request.user) + ' try to buy ' + str(roster_player_to_buy) + ' for team '
                       + str(team) + ' but can\'t have player for this position. Positional Hired '
                       + str(number_of_roster_player_hired)
                       + ' permitted player max quantity ' + str(roster_player_to_buy.max_quantity))
        return False

    return True


def add_re_roll_during_team_prepare(team):
    team.re_roll += 1
    team.treasury -= team.roster_team.re_roll_cost
    team.save()


def remove_re_roll_during_team_prepare(team):
    team.re_roll -= 1
    team.treasury += team.roster_team.re_roll_cost
    team.save()


def add_assistant_coach_during_team_prepare(team, request):
    # check money spent
    if team.treasury - 10000 < 0 or team.assistant_coach > 5:
        messages.error(request, 'You don\'t have money for another assistant coach')
    else:
        team.assistant_coach += 1
        team.treasury -= 10000
        team.save()


def remove_assistant_coach_during_team_prepare(team, request):
    # check assistant coach number
    if team.assistant_coach <= 0:
        messages.error(request, 'You don\'t have assistant coach to remove or too many assistant coach')
    else:
        team.assistant_coach -= 1
        team.treasury += 10000
        team.save()


def add_cheerleader_during_team_prepare(team, request):
    # check money spent
    if team.treasury - 10000 < 0 or team.cheerleader > 11:
        messages.error(request, 'You don\'t have money for another cheerleader or too many cheerleaders')
    else:
        team.cheerleader += 1
        team.treasury -= 10000
        team.save()


def remove_cheerleader_during_team_prepare(team, request):
    # check cheerleader number
    if team.cheerleader <= 0:
        messages.error(request, 'You don\'t have cheerleader to remove')
    else:
        team.cheerleader -= 1
        team.treasury += 10000
        team.save()


def add_extra_fan_during_team_prepare(team, request):
    # check money spent
    if team.treasury - 10000 < 0 or team.extra_dedicated_fan > 4:
        messages.error(request, 'You don\'t have money for another extra fan or too many extra fan')
    else:
        team.extra_dedicated_fan += 1
        team.treasury -= 10000
        team.save()


def remove_extra_fan_during_team_prepare(team, request):
    # check extra dedicated fan number
    if team.extra_dedicated_fan <= 0:
        messages.error(request, 'You don\'t have extra fan to remove')
    else:
        team.extra_dedicated_fan -= 1
        team.treasury += 10000
        team.save()


def add_apothecary_during_team_prepare(team, request):
    if team.roster_team.apothecary is False:
        messages.error(request, 'Your team cannot have an apothecary')
    else:
        # check money spent
        if team.treasury - 50000 < 0 or team.apothecary is True:
            messages.error(request,
                           'You don\'t have money for the apothecary or too many apothecary (You can buy only one)')
        else:
            team.apothecary = True
            team.treasury -= 50000
            team.save()


def remove_apothecary_during_team_prepare(team, request):
    # check apothecary presence
    if team.apothecary is False:
        messages.error(request, 'You don\'t have apothecary to remove')
    else:
        team.apothecary = False
        team.treasury += 50000
        team.save()


def change_player_name_number_by_request(player, request):
    player_name = request.POST['new_name']
    player_number = request.POST['new_number']

    if player_name:
        player.name = player_name

    if player_number and player_number != '--':
        player.player_number = int(player_number)

    player.save()


def fire_player_helper(player, team, request):
    # Fired player and add again the cost
    if not player.roster_player.is_journeyman:
        logger.debug('User ' + str(request.user) + ' fire ' + str(player) + ' for team '
                     + str(team) + ' and is not a journeyman so update treasury')
        team.treasury = team.treasury + player.cost

    if player.big_guy:
        team.big_guy_numbers -= 1
    team.number_of_players -= 1
    player.fired = True
    player.missing_next_game = False

    try:
        with transaction.atomic():
            player.save()
            team.value = update_team_value(team, True)
            team.current_team_value = update_team_value(team)
            team.save()
    except Exception as e:
        logger.error('User ' + str(request.user) + ' try to fire ' + str(player) +
                     ' Exception ' + str(e))
        messages.error(request, 'Internal error during fire Player')
        return False

    messages.success(request, 'You fire a ' + str(player.position))
    return True


def buy_team_re_roll(team, request):
    # check money spent and max number
    if team.roster_team.re_roll_cost * 2 > team.treasury or team.re_roll > team.roster_team.re_roll_max:
        messages.error(request,
                       'You don\'t have money for another re roll or you reached the max number of re roll permitted')
    else:
        team.re_roll += 1
        team.treasury -= (team.roster_team.re_roll_cost * 2)
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()


def remove_team_re_roll(team, request):
    # check quantity
    if team.re_roll <= 0:
        messages.error(request, 'You don\'t have re roll to remove')
    else:
        team.re_roll -= 1
        # We don't receive money back for re roll
        # team.treasury += team.roster_team.re_roll_cost
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()


def buy_team_assistant_coach(team, request):
    # check money spent
    if team.treasury - 10000 < 0 or team.assistant_coach > 5:
        messages.error(request, 'You don\'t have money for another assistant coach')
    else:
        team.assistant_coach += 1
        team.treasury -= 10000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()


def remove_team_assistant_coach(team, request):
    # check quantity
    if team.assistant_coach <= 0:
        messages.error(request, 'You don\'t have assistant coach to remove or too many assistant coach')
    else:
        team.assistant_coach -= 1
        team.treasury += 10000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()


def buy_team_cheerleader(team, request):
    # check money spent
    if team.treasury - 10000 < 0 or team.cheerleader > 11:
        messages.error(request, 'You don\'t have money for another cheerleader or too many cheerleaders')
    else:
        team.cheerleader += 1
        team.treasury -= 10000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()


def remove_team_cheerleader(team, request):
    # check money spent and max number
    if team.cheerleader <= 0:
        messages.error(request, 'You don\'t have cheerleader to remove')
    else:
        team.cheerleader -= 1
        team.treasury += 10000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()


def buy_team_apothecary(team, request):
    if team.roster_team.apothecary is False:
        messages.error(request, 'Your team cannot have an apothecary')
    else:
        # check money spent
        if team.treasury - 50000 < 0 or team.apothecary is True:
            messages.error(request,
                           'You don\'t have money for the apothecary or too many apothecary (You can buy only one)')
        else:
            team.apothecary = True
            team.treasury -= 50000
            team.value = update_team_value(team, True)
            team.current_team_value = update_team_value(team)
            team.save()


def remove_team_apothecary(team, request):
    # check quantity
    if team.apothecary is False:
        messages.error(request, 'You don\'t have apothecary to remove')
    else:
        team.apothecary = False
        team.treasury += 50000
        team.value = update_team_value(team, True)
        team.current_team_value = update_team_value(team)
        team.save()


def get_random_skill_search_string(form, request, player):
    category = form.cleaned_data['category']
    first_dice = form.cleaned_data['first_dice']
    second_dice = form.cleaned_data['second_dice']

    if first_dice <= 3:
        first_dice = 1
    if first_dice >= 4:
        first_dice = 4

    search_string = category + str(first_dice) + str(second_dice)
    logger.debug('User ' + str(request.user) + ' random skill for player ' + str(player)
                 + ' First dice set ' + str(form.cleaned_data['first_dice'])
                 + ' Second dice set ' + str(second_dice)
                 + ' First dice ' + str(first_dice) + ' search string ' + search_string)

    return search_string


def update_team_freeze(team):
    try:
        with transaction.atomic():
            # If a team is already frozen or is not belong to a season, don't check the feature: only team in a
            # season could be frozen
            if team.freeze is not True and team.season is not None:
                feature = LeagueConfiguration.objects\
                    .filter(league=team.season.league)\
                    .filter(key='EnableFrozen').first()
                if feature is not None and feature.value == 'true':
                    first_team_match = Match.objects.filter(
                        (Q(first_team=team) | Q(second_team=team)) & Q(played=False))\
                        .order_by('freeze_date')\
                        .first()
                    if first_team_match is not None and first_team_match.freeze_date is not None \
                            and first_team_match.freeze_date <= datetime.today().date():
                        team.freeze = True
                        team.save()
    except Exception as e:
        logger.error(f"Unable to update freeze team for teams {team}")

    return team
