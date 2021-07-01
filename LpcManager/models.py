from django.db import models
from django.db.models import IntegerField, Model
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class Race(models.Model):
    name = models.CharField(max_length=50)


class Skill(models.Model):
    category = models.CharField(max_length=50)
    description = models.TextField(max_length=255, null=True, blank=True, default=None)
    name = models.CharField(max_length=50)


class Trait(models.Model):
    description = models.TextField(max_length=255, null=True, blank=True, default=None)
    name = models.CharField(max_length=50)


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
    primary_skills = models.ManyToManyField(Skill, related_name='primary_skills')
    secondary_skills = models.ManyToManyField(Skill, related_name='secondary_skills')
    traits = models.ManyToManyField(Trait)
