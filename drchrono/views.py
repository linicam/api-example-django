from datetime import datetime

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.context_processors import csrf
from django.views.decorators.http import require_http_methods, require_GET, require_POST

import drchrono.helpers.request_handler
from drchrono import settings
from drchrono.helpers import time_handler, helper, request_handler
from drchrono.helpers.my_decorators import association_check, identity_check
from drchrono.helpers.my_forms import CheckInForm, AvatarForm, IdentityForm, UpdateForm
from drchrono.models import Appointments, Notification, Patient, create_notification


@require_GET
def home(request):
    return redirect('/login/')


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if association_check(request.user):
                return redirect('/identity/')
            return redirect('/oauth/')
        c = {}
        c.update(csrf(request))
        return render_to_response('login.html', c, RequestContext(request))
    else:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if association_check(request.user):
                return redirect('/identity/')
            return redirect('/oauth/')
        else:
            messages.error(request, 'Invalid login info')
            return redirect('/login/')


@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'GET':
        form = UserCreationForm()
        return render_to_response('register.html', {'form': form}, RequestContext(request))
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/oauth/')
        else:
            messages.error(request, 'Already existed or invalid register info')
            return redirect('/register/')


@login_required
@require_GET
def oauth(request):
    if association_check(request.user):
        return redirect('/identity/')
    return render_to_response('oauth.html', context=RequestContext(request))


@login_required
@require_POST
def logout(request):
    auth.logout(request)
    return redirect('/login/')


@login_required
@require_POST
def avatar(request):
    form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)
    if form.is_valid():
        form.save()
        messages.success(request, "Update successfully")
    else:
        messages.error(request, "Invalid avatar file")
    return redirect('/main/', RequestContext(request))


@login_required
@user_passes_test(association_check, login_url='oauth')
@require_http_methods(["GET", "POST"])
def identify(request):
    if request.method == 'GET':
        if 'identity' not in request.session:
            form = IdentityForm(auto_id=False)
            return render_to_response('identity.html', {
                'form': form,
            }, RequestContext(request))
        elif request.session['identity'] == 'doctor':
            return redirect('/main/')
        elif request.session['identity'] == 'patient':
            return redirect('/checkin/')
        else:
            return HttpResponseBadRequest('Invalid identity')
    else:
        if 'identity' not in request.POST:
            messages.error(request, 'Please choose your identity')
            return redirect('/identity/')
        identity = request.POST['identity']
        request.session['identity'] = identity
        if identity == 'doctor':
            # db_handler.get_appointments(request.user, True)
            return redirect('/main')
        elif identity == 'patient':
            return redirect('/checkin')


@login_required
@user_passes_test(association_check, login_url='/oauth/')
@identity_check
@require_GET
def main(request):
    # db_handler.get_appointments(request.user, True)
    return render_to_response('main.html', {
        'user': request.user,
        'form': AvatarForm(instance=request.user)
    }, RequestContext(request))


@login_required
@user_passes_test(association_check, login_url='/oauth/')
@identity_check
@require_POST
def refresh_token(request):
    request_handler.token_request(request.user)
    return HttpResponse('Finished')


@login_required
@user_passes_test(association_check, login_url='/oauth/')
@identity_check
@require_http_methods(["GET", "POST"])
def appointment_requests(request):
    force_syn = request.method == 'POST'
    time_handler.check_clock()
    appointments = drchrono.helpers.request_handler.get_appointments(request.user, force_syn)

    if force_syn:
        return HttpResponse('Update succeed')
    else:
        waited_patients = Appointments.objects.filter(waited_time__gt=0)
        waited_times = waited_patients.values_list('waited_time', flat=True)
        average_wait_time = sum(waited_times) * 1.0 / len(waited_patients) if len(waited_patients) else 0
        ntfs = Notification.objects.filter(user=request.user, tag=Notification.INFO)
        # helper.print_info('ntfs', len(ntfs), len(Notification.objects.all()))
        Notification.objects.filter(user=request.user, tag=Notification.INFO).delete()
        # helper.print_info('ntfs after', len(ntfs), len(Notification.objects.all()))

        return render_to_response('appointments.html', {
            'appointments': appointments,
            'average_wait_time': average_wait_time,
            'in_session': request.user.profile.in_session,
            'notifications': ntfs,
        }, RequestContext(request))


@login_required()
@user_passes_test(association_check, login_url='/oauth/')
@identity_check
@require_POST
def appointment_actions(request, app):
    user = request.user
    appointments = drchrono.helpers.request_handler.get_appointments(user)
    option = request.POST['option']

    try:
        target_app = appointments.get(pk=app)
    except Appointments.DoesNotExist:
        return Http404('Can\'t find appointment')
    if option == 'start':
        if user.profile.in_session:
            return HttpResponseBadRequest('In session')
        user.profile.in_session = app
        time_handler.start_clock(target_app)
        status = 'In Room'
    elif option == 'end':
        if not user.profile.in_session:
            return HttpResponseBadRequest('No session')
        user.profile.in_session = None
        time_handler.stop_clock(target_app)
        status = 'Complete'
    else:
        return HttpResponseBadRequest('Bad action request')
    user.save()
    params = {
        'status': status,
        'appointment': app
    }
    res, content = request_handler.appointment_request(request.user, params, method='PATCH')
    if res.status_code >= 400:
        return HttpResponse(helper.get_error_msg(res.status_code, content), status=res.status_code)
    target_app.status = status
    target_app.save()
    return HttpResponse(option + 'succeed')


