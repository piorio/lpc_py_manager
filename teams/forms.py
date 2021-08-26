from django import forms


class CreateMyTeamForm(forms.Form):
    name = forms.CharField(max_length=100)
    treasury = forms.IntegerField(min_value=0, max_value=2000000)
    roster = forms.ChoiceField()

