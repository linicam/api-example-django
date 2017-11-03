from django.contrib.auth.models import User
from django.db import models


class Doctor(models.Model):
    doctor_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=254)
    email = models.EmailField()
    uid = models.IntegerField()
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=254)
    refresh_token = models.CharField(max_length=254)
    practice_group = models.IntegerField(default=0)
    patients_checked = models.IntegerField(default=0)
    total_wait_time = models.IntegerField(default=0)
    in_session = models.IntegerField(null=True)

    def __str__(self):
        return '_'.join([self.username, str(self.uid), str(self.user_id)])


class Appointments(models.Model):
    appointment = models.IntegerField(primary_key=True)
    patient = models.IntegerField()
    patient_first_name = models.CharField(max_length=254)
    patient_last_name = models.CharField(max_length=254)
    patient_ssn = models.CharField(max_length=20, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    status = models.CharField(max_length=254, null=True)
    scheduled_time = models.DateTimeField()
    duration = models.IntegerField(default=0)
    office = models.CharField(max_length=254, null=True)
    exam_room = models.CharField(max_length=254, null=True)
    start_wait_time = models.DateTimeField(null=True)
    waited_time = models.IntegerField(default=0)

    def __str__(self):
        return '__'.join([str(self.doctor.doctor_id), str(self.appointment), self.patient_first_name,
                         self.patient_last_name, str(self.patient),
                         str(self.scheduled_time)])

    # def get_scheduled_time_string(self):
    #     return self.scheduled_time.strftime('%Y-%m-%dT%H:%M:%S')