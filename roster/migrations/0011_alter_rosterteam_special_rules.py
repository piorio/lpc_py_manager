# Generated by Django 3.2.6 on 2021-08-29 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0010_auto_20210723_0641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rosterteam',
            name='special_rules',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]