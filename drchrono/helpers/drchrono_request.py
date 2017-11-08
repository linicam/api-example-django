from datetime import timedelta

import requests

from drchrono import settings
from drchrono.helpers import helper
from drchrono.helpers.global_vars import DailyGlobalVarsSet
from drchrono.models import Appointments, Patient


class DrchronoRequest:
    headers = {}

    def __init__(self):
        pass

    @classmethod
    def get_header(cls, user):
        if user.pk in cls.headers:
            return cls.headers[user.pk]
        header = get_auth_headers(user.profile.access_token)
        cls.headers[user.pk] = header
        return header

    @classmethod
    def patients_request(cls, user, params, headers=None, method='GET', **kwargs):
        if headers is None:
            headers = {}
        headers.update(cls.get_header(user))
        patients_url = 'https://drchrono.com/api/patients'
        if method == 'GET':
            if 'patient' in params:
                patients_url += '/' + str(params['patient'])
                res = requests.get(patients_url, headers=headers)
                patient = res.json()
                return patient  # if status_code == 200
            else:
                # get all patients
                pass
                # data = requests.get(patients_url, params, headers=headers).json()
                # patients = data['results']
                # patients_url = data['next']
                # while patients_url:
                #     data = requests.get(patients_url, headers=headers).json()
                #     patients.extend(data['results'])
                #     patients_url = data['next']
                # return patients
        elif method == 'PATCH':
            patients_url += '/' + str(params['patient'])
            res = requests.patch(patients_url, params, headers=headers)
            if res.status_code >= 400:
                return False, res.reason
            else:
                return True, res.content

    @classmethod
    def revoke_token_request(cls, user, headers=None, **kwargs):
        if headers is None:
            headers = {}
        headers.update(cls.get_header(user))
        params = {
            'client_id': settings.SOCIAL_AUTH_DRCHRONO_KEY,
            'client_secret': settings.SOCIAL_AUTH_DRCHRONO_SECRET,
            'token': user.profile.access_token
        }
        revoke_token_url = 'https://drchrono.com/o/revoke_token'
        res = requests.post(revoke_token_url, params, headers=headers)
        helper.print_object(res)

    @classmethod
    def office_request(cls, user, params=None, headers=None, **kwargs):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        headers.update(cls.headers)
        offices_url = 'https://drchrono.com/api/offices'
        res = requests.get(offices_url, params, headers=headers)
        helper.print_object(res)

    @classmethod
    def token_request(cls, user):
        params = {
            'grant_type': 'refresh_token',
            'client_id': settings.SOCIAL_AUTH_DRCHRONO_KEY,
            'client_secret': settings.SOCIAL_AUTH_DRCHRONO_SECRET,
            'redirect_uri': '/oauth',
            'refresh_token': user.profile.refresh_token
        }
        helper.print_object(params, title='token request')
        token_url = 'https://drchrono.com/o/token'
        res = requests.post(token_url, data=params)
        helper.print_object(res)

    @classmethod
    def appointment_request(cls, user, params, headers=None, method='GET', **kwargs):
        if headers is None:
            headers = {}
        headers.update(cls.get_header(user))
        appointments_url = 'https://drchrono.com/api/appointments'
        if method == 'GET':
            res = requests.get(appointments_url, params, headers=headers)
            if res.status_code >= 400:
                # handle 401
                return res.status_code, res.reason
            data = res.json()
            appointments = data['results']
            appointments_url = data['next']
            helper.print_info('request apps get', '{0} || {1} || {2}'.format(params, len(appointments), data['next']))
            while appointments_url:
                data = requests.get(appointments_url, headers=headers).json()
                appointments.extend(data['results'])
                appointments_url = data['next']
            return res.status_code, appointments
        elif method == 'PATCH':
            appointments_url += '/' + str(params['appointment'])
            res = requests.patch(appointments_url, params, headers=headers)
            if res.status_code >= 400:
                return res.status_code, res.reason
            else:
                return res.status_code, res.content


def get_auth_headers(access_token):
    return {'Authorization': 'Bearer {0}'.format(access_token)}


def sync_patient(user, app, update_local=False):
    patients = Patient.objects.filter(pk=app['patient'])
    if update_local or len(patients) < 1:
        # helper.print_info('update patient')
        p = DrchronoRequest.patients_request(user, {'patient': app['patient']})
        p_attrs = {
            'patient_id': p['id'],
            'first_name': p['first_name'],
            'last_name': p['last_name'],
            'ssn': p['social_security_number']
        }
        if len(patients) < 1:
            patient = Patient.objects.create(**p_attrs)
        else:
            patients.update(**p_attrs)
            patient = patients[0]
    else:
        patient = patients[0]
    return patient


def sync_appointments(user, update_local=False, period=settings.SYNC_PERIOD):
    date_range = DailyGlobalVarsSet.date.strftime(settings.DATE_FORMAT) + '/' + \
                 (DailyGlobalVarsSet.date + timedelta(period)).strftime(settings.DATE_FORMAT)
    params = {
        'doctor': user.profile.doctor.pk,
        'date_range': date_range,
    }
    res, appointments = DrchronoRequest.appointment_request(user, params)
    if res >= 400:
        helper.print_error('sync_appointments error code', res)
        return
    for app in appointments:
        attrs = {
            'doctor': user.profile.doctor,
            'status': app['status'],
            'patient': sync_patient(user, app, update_local),
            'office': app['office'],
            'scheduled_time': app['scheduled_time'],
            'duration': app['duration'],
            'exam_room': app['exam_room'],
            'appointment': app['id'],
        }
        tar = Appointments.objects.filter(pk=app['id'])
        if len(tar) > 0:
            if update_local:
                if app['status'] == 'Arrived' and tar[0].status != 'Arrived':
                    helper.print_info('update time', app['updated_at'])
                    attrs['start_wait_time'] = app['updated_at']
                tar.update(**attrs)
        else:
            attrs['waited_time'] = 0
            if app['status'] == 'Arrived':
                helper.print_info('update time', app['updated_at'])
                attrs['start_wait_time'] = app['updated_at']
                attrs['check_in_time'] = app['updated_at']
            Appointments.objects.create(**attrs)


def get_future_appointments(user, update_local=False, create_new_in_db=False):
    if create_new_in_db:
        sync_appointments(user, update_local)
    future_date = DailyGlobalVarsSet.date + timedelta(1)
    return Appointments.objects.filter(doctor=user.profile.doctor.pk,
                                       scheduled_time__gte=future_date).order_by(
        'scheduled_time')
