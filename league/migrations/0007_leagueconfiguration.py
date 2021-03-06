# Generated by Django 3.2.5 on 2021-12-10 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0006_remove_tournament_match'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('EnableFrozen', 'EnableFrozen')], max_length=20)),
                ('value', models.CharField(max_length=100)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='league_configuration', to='league.league')),
            ],
        ),
    ]
