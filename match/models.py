from django.db import models
from django.urls import reverse

from teams.models import Team
from django.core.validators import MinValueValidator


# Create your models here.
class Match(models.Model):
    first_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='first_team')
    second_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='second_team')
    match_date = models.DateField()
    first_team_td = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    second_team_td = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    first_team_cas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    first_team_badly_hurt = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    first_team_serious_injury = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    first_team_kill = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    second_team_cas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    second_team_badly_hurt = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    second_team_serious_injury = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    second_team_kill = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)

    def get_absolute_url(self):
        return reverse('match:close_match', args=[str(self.id)])