@login_required
@user_passes_test(association_check, login_url='/oauth/')
@require_http_methods(["GET", "POST"])
def check_in(request):
    if 'appointment' in request.session:
        del request.session['appointment']
    appointments = drchrono.helpers.request_handler.get_appointments(request.user)
    if request.method == 'GET':
        form = CheckInForm()
        return render_to_response('check_in.html', {
            'form': form,
            'identity': request.session['identity'] == 'doctor'
        }, RequestContext(request))
    else:
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        ssn = request.POST['ssn'].strip()

        args = {
            'time': settings.REDIRECT_TIME,
            'first_name': first_name,
            'last_name': last_name,
        }
        apps = appointments.filter(
            Q(status__in=['Confirmed', 'Rescheduled', '', 'In Session', 'Arrived', 'In Room']) |
            Q(status__isnull=True)).filter(scheduled_time__gte=datetime.now())
        if len(first_name) > 0 and len(last_name) > 0:
            apps = apps.filter(patient__last_name__iexact=last_name,
                               patient__first_name__iexact=first_name)
        if ssn is not None and ssn != '':
            s = filter(lambda x: x in '0123456789', ssn)
            # assert isinstance(s, str)
            apps = apps.filter(patient__ssn=(s[:3] + '-' + s[3:5] + '-' + s[5:]))

        l = len(apps)
        if l < 1:
            messages.error(request, 'No appointment find')
        # elif l > 1:
        #     messages.error(request, 'Can not target patient')
        elif len(apps.filter(status__in=['Arrived', 'In Room'])) > 0:
            messages.error(request, 'You\'ve already checked in')
        else:
            appointment = apps[0]
            request.session['appointment'] = appointment.pk
            try:
                patient = Patient.objects.get(pk=appointment.patient_id)
                messages.success(request, 'Welcome, {0} {1}!'.format(patient.first_name, patient.last_name))
            except Patient.DoesNotExist:
                messages.error(request, 'Cannot find corresponding patient')
            return redirect('/update/')
        return render_to_response('check_in_result.html', args, RequestContext(request))


@login_required()
@user_passes_test(association_check, login_url='/oauth/')
@require_http_methods(["GET", "POST"])
def update(request):
    if 'appointment' not in request.session:
        return redirect('/checkin/')
    appointment_id = request.session['appointment']
    try:
        app = Appointments.objects.get(pk=appointment_id)
    except Appointments.DoesNotExist:
        return HttpResponseBadRequest('Cannot find target appointment')
    p = app.patient
    if request.method == 'GET':
        form = UpdateForm(initial={
            'city': p.city,
            'date_of_birth': p.date_of_birth,
            'address': p.address,
            'cell_phone': p.cell_phone,
        })
        return render_to_response('update.html', {
            'form': form,
        }, RequestContext(request))
    else:
        has_error = True
        form = UpdateForm(request.POST)
        if form.is_valid() and helper.check_cell_phtone(request.POST['cell_phone']):
            params = {}
            params.update(form.cleaned_data)
            params['patient'] = p.pk
            res, content = request_handler.patients_request(request.user, params, method='PATCH')
            if res.status_code >= 400:
                messages.error(request, "Server error: {0} {1}".format(res.status_code, content))
            else:
                params = {
                    'status': 'Arrived',
                    'appointment': appointment_id
                }
                res, content = request_handler.appointment_request(request.user, params, method='PATCH')
                if res.status_code >= 400:
                    return HttpResponse(helper.get_error_msg(res.status_code, content), status=res.status_code)
                app.status = 'Arrived'
                app.start_wait_time = datetime.now()
                app.check_in_time = datetime.now()
                app.save()
                Patient.objects.filter(pk=p.patient_id).update(**form.cleaned_data)
                create_notification(app)
                # ntfs = Notification.objects.filter(user=request.user, tag=Notification.INFO)
                # helper.print_info('ntfs in update', len(ntfs), len(Notification.objects.all()))
                has_error = False
                messages.success(request, "You've successfully checked in for appointment scheduled at {0}".format(
                    app.scheduled_time.strftime(settings.DISPLAY_DATETIME_FORMAT)))
        else:
            messages.error(request, "Invalid info, phone number should be 10 digits number")
        return render_to_response('update_result.html', {
            'time': settings.REDIRECT_TIME,
            'has_error': has_error
        }, RequestContext(request))
