from django.contrib.auth.models import User
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


class Tournament(models.Model):
    name = models.CharField(max_length=50)
    STATUS_CHOICES = (
        ('CLOSED', 'CLOSED'),
        ('OPEN', 'OPEN'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season')

    def __str__(self):
        return self.name
