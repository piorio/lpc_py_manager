from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Model


class League(models.Model):
    name = models.CharField(max_length=50)
    STATUS_CHOICES = (
        ('CLOSED', 'CLOSED'),
        ('OPEN', 'OPEN'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    managers = models.ManyToManyField(User, related_name='managers', blank=True)

    def __str__(self):
        return self.name

    def debug(self):
        return 'League {"name": ' + self.name + ',"status": ' + self.status + ',"managers": ' + str(self.managers) + '}'


class Season(models.Model):
    name = models.CharField(max_length=50)
    STATUS_CHOICES = (
        ('CLOSED', 'CLOSED'),
        ('OPEN', 'OPEN'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='league')

    def __str__(self):
        return self.name

    def debug(self):
        return 'Season {"name": ' + self.name + ',"status": ' + self.status + '}'


class Tournament(models.Model):
    name = models.CharField(max_length=50)
    STATUS_CHOICES = (
        ('CLOSED', 'CLOSED'),
        ('OPEN', 'OPEN'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season')
    team = models.ManyToManyField('teams.Team')

    def __str__(self):
        return self.name

    def debug(self):
        return 'Tournament {"name": ' + self.name + ',"status": ' + self.status + '}'


class TournamentTeamResult(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='tournament')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team')
    win = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    loss = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    tie = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_touchdown = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_cas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    league_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def debug(self):
        return 'TournamentResult {"tournament": ' + str(self.tournament) + ', "team":' + str(self.team) + ' }'


class LeagueConfiguration(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='league_configuration')
    CONFIGURATION_KEYS = (
        ('EnableFrozen', 'EnableFrozen'),
    )
    key = models.CharField(max_length=20, choices=CONFIGURATION_KEYS)
    value = models.CharField(max_length=100)
