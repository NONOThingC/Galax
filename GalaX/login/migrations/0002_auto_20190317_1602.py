# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-17 16:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phonenumber',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]