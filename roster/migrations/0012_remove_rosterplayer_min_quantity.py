# Generated by Django 3.2.5 on 2021-08-29 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0011_alter_rosterteam_special_rules'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rosterplayer',
            name='min_quantity',
        ),
    ]
