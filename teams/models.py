from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from roster.models import Race
from django.contrib.auth.models import User

# STATUS -> CREATED READY DISMISS


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    treasury = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20)
    re_roll = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    assistant_coach = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    cheerleader = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    apothecary = models.BooleanField(default=False)
    current_team_value = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    roster_team = models.ForeignKey(Race, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('all_team_detail', args=[str(self.id)])
