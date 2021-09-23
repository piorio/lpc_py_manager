from django import forms


class CreateMyTeamForm(forms.Form):
    name = forms.CharField(max_length=100)
    treasury = forms.IntegerField(min_value=0, max_value=2000000)
    roster = forms.ChoiceField()


class RandomSkill(forms.Form):
    CATEGORY_CHOICE = (
        ('a', 'AGILITY'),
        ('g', 'GENERAL'),
        ('m', 'MUTATION'),
        ('p', 'PASSING'),
        ('s', 'STRENGTH'),
    )
    category = forms.ChoiceField(choices=CATEGORY_CHOICE)
    first_dice = forms.IntegerField(min_value=1, max_value=6)
    second_dice = forms.IntegerField(min_value=1, max_value=6)

