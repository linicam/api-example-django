# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0003_doctor_in_session'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointments',
            old_name='checkin_time',
            new_name='start_wait_time',
        ),
        migrations.RemoveField(
            model_name='appointments',
            name='is_waiting',
        ),
    ]
