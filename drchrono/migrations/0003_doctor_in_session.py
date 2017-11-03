# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0002_auto_20171102_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='in_session',
            field=models.BooleanField(default=False),
        ),
    ]
