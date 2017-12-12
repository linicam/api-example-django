from datetime import timedelta, datetime

import requests
from django.http import HttpResponse

from drchrono import settings
from drchrono.helpers import helper
from drchrono.helpers.global_handler import DbSettings
from drchrono.models import Appointments, Patient


def get_header_with_user(user):
    return {'Authorization': 'Bearer {0}'.format(user.profile.access_token)}


def get_header_with_token(access_token):
    return {'Authorization': 'Bearer {0}'.format(access_token)}


def revoke_token_request(user):
    params = {
        'client_id': settings.SOCIAL_AUTH_DRCHRONO_KEY,
        'client_secret': settings.SOCIAL_AUTH_DRCHRONO_SECRET,
        'token': user.profile.access_token
    }
    revoke_token_url = 'https://drchrono.com/o/revoke_token/'
    res = requests.post(revoke_token_url, params)
    return res


def token_request(user):
    params = {
        'grant_type': 'refresh_token',
        'client_id': settings.SOCIAL_AUTH_DRCHRONO_KEY,
        'client_secret': settings.SOCIAL_AUTH_DRCHRONO_SECRET,
        'redirect_uri': '/oauth',
        'refresh_token': user.profile.refresh_token
    }
    # helper.print_object(params, title='params')
    token_url = 'https://drchrono.com/o/token/'
    res = requests.post(token_url, data=params)
    d = res.json()
    # helper.print_object(d, title='res data')
    user.profile.access_token = d['access_token']
    user.profile.refresh_token = d['refresh_token']
    user.save()
    return res


# def test_request(user, params=None, headers=None):
#     if headers is None:
#         headers = {}
#     headers.update(get_header_with_user(user))
#     params.update({
#         # 'client_id': settings.SOCIAL_AUTH_DRCHRONO_KEY,
#         # 'client_secret': settings.SOCIAL_AUTH_DRCHRONO_SECRET,
#         # 'token': user.profile.access_token,
#         'verbose': True
#     })
#     test_url = 'https://drchrono.com/api/clinical_notes/%s' % params['appointment']
#     helper.print_object(params, title='test params')
#     res = requests.get(test_url, params, headers=headers)
#     helper.print_object(res)
#     return res


def office_request(user, params=None, headers=None):
    if params is None:
        params = {}
    if headers is None:
        headers = {}
    headers.update(get_header_with_user(user))
    offices_url = 'https://drchrono.com/api/offices'
    res = requests.get(offices_url, params, headers=headers)
    return res


def patients_request(user, params, headers=None, method='GET'):
    if headers is None:
        headers = {}
    headers.update(get_header_with_user(user))
    patients_url = 'https://drchrono.com/api/patients'
    if method == 'GET':
        if 'patient' in params:
            patients_url += '/' + str(params['patient'])
            res = requests.get(patients_url, headers=headers)
            if res.status_code >= 400:
                return res, res.reason
            patient = res.json()
            return res, patient
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
            return res, res.reason
        else:
            return res, res.content


def appointment_request(user, params, headers=None, method='GET'):
    if headers is None:
        headers = {}
    headers.update(get_header_with_user(user))
    appointments_url = 'https://drchrono.com/api/appointments'
    if method == 'GET':
        res = requests.get(appointments_url, params, headers=headers)
        if res.status_code >= 400:
            # handle 401
            return res, res.reason
        data = res.json()
        appointments = data['results']
        appointments_url = data['next']
        helper.print_info('request apps get', '{0} || {1} || {2}'.format(params, len(appointments), data['next']))
        while appointments_url:
            data = requests.get(appointments_url, headers=headers).json()
            appointments.extend(data['results'])
            appointments_url = data['next']
        return res, appointments
    elif method == 'PATCH':
        appointments_url += '/' + str(params['appointment'])
        res = requests.patch(appointments_url, params, headers=headers)
        if res.status_code >= 400:
            return res, res.reason
        else:
            return res, res.content


def sync_patient(user, app, update_local=False):
    patients = Patient.objects.filter(pk=app['patient'])
    if update_local or len(patients) < 1:
        # helper.print_info('update patient')
        code, p = patients_request(user, {'patient': app['patient']})
        p_attrs = {
            'patient_id': p['id'],
            'first_name': p['first_name'],
            'last_name': p['last_name'],
            'ssn': p['social_security_number'],
            'city': p['city'],
            'date_of_birth': p['date_of_birth'],
            'cell_phone': p['cell_phone'],
            'address': p['address'],
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
    date_range = DbSettings.date.strftime(settings.DATE_FORMAT) + '/' + \
                 (DbSettings.date + timedelta(period)).strftime(settings.DATE_FORMAT)
    params = {
        'doctor': user.profile.doctor.pk,
        'date_range': date_range,
    }
    res, appointments = appointment_request(user, params)
    if res.status_code >= 400:
        helper.print_error('sync_appointments error code', res.status_code)
        return HttpResponse(status=res.status_code)
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
        try:
            tar = Appointments.objects.get(pk=app['id'])
            if update_local:
                if app['status'] == 'Arrived' and tar.status != 'Arrived':
                    attrs['start_wait_time'] = app['updated_at']
                Appointments.objects.filter(pk=tar.appointment).update(**attrs)
        except Appointments.DoesNotExist:
            attrs['waited_time'] = 0
            if app['status'] == 'Arrived':
                attrs['start_wait_time'] = app['updated_at']
                attrs['check_in_time'] = app['updated_at']
            Appointments.objects.create(**attrs)


# def get_future_appointments(user, update_local=False, create_new_in_db=False):
#     if create_new_in_db:
#         sync_appointments(user, update_local)
#     future_date = DbSettings.date + timedelta(1)
#     return Appointments.objects.filter(doctor=user.profile.doctor.pk,
#                                        scheduled_time__gte=future_date).order_by(
#         'scheduled_time')


def get_appointments(user, update_local=False):
    if DbSettings.date != datetime.now().date():
        DbSettings.date = datetime.now().date()
        update_local = True
    sync_at_gv = update_local or settings.SYNC_AT_GV
    sync_create_new = update_local or settings.SYNC_CREATE_NEW
    if sync_create_new:
        response = sync_appointments(user, sync_at_gv)
        # if response is not None:
        #     return response
    return Appointments.objects.filter(doctor=user.profile.doctor.pk,
                                       scheduled_time__year=DbSettings.date.year,
                                       scheduled_time__month=DbSettings.date.month,
                                       scheduled_time__day=DbSettings.date.day).order_by('scheduled_time')
