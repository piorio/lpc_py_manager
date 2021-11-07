from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from league.models import Season
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
        ('RETIRED', 'RETIRED'),
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
    big_guy_numbers = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(16)])
    number_of_players = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(16)])

    win = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    loss = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    tie = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_touchdown = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_cas = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    league_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    season = models.ForeignKey(Season, on_delete=models.CASCADE, blank=True, null=True)

    def get_my_team_detail_absolute_url(self):
        return reverse('teams:my_team_detail', args=[str(self.id)])

    def get_remove_re_roll_absolute_url(self):
        return reverse('teams:remove_re_roll', args=[str(self.id)])

    def get_buy_assistant_coach_absolute_url(self):
        return reverse('teams:buy_assistant_coach', args=[str(self.id)])

    def get_remove_assistant_coach_absolute_url(self):
        return reverse('teams:remove_assistant_coach', args=[str(self.id)])

    def get_buy_cheerleader_absolute_url(self):
        return reverse('teams:buy_cheerleader', args=[str(self.id)])

    def get_remove_cheerleader_absolute_url(self):
        return reverse('teams:remove_cheerleader', args=[str(self.id)])

    def get_buy_extra_fan_absolute_url(self):
        return reverse('teams:buy_extra_fan', args=[str(self.id)])

    def get_remove_extra_fan_absolute_url(self):
        return reverse('teams:remove_extra_fan', args=[str(self.id)])

    def get_buy_apothecary_absolute_url(self):
        return reverse('teams:buy_apothecary', args=[str(self.id)])

    def get_remove_apothecary_absolute_url(self):
        return reverse('teams:remove_apothecary', args=[str(self.id)])

    def get_manage_player_absolute_url(self):
        return reverse('teams:manage_player', args=[str(self.id)])

    def get_manage_fire_player_absolute_url(self):
        return reverse('teams:manage_fire_player', args=[str(self.id)])

    def get_manage_buy_re_roll_absolute_url(self):
        return reverse('teams:manage_buy_re_roll', args=[str(self.id)])

    def get_manage_remove_re_roll_absolute_url(self):
        return reverse('teams:manage_remove_re_roll', args=[str(self.id)])

    def get_manage_buy_assistant_coach_absolute_url(self):
        return reverse('teams:manage_buy_assistant_coach', args=[str(self.id)])

    def get_manage_remove_assistant_coach_absolute_url(self):
        return reverse('teams:manage_remove_assistant_coach', args=[str(self.id)])

    def get_manage_buy_cheerleader_absolute_url(self):
        return reverse('teams:manage_buy_cheerleader', args=[str(self.id)])

    def get_manage_remove_cheerleader_absolute_url(self):
        return reverse('teams:manage_remove_cheerleader', args=[str(self.id)])

    def get_manage_buy_apothecary_absolute_url(self):
        return reverse('teams:manage_buy_apothecary', args=[str(self.id)])

    def get_manage_remove_apothecary_absolute_url(self):
        return reverse('teams:manage_remove_apothecary', args=[str(self.id)])

    def get_manage_buy_player_absolute_url(self):
        return reverse('teams:manage_buy_player', args=[str(self.id)])

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
    big_guy = models.BooleanField(default=False)
    roster_player = models.ForeignKey(RosterPlayer, on_delete=models.CASCADE, blank=True, default=None)

    extra_skills = models.ManyToManyField(Skill, related_name='extra_skills', blank=True)

    touchdown = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_cas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    badly_hurt = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    serious_injury = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    kill = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    spp = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    intercept = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    deflection = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    complete = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    niggling_injury = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_mvp = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    missing_next_game = models.BooleanField(default=False)
    dead = models.BooleanField(default=False)
    fired = models.BooleanField(default=False)
    spent_spp = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    number_of_matches = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_journeyman = models.BooleanField(default=False)

    LEVEL_CHOICES = (
        ('NONE', 'NONE'),
        ('EXPERIENCED', 'EXPERIENCED'),
        ('VETERAN', 'VETERAN'),
        ('EMERGING STAR', 'EMERGING STAR'),
        ('STAR', 'STAR'),
        ('SUPER STAR', 'SUPER STAR'),
        ('LEGEND', 'LEGEND'),
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='NONE')

    player_number = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def init_with_roster_player(self, roster_player, team):
        self.agility = roster_player.agility
        self.armor_value = roster_player.armor_value
        self.cost = roster_player.cost
        self.value = roster_player.cost
        self.movement_allowance = roster_player.movement_allowance
        self.passing = roster_player.passing
        self.position = roster_player.position
        self.strength = roster_player.strength
        # Roster
        self.roster_team = roster_player.roster_team
        self.team = team
        self.roster_player = roster_player
        # Big Guy
        self.big_guy = roster_player.big_guy

    def set_initial_skills_and_traits(self, roster_player):
        # Skills and traits
        self.base_skills.add(*roster_player.skills.all())
        self.traits.add(*roster_player.traits.all())

    def __str__(self):
        return '[' + str(self.player_number) + '] - ' + self.name + " - (" + self.position + ")"

    def debug(self):
        return str(self)

    def get_random_first_skill_levelup_absolute_url(self):
        return reverse('teams:random_first_skill', args=[str(self.id)])

    def get_random_second_skill_levelup_absolute_url(self):
        return reverse('teams:random_second_skill', args=[str(self.id)])

    def get_choose_first_skill_levelup_absolute_url(self):
        return reverse('teams:select_first_skill', args=[str(self.id)])

    def get_choose_secondary_skill_levelup_absolute_url(self):
        return reverse('teams:select_second_skill', args=[str(self.id)])
