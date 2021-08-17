# Generated by Django 3.2.5 on 2021-08-17 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0006_alter_team_extra_dedicated_fan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='status',
            field=models.CharField(choices=[('CREATED', 'CREATED'), ('READY', 'READY'), ('RETIRED', 'RETIRED')], max_length=20),
        ),
    ]