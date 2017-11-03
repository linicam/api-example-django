# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('patient', models.IntegerField()),
                ('patient_first_name', models.CharField(max_length=254)),
                ('patient_last_name', models.CharField(max_length=254)),
                ('patient_ssn', models.CharField(max_length=20, null=True)),
                ('appointment', models.IntegerField()),
                ('status', models.CharField(max_length=254, null=True)),
                ('scheduled_time', models.DateTimeField()),
                ('office', models.CharField(max_length=254, null=True)),
                ('exam_room', models.CharField(max_length=254, null=True)),
                ('checkin_time', models.DateTimeField(default=None)),
                ('waited_time', models.IntegerField(default=0)),
                ('is_waiting', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=254)),
                ('email', models.EmailField(max_length=254)),
                ('doctor_id', models.IntegerField()),
                ('uid', models.IntegerField()),
                ('access_token', models.CharField(max_length=254)),
                ('refresh_token', models.CharField(max_length=254)),
                ('practice_group', models.IntegerField(default=0)),
                ('patients_checked', models.IntegerField(default=0)),
                ('total_wait_time', models.IntegerField(default=0)),
                ('user', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='appointments',
            name='doctor',
            field=models.ForeignKey(to='drchrono.Doctor'),
        ),
    ]
