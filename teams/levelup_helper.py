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


def get_levelup_cost_by_level(player):
    return level_cost_map[player.level][0]


def get_first_skills(player):
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


def get_all_skills():
    first_skill_dict = {}

    for skill in ['Agility', 'General', 'Strenght', 'Passing', 'Mutation']:
        skill_to_choose = Skill.objects.filter(category=skill)
        first_skill_dict[skill] = skill_to_choose

    print(first_skill_dict)
    return first_skill_dict
