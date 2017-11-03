# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0004_auto_20171102_1540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointments',
            name='id',
        ),
        migrations.RemoveField(
            model_name='doctor',
            name='id',
        ),
        migrations.AlterField(
            model_name='appointments',
            name='appointment',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='doctor_id',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
    ]
