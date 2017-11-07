# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import drchrono.helpers.model_helper


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointments',
            fields=[
                ('appointment', models.IntegerField(serialize=False, primary_key=True)),
                ('status', models.CharField(max_length=254, null=True)),
                ('scheduled_time', models.DateTimeField()),
                ('duration', models.IntegerField(default=0)),
                ('office', models.CharField(max_length=254, null=True)),
                ('exam_room', models.CharField(max_length=254, null=True)),
                ('start_wait_time', models.DateTimeField(null=True)),
                ('check_in_time', models.DateTimeField(null=True)),
                ('waited_time', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('doctor_id', models.IntegerField(serialize=False, primary_key=True)),
                ('username', models.CharField(max_length=254)),
                ('email', models.EmailField(max_length=254)),
                ('uid', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=254)),
                ('tag', models.CharField(default=b'info', max_length=10, choices=[(b'info', b'Info'), (b'error', b'Error')])),
                ('appointment', models.ForeignKey(to='drchrono.Appointments')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('patient_id', models.IntegerField(serialize=False, primary_key=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('ssn', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(max_length=254)),
                ('refresh_token', models.CharField(max_length=254)),
                ('in_session', models.IntegerField(null=True)),
                ('avatar', models.FileField(null=True, upload_to=drchrono.helpers.model_helper.get_upload_file_name)),
                ('doctor', models.ForeignKey(to='drchrono.Doctor', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='appointments',
            name='doctor',
            field=models.ForeignKey(to='drchrono.Doctor'),
        ),
        migrations.AddField(
            model_name='appointments',
            name='patient',
            field=models.ForeignKey(to='drchrono.Patient'),
        ),
    ]
