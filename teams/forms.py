from django import forms


class CreateMyTeamForm(forms.Form):
    name = forms.CharField(max_length=100)
    treasury = forms.IntegerField(min_value=0, max_value=2000000)
    roster = forms.ChoiceField()


class PrepareTeamForm(forms.Form):
    re_roll = forms.IntegerField(min_value=0, max_value=10)
    assistant_coach = forms.IntegerField(min_value=0, max_value=6)
    cheerleader = forms.IntegerField(min_value=0, max_value=12)
    extra_dedicated_fan = forms.IntegerField(min_value=0, max_value=5)
    apothecary = forms.BooleanField(required=False)
