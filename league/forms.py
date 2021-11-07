from django import forms


class RequireNewLeagueForm(forms.Form):
    name = forms.CharField(max_length=100)
    author_email = forms.EmailField(max_length=100)


class RequireNewSeasonForm(forms.Form):
    name = forms.CharField(max_length=100)


class RequireNewTournamentForm(forms.Form):
    name = forms.CharField(max_length=100)


class AddTeamForm(forms.Form):
    team = forms.ChoiceField()
