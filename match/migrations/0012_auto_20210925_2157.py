# Generated by Django 3.2.5 on 2021-09-25 21:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0011_auto_20210924_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='first_team_gold',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='match',
            name='second_team_gold',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
