# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-04-11 01:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sign', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='limit',
            field=models.IntegerField(),
        ),
    ]
