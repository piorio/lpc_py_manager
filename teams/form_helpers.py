class PrepareTeamValidator:
    def __init__(self, treasury, team_cleaned_data, roster_team):
        self.treasury = treasury
        self.team_cleaned_data = team_cleaned_data
        self.roster_team = roster_team

    def validate_form(self):
        (is_valid, treasury, message) = self.__validate_extra_dedicated_fan()
        if not is_valid:
            return is_valid, treasury, message
        (is_valid, treasury, message) = self.__validate_re_roll()
        if not is_valid:
            return is_valid, treasury, message
        self.treasury = treasury
        (is_valid, treasury, message) = self.__validate_assistant_coach()
        if not is_valid:
            return is_valid, treasury, message
        self.treasury = treasury
        (is_valid, treasury, message) = self.__validate_cheerleader()
        if not is_valid:
            return is_valid, treasury, message
        self.treasury = treasury
        (is_valid, treasury, message) = self.__validate_apothecary()
        if not is_valid:
            return is_valid, treasury, message
        self.treasury = treasury
        return True, self.treasury, ''

    def __validate_re_roll(self):
        re_roll = self.team_cleaned_data['re_roll']
        if re_roll > self.roster_team.re_roll_max:
            return False, self.treasury, 'Too much re roll: max number is ' + str(self.roster_team.re_roll_max)

        re_roll_cost = re_roll * self.roster_team.re_roll_cost
        if re_roll_cost > self.treasury:
            return False, self.treasury, 'You don\'t have treasury for re roll'

        new_treasury = self.treasury - re_roll_cost
        return True, new_treasury, ''

    def __validate_assistant_coach(self):
        assistant_coach = self.team_cleaned_data['assistant_coach']
        assistant_coach_cost = assistant_coach * 10000
        if assistant_coach_cost > self.treasury:
            return False, self.treasury, 'You don\'t have treasury for assistant coach'

        new_treasury = self.treasury - assistant_coach_cost
        return True, new_treasury, ''

    def __validate_cheerleader(self):
        cheerleader = self.team_cleaned_data['cheerleader']
        cheerleader_cost = cheerleader * 10000
        if cheerleader_cost > self.treasury:
            return False, self.treasury, 'You don\'t have treasury for cheerleader'

        new_treasury = self.treasury - cheerleader_cost
        return True, new_treasury, ''

    def __validate_apothecary(self):
        apothecary = self.team_cleaned_data['apothecary']
        if apothecary is True and self.roster_team.apothecary is False:
            return False, self.treasury, 'You can\'t have an apothecary'

        apothecary_cost = apothecary * 50000
        if apothecary_cost > self.treasury:
            return False, self.treasury, 'You don\'t have treasury for apothecary'

        new_treasury = self.treasury - apothecary_cost
        return True, new_treasury, ''

    def __validate_extra_dedicated_fan(self):
        extra_dedicated_fan = self.team_cleaned_data['extra_dedicated_fan']
        extra_dedicated_fan_cost = extra_dedicated_fan * 10000
        if extra_dedicated_fan_cost > self.treasury:
            return False, self.treasury, 'You don\'t have treasury for extra dedicated fan'

        new_treasury = self.treasury - extra_dedicated_fan_cost
        return True, new_treasury, ''
