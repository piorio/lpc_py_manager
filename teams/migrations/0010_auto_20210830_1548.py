# Generated by Django 3.2.5 on 2021-08-30 15:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0009_teamplayer_big_guy'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='number_of_players',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(16)]),
        ),
        migrations.AlterField(
            model_name='team',
            name='big_guy_numbers',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(16)]),
        ),
    ]
