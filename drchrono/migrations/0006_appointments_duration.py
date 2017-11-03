# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0005_auto_20171103_0752'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointments',
            name='duration',
            field=models.IntegerField(default=0),
        ),
    ]
