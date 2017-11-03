from datetime import datetime

import requests

from drchrono.models import Doctor, Appointments


def get_auth_headers(access_token):
    return {'Authorization': 'Bearer {0}'.format(access_token)}


def get_doctor(user):
    try:
        doctor = Doctor.objects.get(user=user, username=user.username)
    except Doctor.objects.model.DoesNotExist:
        return None
    return doctor


def print_error(func, msg):
    print func, ' ====ERROR====> ', msg


# global vars, check daily to clear the set
class DailyGlobalVarsSet:
    var = {}
    date = datetime.now().date()

    def __init__(self):
        pass

    def __str__(self):
        return self.var.keys()

    @classmethod
    def get(cls, user, force_sync=False):
        if cls.date != datetime.now().date():
            cls.date = datetime.now().date()
            cls.update()
        doctor = get_doctor(user)
        DrchronoRequest.set_headers(user)
        if doctor.pk in cls.var:
            # if force_update:
            cls.var[doctor.pk].update(force_sync)
            return cls.var[doctor.pk]
        v = GlobalVars(doctor)
        v.update(True)
        cls.var[doctor.pk] = v
        return cls.var[doctor.pk]

    @classmethod
    def update(cls):
        cls.var = {}


# if someone arrived in the last day and still waiting, here has problems
class GlobalVars:
    def __init__(self, doctor):
        self.doctor = doctor
        self.patient = None
        self.appointments = None

    def update(self, sync=False):
        t1 = datetime.now()
        self.appointments = self.update_appointments(sync)
        t2 = datetime.now()
        # print '==========gv updated using {0}============'.format((t2 - t1).total_seconds())

    def update_appointments(self, sync=False):
        if sync:
            # update: use celery to async
            params = {
                'doctor': self.doctor.pk,
                'date': DailyGlobalVarsSet.date,
            }
            appointments = DrchronoRequest.appointment_request(params)
            for app in appointments:
                patient = DrchronoRequest.patients_request({'patient': app['patient']})
                attrs = {
                    'doctor': self.doctor,
                    'patient_first_name': patient['first_name'],
                    'patient': app['id'],
                    'patient_last_name': patient['last_name'],
                    'patient_ssn': patient['social_security_number'],
                    'status': app['status'],
                    'office': app['office'],
                    'scheduled_time': app['scheduled_time'],
                    'duration': app['duration'],
                    'exam_room': app['exam_room'],
                    'appointment': app['id']
                }
                tar = Appointments.objects.filter(pk=app['id'])
                if len(tar) > 0:
                    tar.update(**attrs)
                else:
                    Appointments.objects.create(**attrs)
        return Appointments.objects.filter(doctor=self.doctor.pk, scheduled_time__year=DailyGlobalVarsSet.date.year,
                                           scheduled_time__month=DailyGlobalVarsSet.date.month,
                                           scheduled_time__day=DailyGlobalVarsSet.date.day).order_by('scheduled_time')


class DrchronoRequest:
    headers = None

    def __init__(self):
        pass

    @classmethod
    def set_headers(cls, user):
        if not cls.headers:
            doctor = get_doctor(user)
            cls.headers = get_auth_headers(doctor.access_token)

    @classmethod
    def patients_request(cls, params, headers=None, method='GET', **kwargs):
        if headers is None:
            headers = {}
        headers.update(cls.headers)
        patients_url = 'https://drchrono.com/api/patients'
        if method == 'GET':
            if 'patient' in params:
                patients_url += '/' + str(params['patient'])
                patient = requests.get(patients_url, headers=headers).json()
                return patient  # if status_code == 200
            else:
                data = requests.get(patients_url, params, headers=headers).json()
                patients = data['results']
                patients_url = data['next']
                while patients_url:
                    data = requests.get(patients_url, headers=headers).json()
                    patients.extend(data['results'])
                    patients_url = data['next']
                return patients
        elif method == 'PATCH':
            patients_url += '/' + str(params['patient'])
            res = requests.patch(patients_url, params, headers=headers)
            if res.status_code >= 300:
                return False, res.reason
            else:
                return True, res.content

    @classmethod
    def office_request(cls, params=None, headers=None, **kwargs):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        headers.update(cls.headers)
        offices_url = 'https://drchrono.com/api/offices'
        res = requests.get(offices_url, params, headers=headers)
        print vars(res)

    @classmethod
    def appointment_request(cls, params, headers=None, method='GET', **kwargs):
        if headers is None:
            headers = {}
        headers.update(cls.headers)
        appointments_url = 'https://drchrono.com/api/appointments'
        if method == 'GET':
            res = requests.get(appointments_url, params, headers=headers)
            if res.status_code >= 300:
                return []
            data = res.json()
            appointments = data['results']
            appointments_url = data['next']
            while appointments_url:
                data = requests.get(appointments_url, headers=headers).json()
                appointments.extend(data['results'])
                appointments_url = data['next']
            return appointments
        elif method == 'PATCH':
            appointments_url += '/' + str(params['appointment'])
            res = requests.patch(appointments_url, params, headers=headers)
            if res.status_code >= 300:
                return False, res.reason
            else:
                return True, res.content
        elif method == 'POST':
            return
