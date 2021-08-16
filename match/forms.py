from django import forms


class CloseMatchForm(forms.Form):
    first_team_td = forms.IntegerField(min_value=0, max_value=100)
    second_team_td = forms.IntegerField(min_value=0, max_value=100)
    first_team_badly_hurt = forms.IntegerField(min_value=0, max_value=100, required=False)
    first_team_serious_injury = forms.IntegerField(min_value=0, max_value=100, required=False)
    first_team_kill = forms.IntegerField(min_value=0, max_value=100, required=False)
    second_team_badly_hurt = forms.IntegerField(min_value=0, max_value=100, required=False)
    second_team_serious_injury = forms.IntegerField(min_value=0, max_value=100, required=False)
    second_team_kill = forms.IntegerField(min_value=0, max_value=100, required=False)

