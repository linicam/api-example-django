# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0006_appointments_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='in_session',
            field=models.IntegerField(null=True),
        ),
    ]
