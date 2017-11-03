from datetime import datetime

from django.contrib import auth
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from drchrono.helpers import helper
from drchrono.helpers.helper import DrchronoRequest, DailyGlobalVarsSet
from drchrono.models import Appointments


def logout(request):
    auth.logout(request)
    return redirect('/')


def logged_in(request):
    DrchronoRequest.set_headers(request.user)
    DailyGlobalVarsSet.get(request.user)
    doctor = helper.get_doctor(request.user)
    if not DrchronoRequest.headers:
        DrchronoRequest.set_headers(doctor.access_token)

    return render_to_response('done.html', {
        'doctor': doctor,
    }, RequestContext(request))


def appointment_requests(request):
    force_syn = request.method == 'POST'
    gv = DailyGlobalVarsSet.get(request.user, force_syn)
    doctor = helper.get_doctor(request.user)
    if not DrchronoRequest.headers:
        DrchronoRequest.set_headers(doctor.access_token)

    if not doctor.in_session:
        check_clock(gv)
    # refresh
    gv = DailyGlobalVarsSet.get(request.user)
    appointments = gv.appointments

    waited_patients = Appointments.objects.filter(waited_time__gt=0)
    waited_times = waited_patients.values_list('waited_time', flat=True)
    average_wait_time = sum(waited_times) * 1.0 / len(waited_patients) if len(waited_patients) else 0
    print len(waited_patients), waited_times, average_wait_time, doctor.in_session
    if force_syn:
        return HttpResponse('update succeed')
    else:
        return render_to_response('appointments.html', {
            'appointments': appointments,
            'average_wait_time': average_wait_time,
            'in_session': doctor.in_session
        }, RequestContext(request))


def start_clock(gv):
    apps = gv.appointments.filter(status='Arrived')
    for app in apps:
        now = datetime.now()
        duration = (now - app.start_wait_time).seconds
        app.waited_time += duration
        app.save()


def stop_clock(gv):
    apps = gv.appointments.filter(status='Arrived')
    for app in apps:
        app.start_wait_time = datetime.now()
        app.save()


def check_clock(gv):
    apps = gv.appointments.filter(status='Arrived')
    for app in apps:
        print '===', app.pk
        now = datetime.now()
        duration = (now - app.start_wait_time).seconds
        app.waited_time += duration
        app.start_wait_time = datetime.now()
        app.save()


def options(request):
    gv = DailyGlobalVarsSet.get(request.user)
    doctor = helper.get_doctor(request.user)
    appointment = request.POST['appointment']
    option = request.POST['option']

    try:
        target_app = gv.appointments.get(appointment=appointment)
    except Appointments.objects.model.DoesNotExist:
        return HttpResponseServerError('can\'t find appointment')

    if option == 'start':
        if doctor.in_session:
            return HttpResponseServerError('in session')
        doctor.in_session = appointment
        start_clock(gv)
        status = 'In Room'
        pass
    elif option == 'end':
        if not doctor.in_session:
            return HttpResponseServerError('no session')
        doctor.in_session = None
        stop_clock(gv)
        status = 'Complete'
    else:
        return HttpResponseServerError('wrong option clicked')
    doctor.save()
    params = {
        'status': status,
        'appointment': target_app.appointment
    }
    res, content = DrchronoRequest.appointment_request(params, method='PATCH')
    if not res:
        return HttpResponseServerError(content)
    target_app.status = status
    target_app.save()
    return HttpResponse(option + 'succeed')
    # return HttpResponse('')


def check_in(request):
    gv = DailyGlobalVarsSet.get(request.user)
    if request.method == 'GET':
        return render_to_response('check_in.html', RequestContext(request))
    elif request.method == 'POST':
        doctor = helper.get_doctor(request.user)

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        ssn = request.POST['ssn']
        appointments = gv.appointments.filter(doctor=doctor, patient_last_name__iexact=last_name,
                                              patient_first_name__iexact=first_name,  # start_wait_time__isnull=True,
                                              scheduled_time__gte=datetime.now())
        if ssn is not None and ssn != '':
            appointments = appointments.filter(patient_ssn=ssn)

        msgs = ['Success', 'No appointment find']
        msg_id = 0
        l = len(appointments)
        if l < 1:
            msg_id = 1

        state = msg_id == 0
        msg = msgs[msg_id]

        if state:
            appointment = appointments[0]
            print appointment
            gv.patient = appointment.patient
            params = {
                'status': 'Arrived',
                'appointment': appointment.appointment
            }
            res, content = DrchronoRequest.appointment_request(params, method='PATCH')
            if not res:
                return HttpResponseServerError(res + content)
            appointment.status = 'Arrived'
            appointment.start_wait_time = datetime.now()
            appointment.save()

        return render_to_response('check_in_result.html', {
            'state': state,
            'message': msg,
            'time': 10,
        })


def update(request):
    gv = DailyGlobalVarsSet.get(request.user)
    if request.method == 'GET':
        # patient = PatientSet.get_patient(pid)
        # print patient
        return render_to_response('update.html', RequestContext(request))
    elif request.method == 'POST':
        patient = gv.patient
        if not patient:
            return HttpResponseServerError('no patient checked in')
        post = request.POST
        params = {
            'patient': patient,
            'address': post['address'],
            'cell_phone': post['cell_phone'],
            'city': post['city']
        }
        res, content = DrchronoRequest.patients_request(params, method='PATCH')
        if not res:
            return HttpResponseServerError(res + content)
        # check updated
        # patient = DrchronoRequest.patients_request({
        #     'patient': patient
        # })
        return redirect('/patients')
