# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-04-11 01:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sign', '0002_auto_20190411_0915'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guest',
            old_name='realnanme',
            new_name='realname',
        ),
    ]
