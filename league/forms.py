from django import forms


class RequireNewLeagueForm(forms.Form):
    name = forms.CharField(max_length=100)
    author = forms.CharField(max_length=100)
    author_email = forms.EmailField(max_length=100)
