# Generated by Django 3.2.5 on 2021-10-15 12:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0024_teamplayer_spent_spp'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamplayer',
            name='number_of_matches',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]