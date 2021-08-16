# Generated by Django 3.2.5 on 2021-07-23 16:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0005_auto_20210723_0636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='extra_dedicated_fan',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
    ]