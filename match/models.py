from django.db import models
from django.urls import reverse

from teams.models import Team, TeamPlayer
from django.core.validators import MinValueValidator


# Create your models here.
class Match(models.Model):
    first_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='first_team')
    second_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='second_team')
    match_date_from = models.DateField(default=None, blank=True, null=True)
    match_date_to = models.DateField(default=None, blank=True, null=True)
    first_team_td = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    first_team_cas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    first_team_badly_hurt = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    first_team_serious_injury = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    first_team_kill = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    first_team_extra_fan = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    first_team_fan_factor = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    first_team_gold = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)

    second_team_td = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    second_team_cas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    second_team_badly_hurt = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    second_team_serious_injury = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    second_team_kill = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    second_team_extra_fan = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    second_team_fan_factor = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    second_team_gold = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)

    played = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('match:close_match', args=[str(self.id)])


class TeamPlayerMatchRecord(models.Model):
    player = models.ForeignKey(TeamPlayer, on_delete=models.CASCADE, related_name='matches_player_record')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='matches_match_record')
    ssp = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    died = models.BooleanField(default=False)
    touchdown = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    badly_hart = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    seriously_hurt = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    seriously_injury = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    kill = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    deflection = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    complete = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    received_cas = models.CharField(default='', max_length=100)
    last_injury = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_cas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    intercept = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    deflection = models.IntegerField(default=0, validators=[MinValueValidator(0)])
