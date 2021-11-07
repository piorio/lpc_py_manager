# Generated by Django 3.2.5 on 2021-11-05 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0006_remove_tournament_match'),
        ('match', '0012_auto_20210925_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='league.tournament'),
        ),
    ]
