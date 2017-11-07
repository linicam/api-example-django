from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from drchrono.helpers import model_helper


class Doctor(models.Model):
    doctor_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=254)
    email = models.EmailField()
    uid = models.IntegerField()  # user id

    # user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    # practice_group = models.IntegerField(default=0)
    # patients_checked = models.IntegerField(default=0)
    # total_wait_time = models.IntegerField(default=0)

    def __str__(self):
        return '_'.join([self.username, str(self.pk), str(self.uid)])


class Patient(models.Model):
    patient_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    ssn = models.CharField(max_length=20, null=True)

    def __str__(self):
        return '__'.join([str(self.first_name), str(self.last_name), self.ssn])


class Appointments(models.Model):
    appointment = models.IntegerField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    status = models.CharField(max_length=254, null=True)
    scheduled_time = models.DateTimeField()
    duration = models.IntegerField(default=0)
    office = models.CharField(max_length=254, null=True)
    exam_room = models.CharField(max_length=254, null=True)
    start_wait_time = models.DateTimeField(null=True)
    check_in_time = models.DateTimeField(null=True)
    waited_time = models.IntegerField(default=0)

    def __str__(self):
        return '__'.join([str(self.doctor.doctor_id), str(self.appointment), self.patient.first_name,
                          self.patient.last_name, str(self.patient),
                          str(self.scheduled_time)])


@receiver(post_save, sender=Appointments)
def on_check_in(sender, instance, created, **kwargs):
    if created and instance.status == 'Arrived':
        create_notification(instance)
    # pass


class Notification(models.Model):
    INFO = 'info'
    ERROR = 'error'
    NOTIFICATION_CHOICES = (
        (INFO, 'Info'),
        (ERROR, 'Error')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=254)
    appointment = models.ForeignKey(Appointments)
    tag = models.CharField(choices=NOTIFICATION_CHOICES, default=INFO, max_length=10)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, null=True, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=254)
    refresh_token = models.CharField(max_length=254)
    in_session = models.IntegerField(null=True)
    avatar = models.FileField(null=True, upload_to=model_helper.get_upload_file_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def create_notification(app):
    msg = 'Patient {0} {1} has checked in on {2} for appointment scheduled at {3}'.format(
        app.patient.first_name, app.patient.last_name,
        app.check_in_time,
        app.scheduled_time)
    args = {
        'user': User.objects.get(profile__doctor=app.doctor),
        'message': msg,
        'appointment': app,
        'tag': Notification.INFO,
    }
    Notification.objects.create(**args)
