# Generated by Django 3.2.5 on 2021-09-03 12:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0012_auto_20210903_0745'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamplayer',
            name='deflection',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='teamplayer',
            name='intercept',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
