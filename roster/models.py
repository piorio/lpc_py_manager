from django.db import models
from django.db.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


# Create your models here.
class Race(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.CharField(max_length=50)
    description = models.TextField(max_length=255, null=True, blank=True, default=None)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Trait(models.Model):
    description = models.TextField(max_length=255, null=True, blank=True, default=None)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class RosterTeam(models.Model):
    apothecary = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    re_roll_cost = models.IntegerField(default=0, validators=[MaxValueValidator(1000000), MinValueValidator(0)])
    re_roll_max = models.IntegerField(default=0, validators=[MaxValueValidator(16), MinValueValidator(0)])
    special_rules = models.CharField(max_length=255, null=True, blank=True, default=None)
    tier = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])
    race = models.ForeignKey(Race, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class RosterPlayer(models.Model):
    agility = models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    armor_value = models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    cost = models.IntegerField(default=0, validators=[MaxValueValidator(1000000), MinValueValidator(0)])
    max_quantity = models.IntegerField(default=0, validators=[MaxValueValidator(16), MinValueValidator(0)])
    min_quantity = models.IntegerField(default=0, validators=[MaxValueValidator(16), MinValueValidator(0)])
    movement_allowance = models.IntegerField(default=0, validators=[MaxValueValidator(20), MinValueValidator(0)])
    passing = models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    position = models.CharField(max_length=50)
    strength = models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    # primary_skills = models.ManyToManyField(Skill, related_name='primary_skills', blank=True)
    # secondary_skills = models.ManyToManyField(Skill, related_name='secondary_skills', blank=True)

    primary_skills = models.CharField(default=None, max_length=5)
    secondary_skills = models.CharField(default=None, max_length=5)

    skills = models.ManyToManyField(Skill, related_name='skills', blank=True)
    traits = models.ManyToManyField(Trait, blank=True)
    roster_team = models.ForeignKey(RosterTeam, on_delete=models.CASCADE, related_name='roster_players')

    def __str__(self):
        return self.position
