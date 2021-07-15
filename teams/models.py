from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from roster.models import Race
from django.contrib.auth.models import User


# Create your models here.
class TeamReadyManager(models.Manager):
    def get_queryset(self):
        return super(TeamReadyManager, self).get_queryset().filter(status='READY')


class Team(models.Model):
    objects = models.Manager()  # default manager
    ready_team = TeamReadyManager()  # manager for only read team
    STATUS_CHOICES = (
        ('CREATED', 'CREATED'),
        ('READY', 'READY'),
        ('DISMISS', 'DISMISS'),
    )
    name = models.CharField(max_length=100)
    value = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    treasury = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    re_roll = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    assistant_coach = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    cheerleader = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    apothecary = models.BooleanField(default=False)
    current_team_value = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    roster_team = models.ForeignKey(Race, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team')

    def get_absolute_url(self):
        return reverse('teams:all_team_detail', args=[str(self.id)])

    def get_dismiss_absolute_url(self):
        return reverse('teams:dismiss_team', args=[str(self.id)])

    def __str__(self):
        return self.name
