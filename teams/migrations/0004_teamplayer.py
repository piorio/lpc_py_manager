# Generated by Django 3.2.5 on 2021-07-20 14:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0008_delete_coach'),
        ('teams', '0003_alter_team_roster_team'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agility', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)])),
                ('armor_value', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)])),
                ('cost', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(0)])),
                ('value', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(0)])),
                ('movement_allowance', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(20), django.core.validators.MinValueValidator(0)])),
                ('passing', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)])),
                ('position', models.CharField(max_length=50)),
                ('strength', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)])),
                ('base_skills', models.ManyToManyField(blank=True, related_name='base_skills', to='roster.Skill')),
                ('roster_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roster.rosterteam')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.team')),
                ('traits', models.ManyToManyField(blank=True, to='roster.Trait')),
            ],
        ),
    ]
