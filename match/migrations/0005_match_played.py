# Generated by Django 3.2.5 on 2021-08-18 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0004_auto_20210816_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='played',
            field=models.BooleanField(default=False),
        ),
    ]
