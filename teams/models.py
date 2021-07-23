from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from roster.models import Race, RosterTeam, Skill, Trait, RosterPlayer
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
    roster_team = models.ForeignKey(RosterTeam, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')
    extra_dedicated_fan = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    def get_absolute_url(self):
        return reverse('teams:all_team_detail', args=[str(self.id)])

    def get_dismiss_absolute_url(self):
        return reverse('teams:dismiss_team', args=[str(self.id)])

    def get_prepare_absolute_url(self):
        return reverse('teams:prepare_team', args=[str(self.id)])

    def get_ready_absolute_url(self):
        return reverse('teams:ready_team', args=[str(self.id)])

    def get_buy_player_absolute_url(self):
        return reverse('teams:buy_player', args=[str(self.id)])

    def get_fire_player_absolute_url(self):
        return reverse('teams:fire_player', args=[str(self.id)])

    def get_my_team_detail_absolute_url(self):
        return reverse('teams:my_team_detail', args=[str(self.id)])

    def __str__(self):
        return self.name


class TeamPlayer(models.Model):
    name = models.CharField(default='NAME', max_length=100)
    agility = models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    armor_value = models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    cost = models.IntegerField(default=0, validators=[MaxValueValidator(1000000), MinValueValidator(0)])
    value = models.IntegerField(default=0, validators=[MaxValueValidator(1000000), MinValueValidator(0)])
    movement_allowance = models.IntegerField(default=0, validators=[MaxValueValidator(20), MinValueValidator(0)])
    passing = models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    position = models.CharField(max_length=50)
    strength = models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    base_skills = models.ManyToManyField(Skill, related_name='base_skills', blank=True)
    traits = models.ManyToManyField(Trait, blank=True)
    roster_team = models.ForeignKey(RosterTeam, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')

    def init_with_roster_player(self, roster_player, team):
        self.agility = roster_player.agility
        self.armor_value = roster_player.armor_value
        self.cost = roster_player.cost
        self.value = roster_player.cost
        self.movement_allowance = roster_player.movement_allowance
        self.passing = roster_player.passing
        self.position = roster_player.position
        self.strength = roster_player.strength
        # Skills and traits
        self.roster_team = roster_player.roster_team
        self.team = team

    def __str__(self):
        return self.position
