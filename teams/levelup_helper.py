from django.utils.safestring import mark_safe

from roster.models import Skill

level_cost_map = {
    'NONE': [3, 6, 12, 18],
    'EXPERIENCED': [4, 8, 14, 20],
    'VETERAN': [6, 12, 18, 24],
    'EMERGING STAR': [8, 16, 22, 28],
    'STAR': [10, 20, 26, 32],
    'SUPER STAR': [15, 30, 40, 50]
}


def get_levelup_cost_all_levels(player):
    return level_cost_map[player.level]


def get_levelup_cost_by_level(player, choice):
    return level_cost_map[player.level][choice]


def get_first_skills_dict(player):
    roster_player = player.roster_player
    roster_first_skill = [char for char in roster_player.primary_skills]
    first_skill_dict = {}

    for skill in roster_first_skill:
        first_skill = None
        if skill == 'A':
            first_skill = 'Agility'
        elif skill == 'G':
            first_skill = 'General'
        elif skill == 'S':
            first_skill = 'Strenght'
        elif skill == 'P':
            first_skill = 'Passing'
        elif skill == 'M':
            first_skill = 'Mutation'

        if first_skill is not None:
            skill_to_choose = Skill.objects.filter(category=first_skill)
            first_skill_dict[first_skill] = skill_to_choose

    print(first_skill_dict)
    return first_skill_dict


def get_first_skills_select_option(player):
    roster_player = player.roster_player
    roster_first_skill = [char for char in roster_player.primary_skills]
    response = []

    for roster_skill in roster_first_skill:
        first_skill = None
        if roster_skill == 'A':
            first_skill = 'Agility'
        elif roster_skill == 'G':
            first_skill = 'General'
        elif roster_skill == 'S':
            first_skill = 'Strenght'
        elif roster_skill == 'P':
            first_skill = 'Passing'
        elif roster_skill == 'M':
            first_skill = 'Mutation'

        if first_skill is not None:
            skill_to_choose = Skill.objects.filter(category=first_skill)
            for skill in skill_to_choose:
                value = mark_safe('<option value="' + str(skill.id) + '">' + skill.name + ' (' + first_skill + ')</option>')
                response.append(value)

    print(response)
    return response

def get_second_skills_select_option(player):
    roster_player = player.roster_player
    roster_secondary_skill = [char for char in roster_player.secondary_skills]
    response = []

    for roster_skill in roster_secondary_skill:
        secondary_skill = None
        if roster_skill == 'A':
            secondary_skill = 'Agility'
        elif roster_skill == 'G':
            secondary_skill = 'General'
        elif roster_skill == 'S':
            secondary_skill = 'Strenght'
        elif roster_skill == 'P':
            secondary_skill = 'Passing'
        elif roster_skill == 'M':
            secondary_skill = 'Mutation'

        if secondary_skill is not None:
            skill_to_choose = Skill.objects.filter(category=secondary_skill)
            for skill in skill_to_choose:
                value = mark_safe('<option value="' + str(skill.id) + '">' + skill.name + ' (' + secondary_skill + ')</option>')
                response.append(value)

    print(response)
    return response


def get_first_skills_category(player):
    roster_player = player.roster_player
    roster_first_skill = [char for char in roster_player.primary_skills]
    response = []
    for skill_category in roster_first_skill:
        value = None
        if skill_category == 'A':
            value = mark_safe('<option value="a">AGILITY</option>')
        elif skill_category == 'G':
            value = mark_safe('<option value="g">GENERAL</option>')
        elif skill_category == 'M':
            value = mark_safe('<option value="m">MUTATION</option>')
        elif skill_category == 'P':
            value = mark_safe('<option value="p">PASSING</option>')
        elif skill_category == 'S':
            value = mark_safe('<option value="s">STRENGTH</option>')

        if value is not None:
            response.append(value)

    return response


def get_second_skills_category(player):
    roster_player = player.roster_player
    roster_secondary_skill = [char for char in roster_player.secondary_skills]
    response = []
    for skill_category in roster_secondary_skill:
        value = None
        if skill_category == 'A':
            value = mark_safe('<option value="a">AGILITY</option>')
        elif skill_category == 'G':
            value = mark_safe('<option value="g">GENERAL</option>')
        elif skill_category == 'M':
            value = mark_safe('<option value="m">MUTATION</option>')
        elif skill_category == 'P':
            value = mark_safe('<option value="p">PASSING</option>')
        elif skill_category == 'S':
            value = mark_safe('<option value="s">STRENGTH</option>')

        if value is not None:
            response.append(value)

    return response


def get_new_level(player):
    if player.level == 'NONE':
        return 'EXPERIENCED'
    elif player.level == 'EXPERIENCED':
        return 'VETERAN'
    elif player.level == 'VETERAN':
        return 'EMERGING STAR'
    elif player.level == 'EMERGING STAR':
        return 'STAR'
    elif player.level == 'STAR':
        return 'SUPER STAR'


def get_all_skills():
    first_skill_dict = {}

    for skill in ['Agility', 'General', 'Strenght', 'Passing', 'Mutation']:
        skill_to_choose = Skill.objects.filter(category=skill)
        first_skill_dict[skill] = skill_to_choose

    print(first_skill_dict)
    return first_skill_dict
